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

ace.define("ace/mode/sql_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"], function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;

var SqlHighlightRules = function() {

    var keywords = (
        "ADD|AGGREGATE|ALL|AND|API_VERSION|AS|AVRO|BINARY|BY|CACHED|CASE|CHANGE|CHAR|CLASS|CLOSE_FN|COLUMN|COLUMNS|COMMENT|COMPUTE|CREATE|CROSS|DATA|DATABASE|DATABASES|DECIMAL|DELIMITED|DESCRIBE|DISTINCT|DIV|DROP|ELSE|END|ESCAPED|EXISTS|EXPLAIN|EXTERNAL|FALSE|FIELDS|FILEFORMAT|FINALIZE_FN|FIRST|FORMAT|FORMATTED|FROM|FULL|FUNCTION|FUNCTIONS|GROUP|HAVING|IF|INIT_FN|INNER|INPATH|INSERT|INTEGER|INTERMEDIATE|INTERVAL|INTO|INVALIDATE|JOIN|LAST|LEFT|LIKE|LIMIT|LINES|LOAD|LOCATION|MERGE_FN|METADATA|NOT|NULL|NULLS|OFFSET|OR|ORDER|OUTER|OVERWRITE|PARQUET|PARTITION|PARTITIONED|PARTITIONS|PREPARE_FN|PRODUCED|REAL|REFRESH|REGEXP|RENAME|REPLACE|RETURNS|RIGHT|RLIKE|ROW|SCHEMA|SCHEMAS|SELECT|SEMI|SERDEPROPERTIES|SERIALIZE_FN|SHOW|STATS|STORED|STRAIGHT_JOIN|SYMBOL|TABLE|TABLES|TBLPROPERTIES|TERMINATED|THEN|TO|TRUE|UNCACHED|UNION|UPDATE_FN|USE|USING|VIEW|WHEN|WHERE|WITH"
    );

    var builtinConstants = (
        "TRUE|FALSE|NULL"
    );

    var builtinFunctions = (
        "ABS|ACOS|ASCII|ASIN|ATAN|AVG|BIN|CAST|CEIL|CEILING|COALESCE|CONCAT|CONCAT_WS|COUNT|CONV|COS|DATE_ADD|DATE_SUB|DATEDIFF|DAY|DAYNAME|DAYOFMONTH|DAYOFWEEK|DEGREES|E|EXP|FIND_IN_SET|FLOOR|FNV_HASH|FROM_UNIXTIME|FROM_UTC_TIMESTAMP|GREATEST|GROUP_CONCAT|HEX|HOUR|IF|INITCAP|INSTR|ISNULL|LCASE|LEAST|LENGTH|LN|LOCATE|LOG|LOG10|LOG2|LOWER|LPAD|LTRIM|MAX|MIN|MINUTE|MONTH|NDV|NEGATIVE|NOW|NVL|PARSE_URL|PI|PMOD|POSITIVE|POW|POWER|QUOTIENT|RADIANS|RAND|REGEXP_EXTRACT|REPEAT|REVERSE|ROUND|RPAD|RTRIM|SECOND|SIGN|SIN|SPACE|SQRT|SUBSTR|SUBSTRING|SUM|TAN|TO_DATE|TO_UTC_TIMESTAMP|TRANSLATE|TRIM|UCASE|UNHEX|UNIX_TIMESTAMP|UPPER|USER|WEEKOFYEAR|YEAR|DENSE_RANK|FIRST_VALUE|LAG|LAST_VALUE|LEAD|OVER|RANK|ROW_NUMBER|WINDOW"
    );

    var dataTypes = (
        "TINYINT|SMALLINT|INT|BIGINT|BOOLEAN|FLOAT|DOUBLE|STRING|TIMESTAMP|PARQUETFILE|SEQUENCEFILE|TEXTFILE|RCFILE"
    );

    var keywordMapper = this.createKeywordMapper({
        "support.function": builtinFunctions,
        "keyword": keywords,
        "constant.language": builtinConstants,
        "storage.type": dataTypes
    }, "identifier", false);

    this.$rules = {
        "start" : [ {
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
        } ]
    };
    this.normalizeRules();
};

oop.inherits(SqlHighlightRules, TextHighlightRules);

exports.SqlHighlightRules = SqlHighlightRules;
});

ace.define("ace/mode/impalasql",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/sql_highlight_rules","ace/range"], function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextMode = require("./text").Mode;
var SqlHighlightRules = require("./sql_highlight_rules").SqlHighlightRules;
var Range = require("../range").Range;

var Mode = function() {
    this.HighlightRules = SqlHighlightRules;
};
oop.inherits(Mode, TextMode);

(function() {

    this.lineCommentStart = "--";

    this.$id = "ace/mode/impalasql";
}).call(Mode.prototype);

exports.Mode = Mode;

});
