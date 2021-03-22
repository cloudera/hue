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
import time
import datetime
import re
import logging

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group

import desktop.conf

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _t, gettext as _
else:
  from django.utils.translation import ugettext_lazy as _t, ugettext as _

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Handler for listing groups and groups associated with a user
    """

    try:
        from optparse import make_option
        option_list = BaseCommand.option_list + (
            make_option("--username", help=_t("Groups this user belongs to . "),
                        action="store", default=None),
        )

    except AttributeError, e:
        baseoption_test = 'BaseCommand' in str(e) and 'option_list' in str(e)
        if baseoption_test:
            def add_arguments(self, parser):
                parser.add_argument("--username", help=_t("Groups this user belongs to."),
                                    action="store", default=None)
        else:
            LOG.exception(str(e))
            sys.exit(1)

    def handle(self, *args, **options):
        LOG.info("Listing Hue groups")
        try:
          if options['username'] != None:
            LOG.info("Listing groups for %s" % options['username'])
            user = User.objects.get(username = options['username'])
            groups = user.groups.all()
            for group in groups:
              print group.name
          else:
            LOG.info("Listing all groups")
            groups = Group.objects.all()
            for group in groups:
              print group.name

        except Exception as e:
            LOG.warn("EXCEPTION: Listing groups failed, %s" % e)
