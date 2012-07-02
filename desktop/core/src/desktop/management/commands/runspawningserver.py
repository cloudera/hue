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

import desktop.lib.eventlet_util


import logging
import os
import sys

from django.core.management.base import BaseCommand
from desktop import conf
import spawning.spawning_controller
from desktop.lib.daemon_utils import drop_privileges_if_necessary

from django.utils.translation import ugettext as _

SPAWNING_SERVER_HELP = r"""
  Run Hue using the Spawning WSGI server in asynchronous mode.
"""

SPAWNING_SERVER_OPTIONS = {
  'access_log_file': os.devnull,
  'backdoor': None,
  'chuid': None,
  'coverage': None,
  'daemonize': None,
  'deadman_timeout': 1,
  'factory': 'spawning.django_factory.config_factory',
  'host': conf.HTTP_HOST.get(),
  'max_age': None,
  'max_memory': 0,
  'no_keepalive': None,
  'pidfile': None,
  'port': conf.HTTP_PORT.get(),
  'processes': 1,
  'reload': None,
  'restart_args': None,
  'server_user': conf.SERVER_USER.get(),
  'server_group': conf.SERVER_GROUP.get(),
  'ssl_certificate': conf.SSL_CERTIFICATE.get(),
  'ssl_private_key': conf.SSL_PRIVATE_KEY.get(),
  'status_host': '',
  'status_port': 0,
  'stderr': None,
  'stdout': None,
  'sysinfo': None,
  'threads': 0,
  'verbose': None,
  'watch': None
}

LOG = logging.getLogger(__name__)

class Command(BaseCommand):
    help = _("Spawning Server for Hue.")

    def handle(self, *args, **options):
        from django.conf import settings
        from django.utils import translation

        if not conf.ENABLE_SERVER.get():
            LOG.info("Hue is configured to not start its own web server.")
            sys.exit(0)

        # Activate the current language, because it won't get activated later.
        try:
            translation.activate(settings.LANGUAGE_CODE)
        except AttributeError:
            pass
        runspawningserver()

    def usage(self, subcommand):
        return SPAWNING_SERVER_HELP


def runspawningserver():
  try:
    sock = spawning.spawning_controller.bind_socket(SPAWNING_SERVER_OPTIONS)
  except Exception, ex:
    LOG.error('Could not bind port %s: %s. Exiting' % (str(SPAWNING_SERVER_OPTIONS['port']), ex,))
    return

  drop_privileges_if_necessary(SPAWNING_SERVER_OPTIONS)

  factory = SPAWNING_SERVER_OPTIONS['factory']

  pos_args = ['desktop.settings']

  argv_str_format = '--factory=%s %s --port %s -s %d -t %d'
  argv_str =  argv_str_format % (SPAWNING_SERVER_OPTIONS['factory'],
                                 pos_args[0],
                                 SPAWNING_SERVER_OPTIONS['port'],
                                 SPAWNING_SERVER_OPTIONS['processes'],
                                 SPAWNING_SERVER_OPTIONS['threads'])

  factory_args = {
    'access_log_file': SPAWNING_SERVER_OPTIONS['access_log_file'],
    'args': pos_args,
    'argv_str': argv_str,
    'coverage': SPAWNING_SERVER_OPTIONS['coverage'],
    'deadman_timeout': SPAWNING_SERVER_OPTIONS['deadman_timeout'],
    'host': SPAWNING_SERVER_OPTIONS['host'],
    'max_age' : SPAWNING_SERVER_OPTIONS['max_age'],
    'no_keepalive' : SPAWNING_SERVER_OPTIONS['no_keepalive'],
    'num_processes': SPAWNING_SERVER_OPTIONS['processes'],
    'pidfile': SPAWNING_SERVER_OPTIONS['pidfile'],
    'port': SPAWNING_SERVER_OPTIONS['port'],
    'reload': SPAWNING_SERVER_OPTIONS['reload'],
    'ssl_certificate': SPAWNING_SERVER_OPTIONS['ssl_certificate'],
    'ssl_private_key': SPAWNING_SERVER_OPTIONS['ssl_private_key'],
    'status_host': SPAWNING_SERVER_OPTIONS['status_host'] or SPAWNING_SERVER_OPTIONS['host'],
    'status_port': SPAWNING_SERVER_OPTIONS['status_port'],
    'sysinfo': SPAWNING_SERVER_OPTIONS['sysinfo'],
    'threadpool_workers': SPAWNING_SERVER_OPTIONS['threads'],
    'verbose': SPAWNING_SERVER_OPTIONS['verbose'],
    'watch': SPAWNING_SERVER_OPTIONS['watch']
  }

  os.environ['HUE_SPAWNING'] = 'yes'
  spawning.spawning_controller.start_controller(sock, factory, factory_args)


if __name__ == '__main__':
  runspawningserver()
