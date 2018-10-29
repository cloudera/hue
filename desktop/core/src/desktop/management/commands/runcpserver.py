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
from django.core.management.base import BaseCommand
from desktop import conf
from desktop import supervisor
import os
import sys
from django.utils.translation import ugettext as _

SERVER_HELP = r"""
  Run Hue using either the CherryPy server or the Spawning server, based on
  the current configuration.
"""

LOG = logging.getLogger(__name__)

class Command(BaseCommand):
  help = _("Web server for Hue.")

  def handle(self, *args, **options):
    runserver()

  def usage(self, subcommand):
    return SERVER_HELP

def runserver():
  script_name = "rungunicornserver"
  if conf.USE_CHERRYPY_SERVER.get():
    script_name = "runcherrypyserver"
  cmdv = supervisor.DjangoCommandSupervisee(script_name).cmdv
  os.execv(cmdv[0], cmdv)
  LOG.error("Failed to exec '%s' with argument '%s'" % (cmdv[0], cmdv[1],))
  sys.exit(-1)

if __name__ == '__main__':
  runserver()
