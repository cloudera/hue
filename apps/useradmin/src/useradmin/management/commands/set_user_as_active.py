import os
import sys
import time
import datetime
import re
import logging

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

import desktop.conf

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _t, gettext as _
else:
  from django.utils.translation import ugettext_lazy as _t, ugettext as _

LOG = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Handler for making user(s) active.
    """

    def add_arguments(self, parser):
        parser.add_argument("--usernames", help=_t("One or more user(s) to make active."),nargs='+', action="store",required=True)

    def handle(self, *args, **options):
        if options["usernames"]:
            try:
                LOG.info("Setting user %s as active" % options['usernames'])
                
                user_exist = []
                user_not_exist = []
                usernames = options["usernames"]
                
                for user in usernames:
                    isExist = User.objects.filter(username=user).exists()
                    if (isExist):
                        active_user = User.objects.get(username=user)
                        active_user.is_active = True
                        active_user.save()
                        user_exist.append(user)
                    else:
                        user_not_exist.append(user)
                
                LOG.info("User(s) set as Active: %s" % user_exist)
                LOG.info("User(s) does not exist: %s" % user_not_exist)
            except Exception as e:
                LOG.error("EXCEPTION: setting user %s as active failed: %s" % (options['usernames'], e))