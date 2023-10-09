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

import abc

from ..types import SQLResponse
from .task import TaskParams, TaskType
from .base_model import BaseModel

class BaseService(abc.ABC):
  model: BaseModel

  def __init__(self, model: BaseModel):
    self.model = model

  @abc.abstractmethod
  def call_model(self, data:dict) -> str:
    pass

  def process(self, task_type: TaskType, params: TaskParams) -> SQLResponse:
    task = self.model.get_task(task_type)

    # Step 1 - Build request
    prompt = task.build_prompt(params)
    data = self.model.build_data(prompt)

    # Step 2 - Send request to the model
    response_str = self.call_model(data)

    # Step 3 - Parse response
    response_str = self.model.extract_response(response_str)
    response = task.parser(response_str)

    return response
