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

from desktop.lib.ai.lib.base_service import BaseService
from desktop.lib.ai.lib.base_model import BaseModel
from desktop.lib.ai.models.gpt import GPTModel

from desktop.conf import AI_INTERFACE, get_ai_service_token

_api_url = AI_INTERFACE.BASE_URL.get() # type: ignore
_api_key = get_ai_service_token()
_api_version = AI_INTERFACE.SERVICE_VERSION.get() or "2024-02-15-preview" # type: ignore

class AzureService(BaseService):
  def __init__(self, model_key: str):
    from openai import AzureOpenAI
    self.client = AzureOpenAI(
        api_key=_api_key,
        azure_endpoint=_api_url,
        api_version=_api_version
    )

    super().__init__(self.get_model(model_key))

  def get_model(self, model_key: str) -> BaseModel:
    return GPTModel()

  def call_model(self, data) -> str:
    deployment_name = AI_INTERFACE.MODEL_NAME.get() # type: ignore
    response = self.client.chat.completions.create(
      model=deployment_name,
      temperature=0,
      messages=[data] # type: ignore
    )

    content = response.choices[0].message.content
    return content.strip() if content else ""
