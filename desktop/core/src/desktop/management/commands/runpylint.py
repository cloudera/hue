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
import os.path
import subprocess

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from desktop.lib import paths
from django.utils.translation import ugettext as _

class Command(BaseCommand):
  help = _("""
  Runs pylint on desktop and app code.

  With no arguments, or with "all", this will run pylint on all
  installed apps.  Otherwise, specify modules to run, as well
  as other parameters to pylint.  Note that you'll want to preface the section
  of pylint arguments with "--" so Django's manage.py passes them along.

  Examples:
    python core/manage.py runpylint all -- -f parseable
    python core/manage.py runpylint filebrowser
    python core/manage.py runpylint
  """)

  def valid_app(self):
    from desktop import appmanager
    apps = ["desktop"]
    for app in appmanager.DESKTOP_APPS:
      apps.append(app.name)
    return apps

  def add_arguments(self, parser):
    parser.add_argument('-f', '--force', dest='force', default='true', action="store_true")
    parser.add_argument('--output-format',
      action='store', dest='outputformat', default='parseable')
    parser.add_argument('-a', '--app', dest='app', action='store', default='all', choices=self.valid_app())

  def handle(self, *args, **options):
    """Check the source code using PyLint."""

    # Note that get_build_dir() is suitable for testing use only.
    pylint_prog = paths.get_build_dir('env', 'bin', 'pylint')
    pylint_args = [pylint_prog, "--rcfile=" + settings.PYLINTRC]

    if options['app']=='all':
      pylint_args.extend(self.valid_app())
    else:
      pylint_args.append(options['app'])

    if options['force']:
      pylint_args.append('-f')

    if options['outputformat']:
      pylint_args.append(options['outputformat'])

    if not os.path.exists(pylint_prog):
      msg = _("Cannot find pylint at '%(path)s'. Please install pylint first.") % {'path': pylint_prog}
      logging.error(msg)
      raise CommandError(msg)

    logging.info("Running pylint with args: %s" % (" ".join(pylint_args),))

    # We exec pylint directly due to a "maximum recursion depth" bug when doing
    # pylint.lint(...) programmatically.
    subprocess.call(pylint_args)
