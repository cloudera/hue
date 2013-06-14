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

from exception import SqoopException
from form import Form


class Connection(object):
  """
  Sqoop connection object.

  Example of sqoop connection dictionary received by server: {
    "id": -1,
    "updated": 1371245829436,
    "created": 1371245829436,
    "name": "test1",
    "connector": [
      {
        "id": 1,
        "inputs": [
          {
            "id": 1,
            "name": "connection.jdbcDriver",
            "value": "org.apache.derby.jdbc.EmbeddedDriver",
            "type": "STRING",
            "size": 128,
            "sensitive": false
          },
          {
            "id": 2,
            "name": "connection.connectionString",
            "value": "jdbc%3Aderby%3A%2Ftmp%2Ftest",
            "type": "STRING",
            "size": 128,
            "sensitive": false
          },
          {
            "id": 3,
            "name": "connection.username",
            "type": "STRING",
            "size": 40,
            "sensitive": false
          },
          {
            "id": 4,
            "name": "connection.password",
            "type": "STRING",
            "size": 40,
            "sensitive": true
          },
          {
            "id": 5,
            "name": "connection.jdbcProperties",
            "type": "MAP",
            "sensitive": false
          }
        ],
        "name": "connection",
        "type": "CONNECTION"
      }
    ],
    "connector-id": 1,
    "framework": [
      {
        "id": 4,
        "inputs": [
          {
            "id": 16,
            "name": "security.maxConnections",
            "type": "INTEGER",
            "sensitive": false
          }
        ],
        "name": "security",
        "type": "CONNECTION"
      }
    ]
  }

  Some of the key-value pairs are structured and others are not.
  For example, every connection will have a name, id, and connector-id key,
  but the values of the ``connector`` key will vary given the chosen connector.
  The same is true for the ``framework`` key.

  The connection object will have a single framework component
  and a single connector, for the moment.

  @see sqoop.client.form for more information on unstructured forms in sqoop.
  """
  SKIP = ('id', 'created', 'updated')

  def __init__(self, name, connector_id, connector=None, framework=None, **kwargs):
    self.id = kwargs.setdefault('id', -1)
    self.created = kwargs.setdefault('created', 0)
    self.updated = kwargs.setdefault('updated', 0)
    self.name = name
    self.connector_id = connector_id
    self.connector = connector
    self.framework = framework

  @staticmethod
  def from_dict(connection_dict):
    connection_dict.setdefault('connector', [])
    connection_dict['connector'] = [ Form.from_dict(con_form_dict) for con_form_dict in connection_dict['connector'] ]

    connection_dict.setdefault('framework', [])
    connection_dict['framework'] = [ Form.from_dict(framework_form_dict) for framework_form_dict in connection_dict['framework'] ]

    if not 'connector_id' in connection_dict:
      connection_dict['connector_id'] = connection_dict.setdefault('connector-id', -1)

    return Connection(**connection_dict)

  def to_dict(self):
    d = {
      'id': self.id,
      'name': self.name,
      'created': self.created,
      'updated': self.updated,
      'connector-id': self.connector_id,
      'connector': [ connector.to_dict() for connector in self.connector ],
      'framework': [ framework.to_dict() for framework in self.framework ]
    }
    return d

  def update_from_dict(self, connection_dict):
    self.update(Connection.from_dict(connection_dict))

  def update(self, connection):
    for key in self.__dict__:
      if key not in Connection.SKIP:
        if hasattr(connection, key):
          setattr(self, key, getattr(connection, key))


class SqoopConnectionException(SqoopException):
  """
  This is what the server generally responds with:
  {
    "connector": {
      "status": "UNACCEPTABLE",
      "messages": {
        "connection": {
          "message": "Can't connect to the database with given credentials: No suitable driver found for test",
          "status": "ACCEPTABLE"
        },
        "connection.connectionString": {
          "message": "This do not seem as a valid JDBC URL",
          "status": "UNACCEPTABLE"
        }
      }
    },
    "framework": {
      "status": "FINE",
      "messages": {}
    }
  }
  """
  def __init__(self, connector, framework):
    self.connector = connector
    self.framework = framework

  @classmethod
  def from_dict(cls, error_dict):
    return SqoopConnectionException(**error_dict)

  def to_dict(self):
    return {
      'connector': self.connector,
      'framework': self.framework
    }

  def __str__(self):
    return 'Connector: %s\nFramework: %s\n' % (self.connector, self.framework)

