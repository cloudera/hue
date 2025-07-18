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

import errno
import json
import logging
import mimetypes
import operator
import os
import posixpath
import re
import stat as stat_module
from builtins import str as new_str
from bz2 import decompress
from datetime import datetime
from functools import partial
from gzip import decompress as decompress_gzip
from io import BytesIO, StringIO as string_io
from urllib.parse import quote as urllib_quote, unquote as urllib_unquote, urlparse as lib_urlparse

import pandas as pd
from avro import datafile, io as avro_io
from django.core.files.uploadhandler import StopUpload
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.http import Http404, HttpResponse, HttpResponseNotModified, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import redirect
from django.template.defaultfilters import filesizeformat, stringformat
from django.urls import reverse
from django.utils.html import escape
from django.utils.http import http_date
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods
from django.views.static import was_modified_since

from aws.s3.s3fs import get_s3_home_directory, S3FileSystemException, S3ListAllBucketsException
from aws.s3.upload import S3FineUploaderChunkedUpload
from azure.abfs.upload import ABFSFineUploaderChunkedUpload
from desktop import appmanager
from desktop.auth.backend import is_admin
from desktop.conf import RAZ, TASK_SERVER_V2
from desktop.lib import i18n
from desktop.lib.conf import coerce_bool
from desktop.lib.django_util import format_preserving_redirect, JsonResponse, render
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.export_csvxls import file_reader
from desktop.lib.fs import splitpath
from desktop.lib.fs.gc.gs import get_gs_home_directory
from desktop.lib.fs.ozone.ofs import get_ofs_home_directory
from desktop.lib.fs.ozone.upload import OFSFineUploaderChunkedUpload
from desktop.lib.i18n import smart_str
from desktop.lib.paths import SAFE_CHARACTERS_URI, SAFE_CHARACTERS_URI_COMPONENTS
from desktop.lib.tasks.compress_files.compress_utils import compress_files_in_hdfs
from desktop.lib.tasks.extract_archive.extract_utils import extract_archive_in_hdfs
from desktop.lib.view_util import is_ajax
from desktop.views import serve_403_error
from filebrowser.conf import (
  ARCHIVE_UPLOAD_TEMPDIR,
  ENABLE_EXTRACT_UPLOADED_ARCHIVE,
  FILE_DOWNLOAD_CACHE_CONTROL,
  MAX_SNAPPY_DECOMPRESSION_SIZE,
  REDIRECT_DOWNLOAD,
  SHOW_DOWNLOAD_BUTTON,
  SHOW_UPLOAD_BUTTON,
)
from filebrowser.forms import (
  ChmodFormSet,
  ChownFormSet,
  CopyFormSet,
  EditorForm,
  MkDirForm,
  RenameForm,
  RenameFormSet,
  RestoreFormSet,
  RmTreeFormSet,
  SetReplicationFactorForm,
  TouchForm,
  TrashPurgeForm,
  UploadFileForm,
)
from filebrowser.lib import xxd
from filebrowser.lib.rwx import filetype, rwx
from hadoop.core_site import get_trash_interval
from hadoop.fs.exceptions import WebHdfsException
from hadoop.fs.fsutils import do_overwrite_save
from hadoop.fs.upload import HDFSFineUploaderChunkedUpload, LocalFineUploaderChunkedUpload
from useradmin.models import Group, User

DEFAULT_CHUNK_SIZE_BYTES = 1024 * 4  # 4KB
MAX_CHUNK_SIZE_BYTES = 1024 * 1024  # 1MB

# Defaults for "xxd"-style output.
# Sentences refer to groups of bytes printed together, within a line.
BYTES_PER_LINE = 16
BYTES_PER_SENTENCE = 2

# The maximum size the file editor will allow you to edit
MAX_FILEEDITOR_SIZE = 256 * 1024

# Parquet files start with a specific 4-byte magic number: 'PAR1'
PARQUET_MAGIC_NUMBER = b'PAR1'

INLINE_DISPLAY_MIMETYPE = re.compile(
    r'video/|image/|audio/|application/pdf|application/msword|application/excel|application/vnd\.ms|application/vnd\.openxmlformats'
)

INLINE_DISPLAY_MIMETYPE_EXCEPTIONS = re.compile(r'image/svg\+xml')

SCHEME_PREFIXES = {
    's3a': 's3a://',
    'ofs': 'ofs://',
    'abfs': 'abfs://',
    'hdfs': 'hdfs://',
    'gs': 'gs://',
    'local': 'local://',
}

UPLOAD_CLASSES = {
    's3a': S3FineUploaderChunkedUpload,
    'ofs': OFSFineUploaderChunkedUpload,
    'abfs': ABFSFineUploaderChunkedUpload,
    'hdfs': HDFSFineUploaderChunkedUpload,
    'local': LocalFineUploaderChunkedUpload,
}

if hasattr(ARCHIVE_UPLOAD_TEMPDIR, 'get'):
  os.makedirs(ARCHIVE_UPLOAD_TEMPDIR.get(), exist_ok=True)

logger = logging.getLogger()


def index(request):
  # Redirect to home directory by default
  path = request.user.get_home_directory()

  try:
    if not request.fs.isdir(path):
      path = '/'
  except Exception:
    pass

  return view(request, path)


def _decode_slashes(path):
  # This is a fix for some installations where the path is still having the slash (/) encoded
  # as %2F while the rest of the path is actually decoded.
  encoded_slash = '%2F'
  if path and (
    path.startswith(encoded_slash)
    or path.startswith('abfs:' + encoded_slash)
    or path.startswith('s3a:' + encoded_slash)
    or path.startswith('gs:' + encoded_slash)
    or path.startswith('ofs:' + encoded_slash)
  ):
    path = path.replace(encoded_slash, '/')

  return path


def _normalize_path(path):
  path = _decode_slashes(path)

  # Check if protocol missing / and add it back (e.g. Kubernetes ingress can strip double slash)
  for scheme, prefix in SCHEME_PREFIXES.items():
    single_slash_prefix = f"{scheme}:/"
    if path and path.startswith(single_slash_prefix) and not path.startswith(prefix):
      path = path.replace(single_slash_prefix, prefix)

  return path


def get_scheme(path):
  path = _normalize_path(path)
  for scheme, prefix in SCHEME_PREFIXES.items():
    if path.startswith(prefix):
      return scheme
  return 'hdfs'


