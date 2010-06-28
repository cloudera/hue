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
from django.conf import settings

class Command(BaseCommand):
  help = """
  Runs pylint on desktop code.

  With no arguments, or with "all", this will run pylint on all
  installed apps.  Otherwise, specify modules to run, as well
  as other parameters to pylint.  Note that you'll want to preface the section
  of pylint arguments with "--" so Django's manage.py passes them along.

  Examples:
    python core/manage.py runpylint all -- -f parseable
    python core/manage.py runpylint filebrowser
    python core/manage.py runpylint
  """

  def handle(self, *args, **options):
    """Check the source code using PyLint."""
    import pylint.lint

    # Pylint modifies these, so we need a mutable copy.
    pylint_args = list(args)

    if "all" in pylint_args or len(pylint_args) == 0:
      if "all" in pylint_args:
        pylint_args.remove("all")
      from desktop import appmanager
      apps = ["desktop"]
      for app in appmanager.DESKTOP_APPS:
        apps.append(app.name)
      pylint_args = apps + pylint_args

    pylint_args = ["--rcfile=" + settings.PYLINTRC] + pylint_args

    logging.info("Running pylint with args: %s" % " ".join(pylint_args))
    try:
      pylint.lint.Run(pylint_args)
    except SystemExit:
      logging.debug("Ignoring pylint sys.exit()", exc_info=1)
