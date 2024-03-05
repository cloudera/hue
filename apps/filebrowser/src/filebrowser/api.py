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
import posixpath
import os

from django.http import HttpResponse
from django.utils.translation import gettext as _

from desktop.lib.django_util import JsonResponse
from desktop.lib import fsmanager
from desktop.lib.i18n import smart_unicode
from desktop.lib.fs.ozone.ofs import get_ofs_home_directory
from desktop.lib.fs.gc.gs import get_gs_home_directory

from azure.abfs.__init__ import get_home_dir_for_abfs
from aws.s3.s3fs import get_s3_home_directory

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
def get_filesystems_with_home_dirs(request): # Using as a public API only for now
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
      user_home_dir = get_home_dir_for_abfs(request.user)
    elif fs == 'ofs':
      user_home_dir = get_ofs_home_directory()

    filesystems.append({
      'file_system': fs,
      'user_home_directory': user_home_dir,
    })

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
    raise Exception(_(
      "Error renaming %s to %s. Hashes are not allowed in file or directory names." % (os.path.basename(src_path), dest_path)
      ))

  # If dest_path doesn't have a directory specified, use same dir.
  if "/" not in dest_path:
    src_dir = os.path.dirname(src_path)
    dest_path = request.fs.join(src_dir, dest_path)

  if request.fs.exists(dest_path):
    raise Exception(_('The destination path "%s" already exists.') % dest_path)

  request.fs.rename(src_path, dest_path)
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
    stats = request.fs.get_content_summary(path)
    replication_factor = request.fs.stats(path)['replication']
    stats.summary.update({'replication': replication_factor})
    response['summary'] = stats.summary
  except Exception as e:
    raise Exception(_('Failed to fetch content summary for "%s". ') % path)

  return JsonResponse(response)
