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

from django.http import HttpResponse
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from filebrowser.views import display, listdir_paged


def _get_acl_name(acl):
  return ('default:' if acl['isDefault'] else '') + acl['type'] + ':' + acl['name'] + ':'

def _get_acl(acl):
  return _get_acl_name(acl) + ('r' if acl['r']  else '-') + ('w' if acl['w'] else '-') + ('x' if acl['x'] else '-')

def _diff_list_dir(user_listing, hdfs_listing):
  user_files = [f['stats']['path'] for f in user_listing['files']]
  hdfs_files = [f['stats']['path'] for f in hdfs_listing['files']]
  
  # Files visible by hdfs only  
  hdfs_only = list(set(hdfs_files) - set(user_files))
  new_hdfs = filter(lambda f: f['stats']['path'] in hdfs_only, hdfs_listing['files'])

  for f in new_hdfs:
    f['striked'] = True
    
  listing = user_listing['files'] + new_hdfs
  
  return sorted(listing, key=lambda f: f['path']) 


def list_hdfs(request, path):
  try:
    stats = request.fs.stats(path)
    if stats.isDir:
        json_response = listdir_paged(request, path)
    else:
        json_response = display(request, path)
  except:
    json_response = HttpResponse(json.dumps({'files': []}), mimetype="application/json") # AccessControlException: Permission denied: user=test, access=READ_EXECUTE, inode="/tmp/dir":romain:supergroup:drwxr-xr-x:group::r-x,group:bob:---,group:test:---,default:user::rwx,default:group::r--,default:mask::r--,default:other::rwx (error 403)
  if json.loads(request.GET.get('isDiffMode', 'false')):
    request.doas = 'hdfs'
    hdfs_response = listdir_paged(request, path)
    resp = json.loads(json_response.content)
    resp['files'] = _diff_list_dir(resp, json.loads(hdfs_response.content))
    json_response.content = json.dumps(resp)
      
  return json_response


def get_acls(request):
  path = request.GET.get('path')
  try:
    acls = request.fs.get_acl_status(path)
  except Exception, e:
    acls = None

  return HttpResponse(json.dumps(acls is not None and acls['AclStatus'] or None), mimetype="application/json")


def update_acls(request):
  path = request.POST.get('path')
  acls = json.loads(request.POST.get('acls'))
  original_acls = json.loads(request.POST.get('originalAcls'))  
  
  try:
    renamed_acls = set([_get_acl_name(acl) for acl in original_acls]) - set([_get_acl_name(acl) for acl in acls]) # We need to remove ACLs that have been renamed
    _remove_acl_names(request.fs, path, list(renamed_acls))
    _remove_acl_entries(request.fs, path, [acl for acl in acls if acl['status'] == 'deleted'])
    _modify_acl_entries(request.fs, path, [acl for acl in acls if acl['status'] in ('new', 'modified')])
  except Exception, e:
    raise PopupException(unicode(str(e.message), "utf8"))

  return HttpResponse(json.dumps({'status': 0}), mimetype="application/json")



def _modify_acl_entries(fs, path, acls):
  aclspec = ','.join([_get_acl(acl) for acl in acls])
  return fs.modify_acl_entries(path, aclspec)


def _remove_acl_entries(fs, path, acls):
  aclspec = ','.join([_get_acl_name(acl) for acl in acls])
  return fs.remove_acl_entries(path, aclspec)


def _remove_acl_names(fs, path, acl_names):
  aclspec = ','.join(acl_names)
  return fs.remove_acl_entries(path, aclspec)