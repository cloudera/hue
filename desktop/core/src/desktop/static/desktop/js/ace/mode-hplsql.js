ace.define("ace/mode/hplsql_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"], function (require, exports, module) {
    "use strict";
  
    var oop = require("../lib/oop");
    var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;
  
    var HplsqlHighlightRules = function () {
  
      var keywords =
        'ALLOCATE|ASSOCIATE|BREAK|CALL|CLOSE|CMP|CONDITION|COPY|CREATE|CURSOR|DATABASE|DECLARE|DESCRIBE|DIAGNOSTICS|'+
        'DIRECTORY|DROP|EXEC|EXECUTE|EXIT|FETCH|FOR|FROM|FTP|FUNCTION|GET|HANDLER|HIVE|HOST|IF|IMMEDIATE|INCLUDE|'+
        'INSERT|INTO|LEAVE|LOCAL|LOCATOR|LOOP|MAP|NULL|OBJECT|OPEN|PACKAGE|PRINT|PROCEDURE|RESIGNAL|RESULT|'+
        'RETURN|SELECT|SET|SIGNAL|SUMMARY|TABLE|TEMPORARY|TRUNCATE|UPDATE|USE|VALUES|VOLATILE|WHEN|WHILE|.IF|.QUIT';
  
      var builtinConstants = 'FALSE|NULL|TRUE';
  
      var builtinFunctions =
        'CAST|CHAR|COALESCE|CONCAT|CURRENT_DATE|CURRENT_TIMESTAMP|CURRENT_USER|DATE|DBMS_OUTPUT|PUT_LINE|DECODE|'+
        'FROM_UNIXTIME|INSTR|LEN|LENGTH|LOWER|MAX_PART_DATE|MAX_PART_INT|MAX_PART_STRING|MIN_PART_DATE|MIN_PART_INT|'+
        'MIN_PART_STRING|NOW|NVL|NVL2|PART_COUNT|PART_COUNT_BY|PART_LOC|REPLACE|SUBSTR|SUBSTRING|SYSDATE|TIMESTAMP_ISO|'+
        'TO_CHAR|TO_TIMESTAMP|TRIM|UNIX_TIMESTAMP|UPPER';
  
      var dataTypes =
        'BIGINT|BINARY_DOUBLE|BINARY_FLOAT|BINARY_INTEGER|BIT|BOOL|BOOLEAN|CHAR|CHARACTER|DATE|DATETIME|DECIMAL|DOUBLE|'+
        'FLOAT|INT|INT2|INT8|INTEGER|NCHAR|NUMBER|NUMERIC|NVARCHAR|PLS_INTEGER|PRECISION|REAL|RECORD|SIMPLE_DOUBLE|'+
        'SIMPLE_FLOAT|SIMPLE_INTEGER|SMALLINT|SYS_REFCURSOR|TIMESTAMP|TINYINT|VARCHAR|VARCHAR2|UTL_FILE|FILE_TYPE';
  
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
  
    HplsqlHighlightRules.metaData = {
      fileTypes: ["hplsql"],
      name: "Hplsql",
      scopeName: "source.hplsql"
    };
  
    oop.inherits(HplsqlHighlightRules, TextHighlightRules);
  
    exports.HplsqlHighlightRules = HplsqlHighlightRules;
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

ace.define("ace/mode/folding/sqlserver",["require","exports","module","ace/lib/oop","ace/range","ace/mode/folding/cstyle"], function(require, exports, module) {
"use strict";

var oop = require("../../lib/oop");
var Range = require("../../range").Range;
var BaseFoldMode = require("./cstyle").FoldMode;

var FoldMode = exports.FoldMode = function() {};

oop.inherits(FoldMode, BaseFoldMode);

(function() {
    
    this.foldingStartMarker = /(\bCASE\b|\bBEGIN\b)|^\s*(\/\*)/i;
    this.startRegionRe = /^\s*(\/\*|--)#?region\b/;
    
    this.getFoldWidgetRange = function(session, foldStyle, row, forceMultiline) {
        var line = session.getLine(row);
    
        if (this.startRegionRe.test(line)) return this.getCommentRegionBlock(session, line, row);
    
        var match = line.match(this.foldingStartMarker);
        if (match) {
            var i = match.index;
            if (match[1]) return this.getBeginEndBlock(session, row, i, match[1]);
    
            var range = session.getCommentFoldRange(row, i + match[0].length, 1);
            if (range && !range.isMultiLine()) {
                if (forceMultiline) {
                    range = this.getSectionRange(session, row);
                }
                else if (foldStyle != "all") range = null;
            }
    
            return range;
        }
    
        if (foldStyle === "markbegin") return;
        return;
    };
    this.getBeginEndBlock = function(session, row, column, matchSequence) {
        var start = {
            row: row,
            column: column + matchSequence.length
        };
        var maxRow = session.getLength();
        var line;
    
        var depth = 1;
        var re = /(\bCASE\b|\bBEGIN\b)|(\bEND\b)/i;
        while (++row < maxRow) {
            line = session.getLine(row);
            var m = re.exec(line);
            if (!m) continue;
            if (m[1]) depth++;
            else depth--;
    
            if (!depth) break;
        }
        var endRow = row;
        if (endRow > start.row) {
            return new Range(start.row, start.column, endRow, line.length);
        }
    };

}).call(FoldMode.prototype);

});

ace.define("ace/mode/hplsql",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/hplsql_highlight_rules","ace/mode/folding/sqlserver"], function(require, exports, module) {
    "use strict";
    
    var oop = require("../lib/oop");
    var TextMode = require("./text").Mode;
    var HplsqlHighlightRules = require("./hplsql_highlight_rules").HplsqlHighlightRules;
    var FoldMode = require("./folding/sqlserver").FoldMode;
    
    var Mode = function() {
        this.HighlightRules = HplsqlHighlightRules;
        this.foldingRules = new FoldMode();
    };
    oop.inherits(Mode, TextMode);
    
    (function() {
        this.lineCommentStart = "--";
        this.$id = "ace/mode/hplsql"
    
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