def download(request, path):
  """
  Downloads a file.

  This is inspired by django.views.static.serve.
  ?disposition={attachment, inline}
  """
  path = _normalize_path(path)

  if not SHOW_DOWNLOAD_BUTTON.get():
    return serve_403_error(request)
  if not request.fs.exists(path):
    raise Http404(_("File not found: %(path)s.") % {'path': escape(path)})
  if not request.fs.isfile(path):
    raise PopupException(_("'%(path)s' is not a file.") % {'path': path})

  content_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
  stats = request.fs.stats(path)
  mtime = stats['mtime']
  if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'), mtime):
    return HttpResponseNotModified()
    # TODO(philip): Ideally a with statement would protect from leaks, but tricky to do here.
  fh = request.fs.open(path)

  # Verify read permissions on file first
  try:
    request.fs.read(path, offset=0, length=1)
  except WebHdfsException as e:
    if e.code == 403:
      raise PopupException(_('User %s is not authorized to download file at path "%s"') % (request.user.username, path))
    elif request.fs._get_scheme(path).lower() == 'abfs' and e.code == 416:
      # Safe to skip ABFS exception of code 416 for zero length objects, file will get downloaded anyway.
      logger.exception('Skipping exception from ABFS: ' + str(e))
    else:
      raise PopupException(_('Failed to download file at path "%s": %s') % (path, e))

  if REDIRECT_DOWNLOAD.get() and hasattr(fh, 'read_url'):
    response = HttpResponseRedirect(fh.read_url())
    setattr(response, 'redirect_override', True)
  else:
    response = StreamingHttpResponse(file_reader(fh), content_type=content_type)
    if FILE_DOWNLOAD_CACHE_CONTROL.get():
      response["Cache-Control"] = FILE_DOWNLOAD_CACHE_CONTROL.get()
    response["Last-Modified"] = http_date(stats['mtime'])
    response["Content-Length"] = stats['size']
    response['Content-Disposition'] = request.GET.get('disposition', 'attachment; filename="' + stats['name'] + '"') \
                                      if _can_inline_display(path) \
                                      else 'attachment'

  request.audit = {
      'operation': 'DOWNLOAD',
      'operationText': 'User %s downloaded file %s with size: %d bytes' % (request.user.username, path, stats['size']),
      'allowed': True
  }

  return response


def view(request, path):
  """Dispatches viewing of a path to either index() or fileview(), depending on type."""

  # index directory have to be default.
  if not path:
    path = '/'
  path = _normalize_path(path)

  # default_abfs_home is set in jquery.filechooser.js
  if 'default_abfs_home' in request.GET:
    from azure.abfs.__init__ import get_abfs_home_directory
    home_dir_path = get_abfs_home_directory(request.user)
    if request.fs.isdir(home_dir_path):
      return format_preserving_redirect(
          request,
          '/filebrowser/view=' + urllib_quote(home_dir_path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)
      )

  if 'default_s3_home' in request.GET:
    home_dir_path = get_s3_home_directory(request.user)
    if request.fs.isdir(home_dir_path):
      return format_preserving_redirect(
          request,
          '/filebrowser/view=' + urllib_quote(home_dir_path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)
      )

  # default_gs_home is set in jquery.filechooser.js
  if 'default_gs_home' in request.GET:
    home_dir_path = get_gs_home_directory()
    if request.fs.isdir(home_dir_path):
      return format_preserving_redirect(
          request,
          '/filebrowser/view=' + urllib_quote(home_dir_path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)
      )

  # default_ofs_home is set in jquery.filechooser.js
  if 'default_ofs_home' in request.GET:
    home_dir_path = get_ofs_home_directory()
    if request.fs.isdir(home_dir_path):
      return format_preserving_redirect(
          request,
          '/filebrowser/view=' + urllib_quote(home_dir_path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)
      )

  # default_to_home is set in jquery.filechooser.js
  if 'default_to_home' in request.GET:
    home_dir_path = request.user.get_home_directory()
    if request.fs.isdir(home_dir_path):
      return format_preserving_redirect(
          request,
          '/filebrowser/view=' + urllib_quote(home_dir_path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)
      )

  # default_to_home is set in jquery.filechooser.js
  if 'default_to_trash' in request.GET:
    home_trash_path = _home_trash_path(request.fs, request.user, path)
    if request.fs.isdir(home_trash_path):
      return format_preserving_redirect(
          request,
          '/filebrowser/view=' + urllib_quote(home_trash_path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)
      )
    trash_path = request.fs.trash_path(path)
    if request.fs.isdir(trash_path):
      return format_preserving_redirect(
          request,
          '/filebrowser/view=' + urllib_quote(trash_path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)
      )

  try:
    stats = request.fs.stats(path)
    if stats.isDir:
      return listdir_paged(request, path)
    else:
      return display(request, path)
  except S3FileSystemException as e:
    msg = _("S3 filesystem exception.")
    if is_ajax(request):
      exception = {
        'error': smart_str(e)
      }
      return JsonResponse(exception)
    else:
      raise PopupException(msg, detail=e)
  except (IOError, WebHdfsException) as e:
    msg = _("Cannot access: %(path)s. ") % {'path': escape(path)}

    if "Connection refused" in str(e):
      msg += _(" The HDFS REST service is not available. ")

    logger.error(msg + str(e))

    if is_ajax(request):
      exception = {
        'error': msg
      }
      return JsonResponse(exception)
    else:
      raise PopupException(msg, detail=e)


def _home_trash_path(fs, user, path):
  return fs.join(fs.trash_path(path), 'Current', user.get_home_directory()[1:])


def home_relative_view(request, path):
  path = _normalize_path(path)

  home_dir_path = request.user.get_home_directory()
  if request.fs.exists(home_dir_path):
    path = '%s%s' % (home_dir_path, path)

  return view(request, path)


def edit(request, path, form=None):
  """Shows an edit form for the given path. Path does not necessarily have to exist."""
  path = _normalize_path(path)

  try:
    stats = request.fs.stats(path)
  except IOError as ioe:
    # A file not found is OK, otherwise re-raise
    if ioe.errno == errno.ENOENT:
      stats = None
    else:
      raise

  # Can't edit a directory
  if stats and stats['mode'] & stat_module.S_IFDIR:
    raise PopupException(_("Cannot edit a directory: %(path)s") % {'path': path})

  # Maximum size of edit
  if stats and stats['size'] > MAX_FILEEDITOR_SIZE:
    raise PopupException(_("File too big to edit: %(path)s") % {'path': path})

  if not form:
    encoding = request.GET.get('encoding') or i18n.get_site_encoding()
    if stats:
      f = request.fs.open(path)
      try:
        try:
          current_contents = new_str(f.read(), encoding)
        except UnicodeDecodeError:
          raise PopupException(_("File is not encoded in %(encoding)s; cannot be edited: %(path)s.") % {'encoding': encoding, 'path': path})
      finally:
        f.close()
    else:
      current_contents = u""

    form = EditorForm(dict(path=path, contents=current_contents, encoding=encoding))

  data = dict(
      exists=(stats is not None),
      path=path,
      filename=os.path.basename(path),
      dirname=os.path.dirname(path),
      breadcrumbs=parse_breadcrumbs(path),
      is_embeddable=request.GET.get('is_embeddable', False),
      show_download_button=SHOW_DOWNLOAD_BUTTON.get())
  if not is_ajax(request):
    data['stats'] = stats
    data['form'] = form
  return render("edit.mako", request, data)


def save_file(request):
  """
  The POST endpoint to save a file in the file editor.

  Does the save and then redirects back to the edit page.
  """
  form = EditorForm(request.POST)
  is_valid = form.is_valid()
  path = form['path'].value()

  path = _normalize_path(path)

  if request.POST.get('save') == "Save As":
    if not is_valid:
      return edit(request, path, form=form)
    else:
      return render("saveas.mako", request, {'form': form})

  if not path:
    raise PopupException(_("No path specified"))
  if not is_valid:
    return edit(request, path, form=form)

  encoding = form.cleaned_data['encoding']
  data = form.cleaned_data['contents'].encode(encoding)

  try:
    if request.fs.exists(path):
      do_overwrite_save(request.fs, path, data)
    else:
      request.fs.create(path, overwrite=False, data=data)
  except WebHdfsException as e:
    raise PopupException(_("The file could not be saved"), detail=e.message.splitlines()[0])
  except Exception as e:
    raise PopupException(_("The file could not be saved"), detail=e)

  request.path = reverse("filebrowser:filebrowser_views_edit", kwargs=dict(path=path))
  return edit(request, path, form)


