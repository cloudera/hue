ace.define("ace/mode/pig_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"], function (require, exports, module) {
  "use strict";

  var oop = require("../lib/oop");
  var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;

  var PigLatinHighlightRules = function () {

    var keywords = (
        "%DECLARE|%DEFAULT|VOID|IMPORT|RETURNS|ARRANGE|DEFINE|LOAD|FILTER|FOREACH|ORDER|CUBE|DISTINCT|COGROUP|CP|CD|DU|JOIN|CROSS|UNION|SPLIT|INTO|IF|OTHERWISE|ALL|AS|BY|USING|INNER|OUTER|ONSCHEMA|PARALLEL|PARTITION|GROUP|AND|ANY|OR|NOT|GENERATE|FLATTEN|ASC|DESC|DESCRIBE|EXPLAIN|IS|STREAM|THROUGH|STORE|MAPREDUCE|SHIP|CACHE|INPUT|OUTPUT|STDERROR|STDIN|STDOUT|LIMIT|SAMPLE|LEFT|RIGHT|FULL|EQ|GT|LT|GTE|LTE|NEQ|MATCHES|TRUE|FALSE|REGISTER|DUMP|EXEC|HELP|ILLUSTRATE|KILL|LS|MKDIR|MV|PIG|PWD|QUIT|RM|RMF|RUN|SET"
    );

    var builtinFunctions = (
        "ABS|ACOS|ARITY|ASIN|ATAN|AVG|BAGSIZE|BINSTORAGE|BLOOM|BUILDBLOOM|CBRT|CEIL|CONCAT|COPYFROMLOCAL|COPYTOLOCAL|CAT|COR|COS|COSH|COUNT|COUNT_STAR|COV|CONSTANTSIZE|CUBEDIMENSIONS|DIFF|DISTINCT|DOUBLEABS|DOUBLEAVG|DOUBLEBASE|DOUBLEMAX|DOUBLEMIN|DOUBLEROUND|DOUBLESUM|EXP|FLOOR|FLOATABS|FLOATAVG|FLOATMAX|FLOATMIN|FLOATROUND|FLOATSUM|GENERICINVOKER|INDEXOF|INTABS|INTAVG|INTMAX|INTMIN|INTSUM|INVOKEFORDOUBLE|INVOKEFORFLOAT|INVOKEFORINT|INVOKEFORLONG|INVOKEFORSTRING|INVOKER|ISEMPTY|JSONLOADER|JSONMETADATA|JSONSTORAGE|LAST_INDEX_OF|LCFIRST|LOG|LOG10|LOWER|LONGABS|LONGAVG|LONGMAX|LONGMIN|LONGSUM|MAX|MIN|MAPSIZE|MONITOREDUDF|NONDETERMINISTIC|OUTPUTSCHEMA||PIGSTORAGE|PIGSTREAMING|RANDOM|REGEX_EXTRACT|REGEX_EXTRACT_ALL|REPLACE|ROUND|SIN|SINH|SIZE|SQRT|STRSPLIT|SUBSTRING|SUM|STRINGCONCAT|STRINGMAX|STRINGMIN|STRINGSIZE|TAN|TANH|TOBAG|TOKENIZE|TOMAP|TOP|TOTUPLE|TRIM|TEXTLOADER|TUPLESIZE|UCFIRST|UPPER|UTF8STORAGECONVERTER|EVAL|PIGDUMP|PIGSTORAGE"
    );

    var keywordMapper = this.createKeywordMapper({
      "keyword": keywords,
      "support.function": builtinFunctions
    }, "identifier", true);

    this.$rules = {
      start: [
        {
          token: "comment.line.double-dash",
          regex: /--.*$/
        },
        {
          token: "comment.block",
          regex: /\/\*/,
          push: [
            {
              token: "comment.block",
              regex: /\*\//,
              next: "pop"
            },
            {
              defaultToken: "comment.block"
            }
          ]
        },
        {
          token: "constant.language",
          regex: /\b(?:null|true|false|stdin|stdout|stderr)\b/,
          caseInsensitive: true
        },
        {
          token: "constant.numeric",
          regex: /\b[\d]+(?:\.[\d]+)?(?:e[\d]+)?[LF]?\b/,
          caseInsensitive: true
        },
        {
          token: "string.quoted.double",
          regex: /"/,
          push: [
            {
              token: "string.quoted.double",
              regex: /"/,
              next: "pop"
            },
            {
              token: "constant.character.escape",
              regex: /\\./
            },
            {
              defaultToken: "string.quoted.double"
            }
          ]
        },
        {
          token: "string.quoted.single",
          regex: /'/,
          push: [
            {
              token: "string.quoted.single",
              regex: /'/,
              next: "pop"
            },
            {
              token: "constant.character.escape",
              regex: /\\./
            },
            {
              defaultToken: "string.quoted.single"
            }
          ]
        },
        {
          token: "string.quoted.other",
          regex: /`/,
          push: [
            {
              token: "string.quoted.other",
              regex: /`/,
              next: "pop"
            },
            {
              token: "constant.character.escape",
              regex: /\\./
            },
            {
              defaultToken: "string.quoted.other"
            }
          ]
        },
        {
          token: "keyword.operator.arithmetic",
          regex: /\+|-|\*|\/|%/
        },
        {
          token: "keyword.operator.bincond",
          regex: /\?|:/
        },
        {
          token: "keyword.operator.comparison",
          regex: /==|!=|<=|>=|<|>|\bmatches\b/,
          caseInsensitive: true
        },
        {
          token: "keyword.operator.null",
          regex: /\b(?:is\s+null|is\s+not\s+null)\b/,
          caseInsensitive: true
        },
        {
          token: "keyword.operator.boolean",
          regex: /\b(?:and|or|not)\b/,
          caseInsensitive: true
        },
        {
          token: "keyword.operator.relation",
          regex: /\b::\b/
        },
        {
          token: "keyword.operator.dereference",
          regex: /\b(?:\.|#)\b/
        },
        {
          token: "keyword.control.conditional",
          regex: /\b(?:CASE|WHEN|THEN|ELSE|END)\b/,
          caseInsensitive: true
        },
        {
          token: "keyword.control.relational",
          regex: /\b(?:ASSERT|COGROUP|CROSS|CUBE|distinct|filter|foreach|generate|group|join|limit|load|order|sample|split|store|stream|union)\b/,
          caseInsensitive: true
        },
        {
          token: "keyword.control.diagnostic",
          regex: /\b(?:describe|dump|explain|illustrate)\b/,
          caseInsensitive: true
        },
        {
          token: "keyword.control.macro",
          regex: /\b(?:define|import|register)\b/,
          caseInsensitive: true
        },
        {
          token: "keyword.control.clause",
          regex: /\b(?:any|all|asc|arrange|as|asc|by|desc|full|if|inner|into|left|outer|parallel|returns|right|through|using)\b/,
          caseInsensitive: true
        },
        {
          token: "support.function.operator",
          regex: /\bFLATTEN\b/,
          caseInsensitive: true
        },
        {
          token: "support.function.operation",
          regex: /\b(?:CUBE|ROLLUP)\b/,
          caseInsensitive: true
        },
        {
          token: "support.function.eval",
          regex: /\b(?:AVG|CONCAT|COUNT|COUNT_STAR|DIFF|IsEmpty|MAX|MIN|PluckTuple|SIZE|SUBTRACT|SUM|Terms|TOKENIZE|Usage)\b/
        },
        {
          token: "support.function.math",
          regex: /\b(?:ABS|ACOS|ASIN|ATAN|CBRT|CEIL|COS|COSH|EXP|FLOOR|LOG|LOG10|RANDOM|ROUND|SIN|SINH|SORT|TAN|TANH)\b/
        },
        {
          token: "support.function.string",
          regex: /\b(?:ENDSWITH|EqualsIgnoreCase|INDEXOF|LAST_INDEX_OF|LCFIRST|LOWER|LTRIM|REGEX_EXTRACT|REGEX_EXTRACT_ALL|REPLACE|RTRIM|STARTSWITH|STRSPLIT|SUBSTRING|TRIM|UCFIRST|UPPER)\b/
        },
        {
          token: "support.function.datetime",
          regex: /\b(?:AddDuration|CurrentTime|DaysBetween|GetDay|GetHour|GetMilliSecond|GetMinute|GetMonth|GetSecond|GetWeek|GetWeekYear|GetYear|HoursBetween|MilliSecondsBetween|MinutesBetween|MonthsBetween|SecondsBetween|SubtractDuration|ToDate|ToMilliSeconds|ToString|ToUnixTime|WeeksBetween|YearsBetween)\b/
        },
        {
          token: "support.function.tuple",
          regex: /\b(?:TOTUPLE|TOBAG|TOMAP|TOP)\b/,
          caseInsensitive: true
        },
        {
          token: "support.function.macro",
          regex: /\b(?:input|output|ship|cache)\b/,
          caseInsensitive: true
        },
        {
          token: "support.function.storage",
          regex: /\b(?:AvroStorage|BinStorage|BinaryStorage|HBaseStorage|JsonLoader|JsonStorage|PigDump|PigStorage|PigStreaming|TextLoader|TrevniStorage)\b/,
          caseInsensitive: true
        },
        {
          token: "keyword.other.command.shell",
          regex: /\b(?:fs|sh)\b/,
          caseInsensitive: true
        },
        {
          token: "keyword.other.command.shell.file",
          regex: /\b(?:cat|cd|copyFromLocal|copyToLocal|cp|ls|mkdir|mv|pwd|rm|rmf)\b/,
          caseInsensitive: true
        },
        {
          token: "keyword.other.command.shell.utility",
          regex: /\b(?:clear|exec|help|history|kill|quit|run|set)\b/,
          caseInsensitive: true
        },
        {
          token: "storage.type.simple",
          regex: /\b(?:int|long|float|double|chararray|bytearray|boolean|datetime|biginteger|bigdecimal)\b/,
          caseInsensitive: true
        },
        {
          token: "storage.type.complex",
          regex: /\b(?:tuple|bag|map)\b/,
          caseInsensitive: true
        },
        {
          token: "variable.other.positional",
          regex: /\$[0-9_]+/
        },
        {
          token: "variable.other.alias",
          regex: /\b[a-z][a-z0-9_]*\b/,
          caseInsensitive: true
        },
        {
          token : keywordMapper,
          regex : "[a-zA-Z_$][a-zA-Z0-9_$]*\\b"
        }
      ]
    };

    this.normalizeRules();
  };

  PigLatinHighlightRules.metaData = {
    fileTypes: ["pig"],
    name: "Pig Latin",
    scopeName: "source.pig_latin"
  };

  oop.inherits(PigLatinHighlightRules, TextHighlightRules);

  exports.PigLatinHighlightRules = PigLatinHighlightRules;
});

