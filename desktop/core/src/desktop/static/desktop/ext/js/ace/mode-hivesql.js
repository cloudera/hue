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
        "ADD|AFTER|ALL|ALTER|ANALYZE|AND|ARCHIVE|AS|ASC|BETWEEN|BUCKET|BUCKETS|BY|CASCADE|CHANGE|CLI|CLUSTER|CLUSTERED|COALESCE|COLLECTION|COLUMN|COLUMNS|COMMENT|COMPUTE|CREATE|CROSS|DATA|DATABASE|DATABASES|DBPROPERTIES|DEFERRED|DELIMITED|DEPENDENCY|DESC|DESCRIBE|DIRECTORY|DISABLE|DISTINCT|DISTRIBUTE|DOT|DROP|ENABLE|ESCAPED|EXISTS|EXPLAIN|EXPORT|EXTENDED|EXTERNAL|FIELDS|FILEFORMAT|FIRST|FORMAT|FORMATTED|FROM|FULL|FUNCTION|FUNCTIONS|GRANT|GROUP|HAVING|IDXPROPERTIES|IF|IGNORE|IMPORT|IN|INDEX|INDEXES|INPATH|INSERT|INTO|IS|ITEMS|JOIN|KEYS|LATERAL|LEFT|LIKE|LIMIT|LINES|LOAD|LOCAL|LOCATION|LOCKS|MAP|MAPJOIN|MSCK|NOT|OF|OFFLINE|ON|OPTION|ORDER|OUT|OUTER|OVERWRITE|PARTITION|PARTITIONED|PARTITIONS|PERCENT|PRIVILEGES|PROTECTION|REBUILD|RECORDREADER|RECOVER|REDUCE|REGEXP|RENAME|REPAIR|REPLACE|RESTRICT|REVOKE|RIGHT|RLIKE|ROLE|ROW|SCHEMA|SCHEMAS|SELECT|SEMI|SEPARATED|SERDE|SERDEPROPERTIES|SET|SHOW|SKEWED|SORT|SORTED|STATISTICS|STORED|SUM|TABLE|TABLES|TABLESAMPLE|TBLPROPERTIES|TEMPORARY|TERMINATED|TO|TOUCH|TRANSFORM|TRUNCATE|UNARCHIVE|UNION|US|USER|USING|VIEW|WHERE|WITH"
    );

    var builtinConstants = (
        "TRUE|FALSE|NULL"
    );

    var builtinFunctions = (
        "ROUND|FLOOR|CEIL|CEILING|RAND|EXP|LN|LOG10|LOG2|LOG|POW|POWER|SQRT|BIN|HEX|UNHEX|CONV|ABS|PMOD|SIN|ASIN|COS|ACOS|TAN|ATAN|DEGREES|RADIANS|POSITIVE|NEGATIVE|SIGN|E|PI|SIZE|MAP_KEYS|MAP_VALUES|ARRAY_CONTAINS|SORT_ARRAY|BINARY|CAST|FROM_UNIXTIME|UNIX_TIMESTAMP|TO_DATE|YEAR|MONTH|DAY|HOUR|MINUTE|SECOND|WEEKOFYEAR|DATEDIFF|DATE_ADD|DATE_SUB|FROM_UTC_TIMESTAMP|TO_UTC_TIMESTAMP|ASCII|CONCAT|CONTEXT_NGRAMS|CONCAT_WS|FIND_IN_SET|FORMAT_NUMBER|GET_JSON_OBJECT|IN_FILE|INSTR|LENGTH|LOCATE|LOWER|LCASE|LPAD|LTRIM|NGRAMS|PARSE_URL|PRINTF|REGEXP_EXTRACT|REGEXP_REPLACE|REPEAT|REVERSE|RPAD|RTRIM|SENTENCES|SPACE|SPLIT|STR_TO_MAP|SUBSTR|SUBSTRING|TRANSLATE|TRIM|UPPER|UCASE|JAVA_METHOD|REFLECT|XPATH|XPATH_SHORT|XPATH_INT|XPATH_LONG|XPATH_FLOAT|XPATH_DOUBLE|XPATH_NUMBER|XPATH_STRING|COUNT|SUM|AVG|MIN|MAX|VARIANCE|VAR_SAMP|STDEV_POP|STDEV_SAMP|COVAR_POP|COVAR_SAMP|CORR|PERCENTILE|PERCENTILE_APPROX|HISTOGRAM_NUMERIC|COLLECT_SET|INLINE|EXPLODE|JSON_TUPLE|PARSE_URL_TUPLE|GET_JSON_OBJECT"
    );

    var dataTypes = (
        "TINYINT|SMALLINT|INT|BIGINT|BOOLEAN|FLOAT|DOUBLE|STRING|BINARY|TIMESTAMP|DECIMAL|ARRAY|MAP|STRUCT|UNIONTYPE|DELIMITED|SERDE|SEQUENCEFILE|TEXTFILE|RCFILE|INPUTFORMAT|OUTPUTFORMAT"
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

ace.define("ace/mode/hivesql",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/sql_highlight_rules","ace/range"], function(require, exports, module) {
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

    this.$id = "ace/mode/hivesql";
}).call(Mode.prototype);

exports.Mode = Mode;

});