def parse_breadcrumbs(path):
  parts = splitpath(path)
  url, breadcrumbs = '', []
  for part in parts:
    if url and not url.endswith('/'):
      url += '/'
    url += part
    breadcrumbs.append({'url': url, 'label': part})
  return breadcrumbs


def listdir(request, path):
  """
  Implements directory listing (or index).

  Intended to be called via view().
  """
  path = _normalize_path(path)

  if not request.fs.isdir(path):
    raise PopupException(_("Not a directory: %(path)s") % {'path': path})

  file_filter = request.GET.get('file_filter', 'any')

  assert file_filter in ['any', 'file', 'dir']

  home_dir_path = request.user.get_home_directory()

  breadcrumbs = parse_breadcrumbs(path)

  data = {
      'path': path,
      'file_filter': file_filter,
      'breadcrumbs': breadcrumbs,
      'current_dir_path': urllib_quote(path.encode('utf-8'), safe=SAFE_CHARACTERS_URI),
      'current_request_path': '/filebrowser/view=' + urllib_quote(path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS),
      'home_directory': home_dir_path if home_dir_path and request.fs.isdir(home_dir_path) else None,
      'cwd_set': True,
      'is_superuser': request.user.username == request.fs.superuser,
      'groups': request.user.username == request.fs.superuser and [str(x) for x in Group.objects.values_list('name', flat=True)] or [],
      'users': request.user.username == request.fs.superuser and [str(x) for x in User.objects.values_list('username', flat=True)] or [],
      'superuser': request.fs.superuser,
      'show_upload': (request.GET.get('show_upload') == 'false' and (False,) or (True,))[0],
      'show_download_button': SHOW_DOWNLOAD_BUTTON.get(),
      'show_upload_button': SHOW_UPLOAD_BUTTON.get(),
      'is_embeddable': request.GET.get('is_embeddable', False),
  }

  stats = request.fs.listdir_stats(path)

  # Include parent dir, unless at filesystem root.
  if not request.fs.isroot(path):
    parent_path = request.fs.parent_path(path)
    parent_stat = request.fs.stats(parent_path)
    # The 'path' field would be absolute, but we want its basename to be
    # actually '..' for display purposes. Encode it since _massage_stats expects byte strings.
    parent_stat['path'] = parent_path
    stats.insert(0, parent_stat)

  data['files'] = [_massage_stats(request, stat_absolute_path(path, stat)) for stat in stats]
  return render('listdir.mako', request, data)


def _massage_page(page, paginator):
  try:
    prev_num = page.previous_page_number()
  except InvalidPage:
    prev_num = 0

  try:
    next_num = page.next_page_number()
  except InvalidPage:
    next_num = 0

  return {
      'number': page.number,
      'num_pages': paginator.num_pages,
      'previous_page_number': prev_num,
      'next_page_number': next_num,
      'start_index': page.start_index(),
      'end_index': page.end_index(),
      'total_count': paginator.count
  }


def listdir_paged(request, path):
  """
  A paginated version of listdir.

  Query parameters:
    pagenum           - The page number to show. Defaults to 1.
    pagesize          - How many to show on a page. Defaults to 15.
    sortby=?          - Specify attribute to sort by. Accepts:
                          (type, name, atime, mtime, size, user, group)
                        Defaults to name.
    descending        - Specify a descending sort order.
                        Default to false.
    filter=?          - Specify a substring filter to search for in
                        the filename field.
  """
  path = _normalize_path(path)

  if not request.fs.isdir(path):
    raise PopupException("Not a directory: %s" % (path,))

  pagenum = int(request.GET.get('pagenum', 1))
  pagesize = int(request.GET.get('pagesize', 30))
  do_as = None
  if is_admin(request.user) or request.user.has_hue_permission(action="impersonate", app="security"):
    do_as = request.GET.get('doas', request.user.username)
  if hasattr(request, 'doas'):
    do_as = request.doas

  if request.fs._get_scheme(path) == 'hdfs':
    home_dir_path = request.user.get_home_directory()
  else:
    home_dir_path = None
  breadcrumbs = parse_breadcrumbs(path)
  s3_listing_not_allowed = ''

  try:
    if do_as:
      all_stats = request.fs.do_as_user(do_as, request.fs.listdir_stats, path)
    else:
      all_stats = request.fs.listdir_stats(path)
  except S3ListAllBucketsException as e:
    s3_listing_not_allowed = str(e)
    all_stats = []

  # Filter first
  filter_str = request.GET.get('filter', None)
  if filter_str:
    filtered_stats = [sb for sb in all_stats if filter_str in sb['name']]
    all_stats = filtered_stats

  # Sort next
  sortby = request.GET.get('sortby', None)
  descending_param = request.GET.get('descending', None)
  if sortby is not None:
    if sortby not in ('type', 'name', 'atime', 'mtime', 'user', 'group', 'size'):
      logger.info("Invalid sort attribute '%s' for listdir." % sortby)
    else:
      all_stats = sorted(all_stats, key=operator.attrgetter(sortby), reverse=coerce_bool(descending_param))

  # Do pagination
  try:
    paginator = Paginator(all_stats, pagesize, allow_empty_first_page=True)
    page = paginator.page(pagenum)
    shown_stats = page.object_list
  except EmptyPage:
    logger.warn("No results found for requested page.")
    paginator = None
    page = None
    shown_stats = []

  # Include same dir always as first option to see stats of the current folder.
  current_stat = request.fs.stats(path)
  # The 'path' field would be absolute, but we want its basename to be
  # actually '.' for display purposes. Encode it since _massage_stats expects byte strings.
  current_stat.path = path
  current_stat.name = "."
  shown_stats.insert(0, current_stat)

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
    page.object_list = [_massage_stats(request, stat_absolute_path(path, s)) for s in shown_stats]

  is_hdfs = request.fs._get_scheme(path) == 'hdfs'
  is_trash_enabled = is_hdfs and int(get_trash_interval()) > 0
  is_fs_superuser = is_hdfs and _is_hdfs_superuser(request)

  data = {
      'path': path,
      'breadcrumbs': breadcrumbs,
      'current_request_path': '/filebrowser/view=' + urllib_quote(path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS),
      'is_trash_enabled': is_trash_enabled,
      'files': page.object_list if page else [],
      'page': _massage_page(page, paginator) if page else {},
      'pagesize': pagesize,
      'home_directory': home_dir_path if home_dir_path and request.fs.isdir(home_dir_path) else None,
      'descending': descending_param,
      # The following should probably be deprecated
      'cwd_set': True,
      'file_filter': 'any',
      'current_dir_path': path,
      'is_fs_superuser': is_fs_superuser,
      'groups': is_fs_superuser and [str(x) for x in Group.objects.values_list('name', flat=True)] or [],
      'users': is_fs_superuser and [str(x) for x in User.objects.values_list('username', flat=True)] or [],
      'superuser': request.fs.superuser,
      'supergroup': request.fs.supergroup,
      'is_sentry_managed': request.fs.is_sentry_managed(path),
      'apps': list(appmanager.get_apps_dict(request.user).keys()),
      'show_download_button': SHOW_DOWNLOAD_BUTTON.get(),
      'show_upload_button': SHOW_UPLOAD_BUTTON.get(),
      'is_embeddable': request.GET.get('is_embeddable', False),
      's3_listing_not_allowed': s3_listing_not_allowed
  }

  options_json = json.dumps(data)
  data['options_json'] = options_json
  return render('listdir.mako', request, data)


