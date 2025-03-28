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
from django.contrib.auth.models import User

import desktop.conf

from django.utils.translation import gettext_lazy as _t, gettext as _

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Handler for running queries from Hue log with database_logging queries
    """

    try:
        from optparse import make_option
        option_list = BaseCommand.option_list + (
            make_option("--username", help=_t("User to delete case sensitive. "),
                        action="store"),
        )

    except AttributeError, e:
        baseoption_test = 'BaseCommand' in str(e) and 'option_list' in str(e)
        if baseoption_test:
            def add_arguments(self, parser):
                parser.add_argument("--username", help=_t("User to delete case sensitive."),
                                    action="store")
        else:
            LOG.exception(str(e))
            sys.exit(1)

    def handle(self, *args, **options):
        LOG.warn("Deleting user: %s" % options['username'])

        usernames = [ options['username'] ]
        try:
            User.objects.filter(username__in=usernames).delete()
        except Exception as e:
            LOG.warn("EXCEPTION: deleting user %s failed: %s" % (options['username'], e))


        LOG.debug("Done deleting user:  %s" % options['username'] )
