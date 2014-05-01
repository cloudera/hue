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

from form import Form


class Connector(object):
  """
  Sqoop connector object.

  Example of sqoop connector dictionary received by server: {
      "id": 1,
      "name": "generic-jdbc-connector",
      "class": "org.apache.sqoop.connector.jdbc.GenericJdbcConnector",
      "job-forms": {
        "IMPORT": [
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
                "type": "STRING",
                "size": 50,
                "sensitive": false
              },
              {
                "id": 14,
                "name": "table.partitionColumn",
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
        "EXPORT": [
          {
            "id": 2,
            "inputs": [
              {
                "id": 6,
                "name": "table.schemaName",
                "type": "STRING",
                "size": 50,
                "sensitive": false
              },
              {
                "id": 7,
                "name": "table.tableName",
                "type": "STRING",
                "size": 50,
                "sensitive": false
              },
              {
                "id": 8,
                "name": "table.sql",
                "type": "STRING",
                "size": 50,
                "sensitive": false
              },
              {
                "id": 9,
                "name": "table.columns",
                "type": "STRING",
                "size": 50,
                "sensitive": false
              }
            ],
            "name": "table",
            "type": "CONNECTION"
          }
        ]
      },
      "con-forms": [
        {
          "id": 1,
          "inputs": [
            {
              "id": 1,
              "name": "connection.jdbcDriver",
              "type": "STRING",
              "size": 128,
              "sensitive": false
            },
            {
              "id": 2,
              "name": "connection.connectionString",
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
      "version": "2.0.0-SNAPSHOT"
    }

  Some of the key-value pairs are structured and others are not.
  For example, every connector will have a name, id, version, class,
  con-forms, and job-forms key, but the values of the ``con-forms``
  and ``job-forms`` keys will vary given the connector.

  The ``job-forms`` and ``con-forms`` keys hold forms.
  The ``job-forms`` key will hold 2 sets of forms: IMPORT and EXPORT.

  Connector APIs will also return a resource dictionary: {
    "1": {
      "ignored.label": "Ignored",
      "table.partitionColumn.help": "A specific column for data partition",
      "table.label": "Database configuration",
      "table.boundaryQuery.label": "Boundary query",
      "ignored.help": "This is completely ignored",
      "ignored.ignored.label": "Ignored",
      "connection.jdbcProperties.help": "Enter any JDBC properties that should be supplied during the creation of connection.",
      "table.tableName.help": "Table name to process data in the remote database",
      "connection.username.help": "Enter the username to be used for connecting to the database.",
      "connection.jdbcDriver.label": "JDBC Driver Class",
      "table.help": "You must supply the information requested in order to create a job object.",
      "table.partitionColumn.label": "Partition column name",
      "ignored.ignored.help": "This is completely ignored",
      "table.warehouse.label": "Data warehouse",
      "table.boundaryQuery.help": "The boundary query for data partition",
      "connection.username.label": "Username",
      "connection.jdbcDriver.help": "Enter the fully qualified class name of the JDBC driver that will be used for establishing this connection.",
      "connection.label": "Connection configuration",
      "table.columns.label": "Table column names",
      "connection.password.label": "Password",
      "table.warehouse.help": "The root directory for data",
      "table.dataDirectory.label": "Data directory",
      "table.sql.label": "Table SQL statement",
      "table.sql.help": "SQL statement to process data in the remote database",
      "table.schemaName.help": "Schema name to process data in the remote database",
      "connection.jdbcProperties.label": "JDBC Connection Properties",
      "table.columns.help": "Specific columns of a table name or a table SQL",
      "connection.connectionString.help": "Enter the value of JDBC connection string to be used by this connector for creating connections.",
      "table.schemaName.label": "Schema name",
      "table.dataDirectory.help": "The sub-directory under warehouse for data",
      "connection.connectionString.label": "JDBC Connection String",
      "connection.help": "You must supply the information requested in order to create a connection object.",
      "connection.password.help": "Enter the password to be used for connecting to the database.",
      "table.tableName.label": "Table name"
    }
  }

  The keys of the dictionary are the IDs of the connector.
  The keys of each entry are names associated with inputs in connector forms.

  @see sqoop.client.form for more information on unstructured forms in sqoop.
  """
  def __init__(self, id, name, version, job_forms, con_forms, resources={}, **kwargs):
    self.id = id
    self.name = name
    self.version = version
    self.job_forms = job_forms
    self.con_forms = con_forms
    self.resources = resources
    setattr(self, 'class', kwargs['class'])

  @staticmethod
  def from_dict(connector_dict, resources_dict={}):
    connector_dict.setdefault('job-forms', {})
    connector_dict['job_forms'] = {}
    if 'IMPORT' in connector_dict['job-forms']:
      connector_dict['job_forms']['IMPORT'] = [ Form.from_dict(job_form_dict) for job_form_dict in connector_dict['job-forms']['IMPORT'] ]
    if 'EXPORT' in connector_dict['job-forms']:
      connector_dict['job_forms']['EXPORT'] = [ Form.from_dict(job_form_dict) for job_form_dict in connector_dict['job-forms']['EXPORT'] ]

    connector_dict.setdefault('con-forms', [])
    connector_dict['con_forms'] = [ Form.from_dict(con_form_dict) for con_form_dict in connector_dict['con-forms'] ]

    connector_dict['resources'] = resources_dict.setdefault(unicode(connector_dict['id']), {})

    return Connector(**force_dict_to_strings(connector_dict))

  def to_dict(self):
    d = {
      'id': self.id,
      'name': self.name,
      'version': self.version,
      'class': getattr(self, 'class'),
      'con-forms': [ con_form.to_dict() for con_form in self.con_forms ],
      'job-forms': {},
      'resources': self.resources
    }
    if 'IMPORT' in self.job_forms:
      d['job-forms']['IMPORT'] = [ job_form.to_dict() for job_form in self.job_forms['IMPORT'] ]
    if 'EXPORT' in self.job_forms:
      d['job-forms']['EXPORT'] = [ job_form.to_dict() for job_form in self.job_forms['EXPORT'] ]
    return d