def scheme_absolute_path(root, path):
  splitPath = lib_urlparse(path)
  splitRoot = lib_urlparse(root)
  if splitRoot.scheme and not splitPath.scheme:
    path = splitPath._replace(scheme=splitRoot.scheme).geturl()
  return path


def stat_absolute_path(path, stat):
  stat.path = scheme_absolute_path(path, stat.path)
  return stat


def _massage_stats(request, stats):
  """
  Massage a stats record as returned by the filesystem implementation
  into the format that the views would like it in.
  """
  path = stats.path
  normalized = request.fs.normpath(path)
  return {
      # Normally value of 'path' should be quoted, but we only use this in POST request so we're ok.
      # Changing this to quoted causes many issues.
      'path': normalized,
      'name': stats.name,
      'stats': stats.to_json_dict(),
      'mtime': datetime.fromtimestamp(stats.mtime).strftime('%B %d, %Y %I:%M %p') if stats.mtime else '',
      'humansize': filesizeformat(stats.size),
      'type': filetype(stats.mode),
      'rwx': rwx(stats.mode, stats.aclBit),
      'mode': stringformat(stats.mode, "o"),
      'url': '/filebrowser/view=' + urllib_quote(normalized.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS),
      'is_sentry_managed': request.fs.is_sentry_managed(path)
  }


def stat(request, path):
  """
  Returns just the generic stats of a file.

  Intended for use via AJAX (and hence doesn't provide
  an HTML view).
  """
  path = _normalize_path(path)

  if not request.fs.exists(path):
    raise Http404(_("File not found: %(path)s") % {'path': escape(path)})
  stats = request.fs.stats(path)
  return JsonResponse(_massage_stats(request, stat_absolute_path(path, stats)))


def content_summary(request, path):
  path = _normalize_path(path)

  if not request.fs.exists(path):
    raise Http404(_("File not found: %(path)s") % {'path': escape(path)})
  response = {'status': -1, 'message': '', 'summary': None}
  try:
    stats = request.fs.get_content_summary(path)
    replication_factor = request.fs.stats(path)['replication']
    stats.summary.update({'replication': replication_factor})
    response['status'] = 0
    response['summary'] = stats.summary
  except WebHdfsException as e:
    response['message'] = _("The file could not be saved") + e.message.splitlines()[0]
  return JsonResponse(response)


def display(request, path):
  """
  Implements displaying part of a file.

  GET arguments are length, offset, mode, compression and encoding
  with reasonable defaults chosen.

  Note that display by length and offset are on bytes, not on characters.
  """
  path = _normalize_path(path)

  if not request.fs.isfile(path):
    raise PopupException(_("Not a file: '%(path)s'") % {'path': path})

  # display inline files just if it's not an ajax request
  if not is_ajax(request):
    if _can_inline_display(path):
      return redirect(reverse('filebrowser:filebrowser_views_download', args=[path]) + '?disposition=inline')

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
      raise PopupException(_("First byte to display must be before last byte to display."))
  else:
    length = int(request.GET.get("length", DEFAULT_CHUNK_SIZE_BYTES))
    # Display first block by default.
    offset = int(request.GET.get("offset", 0))

  mode = request.GET.get("mode")
  compression = request.GET.get("compression")

  if mode and mode not in ["binary", "text"]:
    raise PopupException(_("Mode must be one of 'binary' or 'text'."))
  if offset < 0:
    raise PopupException(_("Offset may not be less than zero."))
  if length < 0:
    raise PopupException(_("Length may not be less than zero."))
  if length > MAX_CHUNK_SIZE_BYTES:
    raise PopupException(_("Cannot request chunks greater than %(bytes)d bytes.") % {'bytes': MAX_CHUNK_SIZE_BYTES})

  # Do not decompress in binary mode.
  if mode == 'binary':
    compression = 'none'
    # Read out based on meta.
  compression, offset, length, contents = read_contents(compression, path, request.fs, offset, length)

  # Get contents as string for text mode, or at least try
  uni_contents = None
  if not mode or mode == 'text':
    if not isinstance(contents, str):
      uni_contents = new_str(contents, encoding, errors='replace')
      is_binary = uni_contents.find(i18n.REPLACEMENT_CHAR) != -1
      # Auto-detect mode
      if not mode:
        mode = is_binary and 'binary' or 'text'
    else:
      # We already have a string.
      uni_contents = contents
      is_binary = False
      mode = 'text'

  # Get contents as bytes
  if mode == "binary":
    xxd_out = list(xxd.xxd(offset, contents, BYTES_PER_LINE, BYTES_PER_SENTENCE))

  dirname = posixpath.dirname(path)
  # Start with index-like data:
  stats = request.fs.stats(path)
  data = _massage_stats(request, stat_absolute_path(path, stats))
  data["is_embeddable"] = request.GET.get('is_embeddable', False)
  # And add a view structure:
  data["success"] = True
  data["view"] = {
      'offset': offset,
      'length': length,
      'end': offset + len(contents),
      'dirname': dirname,
      'mode': mode,
      'compression': compression,
      'size': stats.size,
      'max_chunk_size': str(MAX_CHUNK_SIZE_BYTES)
  }
  data["filename"] = os.path.basename(path)
  data["editable"] = stats.size < MAX_FILEEDITOR_SIZE
  if mode == "binary":
    # This might be the wrong thing for ?format=json; doing the
    # xxd'ing in javascript might be more compact, or sending a less
    # intermediate representation...
    logger.debug("xxd: " + str(xxd_out))
    data['view']['xxd'] = xxd_out
    data['view']['masked_binary_data'] = False
  else:
    data['view']['contents'] = uni_contents
    data['view']['masked_binary_data'] = is_binary

  data['breadcrumbs'] = parse_breadcrumbs(path)
  data['show_download_button'] = SHOW_DOWNLOAD_BUTTON.get()
  data['options_json'] = json.dumps(data)
  return render("display.mako", request, data)


def _can_inline_display(path):
  mimetype = mimetypes.guess_type(path)[0]
  return mimetype is not None and INLINE_DISPLAY_MIMETYPE.search(mimetype) and INLINE_DISPLAY_MIMETYPE_EXCEPTIONS.search(mimetype) is None


