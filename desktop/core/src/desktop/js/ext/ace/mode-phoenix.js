ace.define("ace/mode/phoenix_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"], function (require, exports, module) {
  "use strict";

  var oop = require("../lib/oop");
  var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;

  var PhoenixHighlightRules = function () {

    var keywords = (
        "ADD|ADMIN|AFTER|ALL|ALTER|ANALYZE|AND|ARCHIVE|AS|ASC|AUTHORIZATION|BEFORE|BETWEEN|BOTH|BUCKET|BUCKETS|BY|CACHE|CASCADE|CASE|CAST|CHANGE|CLUSTER|CLUSTERED|CLUSTERSTATUS|COLLECTION|COLUMN|COLUMNS|COMMENT|COMMIT|COMPACT|COMPACTIONS|COMPUTE|CONCATENATE|CONF|CONSTRAINT|CONTINUE|CREATE|CROSS|CUBE|CURRENT|CURRENT_DATE|CURRENT_TIMESTAMP|CURSOR|DATA|DATABASE|DATABASES|DATETIME|DAY|DAYOFWEEK|DBPROPERTIES|DEFERRED|DEFINED|DELETE|DEPENDENCY|DESC|DESCRIBE|DIRECTORIES|DIRECTORY|DISABLE|DISTINCT|DISTRIBUTE|DROP|ELEM_TYPE|ELSE|ENABLE|END|ESCAPED|EXCHANGE|EXCLUSIVE|EXISTS|EXPLAIN|EXPORT|EXTENDED|EXTERNAL|EXTRACT|FETCH|FIELDS|FILE|FILEFORMAT|FIRST|FLOOR|FOLLOWING|FOR|FOREIGN|FORMAT|FORMATTED|FROM|FULL|FUNCTION|FUNCTIONS|GRANT|GROUP|GROUPING|HAVING|HOLD_DDLTIME|HOUR|IDXPROPERTIES|IF|IGNORE|IMPORT|IN|INDEX|INDEXES|INNER|INPATH|INPUTDRIVER|INPUTFORMAT|INSERT|INTERSECT|INTERVAL|INTO|IS|ITEMS|JAR|JOIN|KEY|KEYS|KEY_TYPE|LATERAL|LEFT|LESS|LIKE|LIMIT|LINES|LOAD|LOCAL|LOCATION|LOCK|LOCKS|LOGICAL|LONG|MACRO|MAPJOIN|MATERIALIZED|MINUS|MINUTE|MONTH|MORE|MSCK|NONE|NOSCAN|NOVALIDATE|NOT|NO_DROP|OF|OFFLINE|ON|ONLY|OPTION|OR|ORDER|OUT|OUTER|OUTPUTDRIVER|OUTPUTFORMAT|OVER|OVERWRITE|OWNER|PARTIALSCAN|PARTITION|PARTITIONED|PARTITIONS|PERCENT|PLUS|PRECEDING|PRECISION|PRESERVE|PRETTY|PRIMARY|PRINCIPALS|PROCEDURE|PROTECTION|PURGE|RANGE|READ|READONLY|READS|REBUILD|RECORDREADER|RECORDWRITER|REDUCE|REFERENCES|REGEXP|RELOAD|RENAME|REPAIR|REPLACE|RESTRICT|REVOKE|REWRITE|RIGHT|RLIKE|ROLE|ROLES|ROLLBACK|ROLLUP|ROW|ROWS|SCHEMA|SCHEMAS|SECOND|SELECT|SEMI|SERDEPROPERTIES|SERVER|SET|SETS|SHARED|SHOW|SHOW_DATABASE|SKEWED|SORT|SORTED|SSL|START|STATISTICS|STORED|STREAMTABLE|SYNC|TABLE|TABLES|TABLESAMPLE|TBLPROPERTIES|TEMPORARY|TERMINATED|THEN|TO|TOUCH|TRANSACTIONAL|TRANSACTIONS|TRANSFORM|TRIGGER|TRUNCATE|UNARCHIVE|UNBOUNDED|UNDO|UNION|UNIQUEJOIN|UNLOCK|UNSET|UNSIGNED|UTC_TIMESTAMP|UPDATE|URI|USE|USER|USING|UTC|UTCTIMESTAMP|VALUES|VALUE_TYPE|VIEW|VIEWS|WHEN|WHERE|WHILE|WINDOW|WITH|YEAR"
    );

    var builtinConstants = (
        "FALSE|NULL|TRUE"
    );

    var builtinFunctions = (
        "ABS|ACOS|ADD_MONTHS|AES_DECRYPT|AES_ENCRYPT|ARRAY|ARRAY_CONTAINS|ASCII|ASIN|ATAN|AVG|BASE64|BIN|BINARY|BROUND|CAST|CBRT|CEIL|CEILING|COALESCE|COLLECT_LIST|COLLECT_SET|CONCAT|CONCAT_WS|CONTEXT_NGRAMS|CONV|CORR|COS|COVAR_POP|COVAR_SAMP|COUNT|CRC32|CREATE_UNION|CUME_DIST|CURRENT_DATABASE|CURRENT_DATE|CURRENT_TIMESTAMP|CURRENT_USER|DATE_ADD|DATE_FORMAT|DATE_SUB|DATEDIFF|DAY|DAYOFMONTH|DECODE|DEGREES|DENSE_RANK|E|ENCODE|EXP|EXPLODE|FACTORIAL|FIND_IN_SET|FIRST_VALUE|FLOOR|FORMAT_NUMBER|FROM_UNIXTIME|FROM_UTC_TIMESTAMP|GET_JSON_OBJECT|GREATEST|HASH|HEX|HISTOGRAM_NUMERIC|HOUR|IF|IN_FILE|INLINE|INSTR|INITCAP|ISNOTNULL|ISNULL|JAVA_METHOD|JSON_TUPLE|LAG|LAST_DAY|LAST_VALUE|LEAD|LEAST|LENGTH|LEVENSHTEIN|LCASE|LN|LOCATE|LOG|LOG10|LOG2|LOWER|LPAD|LTRIM|MAP|MAP_KEYS|MAP_VALUES|MAX|MD5|MIN|MINUTE|MONTH|MONTHS_BETWEEN|NAMED_STRUCT|NEGATIVE|NEXT_DAY|NGRAMS|NTILE|NVL|PARSE_URL|PARSE_URL_TUPLE|PERCENT_RANK|PERCENTILE|PERCENTILE_APPROX|PI|PMOD|POSEXPLODE|POSITIVE|POW|POWER|PRINTF|QUARTER|RADIANS|RAND|RANK|REFLECT|REGEXP_EXTRACT|REGEXP_REPLACE|REPEAT|REVERSE|ROUND|ROW_NUMBER|RPAD|RTRIM|SECOND|SHA|SHA1|SHA2|SHIFTLEFT|SHIFTRIGHT|SHIFTRIGHTUNSIGNED|SIGN|SIN|SIZE|SORT_ARRAY|SQRT|STACK|STDDEV_POP|STDDEV_SAMP|STRUCT|SENTENCES|SOUNDEX|SPACE|SPLIT|STR_TO_MAP|SUBSTR|SUBSTRING|SUBSTRING_INDEX|SUM|TAN|TO_DATE|TO_UTC_TIMESTAMP|TRANSLATE|TRIM|TRUNC|UCASE|UNBASE64|UNHEX|UNIX_TIMESTAMP|UPPER|VAR_POP|VAR_SAMP|VARIANCE|WEEKOFYEAR|XPATH|XPATH_BOOLEAN|XPATH_DOUBLE|XPATH_FLOAT|XPATH_INT|XPATH_LONG|XPATH_NUMBER|XPATH_SHORT|XPATH_STRING|YEAR"
    );

    var dataTypes = (
        "ARRAY|BIGINT|BINARY|BOOLEAN|CHAR|DATE|DECIMAL|DELIMITED|DOUBLE|FLOAT|INT|INTEGER|JSONFILE|MAP|NUMERIC|PRECISION|RCFILE|SEQUENCEFILE|SERDE|SMALLINT|STRING|STRUCT|TEXTFILE|TIME|TIMESTAMP|TINYINT|UNIONTYPE|VARCHAR"
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

  PhoenixHighlightRules.metaData = {
    fileTypes: ["pql"],
    name: "Phoenix",
    scopeName: "source.phoenix"
  };

  oop.inherits(PhoenixHighlightRules, TextHighlightRules);

  exports.PhoenixHighlightRules = PhoenixHighlightRules;
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

ace.define("ace/mode/phoenix",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/phoenix_highlight_rules","ace/mode/folding/sqlserver"], function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextMode = require("./text").Mode;
var PhoenixHighlightRules = require("./phoenix_highlight_rules").PhoenixHighlightRules;
var FoldMode = require("./folding/sqlserver").FoldMode;

var Mode = function() {
    this.HighlightRules = PhoenixHighlightRules;
    this.foldingRules = new FoldMode();
};
oop.inherits(Mode, TextMode);

(function() {
    this.lineCommentStart = "--";
    this.$id = "ace/mode/phoenix"

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
