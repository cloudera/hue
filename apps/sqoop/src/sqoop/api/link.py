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

from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _

from sqoop import client, conf
from sqoop.client.exception import SqoopException
from decorators import get_link_or_exception
from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions import StructuredException
from desktop.lib.rest.http_client import RestException
from exception import handle_rest_exception
from utils import list_to_dict
from django.views.decorators.cache import never_cache

__all__ = ['get_links', 'create_link', 'update_link', 'link', 'links', 'link_clone', 'link_delete']


LOG = logging.getLogger(__name__)

@never_cache
def get_links(request):
  response = {
    'status': 0,
    'errors': None,
    'links': []
  }
  try:
    c = client.SqoopClient(conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE, ssl_cert_ca_verify=conf.SSL_CERT_CA_VERIFY.get())
    response['links'] = list_to_dict(c.get_links())
  except RestException, e:
    response.update(handle_rest_exception(e, _('Could not get links.')))
  return JsonResponse(response)

@never_cache
def create_link(request):
  response = {
    'status': 0,
    'errors': None,
    'link': None
  }

  if 'link' not in request.POST:
    raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Error saving link'), data={'errors': 'Link is missing.'}, error_code=400)

  d = json.loads(smart_str(request.POST.get('link')))
  link = client.Link.from_dict(d)

  try:
    c = client.SqoopClient(conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE, ssl_cert_ca_verify=conf.SSL_CERT_CA_VERIFY.get())
    response['link'] = c.create_link(link).to_dict()
  except RestException, e:
    response.update(handle_rest_exception(e, _('Could not create link.')))
  except SqoopException, e:
    response['status'] = 100
    response['errors'] = e.to_dict()
  return JsonResponse(response)

@never_cache
def update_link(request, link):
  response = {
    'status': 0,
    'errors': None,
    'link': None
  }

  if 'link' not in request.POST:
    raise StructuredException(code="INVALID_REQUEST_ERROR", message=_('Error saving link'), data={'errors': 'Link is missing.'}, error_code=400)

  link.update_from_dict(json.loads(smart_str(request.POST.get('link'))))

  try:
    c = client.SqoopClient(conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE, ssl_cert_ca_verify=conf.SSL_CERT_CA_VERIFY.get())
    response['link'] = c.update_link(link).to_dict()
  except RestException, e:
    response.update(handle_rest_exception(e, _('Could not update link.')))
  except SqoopException, e:
    response['status'] = 100
    response['errors'] = e.to_dict()
  return JsonResponse(response)

@never_cache
def links(request):
  if request.method == 'GET':
    return get_links(request)
  elif request.method == 'POST':
    return create_link(request)
  else:
    raise StructuredException(code="INVALID_METHOD", message=_('GET or POST request required.'), error_code=405)

@never_cache
@get_link_or_exception()
def link(request, link):
  response = {
    'status': 0,
    'errors': None,
    'link': None
  }
  if request.method == 'GET':
    response['link'] = link.to_dict()
    return JsonResponse(response)
  elif request.method == 'POST':
    return update_link(request, link)
  else:
    raise StructuredException(code="INVALID_METHOD", message=_('GET or POST request required.'), error_code=405)

@never_cache
@get_link_or_exception()
def link_clone(request, link):
  if request.method != 'POST':
    raise StructuredException(code="INVALID_METHOD", message=_('POST request required.'), error_code=405)

  response = {
    'status': 0,
    'errors': None,
    'link': None
  }

  link.id = -1
  link.name = '%s-copy' % link.name
  try:
    c = client.SqoopClient(conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE, ssl_cert_ca_verify=conf.SSL_CERT_CA_VERIFY.get())
    response['link'] = c.create_link(link).to_dict()
  except RestException, e:
    response.update(handle_rest_exception(e, _('Could not clone link.')))
  except SqoopException, e:
    response['status'] = 100
    response['errors'] = e.to_dict()
  return JsonResponse(response)

@never_cache
@get_link_or_exception()
def link_delete(request, link):
  if request.method != 'POST':
    raise StructuredException(code="INVALID_METHOD", message=_('POST request required.'), error_code=405)

  response = {
    'status': 0,
    'errors': None
  }

  try:
    c = client.SqoopClient(conf.SERVER_URL.get(), request.user.username, request.LANGUAGE_CODE, ssl_cert_ca_verify=conf.SSL_CERT_CA_VERIFY.get())
    c.delete_link(link)
  except RestException, e:
    response.update(handle_rest_exception(e, _('Could not delete link.')))
  except SqoopException, e:
    response['status'] = 100
    response['errors'] = e.to_dict()
  return JsonResponse(response)
