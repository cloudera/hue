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

## TODO(philip): Check escaping more carefully?
## TODO(philip): The whitespace management here is mediocre.
##
## |n is used throughout here, since this is not going to HTML.
##
## Reference: http://wiki.apache.org/hadoop/Hive/LanguageManual/DDL#Create_Table
CREATE DATABASE ${database["name"]} \
% if database["comment"]:
COMMENT "${database["comment"] | n}"
% endif
% if not database.get("use_default_location", True):
LOCATION "${database["external_location"] | n}"
% endif
% if database.get("properties", False):
WITH DBPROPERTIES (\
${ ','.join('%s=%s' % (prop["name"], prop["value"]) for prop in database["properties"]) }\
)
% endif