def read_contents(codec_type, path, fs, offset, length):
  """
  Reads contents of a passed path, by appropriately decoding the data.
  Arguments:
     codec_type - The type of codec to use to decode. (Auto-detected if None).
     path - The path of the file to read.
     fs - The FileSystem instance to use to read.
     offset - Offset to seek to before read begins.
     length - Amount of bytes to read after offset.
     Returns: A tuple of codec_type, offset, length and contents read.
  """
  contents = ''
  fhandle = None

  path = _normalize_path(path)

  try:
    fhandle = fs.open(path)
    stats = fs.stats(path)

    # Auto codec detection for [gzip, avro, snappy, none]
    if not codec_type:
      contents = fhandle.read(3)
      fhandle.seek(0)
      codec_type = 'none'
      if path.endswith('.gz') and detect_gzip(contents):
        codec_type = 'gzip'
        offset = 0
      elif (path.endswith('.bz2') or path.endswith('.bzip2')) and detect_bz2(contents):
        codec_type = 'bz2'
      elif path.endswith('.avro') and detect_avro(contents):
        codec_type = 'avro'
      elif detect_parquet(fhandle):
        codec_type = 'parquet'
      elif path.endswith('.snappy') and snappy_installed():
        codec_type = 'snappy'
      elif snappy_installed() and stats.size <= MAX_SNAPPY_DECOMPRESSION_SIZE.get():
        fhandle.seek(0)
        if detect_snappy(fhandle.read()):
          codec_type = 'snappy'

    fhandle.seek(0)

    if codec_type == 'gzip':
      contents = _read_gzip(fhandle, path, offset, length, stats)
    elif codec_type == 'bz2':
      contents = _read_bz2(fhandle, path, offset, length, stats)
    elif codec_type == 'avro':
      contents = _read_avro(fhandle, path, offset, length, stats)
    elif codec_type == 'parquet':
      contents = _read_parquet(fhandle, path, offset, length, stats)
    elif codec_type == 'snappy':
      contents = _read_snappy(fhandle, path, offset, length, stats)
    else:
      # for 'none' type.
      contents = _read_simple(fhandle, path, offset, length, stats)

  finally:
    if fhandle:
      fhandle.close()

  return (codec_type, offset, length, contents)


def _decompress_snappy(compressed_content):
  try:
    import snappy
    return snappy.decompress(compressed_content)
  except Exception as e:
    raise PopupException(_('Failed to decompress snappy compressed file.'), detail=e)


def _read_snappy(fhandle, path, offset, length, stats):
  if not snappy_installed():
    raise PopupException(_('Failed to decompress snappy compressed file. Snappy is not installed.'))

  if stats.size > MAX_SNAPPY_DECOMPRESSION_SIZE.get():
    raise PopupException(_('Failed to decompress snappy compressed file. '
                           'File size is greater than allowed max snappy decompression size of %d.')
                         % MAX_SNAPPY_DECOMPRESSION_SIZE.get())

  return _read_simple(string_io(_decompress_snappy(fhandle.read())), path, offset, length, stats)


def _read_avro(fhandle, path, offset, length, stats):
  contents = ''
  try:
    fhandle.seek(offset)
    data_file_reader = datafile.DataFileReader(fhandle, avro_io.DatumReader())

    try:
      contents_list = []
      read_start = fhandle.tell()
      # Iterate over the entire sought file.
      for datum in data_file_reader:
        read_length = fhandle.tell() - read_start
        if read_length > length and len(contents_list) > 0:
          break
        else:
          datum_str = str(datum) + "\n"
          contents_list.append(datum_str)
    finally:
      data_file_reader.close()

    contents = "".join(contents_list)
  except Exception as e:
    logging.exception('Could not read avro file at "%s": %s' % (path, e))
    raise PopupException(_("Failed to read Avro file."))
  return contents


def _read_parquet(fhandle, path, offset, length, stats):
  try:
    size = 1 * 128 * 1024 * 1024  # Buffer file stream to 128 MiB chunks

    fhandle.seek(offset)
    file_data = BytesIO(fhandle.read(size))

    data_frame = pd.read_parquet(file_data, engine='pyarrow')

    data_chunk = data_frame.iloc[offset:offset + length].to_string()

    return data_chunk
  except Exception as e:
    logging.exception('Could not read parquet file at "%s": %s' % (path, e))
    raise PopupException(_("Failed to read Parquet file."))


def _read_gzip(fhandle, path, offset, length, stats):
  contents = ''
  if offset and offset != 0:
    raise PopupException(_("Offsets are not supported with Gzip compression."))
  try:
    contents = decompress_gzip(fhandle.read())
  except Exception as e:
    logging.exception('Could not decompress file at "%s": %s' % (path, e))
    raise PopupException(_("Failed to decompress file."))
  return contents


def _read_bz2(fhandle, path, offset, length, stats):
  contents = ''
  try:
    contents = decompress(fhandle.read(length))
  except Exception as e:
    logging.exception('Could not decompress file at "%s": %s' % (path, e))
    raise PopupException(_("Failed to decompress file."))
  return contents


def _read_simple(fhandle, path, offset, length, stats):
  contents = ''
  try:
    fhandle.seek(offset)
    contents = fhandle.read(length)
  except Exception as e:
    logging.exception('Could not read file at "%s": %s' % (path, e))
    raise PopupException(_("Failed to read file."))
  return contents


def detect_gzip(contents):
  '''This is a silly small function which checks to see if the file is Gzip'''
  return contents[:2] == b'\x1f\x8b'


def detect_bz2(contents):
  '''This is a silly small function which checks to see if the file is Bz2'''
  return contents[:3] == b'BZh'


def detect_avro(contents):
  '''This is a silly small function which checks to see if the file is Avro'''
  # Check if the first three bytes are 'O', 'b' and 'j'
  return contents[:3] == b'\x4F\x62\x6A'


def detect_snappy(contents):
  '''
  This is a silly small function which checks to see if the file is Snappy.
  It requires the entire contents of the compressed file.
  This will also return false if snappy decompression if we do not have the library available.
  '''
  try:
    import snappy
    return snappy.isValidCompressed(contents)
  except ImportError:
    logging.exception('failed to detect snappy')
    return False


def detect_parquet(fhandle):
  """
  Detect parquet from magic header bytes.
  """

  fhandle.seek(0)
  magic_number = fhandle.read(4)

  return magic_number == PARQUET_MAGIC_NUMBER


def snappy_installed():
  '''Snappy is library that isn't supported by python2.4'''
  try:
    import snappy  # noqa: F401
    return True
  except ImportError:
    return False
  except Exception:
    logging.exception('failed to verify if snappy is installed')
    return False


def _calculate_navigation(offset, length, size):
  """
  List of (offset, length, string) tuples for suggested navigation through the file.
  If offset is -1, then this option is already "selected".  (Whereas None would
  be the natural pythonic way, Django's template syntax doesn't let us test
  against None (since its truth value is the same as 0).)

  By all means this logic ought to be in the template, but the template
  language is too limiting.
  """
  if offset == 0:
    first, prev = (-1, None, _("First Block")), (-1, None, _("Previous Block"))
  else:
    first, prev = (0, length, _("First Block")), (max(0, offset - length), length, _("Previous Block"))

  if offset + length >= size:
    next, last = (-1, None, _("Next Block")), (-1, None, _("Last Block"))
  else:
    # 1-off Reasoning: if length is the same as size, you want to start at 0.
    next, last = (offset + length, length, _("Next Block")), (max(0, size - length), length, _("Last Block"))

  return first, prev, next, last


def default_initial_value_extractor(request, parameter_names):
  initial_values = {}
  for p in parameter_names:
    val = request.GET.get(p)
    if val:
      initial_values[p] = val
  return initial_values


