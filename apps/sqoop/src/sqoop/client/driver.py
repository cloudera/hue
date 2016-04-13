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


class Driver(object):

  def __init__(self, id, version, job_config=None, config_resources={}, **kwargs):
    self.id = id
    self.version = version
    self.job_config = job_config
    self.config_resources = config_resources

  @staticmethod
  def from_dict(driver_dict):
    driver_dict.setdefault('job_config', {})
    driver_dict['job_config'] = [ Config.from_dict(job_config_dict) for job_config_dict in driver_dict['job-config']]
    driver_dict['config_resources'] =  driver_dict['all-config-resources']

    return Driver(**force_dict_to_strings(driver_dict))

  def to_dict(self):
    d = {
      'id': self.id,
      'version': self.version,
      'job-config': [ job_config.to_dict() for job_config in self.job_config ],
      'all-config-resources': self.config_resources
    }

    return d