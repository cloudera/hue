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

import logging
import mimetypes
import os
import re
from urllib.parse import quote

from django.core.files.uploadhandler import StopUpload
from django.http import FileResponse, HttpResponse, HttpResponseNotModified, HttpResponseRedirect, JsonResponse
from django.utils.http import http_date
from django.views.static import was_modified_since
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.exceptions import APIException, NotFound
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from desktop.lib import fsmanager
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_str
from filebrowser.conf import FILE_DOWNLOAD_CACHE_CONTROL, REDIRECT_DOWNLOAD, SHOW_DOWNLOAD_BUTTON
from filebrowser.operations import (
  check_path_exists,
  compress_files,
  copy_paths,
  create_directory,
  create_file,
  delete_paths,
  extract_archive,
  get_all_filesystems as get_all_filesystems_operation,
  get_available_space_for_upload,
  get_file_contents,
  get_path_stats,
  get_trash_path,
  list_directory,
  move_paths,
  purge_trash,
  rename_file_or_directory,
  restore_from_trash,
  save_file,
  set_ownership,
  set_permissions,
  set_replication,
)
from filebrowser.schemas import (
  CheckExistsSchema,
  CompressFilesSchema,
  CopyOperationSchema,
  CreateDirectorySchema,
  CreateFileSchema,
  DeleteOperationSchema,
  ExtractArchiveSchema,
  GetFileContentsSchema,
  GetStatsSchema,
  GetTrashPathSchema,
  ListDirectorySchema,
  MoveOperationSchema,
  RenameSchema,
  SaveFileSchema,
  SetOwnershipSchema,
  SetPermissionsSchema,
  SetReplicationSchema,
  TrashRestoreSchema,
)
from filebrowser.serializers import (
  CheckExistsSerializer,
  CompressFilesSerializer,
  CopyOperationSerializer,
  CreateDirectorySerializer,
  CreateFileSerializer,
  DeleteOperationSerializer,
  DownloadFileSerializer,
  ExtractArchiveSerializer,
  GetFileContentsSerializer,
  GetStatsSerializer,
  GetTrashPathSerializer,
  ListDirectorySerializer,
  MoveOperationSerializer,
  RenameSerializer,
  SaveFileSerializer,
  SetOwnershipSerializer,
  SetPermissionsSerializer,
  SetReplicationSerializer,
  TrashRestoreSerializer,
  UploadFileSerializer,
)
from filebrowser.utils import get_user_fs
from filebrowser.views import _can_inline_display, _normalize_path, extract_upload_data, perform_upload_task

LOG = logging.getLogger()
RANGE_HEADER_RE = re.compile(r"bytes=(?P<start>\d+)-(?P<end>\d+)?")


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


@api_view(["GET"])
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
  try:
    result = get_all_filesystems_operation(username=request.user.username)
    return Response(result, status=status.HTTP_200_OK)

  except Exception as e:
    LOG.error(f"Error in get_all_filesystems API: {e}")
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


