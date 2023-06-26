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
import sys
from desktop.models import Document2
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _t, gettext as _
else:
  from django.utils.translation import ugettext_lazy as _t, ugettext as _

LOG = logging.getLogger()


class Command(BaseCommand):
  """
  Handler for changing ownership of docs
  """

  try:
    from optparse import make_option
    option_list = BaseCommand.option_list + (
      make_option("--olduser", help=_t("User who's docs need to change ownership. "),
                  action="store"),
      make_option("--newuser", help=_t("User who will own the docs. "),
                  action="store"),
    )

  except AttributeError, e:
    baseoption_test = 'BaseCommand' in str(e) and 'option_list' in str(e)
    if baseoption_test:
      def add_arguments(self, parser):
        parser.add_argument("--olduser", help=_t("User who's docs need to change ownership. "),
                            action="store"),
        parser.add_argument("--newuser", help=_t("User who will own the docs. "),
                            action="store")

    else:
      LOG.exception(str(e))
      sys.exit(1)

  def handle(self, *args, **options):
    LOG.warn("Changing ownership of all docs owned by %s to %s" % (options['olduser'], options['newuser']))

    if not options['olduser']:
      LOG.exception("--olduser option required")
      sys.exit(1)

    if not options['newuser']:
      LOG.exception("--newuser option required")
      sys.exit(1)

    try:
      newuser = User.objects.get(username=options['newuser'])
      olduser = User.objects.get(username=options['olduser'])
      docs = Document2.objects.filter(owner=olduser)
      Document2.objects.filter(owner=olduser).update(owner=newuser)

    except Exception as e:
      LOG.warn(
        "EXCEPTION: Changing ownership of %s's docs to %s failed: %s" % (options['olduser'], options['newuser'], e))
