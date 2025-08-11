#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import mimetypes
import os
import posixpath
from urllib.parse import quote

from django.core.files.uploadhandler import StopUpload
from django.core.paginator import EmptyPage, Paginator
from django.http import HttpResponse, HttpResponseNotModified, HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from django.utils.http import http_date
from django.views.static import was_modified_since
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.exceptions import APIException, NotFound
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from aws.s3.s3fs import get_s3_home_directory, S3ListAllBucketsException
from azure.abfs.__init__ import get_abfs_home_directory
from desktop.auth.backend import is_admin
from desktop.conf import TASK_SERVER_V2
from desktop.lib import fsmanager, i18n
from desktop.lib.conf import coerce_bool
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.export_csvxls import file_reader
from desktop.lib.fs.gc.gs import get_gs_home_directory, GSListAllBucketsException
from desktop.lib.fs.ozone.ofs import get_ofs_home_directory
from desktop.lib.i18n import smart_str
from desktop.lib.tasks.compress_files.compress_utils import compress_files_in_hdfs
from desktop.lib.tasks.extract_archive.extract_utils import extract_archive_in_hdfs
from filebrowser.conf import (
  ENABLE_EXTRACT_UPLOADED_ARCHIVE,
  FILE_DOWNLOAD_CACHE_CONTROL,
  REDIRECT_DOWNLOAD,
  SHOW_DOWNLOAD_BUTTON,
)
from filebrowser.lib.rwx import compress_mode, filetype, rwx
from filebrowser.operations import rename_file_or_directory
from filebrowser.schemas import RenameSchema
from filebrowser.serializers import RenameSerializer, UploadFileSerializer
from filebrowser.utils import get_user_fs, parse_broker_url
from filebrowser.views import (
  _can_inline_display,
  _is_hdfs_superuser,
  _normalize_path,
  DEFAULT_CHUNK_SIZE_BYTES,
  extract_upload_data,
  MAX_CHUNK_SIZE_BYTES,
  perform_upload_task,
  read_contents,
  stat_absolute_path,
)
from hadoop.conf import is_hdfs_trash_enabled
from hadoop.fs.exceptions import WebHdfsException
from hadoop.fs.fsutils import do_overwrite_save
from useradmin.models import Group, User

LOG = logging.getLogger()


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    response = {}
    try:
      return view_fn(*args, **kwargs)
    except Exception as e:
      LOG.exception("Error running %s" % view_fn)
      response["status"] = -1
      response["message"] = smart_str(e)
    return JsonResponse(response)

  return decorator


# Deprecated in favor of get_all_filesystems method for new filebrowser
@error_handler
def get_filesystems(request):
  response = {}

  filesystems = {}
  for k in fsmanager.get_filesystems(request.user):
    filesystems[k] = True

  response["status"] = 0
  response["filesystems"] = filesystems

  return JsonResponse(response)


# TODO: Improve error response further with better context -- Error UX Phase 2
def api_error_handler(view_fn):
  """
  Decorator to handle exceptions and return a JSON response with an error message.
  """

  def decorator(*args, **kwargs):
    try:
      return view_fn(*args, **kwargs)
    except Exception as e:
      LOG.exception(f"Error running {view_fn.__name__}: {str(e)}")
      return JsonResponse({"error": str(e)}, status=500)

  return decorator


def _get_hdfs_home_directory(user):
  return user.get_home_directory()


def _get_config(fs, request):
  config = {}
  if fs == "hdfs":
    is_hdfs_superuser = _is_hdfs_superuser(request)
    config = {
      "is_trash_enabled": is_hdfs_trash_enabled(),
      # TODO: Check if any of the below fields should be part of new Hue user and group management APIs
      "is_hdfs_superuser": is_hdfs_superuser,
      "groups": [str(x) for x in Group.objects.values_list("name", flat=True)] if is_hdfs_superuser else [],
      "users": [str(x) for x in User.objects.values_list("username", flat=True)] if is_hdfs_superuser else [],
      "superuser": request.fs.superuser,
      "supergroup": request.fs.supergroup,
    }
  return config


