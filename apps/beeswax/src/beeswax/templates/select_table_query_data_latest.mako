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
select hiveQueryId, collect_list(`timestamp`) event_time, max(executionmode) as executionmode, max(requestUser) as requestUser, max(queue) as queue, max(otherInfo['QUERY']) as query, max(otherInfo['PERF']) as perf, max(`date`) as `date`, collect_list(eventType) as eventType
% if table["force_refresh"]:
, current_date()
% endif
from sys.${table["name"]}
% if table["request_user"] or table["query_id"] or table["start_date"] or table["start_time"]:
where
  % if table["request_user"]:
  requestUser = "${table["request_user"]}"
  % endif
  % if table["query_id"]:
    % if table["request_user"]:
      and
    % endif
    hiveQueryId = "${table["query_id"]}"
  % endif
  % if table["start_date"]:
    % if table["request_user"] or table["query_id"]:
      and
    % endif
    `date` >= "${table["start_date"]}"
  % endif
  % if table["start_time"]:
    % if table["request_user"] or table["query_id"] or table["start_date"]:
      and
    % endif
    `timestamp` >= ${table["start_time"]}
  % endif
% endif
group by hivequeryId
% if table["status"] == "completed":
having count(`timestamp`) >= 2
% endif
% if table["status"] == "running":
having count(`timestamp`) = 1
% endif
order by event_time[0] desc
% if table["limit"]:
limit ${table["limit"]}
% endif
;