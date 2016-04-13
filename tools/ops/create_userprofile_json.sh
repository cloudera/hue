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

export HUE_BIN=/opt/cloudera/parcels/CDH/share/hue/build/env/bin/hue
export JSON_FILE=/tmp/authuser.json
export TXT_FILE=/tmp/authuser.txt
export METHOD="EXTERNAL"

NEW="false"
echo "["
while read -r LINE
do

   if [[ ${LINE} =~ '--' ]]
   then
     NEW="true"
     echo "  {"
     echo "    \"pk\": $ID,"
     echo "    \"model\": \"useradmin.userprofile\","
     echo "    \"fields\": {"
     echo "      \"creation_method\": \"${METHOD}\","
     echo "      \"user\": $ID,"
     echo "      \"home_directory\": \"/user/$USERNAME\""
       echo "  },"
   fi
   if [[ ${NEW} =~ "false" ]]
   then
     if [[ ${LINE} =~ "pk" ]]
     then
       ID=`echo ${LINE} | awk -F: '{print $2}' | awk -F, '{print $1}' | awk '{print $1}'`
     fi 
     if [[ ${LINE} =~ "username" ]]
     then 
       USERNAME=`echo ${LINE} | awk -F: '{print $2}' | awk -F, '{print $1}' | awk -F\" '{print $2}'`
     fi
   fi
   NEW="false"

done < <(cat ${TXT_FILE})


echo "  {"
echo "    \"pk\": $ID,"
echo "    \"model\": \"useradmin.userprofile\","
echo "    \"fields\": {"
echo "      \"creation_method\": \"${METHOD}\","
echo "      \"user\": $ID,"
echo "      \"home_directory\": \"/user/$USERNAME\""
echo "   }"
echo "]"
