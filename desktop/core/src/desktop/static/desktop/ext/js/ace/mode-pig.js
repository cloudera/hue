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
      "%DECLARE|%DEFAULT|VOID|IMPORT|RETURNS|ARRANGE|DEFINE|LOAD|FILTER|FOREACH|ORDER|CUBE|DISTINCT|COGROUP|CP|CD|DU|"
      + "JOIN|CROSS|UNION|SPLIT|INTO|IF|OTHERWISE|ALL|AS|BY|USING|INNER|OUTER|ONSCHEMA|PARALLEL|"
      + "PARTITION|GROUP|AND|ANY|OR|NOT|GENERATE|FLATTEN|ASC|DESC|DESCRIBE|EXPLAIN|IS|STREAM|THROUGH|STORE|MAPREDUCE|"
      + "SHIP|CACHE|INPUT|OUTPUT|STDERROR|STDIN|STDOUT|LIMIT|SAMPLE|LEFT|RIGHT|FULL|EQ|GT|LT|GTE|LTE|"
      + "NEQ|MATCHES|TRUE|FALSE|REGISTER|DUMP|EXEC|HELP|ILLUSTRATE|KILL|LS|MKDIR|MV|PIG|PWD|QUIT|RM|RMF|RUN|SET"
    );

    var builtinConstants = (
        "TRUE|FALSE|NULL"
    );

    var builtinFunctions = (
      "ABS|ACOS|ARITY|ASIN|ATAN|AVG|BAGSIZE|BINSTORAGE|BLOOM|BUILDBLOOM|CBRT|CEIL|"
      + "CONCAT|COPYFROMLOCAL|COPYTOLOCAL|CAT|COR|COS|COSH|COUNT|COUNT_STAR|COV|CONSTANTSIZE|CUBEDIMENSIONS|DIFF|DISTINCT|DOUBLEABS|"
      + "DOUBLEAVG|DOUBLEBASE|DOUBLEMAX|DOUBLEMIN|DOUBLEROUND|DOUBLESUM|EXP|FLOOR|FLOATABS|FLOATAVG|"
      + "FLOATMAX|FLOATMIN|FLOATROUND|FLOATSUM|GENERICINVOKER|INDEXOF|INTABS|INTAVG|INTMAX|INTMIN|"
      + "INTSUM|INVOKEFORDOUBLE|INVOKEFORFLOAT|INVOKEFORINT|INVOKEFORLONG|INVOKEFORSTRING|INVOKER|"
      + "ISEMPTY|JSONLOADER|JSONMETADATA|JSONSTORAGE|LAST_INDEX_OF|LCFIRST|LOG|LOG10|LOWER|LONGABS|"
      + "LONGAVG|LONGMAX|LONGMIN|LONGSUM|MAX|MIN|MAPSIZE|MONITOREDUDF|NONDETERMINISTIC|OUTPUTSCHEMA||"
      + "PIGSTORAGE|PIGSTREAMING|RANDOM|REGEX_EXTRACT|REGEX_EXTRACT_ALL|REPLACE|ROUND|SIN|SINH|SIZE|"
      + "SQRT|STRSPLIT|SUBSTRING|SUM|STRINGCONCAT|STRINGMAX|STRINGMIN|STRINGSIZE|TAN|TANH|TOBAG|"
      + "TOKENIZE|TOMAP|TOP|TOTUPLE|TRIM|TEXTLOADER|TUPLESIZE|UCFIRST|UPPER|UTF8STORAGECONVERTER|EVAL|PIGDUMP|PIGSTORAGE"
    );

    var dataTypes = (
        "BOOLEAN|INT|LONG|FLOAT|DOUBLE|CHARARRAY|BYTEARRAY|BAG|TUPLE|MAP|DATETIME"
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

ace.define("ace/mode/pig",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/sql_highlight_rules","ace/range"], function(require, exports, module) {
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

    this.$id = "ace/mode/pig";
}).call(Mode.prototype);

exports.Mode = Mode;

});
