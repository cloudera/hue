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

import io
import json

from desktop.lib.ai.lib.base_service import BaseService
from desktop.lib.ai.lib.base_model import BaseModel
from desktop.lib.ai.models.titan import TitanModel
from desktop.lib.ai.models.claude import ClaudeModel

from desktop.conf import AI_INTERFACE
from aws.conf import AWS_ACCOUNTS, get_access_key_id, get_secret_access_key

ACCOUNT_NAME = 'bedrock'

class BedrockService(BaseService):
  def __init__(self, model_name: str):
    import boto3
    self.bedrock = boto3.client(
      'bedrock-runtime',
      aws_access_key_id = get_access_key_id(ACCOUNT_NAME),
      aws_secret_access_key = get_secret_access_key(ACCOUNT_NAME),
      region_name = AWS_ACCOUNTS[ACCOUNT_NAME].REGION.get()
    )

    super().__init__(self.get_model(model_name))

  def get_model(self, model_name: str) -> BaseModel:
    if model_name == "claude":
      return ClaudeModel()
    return TitanModel()

  def call_model(self, data: dict) -> str:
    model_name = AI_INTERFACE.MODEL_NAME.get() or self.model.get_default_name()
    response = self.bedrock.invoke_model(
      modelId=model_name,
      body=json.dumps(data)
    )

    return io.BytesIO(response['body'].read()).readlines()[0].decode('utf-8')
