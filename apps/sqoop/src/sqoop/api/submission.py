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
import socket

from django.utils.translation import ugettext as _

from sqoop import client, conf
from decorators import get_submission_or_exception
from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions import StructuredException
from desktop.lib.rest.http_client import RestException
from exception import handle_rest_exception
from utils import list_to_dict
from django.views.decorators.cache import never_cache

__all__ = ['get_submissions', 'submissions']


LOG = logging.getLogger(__name__)

@never_cache
def get_submissions(request):
  response = {
    'status': 0,
    'errors': None,
    'submissions': []
  }
  status = request.GET.get('status', 'submissions').split(',')
  try:
    c = client.SqoopClient(conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE, ssl_cert_ca_verify=conf.SSL_CERT_CA_VERIFY.get())
    submissions = c.get_submissions()
    response['submissions'] = list_to_dict(submissions)
  except RestException, e:
    response.update(handle_rest_exception(e, _('Could not get submissions.')))
  return JsonResponse(response)

@never_cache
def submissions(request):
  if request.method == 'GET':
    return get_submissions(request)
  else:
    raise StructuredException(code="INVALID_METHOD", message=_('GET request required.'), error_code=405)
