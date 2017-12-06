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

  var SolrHighlightRules = function () {

    var keywords = (
        "AND|OR|NOT|TO|NOW|HOUR|HOURS|DAY|DAYS|MONTH|MONTHS|YEAR|YEARS"
    );

    var builtinFunctions = (
        "ABS|AVG|CHILDFIELD|DEF|DIST|DIV|DOCFREQ|EQ|EXISTS|FIELD|GT|GTE|HLL|HSIN|IDF|IF|LINEAR|LOG|LT|LTE|MAP|MAX|MAX|MAXDOC|MIN|MIN|MS|MUL|NORM|NUMDOCS|ORD|PAYLOAD|PERCENTILE|POW|PRODUCT|QUERY|RECIP|RORD|SCALE|SQEDIST|SQRT|STDDEV|STRDIST|SUB|SUM|SUM|SUMSQ|SUMTOTALTERMFREQ|TERMFREQ|TF|TOP|TOTALTERMFREQ|UNIQUE|VARIANCE|XOR"
    );

    var keywordMapper = this.createKeywordMapper({
        "support.function": builtinFunctions,
        "keyword": keywords
    }, "identifier", true);

    this.$rules = {
      start: [
        {
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
            regex : '\\+|\\-|\\/|\\?|&|\\^|~|:|\\*|\\||!|"|\\[|\\]'
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

  SolrHighlightRules.metaData = {
    fileTypes: ["solr"],
    name: "Solr",
    scopeName: "source.solr"
  };

  oop.inherits(SolrHighlightRules, TextHighlightRules);

  exports.SolrHighlightRules = SolrHighlightRules;
});