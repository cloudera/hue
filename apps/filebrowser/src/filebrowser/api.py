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

from desktop.lib.django_util import JsonResponse
from desktop.lib.fsmanager import FS_GETTERS
from desktop.lib.i18n import smart_unicode

from aws.conf import has_s3_access


LOG = logging.getLogger(__name__)


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    response = {}
    try:
      return view_fn(*args, **kwargs)
    except Exception, e:
      LOG.exception('Error running %s' % view_fn)
      response['status'] = -1
      response['message'] = smart_unicode(e)
    return JsonResponse(response)
  return decorator


@error_handler
def get_filesystems(request):
  response = {}

  filesystems = {}
  for k, v in FS_GETTERS.items():
    if not k.startswith('s3') or has_s3_access(request.user):
      filesystems[k] = v is not None

  response['status'] = 0
  response['filesystems'] = filesystems

  return JsonResponse(response)
