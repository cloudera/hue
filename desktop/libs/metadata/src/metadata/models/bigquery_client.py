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

import io
import json
import logging

from django.utils.translation import ugettext as _

from google.oauth2 import service_account
from google.cloud import bigquery

from notebook.models import make_notebook, MockRequest, get_api

from metadata.models.base import Base


LOG = logging.getLogger(__name__)


class BigQueryClient(Base):

  def __init__(self, user, connector_id, connector):
    super(BigQueryClient, self).__init__(user, connector_id)
    self.connector = connector


  def list_models(self, database):
    params = {
      'snippet': {},
      'database': database,
      'operation': 'models'
    }

    return _get_notebook_api(self.user, self.connector_id).autocomplete(**params)


  def train(self, params):
    options = json.loads(params.get('options', '{}'))

    options['model_type'] = "'%(model_type)s'" % options

    if params.get('data'):
      table = self.create_table_from_text(name=params['model'], data=params['data'])
      name = table['name']
      params['statement'] = 'SELECT * FROM `%(name)s`' % {'name': name}

    params['options'] = ',\n'.join(['%s=%s' % (k, v) for k, v in options.items()])
    data = {
      'snippet': {},
      'operation': '''
          CREATE OR REPLACE MODEL `%(model)s`
          OPTIONS (
            %(options)s
          )
          AS
          %(statement)s
        ''' % params
    }

    _get_notebook_api(self.user, self.connector_id).get_sample_data(**data)

    return self.get_model(name=params['model'])


  def predict(self, params):
    if params.get('data'):
      table = self.create_table_from_text(name=params['model'], data=params['data'])
      name = table['name']
      params['statement'] = 'SELECT * FROM `%(name)s`' % {'name': name}

    data = {
      'snippet': {},
      'operation': '''
          SELECT * FROM ML.PREDICT(
            MODEL `%(model)s`, (
              %(statement)s
            )
          )
        ''' % params
    }
    return _get_notebook_api(self.user, self.connector_id).get_sample_data(**data)


  def delete_model(self, model):
    data = {
      'snippet': {},
      'operation': 'DROP MODEL IF EXISTS `%s`' % model
    }
    return _get_notebook_api(self.user, self.connector_id).get_sample_data(**data)


  def get_model(self, name):
    client = self._get_client()

    # https://cloud.google.com/bigquery/docs/reference/rest/v2/models
    model = client.get_model(name)

    return model._properties


  def upload_data(self, source, destination):
    client = self._get_client()

    table_id = destination['name']

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV, skip_leading_rows=1, autodetect=True,
    )

    job = client.load_table_from_file(source['file'], table_id, job_config=job_config)

    # [OPTIONS(table_option_list)] or ALTER TABLE [IF EXISTS] [[project_name.]dataset_name.]table_name SET OPTIONS(table_set_options_list)
    # description="a table that expires in 2025"
    # labels=[("org_unit", "development")]
    # expiration_timestamp=TIMESTAMP "2025-01-01 00:00:00 UTC"

    job.result()

    table = client.get_table(table_id)

    response = {
      'num_rows': job.output_rows,
      'num_cols': len(table.schema),
      'table': table_id,
      'stats': job.to_api_repr()
    }
    response['message'] = "Loaded %(num_rows)s rows and %(num_cols)s columns to %(table)s" % response
    return response


  def create_table_from_text(self, name, data):
    source = {
      'file': io.StringIO(data)
    }
    # Make it tmp?
    destination = {
      'name': '%(name)s_training' % {'name': name}
    }

    stats = self.upload_data(source, destination)

    return {
      'name': destination['name'],
      'stats': stats
    }


  def _get_client(self):
    credentials_json = json.loads(
      [setting['value'] for setting in self.connector['settings'] if setting['name'] == 'credentials_json'][0]
    )
    credentials = service_account.Credentials.from_service_account_info(credentials_json)

    return bigquery.Client(
        project=credentials_json['project_id'],
        credentials=credentials
    )


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
