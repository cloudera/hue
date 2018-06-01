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
from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions import StructuredException
from desktop.lib.rest.http_client import RestException
from exception import handle_rest_exception
from django.views.decorators.cache import never_cache

__all__ = ['driver']


LOG = logging.getLogger(__name__)

@never_cache
def driver(request):
  response = {
    'status': 0,
    'errors': None,
    'driver': None
  }
  if request.method == 'GET':
    try:
      c = client.SqoopClient(conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE, ssl_cert_ca_verify=conf.SSL_CERT_CA_VERIFY.get())
      response['driver'] = c.get_driver().to_dict()
    except RestException, e:
      response.update(handle_rest_exception(e, _('Could not get driver.')))
    return JsonResponse(response)
  else:
    raise StructuredException(code="INVALID_METHOD", message=_('GET request required.'), error_code=405)
