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


class Framework(object):
  """
  Sqoop framework object.

  Example of sqoop framework dictionary received by server: {
    "id": 1,
    "resources": {
      "output.label": "Output configuration",
      "security.maxConnections.help": "Maximal number of connections that this connection object can use at one point in time",
      "output.storageType.label": "Storage type",
      "output.ignored.help": "This value is ignored",
      "input.label": "Input configuration",
      "security.help": "You must supply the information requested in order to create a job object.",
      "output.storageType.help": "Target on Hadoop ecosystem where to store data",
      "input.inputDirectory.help": "Directory that should be exported",
      "output.outputFormat.label": "Output format",
      "output.ignored.label": "Ignored",
      "output.outputFormat.help": "Format in which data should be serialized",
      "output.help": "You must supply the information requested in order to get information where you want to store your data.",
      "throttling.help": "Set throttling boundaries to not overload your systems",
      "input.inputDirectory.label": "Input directory",
      "throttling.loaders.label": "Loaders",
      "input.help": "Specifies information required to get data from Hadoop ecosystem",
      "throttling.extractors.label": "Extractors",
      "throttling.extractors.help": "Number of extractors that Sqoop will use",
      "security.label": "Security related configuration options",
      "throttling.label": "Throttling resources",
      "throttling.loaders.help": "Number of loaders that Sqoop will use",
      "output.outputDirectory.help": "Output directory for final data",
      "security.maxConnections.label": "Max connections",
      "output.outputDirectory.label": "Output directory"
    },
    "job-forms": {
      "IMPORT": [
        {
          "id": 7,
          "inputs": [
            {
              "id": 20,
              "values": "HDFS",
              "name": "output.storageType",
              "type": "ENUM",
              "sensitive": false
            },
            {
              "id": 21,
              "values": "TEXT_FILE,SEQUENCE_FILE",
              "name": "output.outputFormat",
              "type": "ENUM",
              "sensitive": false
            },
            {
              "id": 22,
              "name": "output.outputDirectory",
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
      ],
      "EXPORT": [
        {
          "id": 5,
          "inputs": [
            {
              "id": 17,
              "name": "input.inputDirectory",
              "type": "STRING",
              "size": 255,
              "sensitive": false
            }
          ],
          "name": "input",
          "type": "CONNECTION"
        },
        {
          "id": 6,
          "inputs": [
            {
              "id": 18,
              "name": "throttling.extractors",
              "type": "INTEGER",
              "sensitive": false
            },
            {
              "id": 19,
              "name": "throttling.loaders",
              "type": "INTEGER",
              "sensitive": false
            }
          ],
          "name": "throttling",
          "type": "CONNECTION"
        }
      ]
    },
    "con-forms": [
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

  The ``job-forms`` and ``con-forms`` keys hold forms.
  The ``job-forms`` key will hold 2 sets of forms: IMPORT and EXPORT.
  ``id`` is for look up in metadata repository.

  The framework API will return resource information.
  The keys are names associated with inputs in the various forms.

  @see sqoop.client.form for more information on unstructured forms in sqoop.
  """
  def __init__(self, id, job_forms, con_forms, resources, **kwargs):
    self.id = id
    self.job_forms = job_forms
    self.con_forms = con_forms
    self.resources = resources

  @staticmethod
  def from_dict(framework_dict):
    framework_dict.setdefault('job-forms', {})
    framework_dict['job_forms'] = {}
    if 'IMPORT' in framework_dict['job-forms']:
      framework_dict['job_forms']['IMPORT'] = [ Form.from_dict(job_form_dict) for job_form_dict in framework_dict['job-forms']['IMPORT'] ]
    if 'EXPORT' in framework_dict['job-forms']:
      framework_dict['job_forms']['EXPORT'] = [ Form.from_dict(job_form_dict) for job_form_dict in framework_dict['job-forms']['EXPORT'] ]

    framework_dict.setdefault('con-forms', [])
    framework_dict['con_forms'] = [ Form.from_dict(con_form_dict) for con_form_dict in framework_dict['con-forms'] ]

    return Framework(**force_dict_to_strings(framework_dict))

  def to_dict(self):
    d = {
      'id': self.id,
      'con-forms': [ con_form.to_dict() for con_form in self.con_forms ],
      'job-forms': {},
      'resources': self.resources
    }
    if 'IMPORT' in self.job_forms:
      d['job-forms']['IMPORT'] = [ job_form.to_dict() for job_form in self.job_forms['IMPORT'] ]
    if 'EXPORT' in self.job_forms:
      d['job-forms']['EXPORT'] = [ job_form.to_dict() for job_form in self.job_forms['EXPORT'] ]
    return d