ace.define("ace/mode/folding/cstyle",["require","exports","module","ace/lib/oop","ace/range","ace/mode/folding/fold_mode"], function(require, exports, module) {
"use strict";

var oop = require("../../lib/oop");
var Range = require("../../range").Range;
var BaseFoldMode = require("./fold_mode").FoldMode;

var FoldMode = exports.FoldMode = function(commentRegex) {
    if (commentRegex) {
        this.foldingStartMarker = new RegExp(
            this.foldingStartMarker.source.replace(/\|[^|]*?$/, "|" + commentRegex.start)
        );
        this.foldingStopMarker = new RegExp(
            this.foldingStopMarker.source.replace(/\|[^|]*?$/, "|" + commentRegex.end)
        );
    }
};
oop.inherits(FoldMode, BaseFoldMode);

(function() {
    
    this.foldingStartMarker = /(\{|\[)[^\}\]]*$|^\s*(\/\*)/;
    this.foldingStopMarker = /^[^\[\{]*(\}|\])|^[\s\*]*(\*\/)/;
    this.singleLineBlockCommentRe= /^\s*(\/\*).*\*\/\s*$/;
    this.tripleStarBlockCommentRe = /^\s*(\/\*\*\*).*\*\/\s*$/;
    this.startRegionRe = /^\s*(\/\*|\/\/)#?region\b/;
    this._getFoldWidgetBase = this.getFoldWidget;
    this.getFoldWidget = function(session, foldStyle, row) {
        var line = session.getLine(row);
    
        if (this.singleLineBlockCommentRe.test(line)) {
            if (!this.startRegionRe.test(line) && !this.tripleStarBlockCommentRe.test(line))
                return "";
        }
    
        var fw = this._getFoldWidgetBase(session, foldStyle, row);
    
        if (!fw && this.startRegionRe.test(line))
            return "start"; // lineCommentRegionStart
    
        return fw;
    };

    this.getFoldWidgetRange = function(session, foldStyle, row, forceMultiline) {
        var line = session.getLine(row);
        
        if (this.startRegionRe.test(line))
            return this.getCommentRegionBlock(session, line, row);
        
        var match = line.match(this.foldingStartMarker);
        if (match) {
            var i = match.index;

            if (match[1])
                return this.openingBracketBlock(session, match[1], row, i);
                
            var range = session.getCommentFoldRange(row, i + match[0].length, 1);
            
            if (range && !range.isMultiLine()) {
                if (forceMultiline) {
                    range = this.getSectionRange(session, row);
                } else if (foldStyle != "all")
                    range = null;
            }
            
            return range;
        }

        if (foldStyle === "markbegin")
            return;

        var match = line.match(this.foldingStopMarker);
        if (match) {
            var i = match.index + match[0].length;

            if (match[1])
                return this.closingBracketBlock(session, match[1], row, i);

            return session.getCommentFoldRange(row, i, -1);
        }
    };
    
    this.getSectionRange = function(session, row) {
        var line = session.getLine(row);
        var startIndent = line.search(/\S/);
        var startRow = row;
        var startColumn = line.length;
        row = row + 1;
        var endRow = row;
        var maxRow = session.getLength();
        while (++row < maxRow) {
            line = session.getLine(row);
            var indent = line.search(/\S/);
            if (indent === -1)
                continue;
            if  (startIndent > indent)
                break;
            var subRange = this.getFoldWidgetRange(session, "all", row);
            
            if (subRange) {
                if (subRange.start.row <= startRow) {
                    break;
                } else if (subRange.isMultiLine()) {
                    row = subRange.end.row;
                } else if (startIndent == indent) {
                    break;
                }
            }
            endRow = row;
        }
        
        return new Range(startRow, startColumn, endRow, session.getLine(endRow).length);
    };
    this.getCommentRegionBlock = function(session, line, row) {
        var startColumn = line.search(/\s*$/);
        var maxRow = session.getLength();
        var startRow = row;
        
        var re = /^\s*(?:\/\*|\/\/|--)#?(end)?region\b/;
        var depth = 1;
        while (++row < maxRow) {
            line = session.getLine(row);
            var m = re.exec(line);
            if (!m) continue;
            if (m[1]) depth--;
            else depth++;

            if (!depth) break;
        }

        var endRow = row;
        if (endRow > startRow) {
            return new Range(startRow, startColumn, endRow, line.length);
        }
    };

}).call(FoldMode.prototype);

});

ace.define("ace/mode/pig",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/pig_highlight_rules","ace/mode/folding/cstyle"], function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextMode = require("./text").Mode;
var PigLatinHighlightRules = require("./pig_highlight_rules").PigLatinHighlightRules;
var FoldMode = require("./folding/cstyle").FoldMode;

var Mode = function() {
    this.HighlightRules = PigLatinHighlightRules;
    this.foldingRules = new FoldMode();
};
oop.inherits(Mode, TextMode);

(function() {
    this.$id = "ace/mode/pig";

    this.getCompletions = function(state, session, pos, prefix) {
        var keywords = this.$keywordList || this.$createKeywordList();
        return keywords.map(function (word) {
            return {
                ignoreCase: true,
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
