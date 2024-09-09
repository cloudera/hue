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
import logging
import operator
import mimetypes
import posixpath

from django.core.paginator import EmptyPage, InvalidPage, Page, Paginator
from django.http import HttpResponse, HttpResponseNotModified, HttpResponseRedirect, StreamingHttpResponse
from django.utils.http import http_date
from django.utils.translation import gettext as _
from django.views.static import was_modified_since

from aws.s3.s3fs import S3FileSystemException, S3ListAllBucketsException, get_s3_home_directory
from azure.abfs.__init__ import get_abfs_home_directory
from desktop.auth.backend import is_admin
from desktop.conf import ENABLE_NEW_STORAGE_BROWSER, RAZ, TASK_SERVER_V2
from desktop.lib import fsmanager, i18n
from desktop.lib.conf import coerce_bool
from desktop.lib.django_util import JsonResponse
from desktop.lib.export_csvxls import file_reader
from desktop.lib.fs.gc.gs import GSListAllBucketsException, get_gs_home_directory
from desktop.lib.fs.ozone.ofs import get_ofs_home_directory
from filebrowser.conf import (
  ARCHIVE_UPLOAD_TEMPDIR,
  ENABLE_EXTRACT_UPLOADED_ARCHIVE,
  FILE_DOWNLOAD_CACHE_CONTROL,
  MAX_SNAPPY_DECOMPRESSION_SIZE,
  REDIRECT_DOWNLOAD,
  SHOW_DOWNLOAD_BUTTON,
  SHOW_UPLOAD_BUTTON,
)
from filebrowser.lib import xxd
from filebrowser.views import (
  BYTES_PER_LINE,
  BYTES_PER_SENTENCE,
  DEFAULT_CHUNK_SIZE_BYTES,
  MAX_CHUNK_SIZE_BYTES,
  MAX_FILEEDITOR_SIZE,
  _can_inline_display,
  _is_hdfs_superuser,
  _massage_page,
  _massage_stats,
  _normalize_path,
  read_contents,
  stat_absolute_path,
)
from hadoop.core_site import get_trash_interval
from hadoop.fs.exceptions import WebHdfsException
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


# TODO: Improve error response further with better context -- Error UX Phase 1 item
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

  # TODO: Improve config name?
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

  try:
    with request.fs.open(path) as fh:
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
  except Exception as e:
    return HttpResponse(f'Failed to download file at path {path}: {str(e)}', status=500)  # TODO: status code?