@api_error_handler
def get_all_filesystems(request):
  """
  Retrieves all configured filesystems along with user-specific configurations.

  This endpoint collects information about available filesystems (e.g., HDFS, S3, GS, etc.),
  user home directories, and additional configurations specific to each filesystem type.

  Args:
    request (HttpRequest): The incoming HTTP request object.

  Returns:
    JsonResponse: A JSON response containing a list of filesystems with their configurations.
  """
  fs_home_dir_mapping = {
    "hdfs": _get_hdfs_home_directory,
    "s3a": get_s3_home_directory,
    "gs": get_gs_home_directory,
    "abfs": get_abfs_home_directory,
    "ofs": get_ofs_home_directory,
  }

  filesystems = []
  for fs in fsmanager.get_filesystems(request.user):
    user_home_dir = fs_home_dir_mapping[fs](request.user)
    config = _get_config(fs, request)

    filesystems.append({"name": fs, "user_home_directory": user_home_dir, "config": config})

  return JsonResponse(filesystems, safe=False)


@api_error_handler
def download(request):
  """
  Downloads a file.

  This is inspired by django.views.static.serve (?disposition={attachment, inline})

  Args:
    request: The current request object

  Returns:
    A response object with the file contents or an error message
  """
  path = request.GET.get("path")
  path = _normalize_path(path)

  if not SHOW_DOWNLOAD_BUTTON.get():
    return HttpResponse("Download operation is not allowed.", status=403)

  if not request.fs.exists(path):
    return HttpResponse(f"File does not exist: {path}", status=404)

  if not request.fs.isfile(path):
    return HttpResponse(f"{path} is not a file.", status=400)

  content_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
  stats = request.fs.stats(path)
  if not was_modified_since(request.META.get("HTTP_IF_MODIFIED_SINCE"), stats["mtime"]):
    return HttpResponseNotModified()

  fh = request.fs.open(path)

  # First, verify read permissions on the file.
  try:
    request.fs.read(path, offset=0, length=1)
  except WebHdfsException as e:
    if e.code == 403:
      return HttpResponse(f"User {request.user.username} is not authorized to download file at path: {path}", status=403)
    elif request.fs._get_scheme(path).lower() == "abfs" and e.code == 416:
      # Safe to skip ABFS exception of code 416 for zero length objects, file will get downloaded anyway.
      LOG.debug("Skipping exception from ABFS:" + str(e))
    else:
      return HttpResponse(f"Failed to download file at path {path}: {str(e)}", status=500)  # TODO: status code?

  if REDIRECT_DOWNLOAD.get() and hasattr(fh, "read_url"):
    response = HttpResponseRedirect(fh.read_url())
    setattr(response, "redirect_override", True)
  else:
    response = StreamingHttpResponse(file_reader(fh), content_type=content_type)

    content_disposition = (
      request.GET.get("disposition") if request.GET.get("disposition") == "inline" and _can_inline_display(path) else "attachment"
    )

    # Extract filename for HDFS and OFS for now because the path stats object has a bug in fetching name field
    # TODO: Fix this super old bug when refactoring the underlying HDFS filesystem code
    filename = os.path.basename(path) if request.fs._get_scheme(path).lower() in ("hdfs", "ofs") else stats["name"]

    # Set the filename in the Content-Disposition header with proper encoding for special characters
    encoded_filename = quote(filename)
    response["Content-Disposition"] = f"{content_disposition}; filename*=UTF-8''{encoded_filename}"

    response["Last-Modified"] = http_date(stats["mtime"])
    response["Content-Length"] = stats["size"]

    if FILE_DOWNLOAD_CACHE_CONTROL.get():
      response["Cache-Control"] = FILE_DOWNLOAD_CACHE_CONTROL.get()

  request.audit = {
    "operation": "DOWNLOAD",
    "operationText": 'User %s downloaded file at path "%s"' % (request.user.username, path),
    "allowed": True,
  }

  return response


def _massage_page(page, paginator):
  return {"page_number": page.number, "page_size": paginator.per_page, "total_pages": paginator.num_pages, "total_size": paginator.count}


