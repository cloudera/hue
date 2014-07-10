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


def get_acls(request):  
  path = request.GET.get('path')
  acls = request.fs.get_acl_status(path)
  return HttpResponse(json.dumps(acls['AclStatus']), mimetype="application/json")


def modify_acl_entries(request):  
  path = request.GET.get('path')
  aclspec = request.GET.get('aclspec')
  info = request.fs.modify_acl_entries(path, aclspec)
  return HttpResponse(json.dumps(info), mimetype="application/json")


def remove_acl_entries(request):  
  path = request.GET.get('path')
  aclspec = request.GET.get('aclspec')
  info = request.fs.remove_acl_entries(path, aclspec)
  return HttpResponse(json.dumps(info), mimetype="application/json")

