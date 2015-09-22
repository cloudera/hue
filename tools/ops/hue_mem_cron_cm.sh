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

#This script will check CM to see if Hue is using too much memory
#then will restart if necessary.

CM_HOSTNAME="cdh53-1.qa.test.com"
CM_PORT="7180"
CM_USERNAME="admin"
CM_PASSWORD="admin"
KILL_ME=5000  #This is the number of MB at which it will kill.
             #Starting with 5000(5gb)
VERBOSE=true #true then this writes out the proc info each time it runs, leave blank
             #to only write out when we kill the process
LOG_FILE=/var/log/hue/`basename "$0" | awk -F\. '{print $1}'`.log
ROTATE_SIZE=10 #MB before rotating, size in MB before rotating log to .1, we only keep
               #2 log files, so 20MB max
TMP_LOCATION=/tmp/hue_mem_cron

main()
{
DATE=`date '+%Y%m%d-%H%M'`
YEAR=`date '+%Y'`
MONTH=`date '+%m'`
DAY=`date '+%d'`
HOUR=`date '+%H'`
MINUTE=`date '+%M'`
YEAR_PRIOR=`date --date='1 minutes ago' '+%Y'`
MONTH_PRIOR=`date --date='1 minutes ago' '+%m'`
DAY_PRIOR=`date --date='1 minutes ago' '+%d'`
HOUR_PRIOR=`date --date='1 minutes ago' '+%H'`
MINUTE_PRIOR=`date --date='1 minutes ago' '+%M'`
MEM_JSON_FILE=${TMP_LOCATION}/mem.json
MB_BYTES="1048576"

mkdir -p ${TMP_LOCATION}

if [[ -f ${LOG_FILE} ]]
then
   LOG_SIZE=`du -sm ${LOG_FILE} | awk '{print $1}'`
   if [[ ${LOG_SIZE} -gt ${ROTATE_SIZE} ]]
   then
      mv ${LOG_FILE} ${LOG_FILE}.1
   fi
fi

MEM_API_URL="/api/v6/timeseries?query=select+mem_rss+where+roleType+%3D+HUE_SERVER&contentType=application%2Fjson&from=${YEAR_PRIOR}-${MONTH_PRIOR}-${DAY_PRIOR}T${HOUR_PRIOR}%3A${MINUTE_PRIOR}%3A00.000Z&to=${YEAR}-${MONTH}-${DAY}T${HOUR}%3A${MINUTE}%3A00.000Z"
#Get memory usage for all Hue roles:
curl -X GET -u ${CM_USERNAME}:${CM_PASSWORD} -i -o ${MEM_JSON_FILE} "http://${CM_HOSTNAME}:${CM_PORT}${MEM_API_URL}"

while read -r LINE
do
   if  [[ ${LINE} =~ .*clusterName* ]]
   then
      CLUSTERNAME=`echo ${LINE} | awk -F\" '{print $4}'`
   fi
   if  [[ ${LINE} =~ .*serviceName* ]]
   then
      SERVICENAME=`echo ${LINE} | awk -F\" '{print $4}'`
   fi
   if  [[ ${LINE} =~ .*roleName* ]]
   then
      ROLENAME=`echo ${LINE} | awk -F\" '{print $4}'`
   fi
   if  [[ ${LINE} =~ .*value* ]]
   then
      MEM=`echo ${LINE} | awk '{print $3}' | awk -F, '{print $1}'`
      MEM=`printf "%.f" $MEM` # convert from scientific to decimal
      MEM_MB=`expr ${MEM} / ${MB_BYTES}`
      debug "${DATE} - ROLENAME: ${ROLENAME} - MEM: ${MEM} - MEM_MB: ${MEM_MB}" 
      if [ ${MEM_MB} -gt ${KILL_ME} ]
      then
         echo "${DATE} - Restart the Hue Process: Too much memory: ${MEM_MB} : ROLENAME: ${ROLENAME}" >> ${LOG_FILE}
         RESTART_API_URL="/api/v8/clusters/${CLUSTERNAME}/services/${SERVICENAME}/roleCommands/restart"
         curl -X POST -u ${CM_USERNAME}:${CM_PASSWORD} -i -H "content-type:application/json" -d "{\"items\" : [\"${ROLENAME}\"]}" "http://${CM_HOSTNAME}:${CM_PORT}${RESTART_API_URL}"
         exit 0
      fi
   fi
done < <(cat ${MEM_JSON_FILE})
}

debug()
{

  if [[ ! -z $VERBOSE ]]
  then
    echo "$1" >> ${LOG_FILE}
  fi

}

main "$@"
