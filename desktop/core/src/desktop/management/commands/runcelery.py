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

import os
import sys
import logging

from celery.bin.celery import CeleryCommand, main as celery_main
from django.core.management.base import BaseCommand
from django.utils import autoreload
from django.utils.translation import gettext as _

from desktop import conf
from desktop.conf import TASK_SERVER_V2
from desktop.lib.daemon_utils import drop_privileges_if_necessary
from desktop.log import DEFAULT_LOG_DIR

SERVER_HELP = r"""
  Run celery worker.
"""

LOG = logging.getLogger()
CELERY_OPTIONS = {
  'server_user': conf.SERVER_USER.get(),
  'server_group': conf.SERVER_GROUP.get(),
}


class Command(BaseCommand):
  help = SERVER_HELP

  def add_arguments(self, parser):
    parser.add_argument('worker')
    parser.add_argument(
        '--app',
        type=str,
        default='desktop.celery'
    )
    parser.add_argument(
        '--concurrency',
        type=int,
        default=1
    )
    parser.add_argument(
        '--loglevel',
        type=str,
        default='INFO'
    )
    parser.add_argument('--beat')
    parser.add_argument(
        '--schedule_file',
        type=str,
        required=True,
        default='celerybeat-schedule',
        help='Path to the celerybeat-schedule file'
    )

  def handle(self, *args, **options):
    runcelery(*args, **options)

  def usage(self, subcommand):
    return SERVER_HELP


def runcelery(*args, **options):
  # Native does not load Hue's config
  log_dir = os.getenv("DESKTOP_LOG_DIR", DEFAULT_LOG_DIR)
  log_file = "%s/celery.log" % (log_dir)
  concurrency = max(int(conf.GUNICORN_NUMBER_OF_WORKERS.get() / 4), 1) or options['concurrency']
  schedule_file = options['schedule_file']
  celery_log_level = TASK_SERVER_V2.CELERY_LOG_LEVEL.get()
  opts = [
    'celery',
    '--app=' + options['app'],
    'worker',
    '--loglevel=' + str(celery_log_level),
    '--concurrency=' + str(concurrency),
    '--beat',
    '-s', schedule_file,
    '--logfile=' + log_file
  ]
  drop_privileges_if_necessary(CELERY_OPTIONS)

  # Set command-line arguments for Celery
  sys.argv = opts

  # Call the Celery main function
  celery_main()

  LOG.info("Stopping command '%s'" % ' '.join(opts))
  sys.exit(-1)


if __name__ == '__main__':
  runcelery(sys.argv[1:])
