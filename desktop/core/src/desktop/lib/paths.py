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
#
# Path-related utilities
#
# These are useful for testing, but shouldn't be heavily depended on,
# since paths have a tendency to change during packaging.

import os

"""
The project directory structure:
    root/                                 <-- Project root (build root, run root)
        apps/                             <-- Apps root
            beeswax/
        desktop/                          <-- Desktop root
            core/
                src/desktop/lib/paths.py  <-- You're reading this file
                ...
        ext/
            thirdparty/...
"""

SAFE_CHARACTERS_URI = '~@#$&()*!+=:;,.?/\''
SAFE_CHARACTERS_URI_COMPONENTS = '~@#$&()*!+=;,.\'' # Removing characters : / ? from safe list for KNOX

def __get_root(*append):
  """
  Returns the root directory of the project.
  """
  if append is None:
    append = [ ]
  path = os.path.join(
              os.path.dirname(__file__),
              "..", "..", "..", "..", "..",
              *append)
  return os.path.abspath(path)


def get_build_dir(*append):
  """
  Returns 'build' directory for Desktop.

  This is used for temporary (and testing) artifacts.
  This is not the root source path.
  """
  return __get_root('build', *append)


def get_desktop_root(*append):
  """
  Returns the directory for Desktop.
  """
  return __get_root("desktop", *append)


def get_apps_root(*append):
  """
  Returns the directory for apps.
  """
  return __get_root("apps", *append)


def get_thirdparty_root(*append):
  """
  Returns the ext/thirdparty directory.
  """
  return __get_root("ext", "thirdparty", *append)


def get_run_root(*append):
  """
  Returns the run time root directory
  """
  return __get_root(*append)


def get_config_root(*append):
  """
  Currently gets it based on the Hadoop configuration location.
  """
  from hadoop.conf import HDFS_CLUSTERS

  yarn_site_path = HDFS_CLUSTERS['default'].HADOOP_CONF_DIR.get()
  return os.path.abspath(os.path.join(yarn_site_path, '..', *append))
