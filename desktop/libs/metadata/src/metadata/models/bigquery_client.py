#!/usr/bin/env python
# -- coding: utf-8 --
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
import logging

from django.utils.translation import ugettext as _
from django.urls import reverse

from notebook.models import make_notebook, MockRequest, get_api

from metadata.models.base import Base


LOG = logging.getLogger(__name__)


class BigQueryClient(Base):

  def list_models(self, database):
    params = {
      'snippet': {},
      'database': database,
      'operation': 'models'
    }

    return _get_notebook_api(self.user, 40).autocomplete(**params)


def _get_notebook_api(user, connector_id, interpreter=None):
  '''
  Helper utils until the API gets simplified.
  '''
  notebook_json = """
    {
      "selectedSnippet": "hive",
      "showHistory": false,
      "description": "Test Query",
      "name": "Test Query",
      "sessions": [
          {
              "type": "hive",
              "properties": [],
              "id": null
          }
      ],
      "type": "hive",
      "id": null,
      "snippets": [{"id":"2b7d1f46-17a0-30af-efeb-33d4c29b1055","type":"%(connector_id)s","status":"running","statement":"select * from web_logs","properties":{"settings":[],"variables":[],"files":[],"functions":[]},"result":{"id":"b424befa-f4f5-8799-a0b4-79753f2552b1","type":"table","handle":{"log_context":null,"statements_count":1,"end":{"column":21,"row":0},"statement_id":0,"has_more_statements":false,"start":{"column":0,"row":0},"secret":"rVRWw7YPRGqPT7LZ/TeFaA==an","has_result_set":true,"statement":"select * from web_logs","operation_type":0,"modified_row_count":null,"guid":"7xm6+epkRx6dyvYvGNYePA==an"}},"lastExecuted": 1462554843817,"database":"default"}],
      "uuid": "d9efdee1-ef25-4d43-b8f9-1a170f69a05a"
  }
  """ % {
    'connector_id': connector_id,
  }
  snippet = json.loads(notebook_json)['snippets'][0]
  snippet['interpreter'] = interpreter

  request = MockRequest(user)

  return get_api(request, snippet)
