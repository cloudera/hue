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
  Generate Log lines to test new Log listener functionality
"""
def argprocessing(args=[], options={}):
  parser = argparse.ArgumentParser(prog='testloglistener', description='Generate log to test new logging functionality')
  parser.add_argument('-s', '--socket', dest='socket', action='store', default='')

  opts = parser.parse_args()
  if opts.socket != '':
    options['socket'] = opts.socket
  else:
    options['socket'] = "%s/hue.uds" % (os.getenv("DESKTOP_LOG_DIR", "/var/log/hue"))

def enable_logging(args, options):
  HUE_DESKTOP_VERSION = pkg_resources.get_distribution("desktop").version or "Unknown"
  # Start basic logging as soon as possible.
  desktop.log.basic_logging("rungunicornserver")
  logging.info("Welcome to Hue from Listener server " + HUE_DESKTOP_VERSION)

class Command(BaseCommand):
  help = _("Test script for logging.")

  def add_arguments(self, parser):
    parser.add_argument('-s', '--socket', help=_("Unix Domain Socket file"), dest='socket',
                        action='store', default='')

  def handle(self, *args, **options):
    if options["socket"] == '':
      options['socket'] = "%s/hue.uds" % (os.getenv("DESKTOP_LOG_DIR", "/var/log/hue"))

    start_testing(args, options)

  def usage(self, subcommand):
    return SERVER_HELP

def start_testing(args, options):
  enable_logging(args, options)
  logger = logging.getLogger()
  i = 0
  import time
  while i < 100:
    logger.info("Hue log testing %s" % i)
    i += 1
    time.sleep(1)

if __name__ == '__main__':
  args = sys.argv[1:]
  options = {}
  argprocessing(args=args, options=options)
  start_testing(args, options)
