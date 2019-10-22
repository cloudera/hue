## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
SELECT
  hiveQueryId,
  `timestamp`,
  executionMode,
  requestUser,
  queue,
  otherInfo["QUERY"],
  otherInfo["PERF"],
  `date`,
  eventType
  FROM sys.${table["name"]}
% if table["start_date"] or table["start_time"] or table["request_user"] or table["query_id"]:
WHERE
  % if table["request_user"]:
  requestUser = "${table["request_user"]}"
  % endif
  % if table["start_date"]:
    % if table["request_user"]:
    and
    % endif
  `date` >= "${table["start_date"]}"
  % endif
  % if table["start_time"]:
    % if table["request_user"] or table["start_date"]:
    and
    % endif
  `timestamp` >= ${table["start_time"]}
  % endif
  % if table["query_id"]:
    % if table["request_user"] or table["start_date"] or table["start_date"]:
    and
    % endif
  `hiveQueryId` = "${table["query_id"]}"
  % endif
% endif
% if table["limit"]:
LIMIT ${table["limit"]}
% endif
;