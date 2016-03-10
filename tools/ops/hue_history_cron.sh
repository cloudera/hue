#!/bin/bash
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

#Cleans up old oozie workflow and beeswax savedqueries to
#prevent the DB from getting too large.
PARCEL_DIR=/opt/cloudera/parcels/CDH
LOG_FILE=/var/log/hue/`basename "$0" | awk -F\. '{print $1}'`.log
LOG_ROTATE_SIZE=10 #MB before rotating, size in MB before rotating log to .1
LOG_ROTATE_COUNT=2 #number of log files, so 20MB max
DATE=`date '+%Y%m%d-%H%M'`
KEEP_DAYS=7    #Number of days of beeswax and oozie history to keep

if [ ! -d "/usr/lib/hadoop" ]
then
   CDH_HOME=$PARCEL_DIR
else
   CDH_HOME=/usr
fi

if [ -d "/var/run/cloudera-scm-agent/process" ]
then
   HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/`ls -1 /var/run/cloudera-scm-agent/process | grep HUE | sort -n | tail -1 `"
else
   HUE_CONF_DIR="/etc/hue/conf"
fi

if [ -d "${CDH_HOME}/lib/hue/build/env/bin" ]
then
   COMMAND="${CDH_HOME}/lib/hue/build/env/bin/hue shell"
else
   COMMAND="${CDH_HOME}/share/hue/build/env/bin/hue shell"
fi

ORACLE_HOME=/opt/cloudera/parcels/ORACLE_INSTANT_CLIENT/instantclient_11_2/
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${ORACLE_HOME}
export CDH_HOME HUE_CONF_DIR ORACLE_HOME LD_LIBRARY_PATH COMMAND

${COMMAND} >> /dev/null 2>&1 <<EOF
from beeswax.models import SavedQuery
from datetime import date, timedelta
from oozie.models import Workflow
from django.db.utils import DatabaseError
import logging
import logging.handlers
import sys

LOGFILE="${LOG_FILE}"
keepDays = ${KEEP_DAYS}
deleteRecords = 900
errorCount = 0
log = logging.getLogger('')
log.setLevel(logging.INFO)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

fh = logging.handlers.RotatingFileHandler(LOGFILE, maxBytes=(1048576*${LOG_ROTATE_SIZE}), backupCount=${LOG_ROTATE_COUNT})
fh.setFormatter(format)
log.addHandler(fh)

log.info('HUE_CONF_DIR: ${HUE_CONF_DIR}')
log.info("Cleaning up anything in the Hue tables oozie*, desktop* and beeswax* older than ${KEEP_DAYS} old")

savedQuerys = SavedQuery.objects.filter(is_auto=True, mtime__lte=date.today() - timedelta(days=keepDays))
totalQuerys = savedQuerys.count()
loopCount = totalQuerys
deleteCount = deleteRecords
log.info("SavedQuerys left: %s" % totalQuerys)
log.info("Looping through querys")
while loopCount > 0:
   if loopCount < deleteCount:
      deleteCount = loopCount
   excludeCount = loopCount - deleteCount
   savedQuerys = SavedQuery.objects.filter(is_auto=True, mtime__lte=date.today() - timedelta(days=keepDays))[:excludeCount].values_list("id", flat=True)
   try:
      SavedQuery.objects.exclude(pk__in=list(savedQuerys)).delete()
      loopCount -= deleteCount
      errorCount = 0
      deleteCount = deleteRecords
   except DatabaseError, e:
      log.info("Non Fatal Exception: %s: %s" % (e.__class__.__name__, e))
      errorCount += 1
      deleteCount = 1
      if errorCount > 9:
         raise
   log.info("querys left: %s" % loopCount)

workflows = Workflow.objects.filter(is_trashed=True, last_modified__lte=date.today() - timedelta(days=keepDays))
totalWorkflows = workflows.count()
loopCount = 1
maxCount = 1000
log.info("Workflows left: %s" % totalWorkflows)
log.info("Looping through workflows")
for w in workflows:
   w.delete(skip_trash=True)
   loopCount += 1
   if loopCount == maxCount:
      totalWorkflows = totalWorkflows - maxCount
      loopCount = 1
      log.info("Workflows left: %s" % totalWorkflows)

EOF
