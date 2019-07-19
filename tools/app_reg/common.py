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

import glob
import logging
import os
import sys
from posixpath import curdir, sep, pardir, join

# The root of the Hue installation
INSTALL_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..'))

# The apps location
APPS_ROOT = os.path.join(INSTALL_ROOT, 'apps')

# Directory holding app.reg
HUE_APP_REG_DIR = os.environ.get("HUE_APP_REG_DIR", INSTALL_ROOT) 

# Directory holding hue.pth
HUE_PTH_DIR = os.environ.get('HUE_PTH_DIR', None)

# The Hue config directory
HUE_CONF_DIR = os.path.join(INSTALL_ROOT, 'desktop', 'conf')

# Virtual env
VIRTUAL_ENV = os.path.join(INSTALL_ROOT, 'build', 'env')

# The Python executable in virtualenv
ENV_PYTHON = os.path.join(VIRTUAL_ENV, 'bin', 'python')

def cmp_version(ver1, ver2):
  """Compare two version strings in the form of 1.2.34"""
  return cmp([int(v) for v in ver1.split('.')], [int(v) for v in ver2.split('.')])

def _get_python_lib_dir():
  glob_path = os.path.join(VIRTUAL_ENV, 'lib', 'python*')
  res = glob.glob(glob_path)
  if len(res) == 0:
    raise SystemError("Cannot find a Python installation in %s. "
                      "Did you do `make hue'?" % glob_path)
  elif len(res) > 1:
    raise SystemError("Found multiple Python installations in %s. "
                      "Please `make clean' first." % glob_path)
  return res[0]

def _get_python_site_packages_dir():
  return os.path.join(_get_python_lib_dir(), 'site-packages')
