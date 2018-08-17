
# adapted from django-extensions (http://code.google.com/p/django-command-extensions/)
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
import time

from importlib import import_module

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _t, ugettext as _
from beeswax.models import SavedQuery
from beeswax.models import Session
from datetime import date, timedelta
from oozie.models import Workflow
from django.db.utils import DatabaseError
import desktop.conf
from desktop.models import Document2
import logging
import logging.handlers

import desktop.conf

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Handler for purging old Query History, Workflow documents and Session data
    """

    try:
        from optparse import make_option
        option_list = BaseCommand.option_list + (
            make_option("--keep-days", help=_t("Number of days of history data to keep."),
                    action="store",
                    type=int,
                    default=30),
        )

    except AttributeError, e:
        baseoption_test = 'BaseCommand' in str(e) and 'option_list' in str(e)
        if baseoption_test:
            def add_arguments(self, parser):
                parser.add_argument("--keep-days", help=_t("Number of days of history data to keep."),
                    action="store",
                    type=int,
                    default=30)
        else:
            LOG.exception(str(e))
            sys.exit(1)


    def objectCleanup(self, objClass, filterType, filterValue, dateField):
        errorCount = 0
        checkCount = 0
        resets = 0
        deleteRecords = self.deleteRecordsBase

        totalObjects = objClass.objects.filter(**{ '%s' % filterType: filterValue, '%s__lte' % dateField: self.timeDeltaObj, })\
                                                .values_list("id", flat=True)
        LOG.info("Looping through %s objects. %s objects to be deleted." % (objClass.__name__, totalObjects.count()))
        while totalObjects.count():
            if deleteRecords < 30 and resets < self.resetMax:
                checkCount += 1
            if checkCount == self.resetCount:
                deleteRecords = self.deleteRecordsBase
                resets += 1
                checkCount = 0
            LOG.info("%s objects left: %s" % (objClass.__name__, totalObjects.count()))
            deleteObjects = objClass.objects.filter(**{ '%s' % filterType: filterValue, '%s__lte' % dateField: self.timeDeltaObj, })\
                                                    .values_list("id", flat=True)[:deleteRecords]
            try:
                objClass.objects.filter(pk__in=list(deleteObjects)).delete()
                errorCount = 0
            except DatabaseError, e:
                LOG.info("Non Fatal Exception: %s: %s" % (e.__class__.__name__, e))
                errorCount += 1
                if errorCount > 9 and deleteRecords == 1:
                    raise
                if deleteRecords > 100:
                    deleteRecords = max(deleteRecords - 100, 1)
                else:
                    deleteRecords = max(deleteRecords - 10, 1)
                LOG.info("Decreasing max delete records to: %s" % deleteRecords)
            totalObjects = objClass.objects.filter(**{'%s' % filterType: filterValue, '%s__lte' % dateField: self.timeDeltaObj, })\
                                                    .values_list("id", flat=True)


    def handle(self, *args, **options):


        self.keepDays = options['keep_days']
        self.timeDeltaObj = date.today() - timedelta(days=self.keepDays)
        self.resetCount = 15
        self.resetMax = 5
        self.deleteRecordsBase = 999  #number of documents to delete in a batch
                                      #to avoid Non Fatal Exception: DatabaseError: too many SQL variables

        LOG.warn("HUE_CONF_DIR: %s" % os.environ['HUE_CONF_DIR'])
        LOG.info("DB Engine: %s" % desktop.conf.DATABASE.ENGINE.get())
        LOG.info("DB Name: %s" % desktop.conf.DATABASE.NAME.get())
        LOG.info("DB User: %s" % desktop.conf.DATABASE.USER.get())
        LOG.info("DB Host: %s" % desktop.conf.DATABASE.HOST.get())
        LOG.info("DB Port: %s" % str(desktop.conf.DATABASE.PORT.get()))
        LOG.info("Cleaning up anything in the Hue tables django_session, oozie*, desktop* and beeswax* older than %s old" % self.keepDays)

        start = time.time()

        #Clean out Hive / Impala Query History
        self.objectCleanup(SavedQuery, 'is_auto', True, 'mtime')

        #Clear out old Hive/Impala sessions
        self.objectCleanup(Session, 'status_code__gte', -10000, 'last_used')

        #Clean out Trashed Workflows
        self.objectCleanup(Workflow, 'is_trashed', True, 'last_modified')

        #Clean out Workflows without a name
        self.objectCleanup(Workflow, 'name', '', 'last_modified')

        #Clean out history Doc2 objects
        self.objectCleanup(Document2, 'is_history', True, 'last_modified')

        #Clean out expired sessions
        LOG.debug("Cleaning out expired sessions from django_session table")

        engine = import_module(settings.SESSION_ENGINE)
        try:
            engine.SessionStore.clear_expired()
        except NotImplementedError:
            LOG.error("Session engine '%s' doesn't support clearing "
                            "expired sessions.\n" % settings.SESSION_ENGINE)


        end = time.time()
        elapsed = (end - start)
        LOG.debug("Total time elapsed (seconds): %.2f" % elapsed)


