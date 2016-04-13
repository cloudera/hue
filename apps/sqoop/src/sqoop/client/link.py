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
from config import Config


class Link(object):

  SKIP = ('id', 'creation_date', 'creation_user', 'update_date', 'update_user')

  def __init__(self, name, connector_id, link_config_values=None, enabled=True, creation_user='hue', creation_date=0, update_user='hue', update_date=0, **kwargs):
    self.id = kwargs.setdefault('id', -1)
    self.creation_user = creation_user
    self.creation_date = creation_date
    self.update_user = update_user
    self.update_date = update_date
    self.enabled = enabled
    self.name = name
    self.connector_id = connector_id
    self.link_config_values = link_config_values

  @staticmethod
  def from_dict(link_dict):
    link_dict.setdefault('link_config_values', [])
    link_dict['link_config_values'] = [ Config.from_dict(link_config_value_dict) for link_config_value_dict in link_dict['link-config-values'] ]

    if not 'connector_id' in link_dict:
      link_dict['connector_id'] = link_dict.setdefault('connector-id', -1)

    if not 'creation_user' in link_dict:
      link_dict['creation_user'] = link_dict.setdefault('creation-user', 'hue')

    if not 'creation_date' in link_dict:
      link_dict['creation_date'] = link_dict.setdefault('creation-date', 0)

    if not 'update_user' in link_dict:
      link_dict['update_user'] = link_dict.setdefault('update-user', 'hue')

    if not 'update_date' in link_dict:
      link_dict['update_date'] = link_dict.setdefault('update-date', 0)

    return Link(**force_dict_to_strings(link_dict))

  def to_dict(self):
    d = {
      'id': self.id,
      'name': self.name,
      'creation-user': self.creation_user,
      'creation-date': self.creation_date,
      'update-user': self.update_user,
      'update-date': self.update_date,
      'connector-id': self.connector_id,
      'link-config-values': [ config.to_dict() for config in self.link_config_values ],
      'enabled': self.enabled
    }
    return d

  def update_from_dict(self, link_dict):
    self.update(Link.from_dict(link_dict))

  def update(self, link):
    for key in self.__dict__:
      if key not in Link.SKIP:
        if hasattr(link, key):
          setattr(self, key, getattr(link, key))
