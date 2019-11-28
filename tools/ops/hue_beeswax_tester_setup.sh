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

#NOTE: This script requires curl to be installed.  Also, it does not have to run on the Hue server, it can run anywhere that curl is installed.  As long as that host can reach the Hue server.

#Please enter the Hue server name below
HUE_SERVER="cdh412-1"

#Please enter the Hue server port below
HUE_PORT="8888"

HUE_PASS_URL="${HUE_SERVER}:${HUE_PORT}/accounts/login/"
HUE_USER_URL="${HUE_SERVER}:${HUE_PORT}/useradmin/users/new"


echo "curl -i -c /tmp/admin_cookie.txt -d \"username=admin&password=admin\" \"${HUE_PASS_URL}\""
curl -i -c /tmp/admin_cookie.txt -d "username=admin&password=admin" "${HUE_PASS_URL}" > /dev/null

for x in {1..100}
do

   user="test$x"
   echo "running Command:"
   echo "curl --data \"username=${user}&is_active=on&first_name=${user}&last_name=${user}&email=&ensure_home_directory=on&groups=1&password1=password&password2=password\" --dump-header /tmp/${user}_headers.txt -i -b /tmp/admin_cookie.txt \"${HUE_USER_URL}\""
   curl --data "username=${user}&is_active=on&first_name=${user}&last_name=${user}&email=&ensure_home_directory=on&groups=1&password1=password&password2=password" --dump-header /tmp/${user}_headers.txt -i -b /tmp/admin_cookie.txt "${HUE_USER_URL}"
   sudo useradd ${user}

done