@api_error_handler
def listdir_paged(request):
  """
  A paginated version of listdir.

  Query parameters:
    pagenum (int): The page number to show. Defaults to 1.
    pagesize (int): How many items to show on a page. Defaults to 30.
    sortby (str): The attribute to sort by. Valid options: 'type', 'name', 'atime', 'mtime', 'user', 'group', 'size'.
                  Defaults to 'name'.
    descending (bool): Sort in descending order when true. Defaults to false.
    filter (str): Substring to filter filenames. Optional.

  Returns:
    JsonResponse: Contains 'files' and 'page' info.

  Raises:
    HttpResponse: With appropriate status codes for errors.
  """
  path = request.GET.get("path", "/")  # Set default path for index directory
  path = _normalize_path(path)

  if not request.fs.isdir(path):
    return HttpResponse(f"{path} is not a directory.", status=400)

  # Extract pagination parameters
  pagenum = int(request.GET.get("pagenum", 1))
  pagesize = int(request.GET.get("pagesize", 30))

  # Determine if operation should be performed as another user
  do_as = None
  if is_admin(request.user) or request.user.has_hue_permission(action="impersonate", app="security"):
    do_as = request.GET.get("doas", request.user.username)
  if hasattr(request, "doas"):
    do_as = request.doas

  # Get stats for all files in the directory
  try:
    if do_as:
      all_stats = request.fs.do_as_user(do_as, request.fs.listdir_stats, path)
    else:
      all_stats = request.fs.listdir_stats(path)
  except (S3ListAllBucketsException, GSListAllBucketsException) as e:
    return HttpResponse(f"Bucket listing is not allowed: {e}", status=403)

  # Apply filter first if specified
  filter_string = request.GET.get("filter")
  if filter_string:
    all_stats = [sb for sb in all_stats if filter_string in sb["name"]]

  # Next, sort with proper handling of None values
  sortby = request.GET.get("sortby", "name")
  descending = coerce_bool(request.GET.get("descending", False))
  valid_sort_fields = {"type", "name", "atime", "mtime", "user", "group", "size"}

  if sortby not in valid_sort_fields:
    LOG.info(f"Ignoring invalid sort attribute '{sortby}' for list directory operation.")
  else:
    numeric_fields = {"size", "atime", "mtime"}

    def sorting_key(item):
      """Generate a sorting key that handles None values for different field types."""
      value = getattr(item, sortby)
      if sortby in numeric_fields:
        # Treat None as 0 for numeric fields for comparison
        return 0 if value is None else value
      else:
        # Treat None as an empty string for non-numeric fields
        return "" if value is None else value

    try:
      all_stats = sorted(all_stats, key=sorting_key, reverse=descending)
    except Exception as sort_error:
      LOG.error(f"Error during sorting with attribute '{sortby}': {sort_error}")
      return HttpResponse("An error occurred while sorting the directory contents.", status=500)

  # Do pagination
  try:
    paginator = Paginator(all_stats, pagesize, allow_empty_first_page=True)
    page = paginator.page(pagenum)
    shown_stats = page.object_list
  except EmptyPage:
    message = "No results found for the requested page."
    LOG.warning(message)
    return HttpResponse(message, status=404)

  if page:
    page.object_list = [_massage_stats(request, stat_absolute_path(path, s)) for s in shown_stats]

  response = {"files": page.object_list if page else [], "page": _massage_page(page, paginator) if page else {}}

  return JsonResponse(response)


@api_error_handler
def display(request):
  """
  Implements displaying part of a file.

  GET arguments are length, offset, mode, compression and encoding
  with reasonable defaults chosen.

  Note that display by length and offset are on bytes, not on characters.
  """
  path = request.GET.get("path", "/")  # Set default path for index directory
  path = _normalize_path(path)

  if not request.fs.isfile(path):
    return HttpResponse(f"{path} is not a file.", status=400)

  encoding = request.GET.get("encoding") or i18n.get_site_encoding()

  # Need to deal with possibility that length is not present
  # because the offset came in via the toolbar manual byte entry.
  end = request.GET.get("end")
  if end:
    end = int(end)

  begin = request.GET.get("begin", 1)
  if begin:
    # Subtract one to zero index for file read
    begin = int(begin) - 1

  if end:
    offset = begin
    length = end - begin
    if begin >= end:
      return HttpResponse("First byte to display must be before last byte to display.", status=400)
  else:
    length = int(request.GET.get("length", DEFAULT_CHUNK_SIZE_BYTES))
    # Display first block by default.
    offset = int(request.GET.get("offset", 0))

  mode = request.GET.get("mode")
  compression = request.GET.get("compression")

  if mode and mode != "text":
    return HttpResponse("Mode value must be 'text'.", status=400)
  if offset < 0:
    return HttpResponse("Offset may not be less than zero.", status=400)
  if length < 0:
    return HttpResponse("Length may not be less than zero.", status=400)
  if length > MAX_CHUNK_SIZE_BYTES:
    return HttpResponse(f"Cannot request chunks greater than {MAX_CHUNK_SIZE_BYTES} bytes.", status=400)

  # Read out based on meta.
  _, offset, length, contents = read_contents(compression, path, request.fs, offset, length)

  # Get contents as string for text mode, or at least try
  file_contents = None
  if isinstance(contents, str):
    file_contents = contents
    mode = "text"
  else:
    try:
      file_contents = contents.decode(encoding)
      mode = "text"
    except UnicodeDecodeError:
      LOG.error("Cannot decode file contents with encoding: %s." % encoding)
      return HttpResponse("Cannot display file content. Please download the file instead.", status=422)

  data = {
    "contents": file_contents,
    "offset": offset,
    "length": length,
    "end": offset + len(contents),
    "mode": mode,
  }

  return JsonResponse(data)


