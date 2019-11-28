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

HUE_SERVER="cdh46-1"
HUE_PORT="8888"
HUE_PASS_URL="${HUE_SERVER}:${HUE_PORT}/accounts/login/"
HUE_CREATE_URL="${HUE_SERVER}:${HUE_PORT}/jobsub/designs/hive/new"
admin_user="cconner"
admin_pass="password"


curl -i -c ${admin_user}_cookie.txt -d "username=${admin_user}&password=${admin_pass}" "${HUE_PASS_URL}" > /dev/null


while read -r LINE
do

   ACTION=`echo ${LINE} | awk '{print $1}'`
   URL=`echo ${LINE} | awk '{print $2}'`
   HUE_CREATE_URL="http://${HUE_SERVER}:${HUE_PORT}/${URL}"
   echo ${ACTION}
   echo ${HUE_CREATE_URL}

   curl -X ${ACTION} --dump-header ${admin_user}_headers.txt -i -b ${admin_user}_cookie.txt "${HUE_CREATE_URL}" > /dev/null
   
   sleep 1

done < <(cat hbase.txt)
