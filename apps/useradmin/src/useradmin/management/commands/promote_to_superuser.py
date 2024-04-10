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
    Handler for promoting a user to superuser
    """    
    def add_arguments(self, parser):
        parser.add_argument("--usernames", help=_t("User(s) to promote to superuser."), nargs='+', action="store",required=True)
    
    def handle(self, *args, **options):
        if options["usernames"]:
            try:
                LOG.warn("Promoting user %s to superuser" % options['usernames'])
                
                user_exist = []
                user_not_exist = []
                usernames = options["usernames"]
                
                for user in usernames:
                    isExist = User.objects.filter(username=user).exists()
                    if (isExist):
                        new_super = User.objects.get(username = user)
                        new_super.is_superuser = True
                        new_super.save()
                        user_exist.append(user)
                    else:
                        user_not_exist.append(user)
                
                LOG.info("User(s) promoted to superuser: %s" % user_exist)
                LOG.info("User(s) does not exist: %s" % user_not_exist)
            except Exception as e:
                LOG.error("EXCEPTION: promoting user %s to superuser failed: %s" % (options['username'], e))