@api_error_handler
def stat(request):
  """
  Returns the generic stats of FS object.
  """
  path = request.GET.get("path")
  path = _normalize_path(path)

  if not request.fs.exists(path):
    return HttpResponse(f"Object does not exist: {path}", status=404)

  stats = request.fs.stats(path)

  return JsonResponse(_massage_stats(request, stat_absolute_path(path, stats)))


@api_error_handler
def upload_chunks(request):
  """
  Handles chunked file uploads using FineUploaderChunkedUploadHandler.

  This method processes the chunked file uploads and checks if the file is larger
  than the single chunk size. If the file is larger, it returns a JSON response
  with the UUID of the file. If the file is smaller, it extracts the upload data
  and performs the upload task.

  Args:
    request (HttpRequest): The HTTP request object containing the chunked file.

  Returns:
    HttpResponse: A JSON response with the UUID of the file if the file is larger
      than the single chunk size, or a JSON response with the result of the
      upload task if the file is smaller. If an error occurs, returns an HTTP
      response with a 500 status code and an error message.

  Raises:
    StopUpload: If an error occurs during chunk file upload.

  Notes:
    This method expects the following parameters in the request:
      - `qqtotalparts` (int): The total number of parts in the chunked file.
      - `qquuid` (str): The UUID of the file.
  """
  try:
    # Process the chunked file uploads using FineUploaderChunkedUploadHandler
    for _ in request.FILES.values():
      pass
  except StopUpload as e:
    error_message = "Error occurred during chunk file upload."
    LOG.error(f"{error_message} {str(e)}")
    return HttpResponse(error_message, status=500)

  # Check if the file is larger than the single chunk size
  total_parts = int(request.GET.get("qqtotalparts", 0))
  if total_parts > 0:
    return JsonResponse({"uuid": request.GET.get("qquuid")})

  # Check if the file is smaller than the chunk size
  elif total_parts == 0:
    try:
      chunks = extract_upload_data(request, "GET")
      response = perform_upload_task(request, **chunks)
      return JsonResponse(response)

    except Exception as e:
      error_message = "Error occurred during chunk file upload."
      LOG.error(f"{error_message} {str(e)}")
      return HttpResponse(error_message, status=500)


@api_error_handler
def upload_complete(request):
  """
  Handles the completion of a file upload.

  Args:
    request (HttpRequest): The HTTP request object.

  Returns:
    JsonResponse: A JSON response containing the result of the upload.
  """
  try:
    chunks = extract_upload_data(request, "POST")
    response = perform_upload_task(request, **chunks)

    return JsonResponse(response)
  except Exception as e:
    error_message = "Error occurred during chunk file upload completion."
    LOG.error(f"{error_message} {str(e)}")
    return HttpResponse(error_message, status=500)


