#!/bin/sh
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

URL=http://localhost:8983/solr

for c in "log_analytics_demo" "twitter_demo" "yelp_demo" "jobs_demo"; do
  u="$URL/$c/update"
  echo Posting file $c to $u
  FILE=../collections/solr_configs_$c/index_data.csv
  curl $u --data-binary @$FILE -H 'Content-type:text/csv'
  echo
done

curl "$URL?softCommit=true"
echo
