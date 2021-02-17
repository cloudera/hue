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
from desktop.models import Document2

import desktop.conf

LOG = logging.getLogger(__name__)


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
            newuser = User.objects.get(username = options['newuser'])
            olduser = User.objects.get(username = options['olduser'])
            docs = Document2.objects.filter(owner=olduser)
            Document2.objects.filter(owner=olduser).update(owner=newuser)

        except Exception as e:
            LOG.warn("EXCEPTION: Changing ownership of %s's docs to %s failed: %s" % (options['olduser'], options['newuser'], e))


