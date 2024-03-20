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

from desktop.lib.ai.lib.task import Task, TaskType, get_task
from desktop.lib.ai.lib.base_model import BaseModel
from desktop.lib.ai.types import SQLResponse

# Prompt templates were adapted from Defog documentation - https://huggingface.co/defog/sqlcoder-7b-2#prompt
# The model is designed to return only SQL, so SUMMARIZE doesn't work at this point

_GENERATE = """### Task
Generate a SQL query to answer [QUESTION]{input}[/QUESTION]

### Instructions
- Query is in {dialect} dialect
- If you cannot answer the question with the available database schema, return 'I do not know'

### Database Schema
The query will run on a database with the following schema:
{metadata}

### Answer
Given the database schema, here is the SQL query that answers [QUESTION]{input}[/QUESTION]
[SQL]"""

_EDIT = """### Task
Modify the Input SQL query to answer [QUESTION]{input}[/QUESTION]

### Instructions
- Query is in {dialect} dialect
- If you cannot answer the question with the available database schema, return 'I do not know'

### Database Schema
The query will run on a database with the following schema:
{metadata}

Input SQL query: {sql}

### Answer
Given the database schema and Input SQL query, here is the modified SQL query that answers [QUESTION]{input}[/QUESTION]
[SQL]"""

_SUMMARIZE = """### Task
Generate a question thats answered by the Input SQL query.

### Instructions
- Query is in {dialect} dialect
- If you cannot answer the question with the available database schema, return 'I do not know'

### Database Schema
The query is associated to a database with the following schema:
{metadata}

Input SQL query: {sql}

### Answer
Given the database schema and Input SQL query, here is the question.
[QUESTION]"""

_OPTIMIZE = """### Task
Optimize the Input SQL query.

### Instructions
- Query is in {dialect} dialect
- Only optimize in a way so that the result of the query remains the same.
- If you cannot answer the question with the available database schema, return 'I do not know'

### Database Schema
The query will run on a database with the following schema:
{metadata}

Input SQL query: {sql}

### Answer
Given the database schema and Input SQL query, here is the optimized SQL query.
[SQL]"""

_FIX = """### Task
Try to fix this syntactically broken Input SQL query.

### Instructions
- Query is in {dialect} dialect
- Do not optimize and only make the minimal modification needed to create a valid query.
- If you cannot answer the question with the available database schema, return 'I do not know'

### Database Schema
The query will run on a database with the following schema:
{metadata}

Input SQL query: {sql}

### Answer
Given the database schema and Input SQL query, here is the optimized SQL query.
[SQL]"""


def _parser(response: str) -> SQLResponse:
  return SQLResponse(
    sql=response,
  )

_TASKS = {
  TaskType.GENERATE: Task(_GENERATE, _parser),
  TaskType.EDIT: Task(_EDIT, _parser),
  TaskType.SUMMARIZE: Task(_SUMMARIZE, _parser),
  TaskType.OPTIMIZE: Task(_OPTIMIZE, _parser),
  TaskType.FIX: Task(_FIX, _parser)
}

class SQLCoderModel(BaseModel):
  def get_default_name(self) -> str:
    return ""

  def get_task(self, task_type: TaskType) -> Task:
    return get_task(_TASKS, task_type)

  def build_data(self, prompt: str) -> dict:
    return {
      "prompt": prompt,
      # "stopping_text": "</code>" - # Not required for sqlcoder
    }

  def extract_response(self, response_str: str) -> str:
    return response_str
