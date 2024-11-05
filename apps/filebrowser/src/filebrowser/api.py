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

import os
import json
import logging
import operator
import mimetypes
import posixpath
from io import BytesIO as string_io

from django.core.paginator import EmptyPage, Paginator
from django.http import HttpResponse, HttpResponseNotModified, HttpResponseRedirect, StreamingHttpResponse
from django.utils.http import http_date
from django.utils.translation import gettext as _
from django.views.static import was_modified_since

from aws.s3.s3fs import S3ListAllBucketsException, get_s3_home_directory
from azure.abfs.__init__ import get_abfs_home_directory
from desktop.auth.backend import is_admin
from desktop.conf import TASK_SERVER_V2
from desktop.lib import fsmanager, i18n
from desktop.lib.conf import coerce_bool
from desktop.lib.django_util import JsonResponse
from desktop.lib.export_csvxls import file_reader
from desktop.lib.fs.gc.gs import GSListAllBucketsException, get_gs_home_directory
from desktop.lib.fs.ozone.ofs import get_ofs_home_directory
from desktop.lib.i18n import smart_str
from desktop.lib.tasks.compress_files.compress_utils import compress_files_in_hdfs
from desktop.lib.tasks.extract_archive.extract_utils import extract_archive_in_hdfs
from filebrowser.conf import (
  ENABLE_EXTRACT_UPLOADED_ARCHIVE,
  FILE_DOWNLOAD_CACHE_CONTROL,
  MAX_FILE_SIZE_UPLOAD_LIMIT,
  REDIRECT_DOWNLOAD,
  SHOW_DOWNLOAD_BUTTON,
)
from filebrowser.lib import xxd
from filebrowser.lib.rwx import compress_mode, filetype, rwx
from filebrowser.utils import parse_broker_url
from filebrowser.views import (
  DEFAULT_CHUNK_SIZE_BYTES,
  MAX_CHUNK_SIZE_BYTES,
  _can_inline_display,
  _is_hdfs_superuser,
  _massage_page,
  _normalize_path,
  read_contents,
  stat_absolute_path,
)
from hadoop.core_site import get_trash_interval
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
      LOG.exception('Error running %s' % view_fn)
      response['status'] = -1
      response['message'] = smart_str(e)
    return JsonResponse(response)

  return decorator


@error_handler
def get_filesystems(request):
  response = {}

  filesystems = {}
  for k in fsmanager.get_filesystems(request.user):
    filesystems[k] = True

  response['status'] = 0
  response['filesystems'] = filesystems

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
      LOG.exception(f'Error running {view_fn.__name__}: {str(e)}')
      return JsonResponse({'error': str(e)}, status=500)

  return decorator


@api_error_handler
def get_filesystems_with_home_dirs(request):
  filesystems = []
  user_home_dir = ''

  for fs in fsmanager.get_filesystems(request.user):
    if fs == 'hdfs':
      user_home_dir = request.user.get_home_directory()
    elif fs == 's3a':
      user_home_dir = get_s3_home_directory(request.user)
    elif fs == 'gs':
      user_home_dir = get_gs_home_directory(request.user)
    elif fs == 'abfs':
      user_home_dir = get_abfs_home_directory(request.user)
    elif fs == 'ofs':
      user_home_dir = get_ofs_home_directory()

    filesystems.append(
      {
        'file_system': fs,
        'user_home_directory': user_home_dir,
      }
    )

  return JsonResponse(filesystems, safe=False)


