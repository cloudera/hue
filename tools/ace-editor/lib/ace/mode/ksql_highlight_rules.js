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

  var KsqlHighlightRules = function () {
    // regexp must not have capturing parentheses. Use (?:) instead.
    // regexps are ordered -> the first match is used

    var keywords = (
        "EMIT|CHANGES|SELECT|FROM|AS|DISTINCT|WHERE|WITHIN|WINDOW|GROUP|BY|HAVING|LIMIT|AT|OR|AND|IN|NOT|EXISTS|BETWEEN|LIKE|IS|INTEGER|DATE|TIME|TIMESTAMP|INTERVAL|YEAR|MONTH|DAY|HOUR|MINUTE|SECOND|MILLISECOND|YEARS|MONTHS|DAYS|HOURS|MINUTES|SECONDS|MILLISECONDS|ZONE|TUMBLING|HOPPING|SIZE|ADVANCE|CASE|WHEN|THEN|ELSE|END|JOIN|FULL|OUTER|INNER|LEFT|RIGHT|ON|PARTITION|STRUCT|WITH|VALUES|CREATE|TABLE|TOPIC|STREAM|STREAMS|INSERT|DELETE|INTO|DESCRIBE|EXTENDED|PRINT|EXPLAIN|ANALYZE|TYPE|TYPES|CAST|SHOW|LIST|TABLES|TOPICS|QUERY|QUERIES|TERMINATE|LOAD|COLUMNS|COLUMN|PARTITIONS|FUNCTIONS|FUNCTION|DROP|TO|RENAME|ARRAY|MAP|SET|RESET|SESSION|SAMPLE|EXPORT|CATALOG|PROPERTIES|BEGINNING|UNSET|RUN|SCRIPT|DECIMAL|KEY|CONNECTOR|CONNECTORS|SINK|SOURCE|IF"
    );

    var builtinConstants = (
        "FALSE|NULL|TRUE"
    );

    var builtinFunctions = (
        "ABS|ARRAYCONTAINS|CEIL|CONCAT|DATETOSTRING|ELT|EXTRACTJSONFIELD|FIELD|FLOOR|GEO_DISTANCE|IFNULL|LCASE|LEN|MASK|MASK_KEEP_LEFT|MASK_KEEP_RIGHT|MASK_LEFT|MASK_RIGHT|RANDOM|ROUND|SPLIT|STRINGTODATE|STRINGTOTIMESTAMP|SUBSTRING|TIMESTAMPTOSTRING|TRIM|UCASE|URL_DECODE_PARAM|URL_ENCODE_PARAM|URL_EXTRACT_FRAGMENT|URL_EXTRACT_HOST|URL_EXTRACT_PARAMETER|URL_EXTRACT_PATH|URL_EXTRACT_PORT|URL_EXTRACT_PROTOCOL|URL_EXTRACT_QUERY|COLLECT_LIST|COLLECT_SET|COUNT|HISTOGRAM|MAX|MIN|SUM|TOPK|TOPKDISTINCT|WindowStart|WindowEnd"
    );

    var dataTypes = (
        "BOOLEAN|INTEGER|INT|BIGINT|DOUBLE|VARCHAR|STRING|ARRAY|MAP|STRUCT"
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

  KsqlHighlightRules.metaData = {
    fileTypes: ["ksql"],
    name: "ksql",
    scopeName: "source.ksql"
  };

  oop.inherits(KsqlHighlightRules, TextHighlightRules);

  exports.KsqlHighlightRules = KsqlHighlightRules;
});
