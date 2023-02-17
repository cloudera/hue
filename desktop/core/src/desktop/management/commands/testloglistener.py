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
import argparse
import desktop.log
import logging
import logging.config
import os
import pkg_resources
import sys

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

SERVER_HELP = r"""
  Run Python log tester
"""
def argprocessing(args=[], options={}):
  parser = argparse.ArgumentParser(prog='testloglistener', description='What this program does', epilog='Text at the bottom of help')
  parser.add_argument('-s', '--socket', dest='socket', action='store', default='/tmp/hue.uds')

  opts = parser.parse_args()
  if opts.socket:
    options['socket'] = opts.socket

def enable_logging(args, options):
  HUE_DESKTOP_VERSION = pkg_resources.get_distribution("desktop").version or "Unknown"
  # Start basic logging as soon as possible.
  if "HUE_PROCESS_NAME" not in os.environ:
    _proc = os.path.basename(len(sys.argv) > 1 and sys.argv[1] or sys.argv[0])
    os.environ["HUE_PROCESS_NAME"] = _proc

  desktop.log.basic_logging(os.environ["HUE_PROCESS_NAME"])
  logging.info("Welcome to Hue from Listener server " + HUE_DESKTOP_VERSION)

class Command(BaseCommand):
  help = _("Web server for Hue.")

  def add_arguments(self, parser):
    parser.add_argument('--socket', help=_("Unix Domain Socket file"), action='store', default=None)

  def handle(self, *args, **options):
    start_testing(args, options)

  def usage(self, subcommand):
    return SERVER_HELP

def start_testing(args, options):
  enable_logging(args, options)
  logger = logging.getLogger()
  i=0
  import time
  while i<100:
    logger.info("Hue log testing %s" % i)
    i += 1
    time.sleep(1)

if __name__ == '__main__':
  args=sys.argv[1:]
  options={}
  argprocessing(args=args, options=options)
  start_testing(args, options)