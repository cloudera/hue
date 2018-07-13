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

from configobj import ConfigObj

from django.core.management.base import BaseCommand, CommandError

import simplejson as json

import logging

import sys


DEFAULT_HUE_CONFIG_PATH = "/etc/hue/conf/hue.ini"

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
  """ Overrides sections of the hue.ini with the supplied dictionary entries.

  e.g. hue override_config --inline_override="{\"desktop\":{\"cherrypy_server_threads\":50}}"
  to override [desktop] cherrypy_server_threads entry
  """
  def add_arguments(self, parser):
    parser.add_argument('-c', '--config_path', default=DEFAULT_HUE_CONFIG_PATH, action='store', dest='config_path',
                  help='Absolute hue.ini file path where config should be written or merged to')

    parser.add_argument('-o', '--override_path', dest='override_path', action='store',
                  help='Absolute file path of a local JSON file to be merged with hue.ini')

    parser.add_argument('-i', '--inline_override', dest='inline_override', action='store',
                  help='A JSON dictionary to be merged with hue.ini')

  def handle(self, *args, **options):

    override_path = options['override_path']
    inline_override = options['inline_override']

    # Mutually exclusive options:
    if override_path and inline_override:
      message = 'You can supply only one of %s' % ' or '.join(('inline_override (i)', 'override_path (o)',))
      raise CommandError(message)

    if override_path:
      with open(override_path) as fp:
        overrides = json.load(fp)
    elif inline_override:
      overrides = json.loads(inline_override)
    else:
      overrides = json.load(sys.stdin)

    Command._merge_config_with_dict_overrides(options['config_path'], overrides)

  @staticmethod
  def _merge_config_with_dict_overrides(config_path, overrides):
    config = ConfigObj(config_path)
    config.merge(overrides)
    config.write()
