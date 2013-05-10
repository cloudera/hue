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

# The Hue config directory
HUE_CONF_DIR = os.path.join(INSTALL_ROOT, 'desktop', 'conf')

# Virtual env
VIRTUAL_ENV = os.path.join(INSTALL_ROOT, 'build', 'env')

# The Python executable in virtualenv
ENV_PYTHON = os.path.join(VIRTUAL_ENV, 'bin', 'python')

def cmp_version(ver1, ver2):
  """Compare two version strings in the form of 1.2.34"""
  return cmp(ver1.split('.'), ver2.split('.'))

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


# Creates os.path.relpath for Python 2.4 and 2.5
if not hasattr(os.path, 'relpath'):
  # default to posixpath definition
  # no windows support
  def relpath(path, start=os.path.curdir):
    """Return a relative version of a path"""

    if not path:
      raise ValueError("no path specified")

    start_list = os.path.abspath(start).split(os.path.sep)
    path_list = os.path.abspath(path).split(os.path.sep)

    # Work out how much of the filepath is shared by start and path.
    i = len(os.path.commonprefix([start_list, path_list]))

    rel_list = [os.path.pardir] * (len(start_list)-i) + path_list[i:]
    if not rel_list:
        return os.path.curdir
    return os.path.join(*rel_list)
  os.path.relpath = relpath