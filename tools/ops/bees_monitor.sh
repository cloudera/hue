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

API_URL='localhost:7180'
CLUSTER='Cluster 1 - CDH4'
EMAIL_TO='root'

curl -u admin "http://$API_URL/api/v2/clusters/$CLUSTER/services" > new_status
diff new_status old_status > last_change
if [ $? -ne 0 ]
then
cat last_change new_status | mail -s "Status of $CLUSTER has Changed" $EMAIL_TO
fi

mv new_status old_status
