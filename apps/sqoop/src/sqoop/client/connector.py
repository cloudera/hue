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

from config import Config


class Connector(object):

  def __init__(self, id, name, version, link_config, job_config, config_resources={}, **kwargs):
    self.id = id
    self.name = name
    self.version = version
    self.job_config = job_config
    self.link_config = link_config
    self.config_resources = config_resources
    setattr(self, 'class', kwargs['class'])

  @staticmethod
  def from_dict(connector_dict):

    connector_dict.setdefault('link_config', [])
    connector_dict['link_config'] = [ Config.from_dict(link_config_dict) for link_config_dict in connector_dict['link-config'] ]

    connector_dict.setdefault('job_config', {})
    connector_dict['job_config'] = {}
    if 'FROM' in connector_dict['job-config']:
      connector_dict['job_config']['FROM'] = [ Config.from_dict(from_config_dict) for from_config_dict in connector_dict['job-config']['FROM'] ]
    if 'TO' in connector_dict['job-config']:
      connector_dict['job_config']['TO'] = [ Config.from_dict(to_config_dict) for to_config_dict in connector_dict['job-config']['TO'] ]

    connector_dict['config_resources'] =  connector_dict['all-config-resources']

    return Connector(**force_dict_to_strings(connector_dict))

  def to_dict(self):
    d = {
      'id': self.id,
      'name': self.name,
      'version': self.version,
      'class': getattr(self, 'class'),
      'link-config': [ link_config.to_dict() for link_config in self.link_config ],
      'job-config': {},
      'all-config-resources': self.config_resources
    }
    if 'FROM' in self.job_config:
      d['job-config']['FROM'] = [ job_config.to_dict() for job_config in self.job_config['FROM'] ]
    if 'TO' in self.job_config:
      d['job-config']['TO'] = [ job_config.to_dict() for job_config in self.job_config['TO'] ]
    return d
