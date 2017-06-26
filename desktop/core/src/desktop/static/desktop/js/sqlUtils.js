// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.


var SqlUtils = (function () {

  var hiveReservedKeywords = {
    ALL: true, ALTER: true, AND: true, ARRAY: true, AS: true, AUTHORIZATION: true, BETWEEN: true, BIGINT: true, BINARY: true, BOOLEAN: true, BOTH: true, BY: true, CASE: true, CAST: true,
    CHAR: true, COLUMN: true, CONF: true, CREATE: true, CROSS: true, CUBE: true, CURRENT: true, CURRENT_DATE: true, CURRENT_TIMESTAMP: true, CURSOR: true,
    DATABASE: true, DATE: true, DECIMAL: true, DELETE: true, DESCRIBE: true, DISTINCT: true, DOUBLE: true, DROP: true, ELSE: true, END: true, EXCHANGE: true, EXISTS: true,
    EXTENDED: true, EXTERNAL: true, FALSE: true, FETCH: true, FLOAT: true, FOLLOWING: true, FOR: true, FROM: true, FULL: true, FUNCTION: true, GRANT: true, GROUP: true,
    GROUPING: true, HAVING: true, IF: true, IMPORT: true, IN: true, INNER: true, INSERT: true, INT: true, INTERSECT: true, INTERVAL: true, INTO: true, IS: true, JOIN: true, LATERAL: true,
    LEFT: true, LESS: true, LIKE: true, LOCAL: true, MACRO: true, MAP: true, MORE: true, NONE: true, NOT: true, NULL: true, OF: true, ON: true, OR: true, ORDER: true, OUT: true, OUTER: true, OVER: true,
    PARTIALSCAN: true, PARTITION: true, PERCENT: true, PRECEDING: true, PRESERVE: true, PROCEDURE: true, RANGE: true, READS: true, REDUCE: true,
    REGEXP: true, REVOKE: true, RIGHT: true, RLIKE: true, ROLLUP: true, ROW: true, ROWS: true,
    SELECT: true, SET: true, SMALLINT: true, TABLE: true, TABLESAMPLE: true, THEN: true, TIMESTAMP: true, TO: true, TRANSFORM: true, TRIGGER: true, TRUE: true,
    TRUNCATE: true, UNBOUNDED: true, UNION: true, UNIQUEJOIN: true, UPDATE: true, USER: true, USING: true, VALUES: true, VARCHAR: true, WHEN: true, WHERE: true,
    WINDOW: true, WITH: true
  };

  var extraHiveReservedKeywords = {
    ASC: true, CLUSTER: true, DESC: true, DISTRIBUTE: true, FORMATTED: true, FUNCTION: true, INDEX: true, INDEXES: true, LIMIT: true, LOCK: true, SCHEMA: true, SORT: true
  };

  var impalaReservedKeywords = {
    ADD: true, AGGREGATE: true, ALL: true, ALTER: true, AND: true, API_VERSION: true, AS: true, ASC: true, AVRO: true, BETWEEN: true, BIGINT: true, BINARY: true, BOOLEAN: true, BY: true, CACHED: true, CASE: true, CAST: true, CHANGE: true, CHAR: true, CLASS: true, CLOSE_FN: true,
    COLUMN: true, COLUMNS: true, COMMENT: true, COMPUTE: true, CREATE: true, CROSS: true, DATA: true, DATABASE: true, DATABASES: true, DATE: true, DATETIME: true, DECIMAL: true, DELIMITED: true, DESC: true, DESCRIBE: true, DISTINCT: true, DIV: true, DOUBLE: true, DROP: true, ELSE: true, END: true,
    ESCAPED: true, EXISTS: true, EXPLAIN: true, EXTERNAL: true, FALSE: true, FIELDS: true, FILEFORMAT: true, FINALIZE_FN: true, FIRST: true, FLOAT: true, FORMAT: true, FORMATTED: true, FROM: true, FULL: true, FUNCTION: true, FUNCTIONS: true, GROUP: true, HAVING: true, IF: true, IN: true, INCREMENTAL: true,
    INIT_FN: true, INNER: true, INPATH: true, INSERT: true, INT: true, INTEGER: true, INTERMEDIATE: true, INTERVAL: true, INTO: true, INVALIDATE: true, IS: true, JOIN: true, KEY: true, KUDU: true, LAST: true, LEFT: true, LIKE: true, LIMIT: true, LINES: true, LOAD: true, LOCATION: true, MERGE_FN: true, METADATA: true,
    NOT: true, NULL: true, NULLS: true, OFFSET: true, ON: true, OR: true, ORDER: true, OUTER: true, OVERWRITE: true, PARQUET: true, PARQUETFILE: true, PARTITION: true, PARTITIONED: true, PARTITIONS: true, PREPARE_FN: true, PRIMARY: true, PRODUCED: true, RCFILE: true, REAL: true, REFRESH: true, REGEXP: true, RENAME: true,
    REPLACE: true, RETURNS: true, RIGHT: true, RLIKE: true, ROW: true, SCHEMA: true, SCHEMAS: true, SELECT: true, SEMI: true, SEQUENCEFILE: true, SERDEPROPERTIES: true, SERIALIZE_FN: true, SET: true, SHOW: true, SMALLINT: true, STATS: true, STORED: true, STRAIGHT_JOIN: true, STRING: true, SYMBOL: true, TABLE: true,
    TABLES: true, TBLPROPERTIES: true, TERMINATED: true, TEXTFILE: true, THEN: true, TIMESTAMP: true, TINYINT: true, TO: true, TRUE: true, UNCACHED: true, UNION: true, UPDATE_FN: true, USE: true, USING: true, VALUES: true, VIEW: true, WHEN: true, WHERE: true, WITH: true
  };

  return {
    backTickIfNeeded: function (sourceType, identifier) {
      if (identifier.indexOf('`') === 0) {
        return identifier;
      }
      var upperIdentifier = identifier.toUpperCase();
      if (sourceType === 'hive' && (hiveReservedKeywords[upperIdentifier] || extraHiveReservedKeywords[upperIdentifier])) {
        return '`' + identifier + '`';
      }
      if (sourceType === 'impala' && impalaReservedKeywords[upperIdentifier]) {
        return '`' + identifier + '`';
      }
      if ((sourceType !== 'impala' && sourceType !== 'hive') && (impalaReservedKeywords[upperIdentifier] || hiveReservedKeywords[upperIdentifier] || extraHiveReservedKeywords[upperIdentifier])) {
        return '`' + identifier + '`';
      }
      if (!/^[A-Za-z][A-Za-z0-9_]*$/.test(identifier)) {
        return '`' + identifier + '`';
      }
      return identifier;
    }
  }

})();