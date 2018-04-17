#!/usr/bin/env python
# -- coding: utf-8 --
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
import logging

from metadata.manager_client import ManagerApi

try:
  from collections import OrderedDict
except ImportError:
  from ordereddict import OrderedDict # Python 2.6

from django.http import Http404
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import force_unicode, smart_unicode

from metadata.conf import has_navigator
from metadata.navigator_client import NavigatorApiException


LOG = logging.getLogger(__name__)


class ManagerApiException(Exception):
  def __init__(self, message=None):
    self.message = message or _('No error message, please check the logs.')

  def __str__(self):
    return str(self.message)

  def __unicode__(self):
    return smart_unicode(self.message)


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    status = 500
    response = {
      'message': ''
    }

    try:
      if has_navigator(args[0].user): # TODO
        return view_fn(*args, **kwargs)
      else:
        raise NavigatorApiException('Navigator API is not configured.')
    except NavigatorApiException, e:
      try:
        response['message'] = json.loads(e.message)
      except Exception:
        response['message'] = force_unicode(e.message)
    except Exception, e:
      message = force_unicode(e)
      response['message'] = message
      LOG.exception(message)

    return JsonResponse(response, status=status)
  return decorator


@error_handler
def hello(request):
  api = ManagerApi(request.user)

  response = api.tools_echo()

  return JsonResponse(response)
