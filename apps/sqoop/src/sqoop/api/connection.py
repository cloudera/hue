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

try:
  import json
except ImportError:
  import simplejson as json
import logging
import socket

from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _

from sqoop import client, conf
from sqoop.client.connection import SqoopConnectionException
from decorators import get_connection_or_exception
from desktop.lib.exceptions import StructuredException
from desktop.lib.rest.http_client import RestException
from exception import handle_rest_exception
from utils import list_to_dict
from django.views.decorators.cache import never_cache

__all__ = ['get_connections', 'create_connection', 'update_connection', 'connection', 'connections', 'connection_clone', 'connection_delete']


LOG = logging.getLogger(__name__)

@never_cache
def get_connections(request):
  response = {
    'status': 0,
    'errors': None,
    'connections': []
  }
  try:
    c = client.SqoopClient(conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE)
    response['connections'] = list_to_dict(c.get_connections())
  except RestException, e:
    response.update(handle_rest_exception(e, _('Could not get connections.')))
  return HttpResponse(json.dumps(response), mimetype="application/json")

@never_cache
def create_connection(request):
  response = {
    'status': 0,
    'errors': None,
    'connection': None
  }

  if 'connection' not in request.POST:
    raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Error saving connection'), data={'errors': 'Connection is missing.'}, error_code=400)

  d = json.loads(smart_str(request.POST['connection']))
  conn = client.Connection.from_dict(d)

  try:
    c = client.SqoopClient(conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE)
    response['connection'] = c.create_connection(conn).to_dict()
  except RestException, e:
    response.update(handle_rest_exception(e, _('Could not create connection.')))
  except SqoopConnectionException, e:
    response['status'] = 100
    response['errors'] = e.to_dict()
  return HttpResponse(json.dumps(response), mimetype="application/json")

@never_cache
def update_connection(request, connection):
  response = {
    'status': 0,
    'errors': None,
    'connection': None
  }

  if 'connection' not in request.POST:
    raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Error saving connection'), data={'errors': 'Connection is missing.'}, error_code=400)

  connection.update_from_dict(json.loads(smart_str(request.POST['connection'])))

  try:
    c = client.SqoopClient(conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE)
    response['connection'] = c.update_connection(connection).to_dict()
  except RestException, e:
    response.update(handle_rest_exception(e, _('Could not update connection.')))
  except SqoopConnectionException, e:
    response['status'] = 100
    response['errors'] = e.to_dict()
  return HttpResponse(json.dumps(response), mimetype="application/json")

@never_cache
def connections(request):
  if request.method == 'GET':
    return get_connections(request)
  elif request.method == 'POST':
    return create_connection(request)
  else:
    raise StructuredException(code="INVALID_METHOD", message=_('GET or POST request required.'), error_code=405)

@never_cache
@get_connection_or_exception()
def connection(request, connection):
  response = {
    'status': 0,
    'errors': None,
    'connection': None
  }
  if request.method == 'GET':
    response['connection'] = connection.to_dict()
    return HttpResponse(json.dumps(response), mimetype="application/json")
  elif request.method == 'POST':
    return update_connection(request, connection)
  else:
    raise StructuredException(code="INVALID_METHOD", message=_('GET or POST request required.'), error_code=405)

@never_cache
@get_connection_or_exception()
def connection_clone(request, connection):
  if request.method != 'POST':
    raise StructuredException(code="INVALID_METHOD", message=_('POST request required.'), error_code=405)

  response = {
    'status': 0,
    'errors': None,
    'connection': None
  }

  connection.id = -1
  connection.name = '%s-copy' % connection.name
  try:
    c = client.SqoopClient(conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE)
    response['connection'] = c.create_connection(connection).to_dict()
  except RestException, e:
    response.update(handle_rest_exception(e, _('Could not clone connection.')))
  except SqoopConnectionException, e:
    response['status'] = 100
    response['errors'] = e.to_dict()
  return HttpResponse(json.dumps(response), mimetype="application/json")

@never_cache
@get_connection_or_exception()
def connection_delete(request, connection):
  if request.method != 'POST':
    raise StructuredException(code="INVALID_METHOD", message=_('POST request required.'), error_code=405)

  response = {
    'status': 0,
    'errors': None
  }

  try:
    c = client.SqoopClient(conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE)
    c.delete_connection(connection)
  except RestException, e:
    response.update(handle_rest_exception(e, _('Could not delete connection.')))
  except SqoopConnectionException, e:
    response['status'] = 100
    response['errors'] = e.to_dict()
  return HttpResponse(json.dumps(response), mimetype="application/json")