@api_error_handler
def download(request):
  """
  Downloads a file.

  This is inspired by django.views.static.serve (?disposition={attachment, inline})

  :param request: The current request object
  :return: A response object with the file contents or an error message
  """
  path = request.GET.get('path')
  path = _normalize_path(path)

  if not SHOW_DOWNLOAD_BUTTON.get():
    return HttpResponse('Download operation is not allowed.', status=403)

  if not request.fs.exists(path):
    return HttpResponse(f'File does not exist: {path}', status=404)

  if not request.fs.isfile(path):
    return HttpResponse(f'{path} is not a file.', status=400)

  content_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
  stats = request.fs.stats(path)
  if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'), stats['mtime'], stats['size']):
    return HttpResponseNotModified()

  fh = request.fs.open(path)

  # First, verify read permissions on the file.
  try:
    request.fs.read(path, offset=0, length=1)
  except WebHdfsException as e:
    if e.code == 403:
      return HttpResponse(f'User {request.user.username} is not authorized to download file at path: {path}', status=403)
    elif request.fs._get_scheme(path).lower() == 'abfs' and e.code == 416:
      # Safe to skip ABFS exception of code 416 for zero length objects, file will get downloaded anyway.
      LOG.debug('Skipping exception from ABFS:' + str(e))
    else:
      return HttpResponse(f'Failed to download file at path {path}: {str(e)}', status=500)  # TODO: status code?

  if REDIRECT_DOWNLOAD.get() and hasattr(fh, 'read_url'):
    response = HttpResponseRedirect(fh.read_url())
    setattr(response, 'redirect_override', True)
  else:
    response = StreamingHttpResponse(file_reader(fh), content_type=content_type)

    response["Last-Modified"] = http_date(stats['mtime'])
    response["Content-Length"] = stats['size']
    response['Content-Disposition'] = (
      request.GET.get('disposition', 'attachment; filename="' + stats['name'] + '"') if _can_inline_display(path) else 'attachment'
    )

    if FILE_DOWNLOAD_CACHE_CONTROL.get():
      response["Cache-Control"] = FILE_DOWNLOAD_CACHE_CONTROL.get()

  request.audit = {
    'operation': 'DOWNLOAD',
    'operationText': 'User %s downloaded file at path "%s"' % (request.user.username, path),
    'allowed': True,
  }

  return response


@api_error_handler
def listdir_paged(request):
  """
  A paginated version of listdir.

  Query parameters:
    pagenum           - The page number to show. Defaults to 1.
    pagesize          - How many to show on a page. Defaults to 30.
    sortby=?          - Specify attribute to sort by. Accepts: (type, name, atime, mtime, size, user, group). Defaults to name.
    descending        - Specify a descending sort order. Default to false.
    filter=?          - Specify a substring filter to search for in the filename field.
  """
  path = request.GET.get('path', '/')  # Set default path for index directory
  path = _normalize_path(path)

  if not request.fs.isdir(path):
    return HttpResponse(f'{path} is not a directory.', status=400)

  pagenum = int(request.GET.get('pagenum', 1))
  pagesize = int(request.GET.get('pagesize', 30))

  do_as = None
  if is_admin(request.user) or request.user.has_hue_permission(action="impersonate", app="security"):
    do_as = request.GET.get('doas', request.user.username)
  if hasattr(request, 'doas'):
    do_as = request.doas

  try:
    if do_as:
      all_stats = request.fs.do_as_user(do_as, request.fs.listdir_stats, path)
    else:
      all_stats = request.fs.listdir_stats(path)
  except (S3ListAllBucketsException, GSListAllBucketsException) as e:
    return HttpResponse(f'Bucket listing is not allowed: {str(e)}', status=403)

  # Filter first
  filter_string = request.GET.get('filter')
  if filter_string:
    filtered_stats = [sb for sb in all_stats if filter_string in sb['name']]
    all_stats = filtered_stats

  # Sort next
  sortby = request.GET.get('sortby')
  descending_param = request.GET.get('descending')
  if sortby:
    if sortby not in ('type', 'name', 'atime', 'mtime', 'user', 'group', 'size'):
      LOG.info(f'Invalid sort attribute {sortby} for list directory operation. Skipping it.')
    else:
      all_stats = sorted(all_stats, key=operator.attrgetter(sortby), reverse=coerce_bool(descending_param))

  # Do pagination
  try:
    paginator = Paginator(all_stats, pagesize, allow_empty_first_page=True)
    page = paginator.page(pagenum)
    shown_stats = page.object_list
  except EmptyPage:
    message = "No results found for the requested page."
    LOG.warning(message)
    return HttpResponse(message, status=404)  # TODO: status code?

  if page:
    page.object_list = [_massage_stats(request, stat_absolute_path(path, s)) for s in shown_stats]

  # TODO: Shift below fields to /get_config?
  is_hdfs = request.fs._get_scheme(path) == 'hdfs'
  is_trash_enabled = is_hdfs and int(get_trash_interval()) > 0
  is_fs_superuser = is_hdfs and _is_hdfs_superuser(request)

  response = {
    'is_trash_enabled': is_trash_enabled,
    'files': page.object_list if page else [],
    'page': _massage_page(page, paginator) if page else {},  # TODO: Check if we need to clean response of _massage_page
    # TODO: Check what to keep or what to remove? or move some fields to /get_config?
    'is_fs_superuser': is_fs_superuser,
    'groups': is_fs_superuser and [str(x) for x in Group.objects.values_list('name', flat=True)] or [],
    'users': is_fs_superuser and [str(x) for x in User.objects.values_list('username', flat=True)] or [],
    'superuser': request.fs.superuser,
    'supergroup': request.fs.supergroup,
  }

  return JsonResponse(response)


