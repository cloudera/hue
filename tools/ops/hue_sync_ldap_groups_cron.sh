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

#Cron script to sync ldap groups via cron
PARCEL_DIR=/opt/cloudera/parcels/CDH
DATE=`date '+%Y%m%d-%H%M'`
LOG_FILE=/var/log/hue/`basename "$0" | awk -F\. '{print $1}'`.log
LOG_ROTATE_SIZE=10 #MB before rotating, size in MB before rotating log to .1
LOG_ROTATE_COUNT=2 #number of log files, so 20MB max

if [[ ! ${USER} =~ .*root* ]]
then
   echo "Script must be run as root: exiting"
   exit 1
fi

if [[ -f ${LOG_FILE} ]]
then
   LOG_SIZE=`du -sm ${LOG_FILE} | awk '{print $1}'`
   if [[ ${LOG_SIZE} -gt ${ROTATE_SIZE} ]]
   then
      mv ${LOG_FILE} ${LOG_FILE}.1
   fi
fi

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
   COMMAND="${CDH_HOME}/lib/hue/build/env/bin/hue sync_ldap_users_and_groups"
else
   COMMAND="${CDH_HOME}/share/hue/build/env/bin/hue sync_ldap_users_and_groups"
fi

export CDH_HOME HUE_CONF_DIR COMMAND

echo "${DATE} - Syncing Ldap Groups" >> ${LOG_FILE}
echo "${DATE} - HUE_CONF_DIR: ${HUE_CONF_DIR}" >> ${LOG_FILE}
cd /tmp
${COMMAND} >> ${LOG_FILE}
