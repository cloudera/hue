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

define(function (require, exports, module) {
  "use strict";

  var oop = require("../lib/oop");
  var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;

  var HiveHighlightRules = function () {
    // regexp must not have capturing parentheses. Use (?:) instead.
    // regexps are ordered -> the first match is used

    var keywords =
      'ABORT|ADD|ADMIN|AFTER|ALL|ALTER|ANALYZE|AND|ARCHIVE|AS|ASC|AST|AUTHORIZATION|BETWEEN|BUCKET|BUCKETS|BY|' +
      'CACHE|CASCADE|CASE|CBO|CHANGE|CHECK|CLUSTER|CLUSTERED|COLLECTION|COLUMN|COLUMNS|COMMENT|COMPACT|COMPACTIONS|' +
      'COMPUTE|CONCATENATE|CONF|CONNECTOR|CONNECTORS|CONSTRAINT|COST|CREATE|CROSS|CUBE|CURRENT|DATA|DATABASE|' +
      'DATABASES|DBPROPERTIES|DCPROPERTIES|DEFAULT|DEFERRED|DEFINED|DELETE|DEPENDENCY|DESC|DESCRIBE|DETAIL|DIRECTORY|' +
      'DISABLE|DISTINCT|DISTRIBUTE|DISTRIBUTED|DIV|DROP|ELSE|ENABLE|END|ESCAPED|EXCHANGE|EXISTS|EXPLAIN|EXPORT|' +
      'EXPRESSION|EXTENDED|EXTERNAL|FIELDS|FILE|FILEFORMAT|FIRST|FOLLOWING|FOR|FOREIGN|FORMAT|FORMATTED|FROM|FULL|' +
      'FUNCTION|FUNCTIONS|GRANT|GROUP|GROUPING|HAVING|IDXPROPERTIES|IF|IMPORT|IN|INDEX|INDEXES|INNER|INPATH|' +
      'INPUTFORMAT|INSERT|INTO|IS|ITEMS|JAR|JOIN|JOINCOST|KEY|KEYS|LAST|LATERAL|LEFT|LIKE|LIMIT|LINES|LITERAL|LOAD|' +
      'LOCAL|LOCATION|LOCK|LOCKS|MACRO|MATCHED|MATERIALIZED|MERGE|METADATA|MSCK|NO_DROP|NONE|NORELY|NOSCAN|NOT|' +
      'NOVALIDATE|NULLS|OF|OFFLINE|ON|ONLY|OPERATOR|OPTION|OR|ORDER|OUT|OUTER|OUTPUTFORMAT|OVER|OVERWRITE|OWNER|' +
      'PARTITION|PARTITIONED|PARTITIONS|PERCENT|PRECEDING|PRIMARY|PRIVILEGES|PURGE|QUARTER|RANGE|REBUILD|RECOVER|' +
      'REFERENCES|REGEXP|RELOAD|RELY|REMOTE|RENAME|REPAIR|REPLACE|REPLICATION|RESTRICT|REVOKE|REWRITE|RIGHT|RLIKE|' +
      'ROLE|ROLES|ROLLUP|ROW|ROWS|SCHEMA|SCHEMAS|SELECT|SEMI|SERDEPROPERTIES|SET|SETS|SHOW|SHOW_DATABASE|SKEWED|SORT|' +
      'SORTED|SPEC|STATISTICS|STORED|SUMMARY|SYNC|TABLE|TABLES|TABLESAMPLE|TBLPROPERTIES|TEMPORARY|TERMINATED|THEN|' +
      'TO|TOUCH|TRANSACTIONAL|TRANSACTIONS|TRUNCATE|TYPE|UNARCHIVE|UNBOUNDED|UNION|UNIQUE|UPDATE|URL|USE|USER|USING|' +
      'VALUES|VECTORIZATION|VIEW|VIEWS|WAIT|WHEN|WHERE|WINDOW|WITH';

    var builtinConstants =
      'AVRO|DELIMITED|FALSE|ICEBERG|JSONFILE|NULL|ORC|PARQUET|RCFILE|SEQUENCEFILE|SERDE|TEXTFILE|TRUE';

    var builtinFunctions =
      'ABS|ACOS|ADD_MONTHS|AES_DECRYPT|AES_ENCRYPT|ARRAY|ARRAY_CONTAINS|ASCII|ASIN|ATAN|AVG|BASE64|BIN|BINARY|' +
      'BROUND|CAST|CBRT|CEIL|CEILING|COALESCE|COLLECT_LIST|COLLECT_SET|CONCAT|CONCAT_WS|CONTEXT_NGRAMS|CONV|CORR|' +
      'COS|COVAR_POP|COVAR_SAMP|COUNT|CRC32|CREATE_UNION|CUME_DIST|CURRENT_DATABASE|CURRENT_DATE|' +
      'CURRENT_TIMESTAMP|CURRENT_USER|DATE_ADD|DATE_FORMAT|DATE_SUB|DATEDIFF|DAY|DAYOFMONTH|DAYOFWEEK|DECODE|' +
      'DEGREES|DENSE_RANK|E|ENCODE|EXP|EXPLODE|FACTORIAL|FIND_IN_SET|FIRST_VALUE|FLOOR|FORMAT_NUMBER|FROM_UNIXTIME|' +
      'FROM_UTC_TIMESTAMP|GET_JSON_OBJECT|GREATEST|HASH|HEX|HISTOGRAM_NUMERIC|HOUR|IF|IN_FILE|INLINE|INSTR|INITCAP|' +
      'ISNOTNULL|ISNULL|JAVA_METHOD|JSON_TUPLE|LAG|LAST_DAY|LAST_VALUE|LEAD|LEAST|LENGTH|LEVENSHTEIN|LCASE|LN|' +
      'LOCATE|LOG|LOG10|LOG2|LOWER|LPAD|LTRIM|MAP|MAP_KEYS|MAP_VALUES|MAX|MD5|MIN|MINUTE|MONTH|MONTHS_BETWEEN|' +
      'NAMED_STRUCT|NEGATIVE|NEXT_DAY|NGRAMS|NTILE|NVL|PARSE_URL|PARSE_URL_TUPLE|PERCENT_RANK|PERCENTILE|' +
      'PERCENTILE_APPROX|PI|PMOD|POSEXPLODE|POSITIVE|POW|POWER|PRINTF|QUARTER|RADIANS|RAND|RANK|REFLECT|' +
      'REGEXP_EXTRACT|REGEXP_REPLACE|REPEAT|REVERSE|ROUND|ROW_NUMBER|RPAD|RTRIM|SECOND|SHA|SHA1|SHA2|SHIFTLEFT|' +
      'SHIFTRIGHT|SHIFTRIGHTUNSIGNED|SIGN|SIN|SIZE|SORT_ARRAY|SQRT|STACK|STDDEV_POP|STDDEV_SAMP|STRUCT|SENTENCES|' +
      'SOUNDEX|SPACE|SPLIT|STR_TO_MAP|SUBSTR|SUBSTRING|SUBSTRING_INDEX|SUM|TAN|TO_DATE|TO_UTC_TIMESTAMP|TRANSLATE|' +
      'TRIM|TRUNC|UCASE|UNBASE64|UNHEX|UNIX_TIMESTAMP|UPPER|VAR_POP|VAR_SAMP|VARIANCE|WEEK|WEEKOFYEAR|XPATH|' +
      'XPATH_BOOLEAN|XPATH_DOUBLE|XPATH_FLOAT|XPATH_INT|XPATH_LONG|XPATH_NUMBER|XPATH_SHORT|XPATH_STRING|YEAR';

    var dataTypes =
      'ARRAY|BIGINT|BINARY|BOOLEAN|CHAR|DATE|DECIMAL|DOUBLE|FLOAT|INT|INTEGER|MAP|PRECISION|SMALLINT|STRING|STRUCT|' +
      'TIMESTAMP|TINYINT|UNIONTYPE|VARCHAR';

    var keywordMapper = this.createKeywordMapper({
        "support.function": builtinFunctions,
        "keyword": keywords,
        "constant.language": builtinConstants,
        "storage.type": dataTypes
    }, "identifier", true);

    this.$rules = {
      start: [
        {
            token : "comment",
            regex : "--.*$"
        },  {
            token : "comment",
            start : "/\\*",
            end : "\\*/"
        }, {
            token : "string",           // " string
            regex : '".*?"'
        }, {
            token : "string",           // ' string
            regex : "'.*?'"
        }, {
            token : "constant.numeric", // float
            regex : "[+-]?\\d+(?:(?:\\.\\d*)?(?:[eE][+-]?\\d+)?)?\\b"
        }, {
            token : keywordMapper,
            regex : "[a-zA-Z_$][a-zA-Z0-9_$]*\\b"
        }, {
            token : "keyword.operator",
            regex : "\\+|\\-|\\/|\\/\\/|%|<@>|@>|<@|&|\\^|~|<|>|<=|=>|==|!=|<>|="
        }, {
            token : "paren.lparen",
            regex : "[\\(]"
        }, {
            token : "paren.rparen",
            regex : "[\\)]"
        }, {
            token : "text",
            regex : "\\s+"
        }
      ]
    };

    this.normalizeRules();
  };

  HiveHighlightRules.metaData = {
    fileTypes: ["hql", "q", "ql"],
    name: "Hive",
    scopeName: "source.hive"
  };

  oop.inherits(HiveHighlightRules, TextHighlightRules);

  exports.HiveHighlightRules = HiveHighlightRules;
});
