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

from enum import Enum
from typing import Callable, Dict
from dataclasses import dataclass

from pyformatting import optional_format
from desktop.conf import AI_INTERFACE
from desktop.lib.ai.types import SQLResponse

import logging
LOG = logging.getLogger()

class TaskType(str, Enum):
  GENERATE = 'generate',
  EDIT = 'edit',
  SUMMARIZE = 'summarize',
  OPTIMIZE = 'optimize',
  FIX = 'fix',
  FILTER_TABLES = 'filter_tables'

@dataclass
class TaskParams:
  dialect: str
  input: str
  sql: str
  metadata: str

class Task:
  def __init__(self, template: str, parser: Callable[[str], SQLResponse]):
    self.template = template
    self.parser = parser

  def build_prompt(self, params: TaskParams) -> str:
    prompt = optional_format(self.template,
                 input=params.input,
                 sql=params.sql,
                 dialect=params.dialect,
                 metadata=params.metadata,
                 dialect_prompt=build_dialect_prompt(params.dialect))
    return prompt

def get_task(tasks: Dict[TaskType, Task], type: TaskType) -> Task:
  task = tasks[type]
  if task is None:
    exp = f'Unsupported task - {type}'
    LOG.error(exp)
    raise Exception(exp)
  return task


def build_dialect_prompt(dialect: str) -> str:
  ADD_TABLE_DATA = AI_INTERFACE.ADD_TABLE_DATA.get()
  dialect_prompt = ""
  if not ADD_TABLE_DATA:
    if dialect.lower() in ["postgresql", "mysql"]:
      dialect_prompt += "Use lower() and ILIKE '%%' unless you are sure about how to match the data."
    else:
      dialect_prompt += "Use lower() and LIKE '%%' unless you are sure about how to match the data."
  return dialect_prompt
