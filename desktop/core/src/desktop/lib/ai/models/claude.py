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
from desktop.lib.ai.utils.xml import extract_tag_content
from desktop.lib.ai.types import SQLResponse

import logging
LOG = logging.getLogger()

_GENERATE = """Act as an {dialect} SQL expert.
Translate the NQL statement into SQL using the following metadata: {metadata}.
List any assumptions not covered by the supplied metadata. {dialect_prompt}

NQL: {input}

Wrap the SQL in a <code> tag and the assumptions in a <assumptions> tag with a closing </assumptions>"""

_EDIT = """Act as an {dialect} SQL expert.
Based on the input modify the SQL using the following metadata: {metadata}.
List any assumptions not covered by the supplied metadata. {dialect_prompt}

SQL query: {sql}
Input: {input}

Wrap the SQL in a <code> tag and the assumptions in a <assumptions> tag with a closing </assumptions>"""

_SUMMARIZE = """Act as an {dialect} SQL expert.
Use the following metadata: {metadata}.

SQL query: {sql}

Explain in detail what the provided SQL query does and wrap the explation in an <explain> tag with closing </explain>.
Provide a short summary in natural language of the expected result. Wrap the summary in a <summary> tag tag with closing </summary>.
"""

_OPTIMIZE = """Act as an {dialect} SQL expert.
Optimize this SQL query and explain the improvement if any. Only optimize in a way so that the result of the query remains the same.
Use the following metadata: {metadata}.

SQL: {sql}

Always explain the optimization or suggest alternative options if any. The explanation should be wrapped in an <explain> tag but should not contain SQL.
If the SQL can be optimized it should be placed in the code tag.

Return the result in the following format:
<code></code>
<explain></explain>
"""

_FIX = """Act as an {dialect} SQL expert.
Try to fix this syntactically broken sql query using the following metadata: {metadata}.

SQL query: {sql}

Do not optimize and only make the minimal modifcation needed to create a valid query.
Wrap the corrected SQL in a <code> tag and the explaination in an <explain> tag with a closing </explain>.

Return the result in the following format:
<code></code>
<explain></explain>
"""

def _code_assumptions_parser(response: str) -> SQLResponse:
  return SQLResponse(
    sql=extract_tag_content('code', response),
    assumptions=extract_tag_content('assumptions', response),
    warning=extract_tag_content('warning', response),
    semanticerror=extract_tag_content('semanticerror', response),
  )


def _code_explain_parser(response: str) -> SQLResponse:
  return SQLResponse(
    sql=extract_tag_content('code', response),
    explain=extract_tag_content('explain', response),
    warning=extract_tag_content('warning', response),
    sqlerror=extract_tag_content('sqlerror', response),
  )


def _summary_parser(response: str) -> SQLResponse:
  return SQLResponse(
    summary=extract_tag_content('summary', response),
    explain=extract_tag_content('explain', response),
  )


_TASKS = {
  TaskType.GENERATE: Task(_GENERATE, _code_assumptions_parser),
  TaskType.EDIT: Task(_EDIT, _code_assumptions_parser),
  TaskType.SUMMARIZE: Task(_SUMMARIZE, _summary_parser),
  TaskType.OPTIMIZE: Task(_OPTIMIZE, _code_explain_parser),
  TaskType.FIX: Task(_FIX, _code_explain_parser)
}

class ClaudeModel(BaseModel):
  def get_default_name(self) -> str:
    return "anthropic.claude-v2"

  def get_task(self, task_type: TaskType) -> Task:
    return get_task(_TASKS, task_type)

  def build_data(self, prompt: str) -> dict:
    return {
      "prompt": f"Human: {prompt}\nAssistant:",
      "max_tokens_to_sample": 300,
      "temperature": 1,
      "top_k": 250,
      "top_p": 0.999,
      "stop_sequences": ["\n\nHuman:"],
      "anthropic_version": "bedrock-2023-05-31" # TODO: Make into a configuration
    }

  def extract_response(self, response_str: str) -> str:
    resp = json.loads(response_str)
    return resp["completion"]
