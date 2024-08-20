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
import posixpath

from django.http import HttpResponse
from django.utils.translation import gettext as _

from aws.s3.s3fs import get_s3_home_directory
from azure.abfs.__init__ import get_abfs_home_directory
from desktop.lib import fsmanager
from desktop.lib.django_util import JsonResponse
from desktop.lib.fs.gc.gs import get_gs_home_directory
from desktop.lib.fs.ozone.ofs import get_ofs_home_directory
from desktop.lib.i18n import smart_unicode
from filebrowser.views import _normalize_path

LOG = logging.getLogger()


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    response = {}
    try:
      return view_fn(*args, **kwargs)
    except Exception as e:
      LOG.exception('Error running %s' % view_fn)
      response['status'] = -1
      response['message'] = smart_unicode(e)
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


@error_handler
def get_filesystems_with_home_dirs(request):  # Using as a public API only for now
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


@error_handler
def mkdir(request):
  path = request.POST.get('path')
  name = request.POST.get('name')

  if name and (posixpath.sep in name or "#" in name):
    raise Exception(_("Error creating %s directory. Slashes or hashes are not allowed in directory name." % name))

  request.fs.mkdir(request.fs.join(path, name))
  return HttpResponse(status=200)


@error_handler
def touch(request):
  path = request.POST.get('path')
  name = request.POST.get('name')

  if name and (posixpath.sep in name):
    raise Exception(_("Error creating %s file. Slashes are not allowed in filename." % name))

  request.fs.create(request.fs.join(path, name))
  return HttpResponse(status=200)


@error_handler
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


@error_handler
def move(request):
  src_path = request.POST.get('src_path')
  dest_path = request.POST.get('dest_path')

  if src_path == dest_path:
    raise Exception(_('Source and destination path cannot be same.'))

  request.fs.rename(src_path, dest_path)
  return HttpResponse(status=200)


@error_handler
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


@error_handler
def content_summary(request, path):
  path = _normalize_path(path)
  response = {}

  if not path:
    raise Exception(_('Path parameter is required to fetch content summary.'))

  if not request.fs.exists(path):
    return JsonResponse(response, status=404)

  try:
    content_summary = request.fs.get_content_summary(path)
    replication_factor = request.fs.stats(path)['replication']

    content_summary.summary.update({'replication': replication_factor})
    response['summary'] = content_summary.summary
  except Exception as e:
    raise Exception(_('Failed to fetch content summary for "%s". ') % path)

  return JsonResponse(response)


@error_handler
def set_replication(request):
  src_path = request.POST.get('src_path')
  replication_factor = request.POST.get('replication_factor')

  result = request.fs.set_replication(src_path, replication_factor)
  if not result:
    raise Exception(_("Failed to set the replication factor."))

  return HttpResponse(status=200)


@error_handler
def rmtree(request):
  path = request.POST.get('path')
  skip_trash = request.POST.get('skip_trash', False)

  request.fs.rmtree(path, skip_trash)

  return HttpResponse(status=200)


@error_handler
def get_trash_path(request):
  path = _normalize_path(request.GET.get('path'))
  response = {}

  trash_path = request.fs.trash_path(path)
  user_home_trash_path = request.fs.join(request.fs.current_trash_path(trash_path), request.user.get_home_directory().lstrip('/'))

  if request.fs.isdir(user_home_trash_path):
    response['trash_path'] = user_home_trash_path
  elif request.fs.isdir(trash_path):
    response['trash_path'] = trash_path
  else:
    response['message'] = _('Trash path not found: The requested trash path for user does not exist.')
    return JsonResponse(response, status=404)

  return JsonResponse(response)


@error_handler
def trash_restore(request):
  path = request.POST.get('path')
  request.fs.restore(path)

  return HttpResponse(status=200)


@error_handler
def trash_purge(request):
  request.fs.purge_trash()

  return HttpResponse(status=200)
