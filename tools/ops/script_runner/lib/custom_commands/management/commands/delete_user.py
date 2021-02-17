#!/usr/bin/env python
import os
import sys
import time
import datetime
import re
import logging

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _t, ugettext as _
from django.contrib.auth.models import User

import desktop.conf

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Handler for deleting users
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


        LOG.debug("Done deleting user: %s" % options['username'] )


