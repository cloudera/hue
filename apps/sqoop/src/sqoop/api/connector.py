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

from __future__ import absolute_import

import sys
import json
import socket
import logging

from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions import StructuredException
from desktop.lib.rest.http_client import RestException
from sqoop import client, conf
from sqoop.api.decorators import get_connector_or_exception
from sqoop.api.exception import handle_rest_exception
from sqoop.api.utils import list_to_dict

__all__ = ['get_connectors', 'connectors', 'connector']


LOG = logging.getLogger()


@never_cache
def get_connectors(request):
  response = {
    'status': 0,
    'errors': None,
    'connectors': []
  }
  try:
    c = client.SqoopClient(
      conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE, ssl_cert_ca_verify=conf.SSL_CERT_CA_VERIFY.get()
    )
    response['connectors'] = list_to_dict(c.get_connectors())
  except RestException as e:
    response.update(handle_rest_exception(e, _('Could not get connectors.')))
  return JsonResponse(response)


def connectors(request):
  if request.method == 'GET':
    return get_connectors(request)
  else:
    raise StructuredException(code="INVALID_METHOD", message=_('GET request required.'), error_code=405)


@never_cache
@get_connector_or_exception()
def connector(request, connector):
  response = {
    'status': 0,
    'errors': None,
    'connector': None
  }
  if request.method == 'GET':
    response['connector'] = connector.to_dict()
    return JsonResponse(response)
  else:
    raise StructuredException(code="INVALID_METHOD", message=_('GET request required.'), error_code=405)
