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

import os.path

# The root of the Hue installation
INSTALL_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..'))

# The Hue config directory
HUE_CONF_DIR = os.path.join(INSTALL_ROOT, 'desktop', 'conf')

# Virtual env
VIRTUAL_ENV = os.path.join(INSTALL_ROOT, 'build', 'env')

# The Python executable in virtualenv
ENV_PYTHON = os.path.join(VIRTUAL_ENV, 'bin', 'python')

def cmp_version(ver1, ver2):
  """Compare two version strings in the form of 1.2.34"""
  return cmp(ver1.split('.'), ver2.split('.'))