class FileAPI(APIView):
  """Handles all file-based operations like download and content retrieval."""

  def get(self, request):
    """
    Dispatches to file download or content retrieval based on 'op' parameter.
    - op=download: Streams the file for download, supporting range requests.
    - default (no 'op' specified): Returns a JSON object with a portion of the file's content.
    """
    op = request.query_params.get("op")

    if op == "download":
      serializer = DownloadFileSerializer(data=request.query_params)
      if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

      try:
        path = _normalize_path(serializer.validated_data["path"])
        fs = get_user_fs(request.user.username)

        if not SHOW_DOWNLOAD_BUTTON.get():
          LOG.warning(f"Download attempt blocked by configuration for user: {request.user.username}")
          return Response({"error": "Download operation is not allowed by system configuration"}, status=status.HTTP_403_FORBIDDEN)

        if not fs.exists(path) or not fs.isfile(path):
          LOG.info(f"Download attempt for non-existent or non-file path: {path} by user: {request.user.username}")
          return Response({"error": f"File does not exist at path: {path}"}, status=status.HTTP_404_NOT_FOUND)

        stats = fs.stats(path)

        if not fs.check_access(path, permission="READ"):
          LOG.error(f"Read permission denied for user {request.user.username} on path: {path}")
          return Response({"error": f"Permission denied: cannot access '{path}'"}, status=status.HTTP_403_FORBIDDEN)

        if_modified_since = request.META.get("HTTP_IF_MODIFIED_SINCE")
        if if_modified_since and not was_modified_since(if_modified_since, stats["mtime"]):
          return HttpResponseNotModified()

        content_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
        fh = fs.open(path)

        # Handle cloud storage redirects first (cloud storage optimization by pre-signed URLs)
        if REDIRECT_DOWNLOAD.get() and hasattr(fh, "read_url"):
          LOG.info(f"Redirecting download for file: {path} by user: {request.user.username}")
          response = HttpResponseRedirect(fh.read_url())
          setattr(response, "redirect_override", True)
        else:
          # Prepare common headers for file-based responses
          disposition = serializer.validated_data["disposition"]
          if disposition == "inline" and not _can_inline_display(path):
            disposition = "attachment"

          # TODO: Known issue - stats["name"] is buggy for these filesystems
          scheme = fs._get_scheme(path).lower()
          filename = os.path.basename(path) if scheme in ("hdfs", "ofs") else stats["name"]

          # Handle Range Requests for resumable downloads and video seeking
          range_header = request.META.get("HTTP_RANGE")
          range_match = RANGE_HEADER_RE.match(range_header) if range_header else None

          if range_match:
            start_byte = int(range_match.group("start"))
            end_byte = range_match.group("end")
            end_byte = int(end_byte) if end_byte else stats["size"] - 1

            if not (0 <= start_byte <= end_byte < stats["size"]):
              return Response({"error": "Requested range not satisfiable"}, status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

            fh.seek(start_byte)
            response = FileResponse(fh, status=status.HTTP_206_PARTIAL_CONTENT, content_type=content_type)
            response["Content-Range"] = f"bytes {start_byte}-{end_byte}/{stats['size']}"
            response["Content-Length"] = end_byte - start_byte + 1
          else:
            # Handle full file download using FileResponse for consistency
            response = FileResponse(fh, content_type=content_type)
            response["Content-Length"] = stats["size"]
            response["Accept-Ranges"] = "bytes"  # Advertise support for range requests

          # Apply common headers for both full and partial file responses
          response["Content-Disposition"] = f"{disposition}; filename*=UTF-8''{quote(filename)}"
          response["Last-Modified"] = http_date(stats["mtime"])
          if FILE_DOWNLOAD_CACHE_CONTROL.get():
            response["Cache-Control"] = FILE_DOWNLOAD_CACHE_CONTROL.get()

        request.audit = {
          "operation": "DOWNLOAD",
          "operationText": f'User {request.user.username} downloaded file at path "{path}"',
          "allowed": True,
        }
        LOG.info(f"File download initiated for '{path}' by user '{request.user.username}'")
        return response

      except ValueError as e:
        LOG.error(f"Invalid request parameters for download: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
      except Exception as e:
        LOG.exception(f"Unexpected error during file download of '{path}': {str(e)}")
        return Response({"error": "An unexpected error occurred during file download."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
      # Get file contents
      serializer = GetFileContentsSerializer(data=request.query_params)
      if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

      try:
        result = get_file_contents(data=GetFileContentsSchema(**serializer.validated_data), username=request.user.username)
        return Response(result, status=status.HTTP_200_OK)

      except FileNotFoundError as e:
        LOG.info(f"File not found during content retrieval: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
      except ValueError as e:
        LOG.warning(f"Bad request for file contents: {str(e)}")

        # Check for decoding error to return a more specific status code
        if "Cannot decode file" in str(e):
          return Response({"error": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
      except Exception as e:
        LOG.exception(f"Unexpected error during file content retrieval: {str(e)}")
        return Response({"error": "An unexpected error occurred while reading the file."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  def put(self, request):
    """
    Create a new file with optional initial content.

    Supports comprehensive validation, parent directory creation,
    and proper error handling with specific HTTP status codes.
    """
    serializer = CreateFileSerializer(data=request.data)
    if not serializer.is_valid():
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
      result = create_file(data=CreateFileSchema(**serializer.validated_data), username=request.user.username)
      return Response(result, status=status.HTTP_201_CREATED)

    except FileExistsError as e:
      LOG.info(f"File creation failed - file exists: {e}")
      return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
    except FileNotFoundError as e:
      LOG.info(f"File creation failed - parent directory not found: {e}")
      return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
      LOG.warning(f"File creation failed - validation error: {e}")
      return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except RuntimeError as e:
      LOG.error(f"File creation failed - runtime error: {e}")
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
      LOG.exception(f"Unexpected error creating file: {e}")
      return Response({"error": "An unexpected error occurred while creating the file."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  def patch(self, request):
    """
    Save/update file contents with comprehensive validation.

    Supports content size validation, encoding checks, parent directory creation,
    and proper error handling with specific HTTP status codes.
    """
    serializer = SaveFileSerializer(data=request.data)
    if not serializer.is_valid():
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
      result = save_file(data=SaveFileSchema(**serializer.validated_data), username=request.user.username)
      return Response(result, status=status.HTTP_200_OK)

    except FileNotFoundError as e:
      LOG.info(f"File save failed - parent directory not found: {e}")
      return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except UnicodeEncodeError as e:
      LOG.warning(f"File save failed - encoding error: {e}")
      return Response({"error": f"Content cannot be encoded with the specified encoding: {e}"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except ValueError as e:
      LOG.warning(f"File save failed - validation error: {e}")
      return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except RuntimeError as e:
      LOG.error(f"File save failed - runtime error: {e}")
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
      LOG.exception(f"Unexpected error saving file: {e}")
      return Response({"error": "An unexpected error occurred while saving the file."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DirectoryAPI(APIView):
  """
  Directory API handling comprehensive directory operations.

  Provides listing and creation functionality with enhanced error handling,
  detailed validation, and proper HTTP status code mapping.
  """

  def get(self, request):
    """
    List directory contents with advanced filtering and pagination.

    Supports comprehensive directory listing with security validation,
    permission checks, filtering, sorting, and pagination.
    """
    serializer = ListDirectorySerializer(data=request.query_params)
    if not serializer.is_valid():
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
      result = list_directory(data=ListDirectorySchema(**serializer.validated_data), username=request.user.username)
      return Response(result, status=status.HTTP_200_OK)

    except FileNotFoundError as e:
      LOG.info(f"Directory listing failed - directory not found: {e}")
      return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except PermissionError as e:
      LOG.warning(f"Directory listing failed - permission denied: {e}")
      return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
      LOG.warning(f"Directory listing failed - validation error: {e}")
      return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except RuntimeError as e:
      LOG.error(f"Directory listing failed - runtime error: {e}")
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
      LOG.exception(f"Unexpected error listing directory: {e}")
      return Response({"error": "An unexpected error occurred while listing the directory."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  def put(self, request):
    """
    Create a new directory with comprehensive validation.

    Supports directory creation with parent directory creation,
    permission setting, and proper error handling.
    """
    serializer = CreateDirectorySerializer(data=request.data)
    if not serializer.is_valid():
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
      result = create_directory(data=CreateDirectorySchema(**serializer.validated_data), username=request.user.username)
      return Response(result, status=status.HTTP_201_CREATED)

    except FileExistsError as e:
      LOG.info(f"Directory creation failed - already exists: {e}")
      return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
    except FileNotFoundError as e:
      LOG.info(f"Directory creation failed - parent directory not found: {e}")
      return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    except PermissionError as e:
      LOG.warning(f"Directory creation failed - permission denied: {e}")
      return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
      LOG.warning(f"Directory creation failed - validation error: {e}")
      return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except RuntimeError as e:
      LOG.error(f"Directory creation failed - runtime error: {e}")
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
      LOG.exception(f"Unexpected error creating directory: {e}")
      return Response({"error": "An unexpected error occurred while creating the directory."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PathStatsAPI(APIView):
  """Path statistics API."""

  def get(self, request):
    """Get path statistics."""
    serializer = GetStatsSerializer(data=request.query_params)
    if not serializer.is_valid():
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
      result = get_path_stats(data=GetStatsSchema(**serializer.validated_data), username=request.user.username)
      return Response(result, status=status.HTTP_200_OK)

    except ValueError as e:
      return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      LOG.exception(f"Error getting path stats: {e}")
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TrashAPI(APIView):
  """Trash API handling trash operations."""

  def get(self, request):
    """Get trash path information."""
    serializer = GetTrashPathSerializer(data=request.query_params)

    if not serializer.is_valid():
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
      result = get_trash_path(data=GetTrashPathSchema(**serializer.validated_data), username=request.user.username)
      return Response(result, status=status.HTTP_200_OK)

    except ValueError as e:
      return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      LOG.exception(f"Error getting trash path: {e}")
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  def delete(self, request):
    """Purge trash."""
    try:
      result = purge_trash(username=request.user.username)
      return Response(result, status=status.HTTP_200_OK)

    except ValueError as e:
      return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      LOG.exception(f"Error purging trash: {e}")
      return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def check_exists_operation(request):
  """Check if multiple paths exist."""
  serializer = CheckExistsSerializer(data=request.data)
  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  try:
    result = check_path_exists(data=CheckExistsSchema(**serializer.validated_data), username=request.user.username)
    return Response(result, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    LOG.exception(f"Error checking path existence: {e}")
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def copy_operation(request):
  """Copy files or directories."""
  serializer = CopyOperationSerializer(data=request.data)
  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  try:
    result = copy_paths(data=CopyOperationSchema(**serializer.validated_data), username=request.user.username)
    return Response(result, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    LOG.exception(f"Error copying paths: {e}")
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def move_operation(request):
  """Move files or directories."""
  serializer = MoveOperationSerializer(data=request.data)
  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  try:
    result = move_paths(data=MoveOperationSchema(**serializer.validated_data), username=request.user.username)
    return Response(result, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    LOG.exception(f"Error moving paths: {e}")
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
def delete_operation(request):
  """Delete files or directories."""
  serializer = DeleteOperationSerializer(data=request.data)
  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  try:
    result = delete_paths(data=DeleteOperationSchema(**serializer.validated_data), username=request.user.username)
    return Response(result, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    LOG.exception(f"Error deleting paths: {e}")
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def trash_restore_operation(request):
  """Restore files from trash."""
  serializer = TrashRestoreSerializer(data=request.data)
  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  try:
    result = restore_from_trash(data=TrashRestoreSchema(**serializer.validated_data), username=request.user.username)
    return Response(result, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    LOG.exception(f"Error restoring from trash: {e}")
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT"])
def permissions_operation(request):
  """Set file/directory permissions."""
  serializer = SetPermissionsSerializer(data=request.data)
  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  try:
    result = set_permissions(data=SetPermissionsSchema(**serializer.validated_data), username=request.user.username)
    return Response(result, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    LOG.exception(f"Error setting permissions: {e}")
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT"])
def ownership_operation(request):
  """Set file/directory ownership."""
  serializer = SetOwnershipSerializer(data=request.data)
  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  try:
    result = set_ownership(data=SetOwnershipSchema(**serializer.validated_data), username=request.user.username)
    return Response(result, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    LOG.exception(f"Error setting ownership: {e}")
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["PUT"])
def replication_operation(request):
  """Set replication factor."""
  serializer = SetReplicationSerializer(data=request.data)
  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  try:
    result = set_replication(data=SetReplicationSchema(**serializer.validated_data), username=request.user.username)
    return Response(result, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    LOG.exception(f"Error setting replication: {e}")
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def compress_operation(request):
  """Compress files into an archive."""
  serializer = CompressFilesSerializer(data=request.data)
  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  try:
    result = compress_files(data=CompressFilesSchema(**serializer.validated_data), username=request.user.username)
    return Response(result, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    LOG.exception(f"Error compressing files: {e}")
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def extract_operation(request):
  """Extract an archive."""
  serializer = ExtractArchiveSerializer(data=request.data)
  if not serializer.is_valid():
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  try:
    result = extract_archive(data=ExtractArchiveSchema(**serializer.validated_data), username=request.user.username)
    return Response(result, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    LOG.exception(f"Error extracting archive: {e}")
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def system_upload_space(request):
  """Get available space for file uploads."""
  try:
    result = get_available_space_for_upload(username=request.user.username)
    return Response(result, status=status.HTTP_200_OK)

  except ValueError as e:
    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
  except Exception as e:
    LOG.exception(f"Error getting upload space: {e}")
    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