@api_error_handler
def display(request):
  """
  Implements displaying part of a file.

  GET arguments are length, offset, mode, compression and encoding
  with reasonable defaults chosen.

  Note that display by length and offset are on bytes, not on characters.
  """
  path = request.GET.get('path', '/')  # Set default path for index directory
  path = _normalize_path(path)

  if not request.fs.isfile(path):
    return HttpResponse(f'{path} is not a file.', status=400)

  encoding = request.GET.get('encoding') or i18n.get_site_encoding()

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

  if mode and mode != 'text':
    return HttpResponse("Mode value must be 'text'.", status=400)
  if offset < 0:
    return HttpResponse("Offset may not be less than zero.", status=400)
  if length < 0:
    return HttpResponse("Length may not be less than zero.", status=400)
  if length > MAX_CHUNK_SIZE_BYTES:
    return HttpResponse(f'Cannot request chunks greater than {MAX_CHUNK_SIZE_BYTES} bytes.', status=400)

  # Read out based on meta.
  compression, offset, length, contents = read_contents(compression, path, request.fs, offset, length)

  # Get contents as string for text mode, or at least try
  file_contents = None
  if isinstance(contents, str):
    file_contents = contents
    mode = 'text'
  else:
    try:
      file_contents = contents.decode(encoding)
      mode = 'text'
    except UnicodeDecodeError:
      file_contents = contents

  data = {
    'contents': file_contents,
    'offset': offset,
    'length': length,
    'end': offset + len(contents),
    'mode': mode,
    'compression': compression,
  }

  return JsonResponse(data)


@api_error_handler
def stat(request):
  """
  Returns the generic stats of FS object.
  """
  path = request.GET.get('path')
  path = _normalize_path(path)

  if not request.fs.exists(path):
    return HttpResponse(f'Object does not exist: {path}', status=404)

  stats = request.fs.stats(path)

  return JsonResponse(_massage_stats(request, stat_absolute_path(path, stats)))


@api_error_handler
def upload_chunks(request):
  pass


@api_error_handler
def upload_complete(request):
  pass


@api_error_handler
def upload_file(request):
  """
  A wrapper around the actual upload view function to clean up the temporary file afterwards if it fails.

  Returns JSON.
  """
  response = {}

  try:
    response = _upload_file(request)
  except Exception as e:
    LOG.exception('Upload operation failed.')

    file = request.FILES.get('file')
    if file and hasattr(file, 'remove'):  # TODO: Call from proxyFS -- Check feasibility of this old comment
      file.remove()

    return HttpResponse(str(e).split('\n', 1)[0], status=500)  # TODO: Check error message and status code

  return JsonResponse(response)


def _upload_file(request):
  """
  Handles file uploaded by HDFSfileUploadHandler.

  The uploaded file is stored in HDFS at its destination with a .tmp suffix.
  We just need to rename it to the destination path.
  """
  # Read request body first to prevent RawPostDataException later on
  body_data_bytes = string_io(request.body)

  uploaded_file = request.FILES['file']
  dest_path = request.POST.get('destination_path')

  if MAX_FILE_SIZE_UPLOAD_LIMIT.get() >= 0 and uploaded_file.size >= MAX_FILE_SIZE_UPLOAD_LIMIT.get():
    raise Exception(f'File exceeds maximum allowed size of {MAX_FILE_SIZE_UPLOAD_LIMIT.get()} bytes for upload operation.')

  if request.fs.isdir(dest_path) and posixpath.sep in uploaded_file.name:
    raise Exception(f'Upload failed: {posixpath.sep} is not allowed in the filename {uploaded_file.name}.')

  filepath = request.fs.join(dest_path, uploaded_file.name)

  try:
    request.fs.upload(request.META, input_data=body_data_bytes, destination=dest_path, username=request.user.username)
  except Exception as ex:
    already_exists = False
    try:
      already_exists = request.fs.exists(filepath)
    except Exception:
      pass

    if already_exists:
      messsage = f'Upload failed: Destination {filepath} already exists.'
    else:
      messsage = f'Upload to {filepath} failed: {str(ex)}'
    raise Exception(messsage)  # TODO: Check error messages above and status code

  response = {
    'uploaded_file_stats': _massage_stats(request, stat_absolute_path(filepath, request.fs.stats(filepath))),
  }

  return response


