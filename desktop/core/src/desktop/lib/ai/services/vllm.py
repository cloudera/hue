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
from desktop.lib.ai.models.llama import LlamaModel

from desktop.conf import AI_INTERFACE, get_ai_service_token

_api_key = get_ai_service_token() or "EMPTY"
_api_url = AI_INTERFACE.BASE_URL.get()

class VLLMService(BaseService):
  def __init__(self, model_key: str):
    from openai import OpenAI

    self.client = OpenAI(
        api_key=_api_key,
        base_url=_api_url,
    )

    super().__init__(self.get_model(model_key))

  def get_model(self, model_key: str) -> BaseModel:
    return LlamaModel()

  def call_model(self, data: dict) -> str:
    model_name = AI_INTERFACE.MODEL_NAME.get() or self.model.get_default_name() # type: ignore
    response = self.client.chat.completions.create(
        model=model_name,
        temperature=1,
        max_tokens=4096,
        messages=[data] # type: ignore
    )

    content = response.choices[0].message.content
    return content.strip() if content else ""
