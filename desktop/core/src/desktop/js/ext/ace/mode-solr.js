ace.define("ace/mode/solr_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"], function (require, exports, module) {
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

ace.define("ace/mode/solr",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/solr_highlight_rules"], function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextMode = require("./text").Mode;
var SolrHighlightRules = require("./solr_highlight_rules").SolrHighlightRules;

var Mode = function() {
    this.HighlightRules = SolrHighlightRules;
};
oop.inherits(Mode, TextMode);

(function() {
    this.$id = "ace/mode/solr";

    this.getCompletions = function(state, session, pos, prefix) {
        var keywords = this.$keywordList || this.$createKeywordList();
        return keywords.map(function (word) {
            return {
                ignoreCase: false,
                name: word,
                value: word,
                upperCaseValue: word.toUpperCase(),
                score: 1,
                meta: "keyword"
            };
        });
    };
}).call(Mode.prototype);

exports.Mode = Mode;
});