@api_error_handler
def listdir_paged(request):
  """
  A paginated version of listdir.

  Query parameters:
    pagenum           - The page number to show. Defaults to 1.
    pagesize          - How many to show on a page. Defaults to 15.
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

  # if request.fs._get_scheme(path) == 'hdfs':
  #   home_dir_path = request.user.get_home_directory()
  # else:
  #   home_dir_path = None

  # breadcrumbs = parse_breadcrumbs(path)

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
    LOG.warn(message)
    return HttpResponse(message, status=404)  # TODO: status code?

  # TODO: Current same dir stats below?

  # # Include same dir always as first option to see stats of the current folder.
  # current_stat = request.fs.stats(path)
  # # The 'path' field would be absolute, but we want its basename to be
  # # actually '.' for display purposes. Encode it since _massage_stats expects byte strings.
  # current_stat.path = path
  # current_stat.name = "."
  # shown_stats.insert(0, current_stat)

  # Include parent dir always as second option, unless at filesystem root or when RAZ is enabled.
  if not (request.fs.isroot(path) or RAZ.IS_ENABLED.get()):
    parent_path = request.fs.parent_path(path)
    parent_stat = request.fs.stats(parent_path)
    # The 'path' field would be absolute, but we want its basename to be
    # actually '..' for display purposes. Encode it since _massage_stats expects byte strings.
    parent_stat['path'] = parent_path
    parent_stat['name'] = ".."
    shown_stats.insert(0, parent_stat)

  if page:
    # TODO: Check if we need to clean response of _massage_stats
    page.object_list = [_massage_stats(request, stat_absolute_path(path, s)) for s in shown_stats]

  # TODO: Shift below fields to /get_config?
  is_hdfs = request.fs._get_scheme(path) == 'hdfs'
  is_trash_enabled = is_hdfs and int(get_trash_interval()) > 0
  is_fs_superuser = is_hdfs and _is_hdfs_superuser(request)

  response = {
      # 'path': path,
      # 'breadcrumbs': breadcrumbs,
      # 'current_request_path': '/filebrowser/view=' + urllib_quote(path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS),
      'is_trash_enabled': is_trash_enabled,
      'files': page.object_list if page else [],
      'page': _massage_page(page, paginator) if page else {},  # TODO: Check if we need to clean response of _massage_page
      'pagesize': pagesize,
      # 'home_directory': home_dir_path if home_dir_path and request.fs.isdir(home_dir_path) else None,
      # 'descending': descending_param,

      # The following should probably be deprecated
      # TODO: Check what to keep or what to remove? or move some fields to /get_config?

      'cwd_set': True,
      'file_filter': 'any',
      # 'current_dir_path': path,
      'is_fs_superuser': is_fs_superuser,
      'groups': is_fs_superuser and [str(x) for x in Group.objects.values_list('name', flat=True)] or [],
      'users': is_fs_superuser and [str(x) for x in User.objects.values_list('username', flat=True)] or [],
      'superuser': request.fs.superuser,
      'supergroup': request.fs.supergroup,
      # 'is_sentry_managed': request.fs.is_sentry_managed(path),
      # 'apps': list(appmanager.get_apps_dict(request.user).keys()),
      'show_download_button': SHOW_DOWNLOAD_BUTTON.get(),
      'show_upload_button': SHOW_UPLOAD_BUTTON.get(),
      # 'is_embeddable': request.GET.get('is_embeddable', False),
      # 's3_listing_not_allowed': s3_listing_not_allowed
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

  # TODO: Check if we still need this or not
  # # display inline files just if it's not an ajax request
  # if not is_ajax(request):
  #   if _can_inline_display(path):
  #     return redirect(reverse('filebrowser:filebrowser_views_download', args=[path]) + '?disposition=inline')

  stats = request.fs.stats(path)
  encoding = request.GET.get('encoding') or i18n.get_site_encoding()

  # I'm mixing URL-based parameters and traditional
  # HTTP GET parameters, since URL-based parameters
  # can't naturally be optional.

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

  if mode and mode not in ["binary", "text"]:
    return HttpResponse("Mode must be one of 'binary' or 'text'.", status=400)
  if offset < 0:
    return HttpResponse("Offset may not be less than zero.", status=400)
  if length < 0:
    return HttpResponse("Length may not be less than zero.", status=400)
  if length > MAX_CHUNK_SIZE_BYTES:
    return HttpResponse(f'Cannot request chunks greater than {MAX_CHUNK_SIZE_BYTES} bytes.', status=400)

  # Do not decompress in binary mode.
  if mode == 'binary':
    compression = 'none'

  # Read out based on meta.
  compression, offset, length, contents = read_contents(compression, path, request.fs, offset, length)

  # Get contents as string for text mode, or at least try
  file_contents = None
  if mode is None or mode == 'text':
    if isinstance(contents, str):
      file_contents = contents
      is_binary = False
      mode = 'text'
    else:
      # TODO: Check if the content is used in OLD CODE, when is_binary was true and replacement character was found.
      # TODO: Then finally check how is binary content sent, is old UI reading from uni_content or the below xxd_out??
      try:
        file_contents = contents.decode(encoding)
        is_binary = False
        mode = 'text'
      except UnicodeDecodeError:
        file_contents = contents
        is_binary = True
        mode = 'binary' if mode is None else mode

  # Get contents as bytes
  if mode == "binary":
    xxd_out = list(xxd.xxd(offset, contents, BYTES_PER_LINE, BYTES_PER_SENTENCE))

  # TODO: Check what all UI needs and clean the field below, currently commenting out few duplicates which needs to be verified.

  # dirname = posixpath.dirname(path)
  # Start with index-like data:

  stats = request.fs.stats(path)
  data = _massage_stats(request, stat_absolute_path(path, stats))  # TODO: Stats required again?
  # data["is_embeddable"] = request.GET.get('is_embeddable', False)

  # And add a view structure:
  # data["success"] = True
  data["view"] = {
      'offset': offset,
      'length': length,
      'end': offset + len(contents),
      # 'dirname': dirname,
      'mode': mode,
      'compression': compression,
      # 'size': stats.size,
      'max_chunk_size': str(MAX_CHUNK_SIZE_BYTES)
  }
  # data["filename"] = os.path.basename(path)
  data["editable"] = stats.size < MAX_FILEEDITOR_SIZE  # TODO: To improve this limit and sent it as /get_config? Needs discussion.

  # TODO: Understand the comment. Check why are we logging file content? Also check how is masked_binary_data used? Finally improve code.
  if mode == "binary":
    # This might be the wrong thing for ?format=json; doing the
    # xxd'ing in javascript might be more compact, or sending a less
    # intermediate representation...
    LOG.debug("xxd: " + str(xxd_out))
    data['view']['xxd'] = xxd_out
    data['view']['masked_binary_data'] = False
  else:
    data['view']['contents'] = file_contents
    data['view']['masked_binary_data'] = is_binary

  # data['breadcrumbs'] = parse_breadcrumbs(path)
  # data['show_download_button'] = SHOW_DOWNLOAD_BUTTON.get()  # TODO: Add as /get_config?

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
def mkdir(request):
  path = request.POST.get('path')
  name = request.POST.get('name')

  if name and (posixpath.sep in name or "#" in name):
    raise Exception(_("Error creating %s directory. Slashes or hashes are not allowed in directory name." % name))

  request.fs.mkdir(request.fs.join(path, name))
  return HttpResponse(status=200)


@api_error_handler
def touch(request):
  path = request.POST.get('path')
  name = request.POST.get('name')

  if name and (posixpath.sep in name):
    raise Exception(_("Error creating %s file. Slashes are not allowed in filename." % name))

  request.fs.create(request.fs.join(path, name))
  return HttpResponse(status=200)


@api_error_handler
def rename(request):
  src_path = request.POST.get('src_path')
  dest_path = request.POST.get('dest_path')

  if "#" in dest_path:
    raise Exception(
      _("Error renaming %s to %s. Hashes are not allowed in file or directory names." % (os.path.basename(src_path), dest_path))
    )

  # If dest_path doesn't have a directory specified, use same directory.
  if "/" not in dest_path:
    src_dir = os.path.dirname(src_path)
    dest_path = request.fs.join(src_dir, dest_path)

  if request.fs.exists(dest_path):
    raise Exception(_('The destination path "%s" already exists.') % dest_path)

  request.fs.rename(src_path, dest_path)
  return HttpResponse(status=200)


@api_error_handler
def move(request):
  src_path = request.POST.get('src_path')
  dest_path = request.POST.get('dest_path')

  if src_path == dest_path:
    raise Exception(_('Source and destination path cannot be same.'))

  request.fs.rename(src_path, dest_path)
  return HttpResponse(status=200)


@api_error_handler
def copy(request):
  src_path = request.POST.get('src_path')
  dest_path = request.POST.get('dest_path')

  if src_path == dest_path:
    raise Exception(_('Source and destination path cannot be same.'))

  # Copy method for Ozone FS returns a string of skipped files if their size is greater than configured chunk size.
  if src_path.startswith('ofs://'):
    ofs_skip_files = request.fs.copy(src_path, dest_path, recursive=True, owner=request.user)
    if ofs_skip_files:
      return HttpResponse(ofs_skip_files, status=200)
  else:
    request.fs.copy(src_path, dest_path, recursive=True, owner=request.user)

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
  path = request.PUT.get('path')
  replication_factor = request.PUT.get('replication_factor')

  result = request.fs.set_replication(path, replication_factor)
  if not result:
    return HttpResponse("Failed to set the replication factor.", status=500)

  return HttpResponse(status=200)


@api_error_handler
def rmtree(request):
  path = request.DELETE.get('path')
  skip_trash = request.DELETE.get('skip_trash', False)

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
