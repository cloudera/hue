#!/bin/bash
#
#Cleans up old oozie workflow and beeswax savedqueries to
#prevent the DB from getting too large.
PARCEL_DIR=/opt/cloudera/parcels/CDH
LOG_FILE=/var/log/hue_history_cron.log
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

export CDH_HOME HUE_CONF_DIR COMMAND

${COMMAND} <<EOF
from beeswax.models import SavedQuery
from datetime import date, timedelta
from oozie.models import Workflow
import logging
import logging.handlers
import sys

LOGFILE="${LOG_FILE}"
keepDays = ${KEEP_DAYS}
log = logging.getLogger('')
log.setLevel(logging.INFO)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

fh = logging.handlers.RotatingFileHandler(LOGFILE, maxBytes=(1048576*${LOG_ROTATE_SIZE}), backupCount=${LOG_ROTATE_COUNT})
fh.setFormatter(format)
log.addHandler(fh)

log.info('HUE_CONF_DIR: ${HUE_CONF_DIR}')
log.info("Cleaning up anything in the Hue tables oozie*, desktop* and beeswax* older than ${KEEP_DAYS} old")

savedQuerys = SavedQuery.objects.filter(is_auto=True, mtime__lte=date.today() - timedelta(days=keepDays))
count = len(savedQuerys)
log.info("SavedQuery count is: %s" % count)
savedQuerys.delete()
savedQuerys = SavedQuery.objects.filter(is_auto=True, mtime__lte=date.today() - timedelta(days=keepDays))
count = len(savedQuerys)
log.info("SavedQuery new count is: %s" % count)

totalWorkflows = len(Workflow.objects.filter(is_trashed=True, last_modified__lte=date.today() - timedelta(days=keepDays)))
loopCount = 1
maxCount = 1000
log.info("workflows left: %s" % totalWorkflows)
log.info("Looping through workflows")
for w in Workflow.objects.filter(is_trashed=True, last_modified__lte=date.today() - timedelta(days=keepDays)):
   w.delete(skip_trash=True)
   loopCount += 1
   if (loopCount == maxCount):
      totalWorkflows = totalWorkflows - maxCount
      loopCount = 1
      log.info("workflows left: %s" % totalWorkflows)

EOF