def formset_initial_value_extractor(request, parameter_names):
  """
  Builds a list of data that formsets should use by extending some fields to every object,
  whilst others are assumed to be received in order.
  Formsets should receive data that looks like this: [{'param1': <something>,...}, ...].
  The formsets should then handle construction on their own.
  """
  def _intial_value_extractor(request):
    if not submitted:  # noqa: F821
      return []
    # Build data with list of in order parameters receive in POST data
    # Size can be inferred from largest list returned in POST data
    data = []
    for param in submitted:  # noqa: F821
      i = 0
      for val in request.POST.getlist(param):
        if len(data) == i:
          data.append({})
        data[i][param] = val
        i += 1
    # Extend every data object with recurring params
    for kwargs in data:
      for recurrent in recurring:  # noqa: F821
        kwargs[recurrent] = request.POST.get(recurrent)
    initial_data = data
    return {'initial': initial_data}

  return _intial_value_extractor


def default_arg_extractor(request, form, parameter_names):
  return [form.cleaned_data[p] for p in parameter_names]


def formset_arg_extractor(request, formset, parameter_names):
  data = []
  for form in formset.forms:
    data_dict = {}
    for p in parameter_names:
      data_dict[p] = form.cleaned_data[p]
    data.append(data_dict)
  return data


def default_data_extractor(request):
  return {'data': request.POST.copy()}


def formset_data_extractor(recurring=[], submitted=[]):
  """
  Builds a list of data that formsets should use by extending some fields to every object,
  whilst others are assumed to be received in order.
  Formsets should receive data that looks like this: [{'param1': <something>,...}, ...].
  The formsets should then handle construction on their own.
  """
  def _data_extractor(request):
    if not submitted:
      return []
    # Build data with list of in order parameters receive in POST data
    # Size can be inferred from largest list returned in POST data
    data = []
    for param in submitted:
      i = 0
      for val in request.POST.getlist(param):
        if len(data) == i:
          data.append({})
        data[i][param] = val
        i += 1
    # Extend every data object with recurring params
    for kwargs in data:
      for recurrent in recurring:
        kwargs[recurrent] = request.POST.get(recurrent)
    initial = list(data)
    return {'initial': initial, 'data': data}

  return _data_extractor


def generic_op(form_class, request, op, parameter_names, piggyback=None, template="fileop.mako",
               data_extractor=default_data_extractor, arg_extractor=default_arg_extractor,
               initial_value_extractor=default_initial_value_extractor, extra_params=None):
  """
  Generic implementation for several operations.

  @param form_class form to instantiate
  @param request incoming request, used for parameters
  @param op callable with the filesystem operation
  @param parameter_names list of form parameters that are extracted and then passed to op
  @param piggyback list of form parameters whose file stats to look up after the operation
  @param data_extractor function that extracts POST data to be used by op
  @param arg_extractor function that extracts args from a given form or formset
  @param initial_value_extractor function that extracts the initial values of a form or formset
  @param extra_params dictionary of extra parameters to send to the template for rendering
  """
  # Use next for non-ajax requests, when available.
  next = request.GET.get("next", request.POST.get("next", None))

  ret = dict({
      'next': next
  })

  if extra_params is not None:
    ret['extra_params'] = extra_params

  for p in parameter_names:
    val = request.GET.get(p)
    if val:
      ret[p] = val

  if request.method == 'POST':
    form = form_class(**data_extractor(request))
    ret['form'] = form
    if form.is_valid():
      args = arg_extractor(request, form, parameter_names)
      try:
        op(*args)
      except (IOError, WebHdfsException) as e:
        msg = _("Cannot perform operation.")
        raise PopupException(msg, detail=e)
      except S3FileSystemException as e:
        msg = _("S3 filesystem exception.")
        raise PopupException(msg, detail=e)
      except NotImplementedError as e:
        msg = _("Cannot perform operation.")
        raise PopupException(msg, detail=e)

      if next:
        logging.debug("Next: %s" % next)
        file_path_prefix = '/filebrowser/view='
        if next.startswith(file_path_prefix):
          decoded_file_path = next[len(file_path_prefix):]
          filepath_encoded_next = file_path_prefix + urllib_quote(decoded_file_path.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)
          return format_preserving_redirect(request, filepath_encoded_next)
        # Doesn't need to be quoted: quoting is done by HttpResponseRedirect.
        return format_preserving_redirect(request, next)
      ret["success"] = True
      try:
        if piggyback:
          piggy_path = form.cleaned_data.get(piggyback)
          ret["result"] = _massage_stats(request, stat_absolute_path(piggy_path, request.fs.stats(piggy_path)))
      except Exception:
        # Hard to report these more naturally here.  These happen either
        # because of a bug in the piggy-back code or because of a
        # race condition.
        logger.exception("Exception while processing piggyback data")
        ret["result_error"] = True

      ret['user'] = request.user
      if is_ajax(request):
        return HttpResponse()
      else:
        return render(template, request, ret)
  else:
    # Initial parameters may be specified with get with the default extractor
    initial_values = initial_value_extractor(request, parameter_names)
    formset = form_class(initial=initial_values)
    ret['form'] = formset
  return render(template, request, ret)


def rename(request):
  def smart_rename(src_path, dest_path):
    """If dest_path doesn't have a directory specified, use same dir."""
    if "#" in dest_path:
      raise PopupException(_("Could not rename folder \"%s\" to \"%s\": Hashes are not allowed in filenames." % (src_path, dest_path)))
    if "/" not in dest_path:
      src_dir = os.path.dirname(src_path)
      dest_path = request.fs.join(src_dir, dest_path)
    if request.fs.exists(dest_path):
      raise PopupException(_('The destination path "%s" already exists.') % dest_path)
    request.fs.rename(src_path, dest_path)

  return generic_op(RenameForm, request, smart_rename, ["src_path", "dest_path"], None)


def set_replication(request):
  def smart_set_replication(src_path, replication_factor):
    result = request.fs.set_replication(urllib_unquote(src_path), replication_factor)
    if not result:
      raise PopupException(_("Setting of replication factor failed"))

  return generic_op(SetReplicationFactorForm, request, smart_set_replication, ["src_path", "replication_factor"], None)


def mkdir(request):
  def smart_mkdir(path, name):
    # Make sure only one directory is specified at a time.
    # No absolute directory specification allowed.
    if posixpath.sep in name or "#" in name:
      raise PopupException(_("Could not name folder \"%s\": Slashes or hashes are not allowed in filenames." % name))
    request.fs.mkdir(request.fs.join(path, name))

  return generic_op(MkDirForm, request, smart_mkdir, ["path", "name"], "path")


def touch(request):
  def smart_touch(path, name):
    # Make sure only the filename is specified.
    # No absolute path specification allowed.
    if posixpath.sep in name:
      raise PopupException(_("Could not name file \"%s\": Slashes are not allowed in filenames." % name))
    request.fs.create(
        request.fs.join(
            (path.encode('utf-8') if not isinstance(path, str) else path),
            (name.encode('utf-8') if not isinstance(name, str) else name)
        )
    )

  return generic_op(TouchForm, request, smart_touch, ["path", "name"], "path")


