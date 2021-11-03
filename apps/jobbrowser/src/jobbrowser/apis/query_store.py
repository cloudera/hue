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

from desktop.lib.rest.http_client import RestException
from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource

from desktop.lib.rest.streamed_resource import stream_response

from beeswax.conf import USE_SASL
from jobbrowser.conf import QUERY_STORE

def error_handler(func):
  def decorator(*args, **kwargs):
    response = {}

    try:
      return func(*args, **kwargs)
    except RestException as e:
      response = {'status': -1}

      ex_response = e.get_parent_ex().response

      if ex_response is not None:
        response['code'] = ex_response.status_code
        response['message'] = ex_response.reason
        response['content'] = ex_response.text
      else:
        response['message'] = 'Query store not reachable!'
        response['content'] = e.message

    finally:
      if response:
        return response

  return decorator

@error_handler
def query_store_proxy(request, path=None):
  client = _create_query_store_client(request)

  resource = Resource(client)
  return resource.invoke(request.method, path, request.GET.dict(), request.body)

@error_handler
def stream_download_bundle(request, id):
  client = _create_query_store_client(request, content_type='application/octet-stream')

  url = 'api/data-bundle/' + id
  return stream_response(client, url)

def _create_query_store_client(request, content_type='application/json; charset=UTF-8'):
  headers = {
    'x-do-as': request.user.username,
    'X-Requested-By': 'das',
    'Content-Type': content_type,
    'Cookie': request.environ.get('HTTP_COOKIE')
  }

  client = HttpClient(QUERY_STORE.SERVER_URL.get())
  client.set_headers(headers)
  client.set_verify(False)

  if USE_SASL.get():
    client.set_kerberos_auth()

  return client
