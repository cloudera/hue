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

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_unicode


def get_api(request, interface):

  if interface == 'navigator':
    from metadata.catalog.navigator_client import NavigatorApi
    return NavigatorApi(user=request.user)
  elif interface == 'atlas':
    from metadata.catalog.atlas_client import AtlasApi
    return AtlasApi(user=request.user)
  elif interface == 'dummy':
    from metadata.catalog.dummy_client import DummyApi
    return DummyApi(user=request.user)
  else:
    raise PopupException(_('Catalog connector interface not recognized: %s') % interface)


class CatalogApiException(Exception):
  def __init__(self, message=None):
    self.message = message or _('No error message, please check the logs.')

  def __str__(self):
    return str(self.message)

  def __unicode__(self):
    return smart_unicode(self.message)


class CatalogEntityDoesNotExistException(Exception):
  def __init__(self, message=None):
    self.message = message or _('No error message, please check the logs.')

  def __str__(self):
    return str(self.message)

  def __unicode__(self):
    return smart_unicode(self.message)


class CatalogAuthException(Exception):
  def __init__(self, message=None):
    self.message = message or _('No error message, please check the logs.')

  def __str__(self):
    return str(self.message)

  def __unicode__(self):
    return smart_unicode(self.message)


# Base API

class Api(object):

  def __init__(self, user=None):
    self.user = user

  # To implement

  def search_entities_interactive(self, query_s=None, limit=100, **filters):
    """For the top search"""
    return {}


  def find_entity(self, source_type, type, name, **filters):
    """e.g. From a database and table name, retrieve the enity id"""
    return {}


  def get_entity(self, entity_id):
    return {}


  def update_entity(self, entity, **metadata):
    return {}


  def add_tags(self, entity_id, tags):
    return {}


  def delete_tags(self, entity_id, tags):
    return {}


  def update_properties(self, entity_id, properties, modified_custom_metadata=None, deleted_custom_metadata_keys=None):
    """For updating entity comments or other attributes"""
    return {}

  # Common APIs

  def get_database(self, name):
    return self.find_entity(source_type='HIVE', type='DATABASE', name=name)


  def get_table(self, database_name, table_name, is_view=False):
    parent_path = '\/%s' % database_name
    return self.find_entity(source_type='HIVE', type='VIEW' if is_view else 'TABLE', name=table_name, parentPath=parent_path)


  def get_field(self, database_name, table_name, field_name):
    parent_path = '\/%s\/%s' % (database_name, table_name)
    return self.find_entity(source_type='HIVE', type='FIELD', name=field_name, parentPath=parent_path)


  def get_partition(self, database_name, table_name, partition_spec):
    raise NotImplementedError


  def get_directory(self, path):
    dir_name, dir_path = self._clean_path(path)
    return self.find_entity(source_type='HDFS', type='DIRECTORY', name=dir_name, fileSystemPath=dir_path)


  def get_file(self, path):
    file_name, file_path = self._clean_path(path)
    return self.find_entity(source_type='HDFS', type='FILE', name=file_name, fileSystemPath=file_path)
