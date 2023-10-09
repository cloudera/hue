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
import re
import json

from desktop.lib.rest.http_client import HttpClient
from desktop.lib.rest.resource import Resource

from .base import LlmApi, Task

_GENERATE = """{metadata}

-- Using valid SQLite, answer the following questions for the tables provided above.

-- {input}

SELECT"""

_EDIT = """Act as an {dialect} SQL expert. Based on the input modify the SQL using the following metadata: {metadata}.
List any assumptions not covered by the supplied metadata.
SQL query: {sql}
Input: {input}
Wrap the SQL in a <code> tag and the assumptions in a <assumptions> tag"""

_SUMMARIZE = """Act as an {dialect} SQL expert.
Explain in natural language using non technical terms, what this query does: {sql}.
"""

_OPTIMIZE = """Act as an {dialect} SQL expert.
Optimize this SQL query and explain the improvement if any.
Wrap the new code in a <code> tag and the explanation in an <explain> tag with a closing </explain>: {sql}
"""

_FIX = """Act as an {dialect} SQL expert.
Fix this broken sql query and explain the fix.
Wrap the corrected code in a <code> tag and the explaination in an <explain> tag with a closing </explain>: {sql}
"""

TASK_TEMPLATES = {
  Task.GENERATE: _GENERATE,
  Task.EDIT: _EDIT,
  Task.SUMMARIZE: _SUMMARIZE,
  Task.OPTIMIZE: _OPTIMIZE,
  Task.FIX: _FIX
}

_base_url = ""
_path = "/api/infer"

def extractTagContent(tag, text):
  matches = re.findall(f'<{tag}>(.*?)</{tag}>', text, flags=re.DOTALL)
  return matches[0] if len(matches) > 0 else None

class LLaMA2Api(LlmApi):
  def __init__(self):
    super().__init__(TASK_TEMPLATES)

  def _get_client(self):
    client = HttpClient(_base_url)
    client.set_verify(False)
    client.set_headers({
      'Content-Type': 'application/json'
    })
    return client

  def infer(self, prompt):
    client = self._get_client()
    resource = Resource(client)
    data = json.dumps({
      'prompt': prompt,
      'stopping_text': '</code>'
    }).encode('utf8')
    response = resource.post(relpath=_path, data=data)
    return response['inference']


  def parse_inference(self, task, inference):
    return {
      'sql': 'SELECT '+inference.strip(),
      'assumptions': ''
    }
