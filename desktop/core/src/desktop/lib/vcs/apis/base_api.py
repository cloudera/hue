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

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)

GITHUB_OFFICIAL = 'github'
GIT_READ_ONLY = 'git-read-only'


def get_api(interface):
  from desktop.lib.vcs.apis.github_api import GithubApi
  from desktop.lib.vcs.apis.github_readonly_api import GithubReadOnlyApi

  if interface == GITHUB_OFFICIAL:
    return GithubApi()
  elif interface == GIT_READ_ONLY:
    return GithubReadOnlyApi()
  else:
    raise PopupException(_('Interface %s is unknown') % interface)


class Api(object):

  def __init__(self):
    pass

  def authorize(self, request): return {}

  def contents(self, request): return {}