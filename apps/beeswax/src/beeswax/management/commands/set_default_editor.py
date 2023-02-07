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
from desktop.models import set_user_preferences
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _t, gettext as _
else:
  from django.utils.translation import ugettext_lazy as _t, ugettext as _

logging.basicConfig()
LOG = logging.getLogger(__name__)


class Command(BaseCommand):
  """
  Handler for renaming duplicate User objects
  """

  try:
    from optparse import make_option
    option_list = BaseCommand.option_list + (
      make_option("--hive", help=_t("Set Hive as default."),
                  action="store_true", default=False, dest='sethive'),
      make_option("--impala", help=_t("Set Impala as default."),
                  action="store_true", default=False, dest='setimpala'),
      make_option("--username", help=_t("User to set."),
                  action="store", default="all", dest='username'),
    )

  except AttributeError, e:
    baseoption_test = 'BaseCommand' in str(e) and 'option_list' in str(e)
    if baseoption_test:
      def add_arguments(self, parser):
        parser.add_argument("--hive", help=_t("Set Hive as default."),
                            action="store_true", default=False, dest='sethive'),
        parser.add_argument("--impala", help=_t("Set Impala as default."),
                            action="store_true", default=False, dest='setimpala'),
        parser.add_argument("--username", help=_t("User to set."),
                            action="store", default="all", dest='username'),

    else:
      LOG.exception(str(e))
      sys.exit(1)

  def handle(self, *args, **options):
    key = "default_app"
    set_props = None
    if options['sethive']:
      set_props = '{"app":"editor","interpreter":"hive"}'
      editor = "hive"
    if options['setimpala']:
      set_props = '{"app":"editor","interpreter":"impala"}'
      editor = "impala"
    if set_props is None:
      set_props = '{"app":"editor","interpreter":"impala"}'
      editor = "impala"

    if options['username'] != "all":
      LOG.info("Setting default interpreter to %s for user %s" % (editor, options['username']))
      user = User.objects.get(username=options['username'])
      set_user_preferences(user, key, set_props)

    else:
      for user in User.objects.filter():
        LOG.info("Setting default interpreter to %s for user %s" % (editor, options['username']))
        set_user_preferences(user, key, set_props)
