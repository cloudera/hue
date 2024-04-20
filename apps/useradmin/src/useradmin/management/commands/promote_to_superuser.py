#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
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

LOG = logging.getLogger()

class Command(BaseCommand):
  """
  Handler for promoting a user to superuser
  """  
  def add_arguments(self, parser):
    parser.add_argument("--usernames", help=_t("User(s) to promote to superuser."), nargs='+', action="store", required=True)
  
  def handle(self, *args, **options):
    if options.get("usernames"):
      try:
        LOG.warn("Promoting user %s to superuser" % options['usernames'])
        
        user_exist = []
        user_not_exist = []
        usernames = options["usernames"]
        
        for user in usernames:
          is_exist = User.objects.filter(username=user).exists()
          if (is_exist):
            new_super=User.objects.get(username = user)
            new_super.is_superuser = True
            new_super.save()
            user_exist.append(user)
          else:
            user_not_exist.append(user)
        
        if (user_exist):
          LOG.info("User(s) promoted to superuser: %s" % user_exist)
        
        if (user_not_exist):
          LOG.info("User(s) does not exist: %s" % user_not_exist)
      
      except Exception as e:
        LOG.error("EXCEPTION: promoting user %s to superuser failed: %s" % (options['username'], e))