@require_http_methods(["POST"])
def rmtree(request):
  recurring = []
  params = ["path"]

  def bulk_rmtree(*args, **kwargs):
    for arg in args:
      request.fs.do_as_user(request.user, request.fs.rmtree, arg['path'], 'skip_trash' in request.GET)
  return generic_op(RmTreeFormSet, request, bulk_rmtree, ["path"], None,
                    data_extractor=formset_data_extractor(recurring, params),
                    arg_extractor=formset_arg_extractor,
                    initial_value_extractor=formset_initial_value_extractor)


@require_http_methods(["POST"])
def move(request):
  recurring = ['dest_path']
  params = ['src_path']

  def bulk_move(*args, **kwargs):
    for arg in args:
      if arg['src_path'] == arg['dest_path']:
        raise PopupException(_('Source path and destination path cannot be same'))
      request.fs.rename(
          arg['src_path'].encode('utf-8') if not isinstance(arg['src_path'], str) else arg['src_path'],
          arg['dest_path'].encode('utf-8') if not isinstance(arg['dest_path'], str) else arg['dest_path']
      )
  return generic_op(RenameFormSet, request, bulk_move, ["src_path", "dest_path"], None,
                    data_extractor=formset_data_extractor(recurring, params),
                    arg_extractor=formset_arg_extractor,
                    initial_value_extractor=formset_initial_value_extractor)


@require_http_methods(["POST"])
def copy(request):
  recurring = ['dest_path']
  params = ['src_path']

  def bulk_copy(*args, **kwargs):
    ofs_skip_files = ''
    for arg in args:
      if arg['src_path'] == arg['dest_path']:
        raise PopupException(_('Source path and destination path cannot be same'))

      # Copy method for OFS returns a string of skipped files if their size is greater than chunk size.
      if arg['src_path'].startswith('ofs://'):
        ofs_skip_files += request.fs.copy(arg['src_path'], arg['dest_path'], recursive=True, owner=request.user)
      else:
        request.fs.copy(arg['src_path'], arg['dest_path'], recursive=True, owner=request.user)

    # Send skipped filenames via raising exception to let users know.
    if ofs_skip_files:
      raise PopupException("Following files were skipped due to file size limitations:" + ofs_skip_files)

  return generic_op(CopyFormSet, request, bulk_copy, ["src_path", "dest_path"], None,
                    data_extractor=formset_data_extractor(recurring, params),
                    arg_extractor=formset_arg_extractor,
                    initial_value_extractor=formset_initial_value_extractor)


@require_http_methods(["POST"])
def chmod(request):
  recurring = ["sticky", "user_read", "user_write", "user_execute",
               "group_read", "group_write", "group_execute",
               "other_read", "other_write", "other_execute"]
  params = ["path"]

  def bulk_chmod(*args, **kwargs):
    op = partial(request.fs.chmod, recursive=request.POST.get('recursive', False))
    for arg in args:
      op(arg['path'], arg['mode'])
  # mode here is abused: on input, it's a string, but when retrieved,
  # it's an int.
  return generic_op(ChmodFormSet, request, bulk_chmod, ['path', 'mode'], "path",
                    data_extractor=formset_data_extractor(recurring, params),
                    arg_extractor=formset_arg_extractor,
                    initial_value_extractor=formset_initial_value_extractor)


@require_http_methods(["POST"])
def chown(request):
  # This is a bit clever: generic_op takes an argument (here, args), indicating
  # which POST parameters to pick out and pass to the given function.
  # We update that mapping based on whether or not the user selected "other".
  param_names = ["path", "user", "group"]
  if request.POST.get("user") == "__other__":
    param_names[1] = "user_other"
  if request.POST.get("group") == "__other__":
    param_names[2] = "group_other"

  recurring = ["user", "group", "user_other", "group_other"]
  params = ["path"]

  def bulk_chown(*args, **kwargs):
    op = partial(request.fs.chown, recursive=request.POST.get('recursive', False))
    for arg in args:
      varg = [urllib_unquote(arg[param]) for param in param_names]
      op(*varg)

  return generic_op(ChownFormSet, request, bulk_chown, param_names, "path",
                    data_extractor=formset_data_extractor(recurring, params),
                    arg_extractor=formset_arg_extractor,
                    initial_value_extractor=formset_initial_value_extractor)


@require_http_methods(["POST"])
def trash_restore(request):
  recurring = []
  params = ["path"]

  def bulk_restore(*args, **kwargs):
    for arg in args:
      request.fs.do_as_user(request.user, request.fs.restore, urllib_unquote(arg['path']))
  return generic_op(RestoreFormSet, request, bulk_restore, ["path"], None,
                    data_extractor=formset_data_extractor(recurring, params),
                    arg_extractor=formset_arg_extractor,
                    initial_value_extractor=formset_initial_value_extractor)


@require_http_methods(["POST"])
def trash_purge(request):
  return generic_op(TrashPurgeForm, request, request.fs.purge_trash, [], None)


def _create_response(request, _fs, result="success", data="Success"):
  return {
      'path': _fs.filepath,
      'result': result,
      'next': request.GET.get("next"),
      'success': True,
      'uuid': _fs.qquuid,
      'status': 0,
      'data': data,
      'task_id': _fs.qquuid
  }


def perform_upload_task(request, *args, **kwargs):
  """
  Uploads a file to the specified destination.
  Args:
    request: The HTTP request object.
    **kwargs: Arbitrary keyword arguments.
  Returns:
    A dictionary containing the following keys:
      - path: The path of the uploaded file.
      - result: The result of the upload operation.
      - next: The URL to redirect to after the upload operation.
      - success: A boolean indicating whether the upload operation was successful.
      - uuid: The UUID of the uploaded file.
      - status: The status of the upload operation.
      - data: Additional data about the upload operation.
  """
  scheme = get_scheme(kwargs['dest'])
  upload_class = UPLOAD_CLASSES.get(scheme, LocalFineUploaderChunkedUpload)
  result = None

  if TASK_SERVER_V2.ENABLED.get():
    # If task server is enabled, upload the file to the task server.
    print("Uploading file to task server")
    _fs = upload_class(request, **kwargs)
    _fs.check_access()
    from filebrowser.tasks import error_handler, upload_file_task
    kwargs["user_id"] = request.user.id
    kwargs["scheme"] = scheme
    kwargs["filepath"] = _fs.filepath
    kwargs["chunk_size"] = _fs.chunk_size
    task_id = kwargs.get("qquuid")
    upload_file_task.apply_async(task_id=task_id, args=(), kwargs=kwargs, link_error=error_handler.s(), queue="default")
    result = "task started %s" % task_id
    logger.info("Task started %s" % task_id)
  else:
    _fs = upload_class(request, **kwargs)
    _fs.upload()
    if scheme == 'hdfs':
      result = _massage_stats(request, stat_absolute_path(_fs.filepath, request.fs.stats(_fs.filepath)))
    else:
      result = "success"
  return _create_response(request, _fs, result=result, data="Success")


def extract_upload_data(request, method):
  data = request.POST if method == "POST" else request.GET
  chunks = {
    "qquuid": data.get('qquuid'),
    "qqpartindex": int(data.get('qqpartindex', 0)),
    "qqpartbyteoffset": int(data.get('qqpartbyteoffset', 0)),
    "qqtotalfilesize": int(data.get('qqtotalfilesize', 0)),
    "qqtotalparts": int(data.get('qqtotalparts', 1)),
    "qqfilename": data.get('qqfilename'),
    "qqchunksize": int(data.get('qqchunksize', 0)),
    "dest": data.get('dest', None),
    "fileFieldLabel": data.get('fileFieldLabel')
  }
  return chunks


