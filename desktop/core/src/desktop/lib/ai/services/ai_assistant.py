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

from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource

from desktop.lib.ai import BaseService

from desktop.conf import AI_INTERFACE

_base_url = AI_INTERFACE.BASE_URL.get()
_path = "/api/infer"

def _get_client():
  client = HttpClient(_base_url)
  client.set_verify(False)
  client.set_headers({
    'Content-Type': 'application/json'
  })
  return client

class OpenAiService(BaseService):
  def __init__(self):
    self.client = _get_client()

  def process(self, prompt: str) -> str:
    resource = Resource(self.client)
    data = json.dumps({
      'prompt': prompt,
      'stopping_text': '</code>' # TODO: make this an argument
    }).encode('utf8')
    response = resource.post(relpath=_path, data=data)
    return response['inference']
