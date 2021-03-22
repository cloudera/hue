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
import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _

from desktop.lib import paths


RULES = [
  'C0326(bad-whitespace)',
  'W0311(bad-indentation)',
  'C0301(line-too-long)'
]


class Command(BaseCommand):
  help = _("""
  Runs pylint on desktop and app code.

  With no arguments, or with "all", this will run pylint on all installed apps. Otherwise, specify a list of files
  or modules to run, as well as other parameters to pylint.
  Note that you'll want to preface the section of pylint arguments with "--" so Django's manage.py passes them along.

  Examples:
    python core/manage.py runpylint all -- -f parseable
    python core/manage.py runpylint --files="apps/jobbrowser/src/jobbrowser/apis/base_api.py desktop/libs/notebook/src/notebook/api.py"
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
    parser.add_argument('--output-format', action='store', dest='outputformat', default='parseable')
    parser.add_argument('-a', '--app', dest='app', action='store', default='all', choices=self.valid_app())
    parser.add_argument('-F', '--files', dest='files', action='store', default=None)

  def handle(self, *args, **options):
    """Check the source code using PyLint."""

    # Note that get_build_dir() is suitable for testing use only.
    pylint_prog = paths.get_build_dir('env', 'bin', 'pylint')
    pylint_args = [
      pylint_prog,
      "--rcfile=" + settings.PYLINTRC,
      "--disable=all",
      "--enable=%s" % ','.join([rule.split('(', 1)[0] for rule in RULES]),
      "--load-plugins=pylint_django"
    ]

    if options['force']:
      pylint_args.append('-f')

    if options['outputformat']:
      pylint_args.append(options['outputformat'])

    if options['files'] is not None:
      pylint_args.extend(options['files'].split())
    elif options['app'] == 'all':
      pylint_args.extend(self.valid_app())
    else:
      pylint_args.append(options['app'])

    if not os.path.exists(pylint_prog):
      msg = _("Cannot find pylint at '%(path)s'. Please install pylint first.") % {'path': pylint_prog}
      logging.error(msg)
      raise CommandError(msg)

    logging.info("Running pylint with args: %s" % (" ".join(pylint_args),))

    # We exec pylint directly due to a "maximum recursion depth" bug when doing
    # pylint.lint(...) programmatically.
    ret = subprocess.call(pylint_args)
    if ret != 0:
      sys.exit(1)
