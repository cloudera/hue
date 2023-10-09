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

from desktop.lib.ai.lib.task import Task, TaskType
from desktop.lib.ai.types import SQLResponse

class BaseModel(abc.ABC):
  @abc.abstractmethod
  def get_default_name(self) -> str:
    pass

  @abc.abstractmethod
  def get_task(self, task_type: TaskType) -> Task:
    pass

  @abc.abstractmethod
  def build_data(self, prompt: str) -> dict:
    pass

  # Extract the text data from the full model response
  @abc.abstractmethod
  def extract_response(self, response: str) -> str:
    pass