@api_error_handler
def mkdir(request):
  # TODO: Check if this needs to be a PUT request
  path = request.POST.get('path')
  name = request.POST.get('name')

  if name and (posixpath.sep in name or "#" in name):
    return HttpResponse(f"Error creating {name} directory. Slashes or hashes are not allowed in directory name.", status=400)

  request.fs.mkdir(request.fs.join(path, name))
  return HttpResponse(status=201)


@api_error_handler
def touch(request):
  path = request.POST.get('path')
  name = request.POST.get('name')

  if name and (posixpath.sep in name):
    return HttpResponse(f"Error creating {name} file: Slashes are not allowed in filename.", status=400)

  request.fs.create(request.fs.join(path, name))
  return HttpResponse(status=201)


@api_error_handler
def save_file(request):
  """
  The POST endpoint to save a file in the file editor.

  Does the save and then redirects back to the edit page.
  """
  path = request.POST.get('path')
  path = _normalize_path(path)

  encoding = request.POST.get('encoding')
  data = request.POST.get('contents').encode(encoding)

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


@api_error_handler
def rename(request):
  source_path = request.POST.get('source_path', '')
  destination_path = request.POST.get('destination_path', '')

  if "#" in destination_path:
    return HttpResponse(
      f"Error creating {os.path.basename(source_path)} to {destination_path}: Hashes are not allowed in file or directory names", status=400
    )

  # If dest_path doesn't have a directory specified, use same directory.
  if "/" not in destination_path:
    source_dir = os.path.dirname(source_path)
    destination_path = request.fs.join(source_dir, destination_path)

  if request.fs.exists(destination_path):
    return HttpResponse(f"The destination path {destination_path} already exists.", status=500)  # TODO: Status code?

  request.fs.rename(source_path, destination_path)
  return HttpResponse(status=200)


@api_error_handler
def move(request):
  source_path = request.POST.get('source_path', '')
  destination_path = request.POST.get('destination_path', '')

  if source_path == destination_path:
    return HttpResponse('Source and destination path cannot be same.', status=400)

  request.fs.rename(source_path, destination_path)
  return HttpResponse(status=200)


@api_error_handler
def copy(request):
  source_path = request.POST.get('source_path', '')
  destination_path = request.POST.get('destination_path', '')

  if source_path == destination_path:
    return HttpResponse('Source and destination path cannot be same.', status=400)

  # Copy method for Ozone FS returns a string of skipped files if their size is greater than configured chunk size.
  if source_path.startswith('ofs://'):
    ofs_skip_files = request.fs.copy(source_path, destination_path, recursive=True, owner=request.user)
    if ofs_skip_files:
      return JsonResponse(ofs_skip_files, status=500)  # TODO: Status code?
  else:
    request.fs.copy(source_path, destination_path, recursive=True, owner=request.user)

  return HttpResponse(status=200)


@api_error_handler
def content_summary(request):
  path = request.GET.get('path')
  path = _normalize_path(path)

  if not path:
    return HttpResponse("Path parameter is required to fetch content summary.", status=400)

  if not request.fs.exists(path):
    return HttpResponse(f'Path does not exist: {path}', status=404)

  response = {}
  try:
    content_summary = request.fs.get_content_summary(path)
    replication_factor = request.fs.stats(path)['replication']

    content_summary.summary.update({'replication': replication_factor})
    response['summary'] = content_summary.summary
  except Exception:
    return HttpResponse(f'Failed to fetch content summary for path: {path}', status=500)

  return JsonResponse(response)


@api_error_handler
def set_replication(request):
  # TODO: Check if this needs to be a PUT request
  path = request.POST.get('path')
  replication_factor = request.POST.get('replication_factor')

  result = request.fs.set_replication(path, replication_factor)
  if not result:
    return HttpResponse("Failed to set the replication factor.", status=500)

  return HttpResponse(status=200)


@api_error_handler
def rmtree(request):
  # TODO: Check if this needs to be a DELETE request
  path = request.POST.get('path')
  skip_trash = request.POST.get('skip_trash', False)

  request.fs.rmtree(path, skip_trash)

  return HttpResponse(status=200)


@api_error_handler
def get_trash_path(request):
  path = request.GET.get('path')
  path = _normalize_path(path)
  response = {}

  trash_path = request.fs.trash_path(path)
  user_home_trash_path = request.fs.join(request.fs.current_trash_path(trash_path), request.user.get_home_directory().lstrip('/'))

  if request.fs.isdir(user_home_trash_path):
    response['trash_path'] = user_home_trash_path
  elif request.fs.isdir(trash_path):
    response['trash_path'] = trash_path
  else:
    response['trash_path'] = None

  return JsonResponse(response)


