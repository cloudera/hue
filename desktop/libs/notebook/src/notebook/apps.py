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

import logging

from django.apps import AppConfig


LOG = logging.getLogger()


class NotebookConfig(AppConfig):
  name = 'notebook'
  verbose_name = "Notebook SQL Assistant"

  def ready(self):
    from django.db import connection
    from notebook.models import install_custom_examples

    table_names = connection.introspection.table_names()
    if 'auth_group' in table_names and ('auth_user' in table_names or 'useradmin_organizationuser' in table_names):
      install_custom_examples()
