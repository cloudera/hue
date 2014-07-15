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


def _get_acl_name(acl):
  return ('default:' if acl['isDefault'] else '') + acl['type'] + ':' + acl['name'] + ':'

def _get_acl(acl):
  return _get_acl_name(acl) + ('r' if acl['r']  else '-') + ('w' if acl['w'] else '-') + ('x' if acl['x'] else '-')


def get_acls(request):
  path = request.GET.get('path')
  acls = request.fs.get_acl_status(path)
  return HttpResponse(json.dumps(acls['AclStatus']), mimetype="application/json")


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