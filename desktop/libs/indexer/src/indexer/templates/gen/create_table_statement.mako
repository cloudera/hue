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

<%!
def col_type(col):
  if col["type"] == "array":
    return "array <%s>" % col_type(col["nested"][0])
  if col["type"] == "struct":
    return "struct <%s>" % ', '.join(struct_column_list({}, col["nested"]))
  elif col["type"] == "map":
    return "map <%s, %s>" % (col["nested"][0]["keyType"], '%s' % col_type(col["nested"][0]) if col["type"] in ('array', 'struct', 'map') else col["type"])
  elif col["type"] == "char":
    return "char(%s)" % col["length"]
  elif col["type"] == "varchar":
    return "varchar(%s)" % col["length"]
  elif col["type"] == "decimal":
    return "decimal(%s, %s)" % (col["precision"], col["scale"])
  return col["type"]

%>

<%!
def struct_column_list(table, columns):
  col_sql = []
  for col in columns:
    comment = ' COMMENT "%(comment)s"' % col if col.get("comment") else ''
    col_sql.append('`%s`:%s%s' % (col["name"], col_type(col), comment))

  return col_sql
%>

<%def name="column_list(table, columns)">\
(
<% first = True %>\
% for col in columns:
%   if first:
<% first = False %>\
%   else:
,
%   endif
  `${ col["name"] | n }` ${ col_type(col) | n } \
%   if col.get("comment"):
COMMENT "${col["comment"]|n}" \
%   endif
% endfor
% if table.get('primary_keys'):
, PRIMARY KEY (${ ', '.join(table['primary_keys']) })
% endif
)\
</%def>\

<%def name="kudu_partition(partition)">
% if partition['name'] == 'HASH':
  HASH (${ ', '.join(partition['columns']) }) PARTITIONS ${ partition['int_val'] }
% elif partition['name'] == 'RANGE BY':
  RANGE BY (${ ', '.join(partition['columns']) }) (${ ', '.join([kudu_range_partition(range_partition) for range_partition in partition['range_partitions']]) })
% endif
</%def>

<%def name="kudu_range_partition(partition)">
PARTITION \
% if partition['name'] == 'VALUES':
  ${ partition['lower_val'] } <${ '=' if include_upper_val else '' } VALUES ${ '=' if include_upper_val else '' } ${ partition['upper_val'] }
% elif partition['name'] == 'VALUE':
  VALUE (${ ', '.join(partition['values']) })
% endif
</%def>


CREATE \
% if table.get("external", False):
EXTERNAL \
% endif
TABLE ${ '`%s`.`%s`' % (database, table["name"]) | n }
${ column_list(table, columns) | n } \
% if kudu_partition_columns  and table.get('file_format') == 'kudu':
PARTITION BY ${ ', '.join([kudu_partition(partition) for partition in kudu_partition_columns]) | n }
% endif
% if table["comment"]:
COMMENT "${table["comment"] | n }"
% endif
% if partition_columns and table.get('file_format') != 'kudu':
PARTITIONED BY ${ column_list(table, partition_columns) | n }
% endif
## TODO: CLUSTERED BY here
## TODO: SORTED BY...INTO...BUCKETS here
% if table.get('row_format'):
ROW FORMAT \
%   if table["row_format"] == "Delimited":
  DELIMITED
%     if table.has_key('field_terminator'):
    FIELDS TERMINATED BY '${table["field_terminator"] | n}'
%     endif
## [LINES TERMINATED BY char]
%     if table.get('collection_terminator') is not None:
    COLLECTION ITEMS TERMINATED BY '${table["collection_terminator"] | n}'
%     endif
%     if table.get('map_key_terminator') is not None:
    MAP KEYS TERMINATED BY '${table["map_key_terminator"] | n}'
%     endif
%   else:
  SERDE '${table["serde_name"] | n}'
%     if table["serde_properties"]:
  WITH SERDEPROPERTIES (${table["serde_properties"] | n})
%     endif
%   endif
% endif
% if table.has_key('file_format'):
  STORED AS ${ table["file_format"] | n } \
% endif
% if table.get("file_format") == "InputFormat":
INPUTFORMAT ${table["input_format_class"] | n} OUTPUTFORMAT ${table["output_format_class"] | n}
% endif
% if table.get("external", False):
LOCATION '${table["path"] | n}'
% endif
% if table.get("skip_header", False):
TBLPROPERTIES("skip.header.line.count" = "1")
% endif
;