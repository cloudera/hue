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

  var ImpalaHighlightRules = function () {
    // regexp must not have capturing parentheses. Use (?:) instead.
    // regexps are ordered -> the first match is used

    var keywords = (
        "ADD|AGGREGATE|ALL|ALTER|ANALYTIC|AND|ANTI|API_VERSION|AS|ASC|AVRO|BETWEEN|BINARY|BLOCK_SIZE|BY|CACHED|CASE|CAST|CHANGE|CLASS|CLOSE_FN|COLUMN|COLUMNS|COMMENT|COMPRESSION|COMPUTE|CREATE|CROSS|CURRENT|DATA|DATABASE|DATABASES|DATE|DATETIME|DEFAULT|DELIMITED|DESC|DESCRIBE|DISTINCT|DIV|DROP|ELSE|ENCODING|END|ESCAPED|EXISTS|EXPLAIN|EXTENDED|EXTERNAL|FIELDS|FILEFORMAT|FINALIZE_FN|FIRST|FOLLOWING|FOR|FORMAT|FORMATTED|FROM|FULL|FUNCTION|FUNCTIONS|GRANT|GROUP|HASH|HAVING|IF|IN|INCREMENTAL|INIT_FN|INNER|INPATH|INSERT|INTEGER|INTERMEDIATE|INTERVAL|INTO|INVALIDATE|IS|JOIN|KEY|LAST|LEFT|LIKE|LIMIT|LINES|LOAD|LOCATION|MERGE_FN|METADATA|NOT|NULLS|OFFSET|ON|OR|ORDER|OUTER|OVER|OVERWRITE|PARQUET|PARTITION|PARTITIONED|PARTITIONS|PRECEDING|PREPARE_FN|PRIMARY|PRODUCED|RANGE|REFRESH|REGEXP|RENAME|REPLACE|RETURNS|REVOKE|RIGHT|RLIKE|ROLE|ROLES|ROW|ROWS|SCHEMA|SCHEMAS|SELECT|SEMI|SERDEPROPERTIES|SERIALIZE_FN|SET|SHOW|STATS|STORED|STRAIGHT_JOIN|SYMBOL|TABLE|TABLES|TBLPROPERTIES|TERMINATED|THEN|TO|UNBOUNDED|UNCACHED|UNION|UPDATE|UPDATE_FN|USE|USING|VALUES|VIEW|WHEN|WHERE|WITH"
    );

    var builtinConstants = (
        "DAY|DAYS|FALSE|HOUR|HOURS|MINUTE|MINUTES|MICROSECOND|MICROSECONDS|MILLISECOND|MILLISECONDS|MONTH|MONTHS|NANOSECOND|NANOSECONDS|NULL|SECOND|SECONDS|TRUE|WEEK|WEEKS|YEAR|YEARS"
    );

    var builtinFunctions = (
        "ABS|ACOS|ADD_MONTHS|ADDDATE|APPX_MEDIAN|ASCII|ASIN|ATAN|AVG|BIN|CAST|CEIL|CEILING|CHAR_LENGTH|CHARACTER_LENGTH|COALESCE|CONCAT|CONCAT_WS|CONV|COS|COUNT|CURRENT_DATABASE|CURRENT_TIMESTAMP|DATE_ADD|DATE_PART|DATE_SUB|DATEDIFF|DAY|DAYNAME|DAYOFMONTH|DAYOFWEEK|DAYOFYEAR|DAYS_ADD|DAYS_SUB|DECODE|DEGREES|DENSE_RANK|E|EXP|EXTRACT|FIND_IN_SET|FIRST_VALUE|FLOOR|FMOD|FNV_HASH|FROM_UNIXTIME|FROM_UTC_TIMESTAMP|GREATEST|GROUP_CONCAT|HEX|HOUR|HOURS_ADD|HOURS_SUB|IF|IFNULL|INITCAP|INSTR|IS_INF|IS_NAN|ISNULL|LAG|LAST_VALUE|LCASE|LEAD|LEAST|LENGTH|LN|LOCATE|LOG|LOG10|LOG2|LOWER|LPAD|LTRIM|MAX|MAX_BIGINT|MAX_INT|MAX_SMALLINT|MAX_TINYINT|MICROSECONDS_ADD|MICROSECONDS_SUB|MILLISECONDS_ADD|MILLISECONDS_SUB|MIN|MIN_BIGINT|MIN_INT|MIN_SMALLINT|MIN_TINYINT|MINUTE|MINUTES_ADD|MINUTES_SUB|MONTH|MONTHS_ADD|MONTHS_SUB|NANOSECONDS_ADD|NANOSECONDS_SUB|NDV|NEGATIVE|NOW|NULLIF|NULLIFZERO|NVL|PARSE_URL|PI|PID|PMOD|POSITIVE|POW|POWER|PRECISION|QUOTIENT|RADIANS|RAND|RANK|REGEXP_EXTRACT|REGEXP_REPLACE|REPEAT|REVERSE|ROUND|ROW_NUMBER|RPAD|RTRIM|SCALE|SECOND|SECONDS_ADD|SECONDS_SUB|SIGN|SIN|SPACE|SQRT|STDDEV|STDDEV_POP|STDDEV_SAMP|STRLEFT|STRRIGHT|SUBDATE|SUBSTR|SUBSTRING|SUM|TAN|TO_DATE|TO_UTC_TIMESTAMP|TRANSLATE|TRIM|TRUNC|UCASE|UNHEX|UNIX_TIMESTAMP|UPPER|USER|VAR_POP|VAR_SAMP|VARIANCE|VARIANCE_POP|VARIANCE_SAMP|VERSION|WEEKOFYEAR|WEEKS_ADD|WEEKS_SUB|YEAR|YEARS_ADD|YEARS_SUB|ZEROIFNULL"
    );

    var dataTypes = (
        "BIGINT|BOOLEAN|CHAR|DECIMAL|DOUBLE|FLOAT|INT|KUDU|PARQUETFILE|REAL|SEQUENCEFILE|RCFILE|SMALLINT|STRING|TEXTFILE|TIMESTAMP|TINYINT|VARCHAR"
    );

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

  ImpalaHighlightRules.metaData = {
    fileTypes: ["iql"],
    name: "Impala",
    scopeName: "source.impala"
  };

  oop.inherits(ImpalaHighlightRules, TextHighlightRules);

  exports.ImpalaHighlightRules = ImpalaHighlightRules;
});