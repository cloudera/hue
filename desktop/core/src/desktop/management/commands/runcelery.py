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
import os
import sys

from desktop import conf
from desktop.lib.daemon_utils import drop_privileges_if_necessary

from django.core.management.base import BaseCommand
from django.utils import autoreload
from django.utils.translation import ugettext as _

SERVER_HELP = r"""
  Run celery worker.
"""

from celery.bin.celery import CeleryCommand
from celery.bin.celery import main as celery_main

LOG = logging.getLogger(__name__)
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
        default='DEBUG'
    )

  def handle(self, *args, **options):
    runcelery(*args, **options)

  def usage(self, subcommand):
    return SERVER_HELP

def runcelery(*args, **options):
  #CeleryCommand().handle_argv(['worker', '--app=desktop.celery', '--concurrency=1', '--loglevel=DEBUG'])
  opts = ['runcelery', 'worker', '--app=' + options['app'], '--concurrency=' + str(options['concurrency']), '--loglevel=' + options['loglevel']]
  drop_privileges_if_necessary(CELERY_OPTIONS)
  if conf.DEV.get():
    autoreload.main(celery_main, (opts,))
  else:
    celery_main(opts)
  LOG.error("Failed to exec '%s' with argument '%s'" % args)
  sys.exit(-1)

if __name__ == '__main__':
  runcelery(sys.argv[1:])