class UploadFileAPI(APIView):
  parser_classes = [MultiPartParser]

  def dispatch(self, request, *args, **kwargs):
    """
    Overrides dispatch to perform manual authentication and set a dynamic upload handler.

    This is necessary to solve a lifecycle conflict where user authentication
    (from a JWT token) must happen before DRF's parsing is triggered, but
    the upload handler must be set before the request body is read.

    Exception handling within this method is done using Django's standard
    `JsonResponse` instead of DRF's `Response`. This is a deliberate
    choice to bypass the DRF rendering lifecycle, which is not fully
    initialized at this early stage and would otherwise cause errors.
    """
    # Manually perform authentication if the user is not already authenticated
    # by a preceding middleware (like SessionMiddleware).
    if not request.user.is_authenticated:
      LOG.debug("User not authenticated, attempting manual authentication in UploadFileAPI.dispatch...")
      try:
        # Use the view's configured authenticators to check for credentials (e.g., JWT).
        for authenticator in self.get_authenticators():
          user_auth_tuple = authenticator.authenticate(request)
          if user_auth_tuple is not None:
            # On successful authentication, attach the user to the request.
            request.user, request.auth = user_auth_tuple
            LOG.debug(f"Manual authentication successful for user '{request.user.username}'.")
            break
      except APIException as e:
        # If authentication itself fails (e.g., invalid token), return an error.
        LOG.warning(f"Manual authentication failed in UploadFileAPI.dispatch: {e.detail}")
        return JsonResponse(e.detail, status=e.status_code)

    # After authentication, we can now proceed with the main logic.
    if not request.user.is_authenticated:
      # If still not authenticated, it's a genuine credentials issue.
      return JsonResponse({"error": "Authentication credentials were not provided or were invalid."}, status=status.HTTP_401_UNAUTHORIZED)

    try:
      # IMPORTANT: Validate query parameters from request.GET for upload handler configuration.
      serializer = UploadFileSerializer(data=request.GET)
      serializer.is_valid(raise_exception=True)
      validated_data = serializer.validated_data
      username = request.user.username

      destination_path = validated_data["destination_path"]
      overwrite = validated_data["overwrite"]

      LOG.debug(f"Dispatching upload for user '{username}' to '{destination_path}' (overwrite: {overwrite}).")

      # Retrieve user-specific filesystem and the appropriate handler.
      fs = get_user_fs(username)
      upload_handler = fs.get_upload_handler(destination_path, overwrite)

      if not upload_handler:
        LOG.error(f"No supported upload handler found for user '{username}' at path: {destination_path}")
        raise NotFound({"error": f"No supported upload handler found for path: {destination_path}"})

      LOG.info(f"Applying upload handler '{upload_handler.__class__.__name__}' for user '{username}'.")
      request.upload_handlers = [upload_handler]

    except APIException as e:
      LOG.warning(f"API Exception during upload setup in UploadFileAPI.dispatch: {e.detail}")
      return JsonResponse(e.detail, status=e.status_code)
    except Exception as e:
      LOG.exception(f"An unexpected error occurred while setting the upload handler in UploadFileAPI.dispatch: {e}")
      return JsonResponse({"error": "A server error occurred during upload initialization."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # IMPORTANT: After setup, continue to the standard DRF dispatch process.
    return super().dispatch(request, *args, **kwargs)

  def post(self, request, *args, **kwargs):
    """Handles the file upload response after the upload handler has done its work.

    This method is called after the upload handler has uploaded the file.
    request.FILES now contains the metadata dict returned by the upload handler.
    """
    try:
      uploaded_file = request.FILES.get("file")

      LOG.debug(f"Retrieved uploaded file metadata: {type(uploaded_file)}")

      if not isinstance(uploaded_file, dict):
        LOG.error(f"Invalid upload response - expected dict, got: {type(uploaded_file)}")
        return Response(
          {"error": "File upload failed or was not handled correctly by the upload handler."}, status=status.HTTP_400_BAD_REQUEST
        )

      LOG.info("File upload completed successfully")
      response_data = {"file_stats": uploaded_file}

      return Response(response_data, status=status.HTTP_201_CREATED)

    except PopupException as e:
      LOG.exception(f"Upload failed with PopupException: {e.message} (code: {e.error_code})")
      return Response({"error": e.message}, status=e.error_code)
    except Exception as e:
      LOG.exception(f"Unexpected error in UploadFileAPI.post: {e}")
      return Response({"error": "An unexpected error occurred while uploading the file."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_error_handler
def mkdir(request):
  """
  Create a new directory at the specified path with the given name.

  Args:
    request (HttpRequest): The HTTP request object containing the data.

  Returns:
    A HttpResponse with a status code and message indicating the success or failure of the directory creation.
  """
  # TODO: Check if this needs to be a PUT request
  path = request.POST.get("path")
  name = request.POST.get("name")

  # Check if path and name are provided
  if not path or not name:
    return HttpResponse("Missing required parameters: path and name are required.", status=400)

  # Validate the 'name' parameter for invalid characters
  if posixpath.sep in name or "#" in name:
    return HttpResponse("Slashes or hashes are not allowed in directory name. Please choose a different name.", status=400)

  dir_path = request.fs.join(path, name)

  # Check if the directory already exists
  if request.fs.isdir(dir_path):
    return HttpResponse(f"Error creating {name} directory: Directory already exists.", status=409)

  request.fs.mkdir(dir_path)
  return HttpResponse(status=201)


@api_error_handler
def touch(request):
  path = request.POST.get("path")
  name = request.POST.get("name")

  # Check if path and name are provided
  if not path or not name:
    return HttpResponse("Missing parameters: path and name are required.", status=400)

  # Validate the 'name' parameter for invalid characters
  if name and (posixpath.sep in name):
    return HttpResponse("Slashes are not allowed in filename. Please choose a different name.", status=400)

  file_path = request.fs.join(path, name)

  # Check if the file already exists
  if request.fs.isfile(file_path):
    return HttpResponse(f"Error creating {name} file: File already exists.", status=409)

  request.fs.create(file_path)
  return HttpResponse(status=201)


@api_error_handler
def save_file(request):
  """
  The POST endpoint to save a file in the file editor.

  Does the save and then redirects back to the edit page.
  """
  path = request.POST.get("path")
  path = _normalize_path(path)

  encoding = request.POST.get("encoding")
  data = request.POST.get("contents").encode(encoding)

  if not path:
    return HttpResponse("Path parameter is required for saving the file.", status=400)

  try:
    if request.fs.exists(path):
      do_overwrite_save(request.fs, path, data)
    else:
      request.fs.create(path, overwrite=False, data=data)
  except Exception as e:
    return HttpResponse(f"The file could not be saved: {str(e)}", status=500)  # TODO: Status code?

  # TODO: Any response field required?
  return HttpResponse(status=200)


@api_view(["POST"])
@parser_classes([JSONParser])
def rename(request):
  """
  Rename a file or directory.

  This endpoint renames a file or directory from a source path to a destination path.
  The destination can be an absolute path or a relative path from the source's parent directory.

  Args:
    request (HttpRequest): The request object containing source and destination paths.

  Returns:
    Response: A Response object with a success message or an error message with the appropriate status code.
  """
  serializer = RenameSerializer(data=request.data)

  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  rename_params = RenameSchema(**serializer.validated_data)
  try:
    result = rename_file_or_directory(data=rename_params, username=request.user.username)
    return Response(result, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    LOG.exception(f"Error renaming file: {e}")
    return Response({"error": "An unexpected error occurred during rename operation"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _is_destination_parent_of_source(request, source_path, destination_path):
  """Check if the destination path is the parent directory of the source path."""
  return request.fs.parent_path(source_path) == request.fs.normpath(destination_path)


def _validate_copy_move_operation(request, source_path, destination_path):
  """Validate the input parameters for copy and move operations for different scenarios."""

  # Check if source and destination paths are provided
  if not source_path or not destination_path:
    return HttpResponse("Missing required parameters: source_path and destination_path are required.", status=400)

  # Check if paths are identical
  if request.fs.normpath(source_path) == request.fs.normpath(destination_path):
    return HttpResponse("Source and destination paths must be different.", status=400)

  # Verify source path exists
  if not request.fs.exists(source_path):
    return HttpResponse("Source file or folder does not exist.", status=404)

  # Check if the destination path is a directory
  if not request.fs.isdir(destination_path):
    return HttpResponse("Destination path must be a directory.", status=400)

  # Check if destination path is parent of source path
  if _is_destination_parent_of_source(request, source_path, destination_path):
    return HttpResponse("Destination cannot be the parent directory of source.", status=400)

  # Check if file or folder already exists at destination path
  if request.fs.exists(request.fs.join(destination_path, os.path.basename(source_path))):
    return HttpResponse("File or folder already exists at destination path.", status=409)


@api_error_handler
def move(request):
  """
  Move a file or folder from source path to destination path.

  Args:
    request: The request object containing source and destination paths

  Returns:
    Success or error response with appropriate status codes
  """
  source_path = request.POST.get("source_path", "")
  destination_path = request.POST.get("destination_path", "")

  # Validate the operation and return error response if any scenario fails
  validation_response = _validate_copy_move_operation(request, source_path, destination_path)
  if validation_response:
    return validation_response

  request.fs.rename(source_path, destination_path)
  return HttpResponse(status=200)


@api_error_handler
def copy(request):
  """
  Copy a file or folder from the source path to the destination path.

  Args:
    request: The request object containing source and destination path

  Returns:
    Success or error response with appropriate status codes
  """
  source_path = request.POST.get("source_path", "")
  destination_path = request.POST.get("destination_path", "")

  # Validate the operation and return error response if any scenario fails
  validation_response = _validate_copy_move_operation(request, source_path, destination_path)
  if validation_response:
    return validation_response

  # Copy method for Ozone FS returns a string of skipped files if their size is greater than configured chunk size.
  if source_path.startswith("ofs://"):
    ofs_skip_files = request.fs.copy(source_path, destination_path, recursive=True, owner=request.user)
    if ofs_skip_files:
      return JsonResponse({"skipped_files": ofs_skip_files}, status=500)  # TODO: Status code?
  else:
    request.fs.copy(source_path, destination_path, recursive=True, owner=request.user)

  return HttpResponse(status=200)


@api_error_handler
def content_summary(request):
  path = request.GET.get("path")
  path = _normalize_path(path)

  if not path:
    return HttpResponse("Path parameter is required to fetch content summary.", status=400)

  if not request.fs.exists(path):
    return HttpResponse(f"Path does not exist: {path}", status=404)

  response = {}
  try:
    content_summary = request.fs.get_content_summary(path)
    replication_factor = request.fs.stats(path)["replication"]

    content_summary.summary.update({"replication": replication_factor})
    response = content_summary.summary
  except Exception:
    return HttpResponse(f"Failed to fetch content summary for path: {path}", status=500)

  return JsonResponse(response)


@api_error_handler
def set_replication(request):
  # TODO: Check if this needs to be a PUT request
  path = request.POST.get("path")
  replication_factor = request.POST.get("replication_factor")

  result = request.fs.set_replication(path, replication_factor)
  if not result:
    return HttpResponse("Failed to set the replication factor.", status=500)

  return HttpResponse(status=200)


@api_error_handler
def rmtree(request):
  # TODO: Check if this needs to be a DELETE request
  path = request.POST.get("path")
  skip_trash = coerce_bool(request.POST.get("skip_trash", False))

  request.fs.rmtree(path, skip_trash)

  return HttpResponse(status=200)


@api_error_handler
def get_trash_path(request):
  path = request.GET.get("path")
  path = _normalize_path(path)
  response = {}

  trash_path = request.fs.trash_path(path)
  user_home_trash_path = request.fs.join(request.fs.current_trash_path(trash_path), request.user.get_home_directory().lstrip("/"))

  if request.fs.isdir(user_home_trash_path):
    response["trash_path"] = user_home_trash_path
  elif request.fs.isdir(trash_path):
    response["trash_path"] = trash_path
  else:
    response["trash_path"] = None

  return JsonResponse(response)


@api_error_handler
def trash_restore(request):
  path = request.POST.get("path")
  request.fs.restore(path)

  return HttpResponse(status=200)


@api_error_handler
def trash_purge(request):
  request.fs.purge_trash()

  return HttpResponse(status=200)


@api_error_handler
def chown(request):
  # TODO: Check if this needs to be a PUT request
  path = request.POST.get("path")
  user = request.POST.get("user")
  group = request.POST.get("group")
  recursive = coerce_bool(request.POST.get("recursive", False))

  # TODO: Check if we need to explicitly handle encoding anywhere
  request.fs.chown(path, user, group, recursive=recursive)

  return HttpResponse(status=200)


@api_error_handler
def chmod(request):
  # TODO: Check if this needs to be a PUT request
  # Order matters for calculating mode below
  perm_names = (
    "user_read",
    "user_write",
    "user_execute",
    "group_read",
    "group_write",
    "group_execute",
    "other_read",
    "other_write",
    "other_execute",
    "sticky",
  )
  path = request.POST.get("path")
  permission = json.loads(request.POST.get("permission", "{}"))

  mode = compress_mode([coerce_bool(permission.get(p)) for p in perm_names])

  request.fs.chmod(path, mode, recursive=coerce_bool(permission.get("recursive", False)))

  return HttpResponse(status=200)


@api_error_handler
def extract_archive_using_batch_job(request):
  # TODO: Check core logic with E2E tests -- dont use it until then
  if not ENABLE_EXTRACT_UPLOADED_ARCHIVE.get():
    return HttpResponse("Extract archive operation is disabled by configuration.", status=500)  # TODO: status code?

  upload_path = request.fs.netnormpath(request.POST.get("upload_path"))
  archive_name = request.POST.get("archive_name")

  if upload_path and archive_name:
    try:
      # TODO: Check is we really require urllib_unquote here? Maybe need to improve old oozie methods also?
      # upload_path = urllib_unquote(upload_path)
      # archive_name = urllib_unquote(archive_name)
      response = extract_archive_in_hdfs(request, upload_path, archive_name)
    except Exception as e:
      return HttpResponse(f"Failed to extract archive: {str(e)}", status=500)  # TODO: status code?

  return JsonResponse(response)


@api_error_handler
def compress_files_using_batch_job(request):
  # TODO: Check core logic with E2E tests -- dont use it until then
  if not ENABLE_EXTRACT_UPLOADED_ARCHIVE.get():
    return HttpResponse("Compress files operation is disabled by configuration.", status=500)  # TODO: status code?

  upload_path = request.fs.netnormpath(request.POST.get("upload_path"))
  archive_name = request.POST.get("archive_name")
  file_names = request.POST.getlist("file_name")

  if upload_path and file_names and archive_name:
    try:
      response = compress_files_in_hdfs(request, file_names, upload_path, archive_name)
    except Exception as e:
      return HttpResponse(f"Failed to compress files: {str(e)}", status=500)  # TODO: status code?
  else:
    return HttpResponse("Output directory is not set.", status=500)  # TODO: status code?

  return JsonResponse(response)


@api_error_handler
def get_available_space_for_upload(request):
  redis_client = parse_broker_url(TASK_SERVER_V2.BROKER_URL.get())
  try:
    upload_available_space = int(redis_client.get("upload_available_space"))
    if upload_available_space is None:
      return HttpResponse("upload_available_space key is not set in Redis.", status=500)  # TODO: status code?

    return JsonResponse({"upload_available_space": upload_available_space})
  except Exception as e:
    message = f"Failed to get available space from Redis: {str(e)}"
    LOG.exception(message)
    return HttpResponse(message, status=500)  # TODO: status code?
  finally:
    redis_client.close()


@api_error_handler
def bulk_op(request, op):
  # TODO: Also try making a generic request data fetching helper method
  bulk_dict = request.POST.copy()
  path_list = request.POST.getlist("source_path") if op in (copy, move) else request.POST.getlist("path")

  error_dict = {}
  for p in path_list:
    tmp_dict = bulk_dict
    if op in (copy, move):
      tmp_dict["source_path"] = p
    else:
      tmp_dict["path"] = p

    request.POST = tmp_dict
    response = op(request)

    if response.status_code != 200:
      # TODO: Improve the error handling with new error UX
      # Currently, we are storing the error in the error_dict based on response type for each path
      res_content = response.content.decode("utf-8")
      if isinstance(response, JsonResponse):
        error_dict[p] = json.loads(res_content)  # Simply assign to not have dupicate error fields
      else:
        error_dict[p] = {"error": res_content}

  if error_dict:
    return JsonResponse(error_dict, status=500)  # TODO: Check if we need diff status code or diff json structure?

  return HttpResponse(status=200)  # TODO: Check if we need to send some message or diff status code?


def _massage_stats(request, stats):
  """
  Massage a stats record as returned by the filesystem implementation
  into the format that the views would like it in.
  """
  stats_dict = stats.to_json_dict()
  normalized_path = request.fs.normpath(stats_dict.get("path"))

  stats_dict.update(
    {
      "path": normalized_path,
      "type": filetype(stats.mode),
      "rwx": rwx(stats.mode, stats.aclBit),
    }
  )

  return stats_dict