@api_error_handler
def trash_restore(request):
  path = request.POST.get('path')
  request.fs.restore(path)

  return HttpResponse(status=200)


@api_error_handler
def trash_purge(request):
  request.fs.purge_trash()

  return HttpResponse(status=200)


@api_error_handler
def chown(request):
  # TODO: Check if this needs to be a PUT request
  path = request.POST.get('path')
  user = request.POST.get("user")
  group = request.POST.get("group")
  recursive = request.POST.get('recursive', False)

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
  path = request.POST.get('path')
  permission = json.loads(request.POST.get("permission", '{}'))

  mode = compress_mode([coerce_bool(permission.get(p)) for p in perm_names])

  request.fs.chmod(path, mode, recursive=permission.get('recursive', False))

  return HttpResponse(status=200)


@api_error_handler
def extract_archive_using_batch_job(request):
  # TODO: Check core logic with E2E tests -- dont use it until then
  if not ENABLE_EXTRACT_UPLOADED_ARCHIVE.get():
    return HttpResponse("Extract archive operation is disabled by configuration.", status=500)  # TODO: status code?

  upload_path = request.fs.netnormpath(request.POST.get('upload_path'))
  archive_name = request.POST.get('archive_name')

  if upload_path and archive_name:
    try:
      # TODO: Check is we really require urllib_unquote here? Maybe need to improve old oozie methods also?
      # upload_path = urllib_unquote(upload_path)
      # archive_name = urllib_unquote(archive_name)
      response = extract_archive_in_hdfs(request, upload_path, archive_name)
    except Exception as e:
      return HttpResponse(f'Failed to extract archive: {str(e)}', status=500)  # TODO: status code?

  return JsonResponse(response)


@api_error_handler
def compress_files_using_batch_job(request):
  # TODO: Check core logic with E2E tests -- dont use it until then
  if not ENABLE_EXTRACT_UPLOADED_ARCHIVE.get():
    return HttpResponse("Compress files operation is disabled by configuration.", status=500)  # TODO: status code?

  upload_path = request.fs.netnormpath(request.POST.get('upload_path'))
  archive_name = request.POST.get('archive_name')
  file_names = request.POST.getlist('files[]')  # TODO: Check if this param is correct? Need to improve it?

  if upload_path and file_names and archive_name:
    try:
      response = compress_files_in_hdfs(request, file_names, upload_path, archive_name)
    except Exception as e:
      return HttpResponse(f'Failed to compress files: {str(e)}', status=500)  # TODO: status code?
  else:
    return HttpResponse('Output directory is not set.', status=500)  # TODO: status code?

  return JsonResponse(response)


@api_error_handler
def get_available_space_for_upload(request):
  redis_client = parse_broker_url(TASK_SERVER_V2.BROKER_URL.get())
  try:
    upload_available_space = int(redis_client.get('upload_available_space'))
    if upload_available_space is None:
      return HttpResponse("upload_available_space key is not set in Redis.", status=500)  # TODO: status code?

    return JsonResponse({'upload_available_space': upload_available_space})
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
  path_list = request.POST.getlist('source_path') if op in (copy, move) else request.POST.getlist('path')

  error_dict = {}
  for p in path_list:
    tmp_dict = bulk_dict
    if op in (copy, move):
      tmp_dict['source_path'] = p
    else:
      tmp_dict['path'] = p

    request.POST = tmp_dict
    response = op(request)

    if response.status_code != 200:
      error_dict[p] = {'error': response.content}
      if op == copy and p.startswith('ofs://'):
        error_dict[p].update({'ofs_skip_files': response.content})

  if error_dict:
    return JsonResponse(error_dict, status_code=500)  # TODO: Check if we need diff status code or diff json structure?

  return HttpResponse(status=200)  # TODO: Check if we need to send some message or diff status code?


def _massage_stats(request, stats):
  """
  Massage a stats record as returned by the filesystem implementation
  into the format that the views would like it in.
  """
  stats_dict = stats.to_json_dict()
  normalized_path = request.fs.normpath(stats_dict.get('path'))

  stats_dict.update(
    {
      'path': normalized_path,
      'type': filetype(stats.mode),
      'rwx': rwx(stats.mode, stats.aclBit),
    }
  )

  return stats_dict
