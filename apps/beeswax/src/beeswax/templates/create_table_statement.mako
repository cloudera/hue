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
<%!
def col_type(col):
  if col["column_type"] == "array":
    return "array <%s>" % col["array_type"]
  elif col["column_type"] == "map":
    return "map <%s, %s>" % (col["map_key_type"], col["map_value_type"])
  elif col["column_type"] == "char":
    return "char(%d)" % col["char_length"]
  elif col["column_type"] == "varchar":
    return "varchar(%d)" % col["varchar_length"]
  return col["column_type"]
%>\
<%def name="column_list(columns)">\
## Returns (foo int, bar string)-like data for columns
(
<% first = True %>\
% for col in columns:
%   if first:
<% first = False %>\
%   else:
,
%   endif
  `${col["column_name"]|n}` ${col_type(col)|n} \
%   if col.get("comment"):
COMMENT "${col["comment"]|n}" \
%   endif
% endfor
) \
</%def>\
#########################
CREATE \
% if table.get("load_data", "IMPORT") == 'EXTERNAL':
EXTERNAL \
% endif
TABLE `${ '%s.%s' % (database, table["name"]) | n }`
${column_list(columns)|n}
% if table["comment"]:
COMMENT "${table["comment"] | n}"
% endif
% if len(partition_columns) > 0:
PARTITIONED BY ${column_list(partition_columns)|n}
% endif
## TODO: CLUSTERED BY here
## TODO: SORTED BY...INTO...BUCKETS here
ROW FORMAT \
% if table.has_key('row_format'):
%   if table["row_format"] == "Delimited":
  DELIMITED
%     if table.has_key('field_terminator'):
    FIELDS TERMINATED BY '${table["field_terminator"] | n}'
%     endif
%     if table.has_key('collection_terminator'):
    COLLECTION ITEMS TERMINATED BY '${table["collection_terminator"] | n}'
%     endif
%     if table.has_key('map_key_terminator'):
    MAP KEYS TERMINATED BY '${table["map_key_terminator"] | n}'
%     endif
%   else:
  SERDE ${table["serde_name"] | n}
%     if table["serde_properties"]:
  WITH SERDEPROPERTIES ${table["serde_properties"] | n}
%     endif
%   endif
% endif
% if table.has_key('file_format'):
  STORED AS ${table["file_format"] | n} \
% endif
% if table.get("file_format") == "InputFormat":
INPUTFORMAT ${table["input_format_class"] | n} OUTPUTFORMAT ${table["output_format_class"] | n}
% endif
% if table.get("load_data", "IMPORT") == 'EXTERNAL':
LOCATION "${table["path"] | n}"
% endif
% if table.get("skip_header", False):
TBLPROPERTIES("skip.header.line.count" = "1")
% endif