@require_http_methods(["POST"])
def upload_chunks(request):
  """
  View function to handle chunked file uploads using Fine Uploader.
  Args:
  - request: The HTTP request object.
  Returns:
  - JsonResponse: A JSON response object with the following keys:
    - success: A boolean indicating whether the upload was successful.
    - uuid: A string representing the unique identifier for the uploaded file.
    - error: A string representing the error message if the upload failed.
  """
  try:
    for _ in request.FILES.values():  # This processes the upload.
      pass
  except StopUpload:
    return JsonResponse({"success": False, "error": "Error in upload"})

  # case where file is larger than the single chunk size
  if int(request.GET.get("qqtotalparts", 0)) > 0:
    return JsonResponse({"success": True, "uuid": request.GET.get("qquuid")})

  # case where file is smaller than the chunk size
  if int(request.GET.get("qqtotalparts", 0)) == 0:
    chunks = extract_upload_data(request, "GET")
    try:
      response = perform_upload_task(request, **chunks)
      return JsonResponse(response)
    except PopupException as e:
      logger.error(f"Upload failed: {e}")
      return JsonResponse({"success": False, "error": str(e)})
    except Exception as e:
      # For unexpected exceptions, log the full error but return a generic message
      logger.exception(f"Unexpected error during upload: {e}")
      return JsonResponse({"success": False, "error": "Upload failed due to an unexpected error"})
  return JsonResponse({"success": False, "error": "Unsupported request method"})


@require_http_methods(["POST"])
def upload_complete(request):
  """
  View function that handles the completion of a file upload.
  Args:
    request (HttpRequest): The HTTP request object.
  Returns:
    JsonResponse: A JSON response containing the result of the upload.
  """
  chunks = extract_upload_data(request, "POST")
  try:
    response = perform_upload_task(request, **chunks)
    return JsonResponse(response)
  except PopupException as e:
    logger.error(f"Upload failed: {e}")
    return JsonResponse({"success": False, "error": str(e)})
  except Exception as e:
    # For unexpected exceptions, log the full error but return a generic message
    logger.exception(f"Unexpected error during upload: {e}")
    return JsonResponse({"success": False, "error": "Upload failed due to an unexpected error"})


@require_http_methods(["POST"])
def upload_file(request):
  """
  A wrapper around the actual upload view function to clean up the temporary file afterwards if it fails.

  Returns JSON.
  e.g. {'status' 0/1, data:'message'...}
  """
  response = {'status': -1, 'data': ''}

  try:
    resp = _upload_file(request)
    response.update(resp)
  except Exception as ex:
    logger.exception('Upload failure')
    response['data'] = smart_str(ex).split('\n', 1)[0]
    hdfs_file = request.FILES.get('hdfs_file')
    if hdfs_file and hasattr(hdfs_file, 'remove'):  # TODO: Call from proxyFS
      hdfs_file.remove()

  return JsonResponse(response)


def _upload_file(request):
  """
  Handles file uploaded by HDFSfileUploadHandler.

  The uploaded file is stored in HDFS at its destination with a .tmp suffix.
  We just need to rename it to the destination path.
  """
  form = UploadFileForm(request.POST, request.FILES)
  response = {'status': -1, 'data': ''}

  if request.META.get('upload_failed'):
    raise PopupException(request.META.get('upload_failed'))

  if form.is_valid():
    uploaded_file = request.FILES['hdfs_file']
    dest = request.GET['dest']
    filepath = request.fs.join(dest, uploaded_file.name)

    if request.fs.isdir(dest) and posixpath.sep in uploaded_file.name:
      raise PopupException(_('Sorry, no "%(sep)s" in the filename %(name)s.' % {'sep': posixpath.sep, 'name': uploaded_file.name}))

    try:
      request.fs.upload(file=uploaded_file, path=dest, username=request.user.username)
      response['status'] = 0
    except IOError as ex:
      already_exists = False
      try:
        already_exists = request.fs.exists(dest)
      except Exception:
        pass
      if already_exists:
        msg = _('Destination %(name)s already exists.') % {'name': filepath}
      else:
        msg = _('Copy to %(name)s failed: %(error)s') % {'name': filepath, 'error': ex}
      raise PopupException(msg)

    response.update({
        'path': filepath,
        'result': _massage_stats(request, stat_absolute_path(filepath, request.fs.stats(filepath))),
        'next': request.GET.get("next")
    })

    return response
  else:
    raise PopupException(_("Error in upload form: %s") % (form.errors,))


@require_http_methods(["POST"])
def extract_archive_using_batch_job(request):

  response = {'status': -1, 'data': ''}
  if ENABLE_EXTRACT_UPLOADED_ARCHIVE.get():
    upload_path = request.fs.netnormpath(request.POST.get('upload_path', None))
    archive_name = request.POST.get('archive_name', None)

    if upload_path and archive_name:
      try:
        upload_path = urllib_unquote(upload_path)
        archive_name = urllib_unquote(archive_name)
        response = extract_archive_in_hdfs(request, upload_path, archive_name)
      except Exception as e:
        response['message'] = _('Exception occurred while extracting archive: %s' % e)
  else:
    response['message'] = _('ERROR: Configuration parameter enable_extract_uploaded_archive ' +
                            'has to be enabled before calling this method.')

  return JsonResponse(response)


@require_http_methods(["POST"])
def compress_files_using_batch_job(request):

  response = {'status': -1, 'data': ''}
  if ENABLE_EXTRACT_UPLOADED_ARCHIVE.get():
    upload_path = request.fs.netnormpath(request.POST.get('upload_path', None))
    archive_name = request.POST.get('archive_name', None)
    file_names = request.POST.getlist('files[]')

    if upload_path and file_names and archive_name:
      try:
        response = compress_files_in_hdfs(request, file_names, upload_path, archive_name)
      except Exception as e:
        response['message'] = _('Exception occurred while compressing files: %s' % e)
    else:
      response['message'] = _('Error: Output directory is not set.')
  else:
    response['message'] = _('ERROR: Configuration parameter enable_extract_uploaded_archive ' +
                            'has to be enabled before calling this method.')

  return JsonResponse(response)


def status(request):
  status = request.fs.status()
  data = {
      # Beware: "messages" is special in the context browser.
      'msgs': status.get_messages(),
      'health': status.get_health(),
      'datanode_report': status.get_datanode_report(),
      'name': request.fs.name
  }
  return render("status.mako", request, data)


def truncate(toTruncate, charsToKeep=50):
  """
  Returns a string truncated to 'charsToKeep' length plus ellipses.
  """
  if len(toTruncate) > charsToKeep:
    truncated = toTruncate[:charsToKeep] + "..."
    return truncated
  else:
    return toTruncate


def unquote_url(url):
  url = urllib_unquote(url.encode('utf-8') if not isinstance(url, str) else url)
  return url.decode('utf-8') if isinstance(url, bytes) else url


def _is_hdfs_superuser(request):
  return request.user.username == request.fs.superuser or request.user.groups.filter(name__exact=request.fs.supergroup).exists()
