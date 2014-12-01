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
import logging

from django.http import HttpResponse
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode

from spark.decorators import json_error_handler
from spark.models import get_api


LOG = logging.getLogger(__name__)


@json_error_handler
def create_session(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  try:
    response['session'] = get_api(request.user, snippet).create_session(lang=snippet['type'])
    response['status'] = 0
  except Exception, e:
    raise PopupException(e, title=_('Error while accessing query server'))
    response['error'] = force_unicode(str(e))

  return HttpResponse(json.dumps(response), mimetype="application/json")

@json_error_handler
def execute(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  try:
    response['handle'] = get_api(request.user, snippet).execute(notebook, snippet)
    response['status'] = 0
  except Exception, e:
    raise PopupException(e, title=_('Error while accessing query server'))
    response['error'] = force_unicode(str(e))

  return HttpResponse(json.dumps(response), mimetype="application/json")


@json_error_handler
def check_status(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  try:
    response['query_status'] = get_api(request.user, snippet).check_status(notebook, snippet)
    response['status'] = 0
  except Exception, e:
    raise PopupException(e, title=_('Error while accessing query server'))
    response['error'] = force_unicode(str(e))

  return HttpResponse(json.dumps(response), mimetype="application/json")


@json_error_handler
def fetch_result(request):
  response = {'status': -1}

  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))

  try:
    response['result'] = get_api(request.user, snippet).fetch_result(notebook, snippet)
    response['status'] = 0
  except Exception, e:
    raise PopupException(e, title=_('Error while accessing query server'))
    response['error'] = force_unicode(str(e))

  return HttpResponse(json.dumps(response), mimetype="application/json")
