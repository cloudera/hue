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

# NOTE: This script requires curl to be installed.  Also, it does not have to run on the Hue server, it can run anywhere that curl is installed.  As long as that host can reach the Hue server.

# Please change USERS to contain a list of users that you would like to use to generate load
USERS="cconner test1 test2 test3 test4 test5 test6 test7 test8 test9 test10"

#Please enter the Hue server name below
HUE_SERVER="cdh412-1"

#Please enter the Hue server port below
HUE_PORT="8888"

#Please enter the base name of each file.  They will be called ${HUE_FILE_BASE}${count}.txt.  So hue_file_test_ = hue_file_test_1.txt ....  NOTE: this must match HUE_FILE_BASE in hue_file_tester_setup.sh
HUE_FILE_BASE="hue_file_test_"

#Plase enter the directory in HDFS where the above files were stored.  NOTE: this must match HDFS_LOCATION in hue_file_tester_setup.sh
HDFS_LOCATION="/tmp/hue_file_test"

#Please enter the number of files that were created in $HDFS_LOCATION.  NOTE: this must match or be less than the value of FILE_COUNT in hue_file_tester_setup.sh
FILE_COUNT=10

#Please create an entry below for every user that you added to USERS above.  After the = replace "password" with the correct password for each user.  If you have more or less than the number of entries below, add or delete rows as necessary.
declare -A password_hash
password_hash[cconner]="password"
password_hash[test1]="password"
password_hash[test2]="password"
password_hash[test3]="password"
password_hash[test4]="password"
password_hash[test5]="password"
password_hash[test6]="password"
password_hash[test7]="password"
password_hash[test8]="password"
password_hash[test9]="password"
password_hash[test10]="password"


HUE_PASS_URL="${HUE_SERVER}:${HUE_PORT}/accounts/login/"
HUE_FILE_URL="${HUE_SERVER}:${HUE_PORT}/filebrowser/view${HDFS_LOCATION}"

for user in $USERS
do
    echo "Running Command:"
    echo "curl -i -c /tmp/${user}_cookie.txt -d \"username=${user}&password=${password_hash[${user}]}\" \"${HUE_PASS_URL}\""
    curl -i -c /tmp/${user}_cookie.txt -d "username=${user}&password=${password_hash[${user}]}" "${HUE_PASS_URL}"
done

while [ 1 ]
do
   for user in $USERS
   do
      rand_data=$((RANDOM%${FILE_COUNT}+1))
      rand_sleep=$((RANDOM%10+1))
      rand_offset=$((RANDOM%32000+1))
      hue_file="${HUE_FILE_BASE}${rand_data}.txt"
      echo "Running Command:"
      echo "curl -i -b /tmp/${user}_cookie.txt \"$HUE_FILE_URL/${hue_file}?offset=${rand_offset}&length=4096&compression=none&mode=text\" > /dev/null"
      curl -i -b /tmp/${user}_cookie.txt "$HUE_FILE_URL/${hue_file}?offset=${rand_offset}&length=4096&compression=none&mode=text" > /dev/null
      sleep ${rand_sleep}
    done
done
