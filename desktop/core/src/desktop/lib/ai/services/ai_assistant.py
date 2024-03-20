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
from desktop.lib.ai.lib.task import TaskParams, TaskType
from desktop.lib.ai.lib.base_model import BaseModel
from desktop.lib.ai.lib.base_service import BaseService
from desktop.lib.ai.models.sqlcoder import SQLCoderModel

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

class AiService(BaseService):
  def __init__(self, model_key: str):
    self.client = _get_client()
    super().__init__(self.get_model(model_key))

  def get_model(self, model_key: str) -> BaseModel:
    return SQLCoderModel()

  def call_model(self, data: dict) -> str:
    resource = Resource(self.client)
    data_str = json.dumps(data).encode('utf8')
    response = resource.post(relpath=_path, data=data_str)
    return response['inference']
