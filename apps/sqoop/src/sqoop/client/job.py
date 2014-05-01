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

import logging

from desktop.lib.python_util import force_dict_to_strings

from exception import SqoopException
from form import Form


class Job(object):
  """
  Sqoop job object.

  Example of sqoop job dictionary received by server: {
    "connection-id": 1,
    "id": 1,
    "updated": 1371246055277,
    "created": 1371246055277,
    "name": "import1",
    "connector": [
      {
        "id": 3,
        "inputs": [
          {
            "id": 10,
            "name": "table.schemaName",
            "type": "STRING",
            "size": 50,
            "sensitive": false
          },
          {
            "id": 11,
            "name": "table.tableName",
            "value": "derbyDB",
            "type": "STRING",
            "size": 50,
            "sensitive": false
          },
          {
            "id": 12,
            "name": "table.sql",
            "type": "STRING",
            "size": 50,
            "sensitive": false
          },
          {
            "id": 13,
            "name": "table.columns",
            "value": "addr",
            "type": "STRING",
            "size": 50,
            "sensitive": false
          },
          {
            "id": 14,
            "name": "table.partitionColumn",
            "value": "num",
            "type": "STRING",
            "size": 50,
            "sensitive": false
          },
          {
            "id": 15,
            "name": "table.boundaryQuery",
            "type": "STRING",
            "size": 50,
            "sensitive": false
          }
        ],
        "name": "table",
        "type": "CONNECTION"
      }
    ],
    "connector-id": 1,
    "type": "IMPORT",
    "framework": [
      {
        "id": 7,
        "inputs": [
          {
            "id": 20,
            "values": "HDFS",
            "name": "output.storageType",
            "value": "HDFS",
            "type": "ENUM",
            "sensitive": false
          },
          {
            "id": 21,
            "values": "TEXT_FILE,SEQUENCE_FILE",
            "name": "output.outputFormat",
            "value": "TEXT_FILE",
            "type": "ENUM",
            "sensitive": false
          },
          {
            "id": 22,
            "name": "output.outputDirectory",
            "value": "%2Ftmp%2Fimport1-out",
            "type": "STRING",
            "size": 255,
            "sensitive": false
          }
        ],
        "name": "output",
        "type": "CONNECTION"
      },
      {
        "id": 8,
        "inputs": [
          {
            "id": 23,
            "name": "throttling.extractors",
            "type": "INTEGER",
            "sensitive": false
          },
          {
            "id": 24,
            "name": "throttling.loaders",
            "type": "INTEGER",
            "sensitive": false
          }
        ],
        "name": "throttling",
        "type": "CONNECTION"
      }
    ]
  }

  Some of the key-value pairs are structured and others are not.
  For example, every job will have a name, id, type, connection-id, and connector-id key,
  but the values of the ``connector`` and ``connection`` keys
  will vary given the chosen connector and connection.
  The same is true for the ``framework`` key.

  The job object will have two framework components
  and a single connector, for the moment.

  @see sqoop.client.form for more information on unstructured forms in sqoop.
  """
  SKIP = ('id', 'creation_date', 'creation_user', 'update_date', 'update_user')

  def __init__(self, type, name, connection_id, connector_id, connector=None, framework=None, enabled=True, creation_user='hue', creation_date=0, update_user='hue', update_date=0, **kwargs):
    self.id = kwargs.setdefault('id', -1)
    self.creation_user = creation_user
    self.creation_date = creation_date
    self.update_user = update_user
    self.update_date = update_date
    self.enabled = enabled
    self.type = type
    self.name = name
    self.connection_id = connection_id
    self.connector_id = connector_id
    self.connector = connector
    self.framework = framework

  @staticmethod
  def from_dict(job_dict):
    job_dict.setdefault('connector', [])
    job_dict['connector'] = [ Form.from_dict(con_form_dict) for con_form_dict in job_dict['connector'] ]

    job_dict.setdefault('framework', [])
    job_dict['framework'] = [ Form.from_dict(framework_form_dict) for framework_form_dict in job_dict['framework'] ]

    if not 'connection_id' in job_dict:
      job_dict['connection_id'] = job_dict['connection-id']

    if not 'connector_id' in job_dict:
      job_dict['connector_id'] = job_dict['connector-id']

    if not 'creation_user' in job_dict:
      job_dict['creation_user'] = job_dict.setdefault('creation-user', 'hue')

    if not 'creation_date' in job_dict:
      job_dict['creation_date'] = job_dict.setdefault('creation-date', 0)

    if not 'update_user' in job_dict:
      job_dict['update_user'] = job_dict.setdefault('update-user', 'hue')

    if not 'update_date' in job_dict:
      job_dict['update_date'] = job_dict.setdefault('update-date', 0)

    return Job(**force_dict_to_strings(job_dict))

  def to_dict(self):
    d = {
      'id': self.id,
      'type': self.type,
      'name': self.name,
      'creation-user': self.creation_user,
      'creation-date': self.creation_date,
      'update-user': self.update_user,
      'update-date': self.update_date,
      'connection-id': self.connection_id,
      'connector-id': self.connector_id,
      'connector': [ connector.to_dict() for connector in self.connector ],
      'framework': [ framework.to_dict() for framework in self.framework ],
      'enabled': self.enabled
    }
    return d

  def update_from_dict(self, job_dict):
    self.update(Job.from_dict(job_dict))

  def update(self, job):
    for key in self.__dict__:
      if key not in Job.SKIP:
        setattr(self, key, getattr(job, key, getattr(self, key)))

class SqoopJobException(SqoopException):
  """
  This is what the sqoop server generally responds with:
  {
    "connector": {
      "status": "UNACCEPTABLE",
      "messages": {
        "table": {
          "message": "Either table name or SQL must be specified",
          "status": "UNACCEPTABLE"
        }
      }
    },
    "framework": {
      "status": "UNACCEPTABLE",
      "messages": {
        "output.outputDirectory": {
          "message": "Output directory is empty",
          "status": "UNACCEPTABLE"
        }
      }
    }
  }
  """
  def __init__(self, connector, framework):
    self.connector = connector
    self.framework = framework

  @classmethod
  def from_dict(cls, error_dict):
    return SqoopJobException(**force_dict_to_strings(error_dict))

  def to_dict(self):
    return {
      'connector': self.connector,
      'framework': self.framework
    }

  def __str__(self):
    return 'Connector: %s\nFramework: %s\n' % (self.connector, self.framework)

