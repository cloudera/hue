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
Helpers to build the apps
"""

import logging
import os
import subprocess

import common

LOG = logging.getLogger(__name__)

def runcmd(cmdv, additional_env=None):
  """
  runcmd(cmdv, additional_env=None) -> status code
  """
  env = os.environ.copy()
  if additional_env is not None:
    env.update(additional_env)
  LOG.debug("Running '%s' with %r" % (' '.join(cmdv), additional_env))
  popen = subprocess.Popen(cmdv, env=env)
  return popen.wait()


def make_app(app):
  """
  make_app() -> True/False

  Call `make egg-info ext-eggs' on the app.
  """
  cmdv = [ 'make', '-C', app.path, 'egg-info', 'ext-eggs' ]
  return runcmd(cmdv, dict(ROOT=common.INSTALL_ROOT)) == 0


def make_syncdb():
  """
  make_syncdb() -> True/False
  """
  cmdv = [ 'make', '-C', os.path.join(common.INSTALL_ROOT, 'desktop'), '-B', 'syncdb' ]
  return runcmd(cmdv) == 0
