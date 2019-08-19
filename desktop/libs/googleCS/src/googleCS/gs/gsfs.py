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

"""
Interfaces for Google Storage
"""
from future import standard_library
standard_library.install_aliases()
from builtins import object
import logging
import os
import threading

from hadoop.hdfs_site import get_umask_mode

from googleCS.conf import PERMISSION_ACTION_GOOGLECS


class GSFileSystem(object):
  def __init__(self, gs_connection, expiration=None):
    self._gs_connection = gs_connection
    self._filebrowser_action = PERMISSION_ACTION_GOOGLECS
    self.user = None
    self.is_sentry_managed = lambda path: False
    self.superuser = None
    self.supergroup = None
    self.expiration = expiration

  def get_bucket(self, name):
    return self._gs_connection.get_bucket(name)