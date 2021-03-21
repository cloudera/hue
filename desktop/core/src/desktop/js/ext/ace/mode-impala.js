ace.define("ace/mode/impala_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"], function (require, exports, module) {
  "use strict";

  var oop = require("../lib/oop");
  var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;

  var ImpalaHighlightRules = function () {

    var keywords = (
        "ADD|AGGREGATE|ALL|ALLOCATE|ALTER|ANALYTIC|AND|ANTI|ANY|API_VERSION|ARE|ARRAY_AGG|ARRAY_MAX_CARDINALITY|AS|ASC|ASENSITIVE|ASYMMETRIC|AT|ATOMIC|AUTHORIZATION|AVRO|BEGIN_FRAME|BEGIN_PARTITION|BETWEEN|BINARY|BLOB|BLOCK_SIZE|BOTH|BY|CACHED|CALLED|CARDINALITY|CASCADE|CASCADED|CASE|CAST|CHANGE|CHARACTER|CLASS|CLOB|CLOSE_FN|COLLATE|COLLECT|COLUMN|COLUMNS|COMMENT|COMMIT|COMPRESSION|COMPUTE|CONDITION|CONNECT|CONSTRAINT|CONTAINS|CONVERT|COPY|CORR|CORRESPONDING|COVAR_POP|COVAR_SAMP|CREATE|CROSS|CUBE|CURRENT|CURRENT_DATE|CURRENT_DEFAULT_TRANSFORM_GROUP|CURRENT_PATH|CURRENT_ROLE|CURRENT_ROW|CURRENT_SCHEMA|CURRENT_TIME|CURRENT_TRANSFORM_GROUP_FOR_TYPE|CURSOR|CYCLE|DATA|DATABASE|DATABASES|DATE|DATETIME|DEALLOCATE|DEC|DECFLOAT|DECLARE|DEFAULT|DEFINE|DELETE|DELIMITED|DEREF|DESC|DESCRIBE|DETERMINISTIC|DISCONNECT|DISTINCT|DIV|DROP|DYNAMIC|EACH|ELEMENT|ELSE|EMPTY|ENCODING|END|END_FRAME|END_PARTITION|EQUALS|ESCAPE|ESCAPED|EVERY|EXCEPT|EXEC|EXECUTE|EXISTS|EXPLAIN|EXTENDED|EXTERNAL|FETCH|FIELDS|FILEFORMAT|FILES|FILTER|FINALIZE_FN|FIRST|FOLLOWING|FOR|FOREIGN|FORMAT|FORMATTED|FRAME_ROW|FREE|FROM|FULL|FUNCTION|FUNCTIONS|FUSION|GET|GLOBAL|GRANT|GROUP|GROUPING|GROUPS|HASH|HAVING|HOLD|IF|IGNORE|ILIKE|IN|INCREMENTAL|INDICATOR|INIT_FN|INITIAL|INNER|INOUT|INPATH|INSENSITIVE|INSERT|INTEGER|INTERMEDIATE|INTERSECT|INTERSECTION|INTERVAL|INTO|INVALIDATE|IREGEXP|IS|JOIN|JSON_ARRAY|JSON_ARRAYAGG|JSON_EXISTS|JSON_OBJECT|JSON_OBJECTAGG|JSON_QUERY|JSON_TABLE|JSON_TABLE_PRIMITIVE|JSON_VALUE|KEY|LARGE|LAST|LATERAL|LEADING|LEFT|LIKE|LIKE_REGEX|LIMIT|LINES|LISTAGG|LOAD|LOCAL|LOCALTIMESTAMP|LOCATION|MATCH|MATCH_NUMBER|MATCH_RECOGNIZE|MATCHES|MERGE|MERGE_FN|METADATA|METHOD|MODIFIES|MULTISET|NATIONAL|NATURAL|NCHAR|NCLOB|NO|NONE|NORMALIZE|NOT|NTH_VALUE|NULLS|NUMERIC|OCCURRENCES_REGEX|OCTET_LENGTH|OF|OFFSET|OMIT|ON|ONE|ONLY|OR|ORDER|OUT|OUTER|OVER|OVERLAPS|OVERLAY|OVERWRITE|PARQUET|PARTITION|PARTITIONED|PARTITIONS|PATTERN|PER|PERCENT|PERCENTILE_CONT|PERCENTILE_DISC|PORTION|POSITION|POSITION_REGEX|PRECEDES|PRECEDING|PREPARE|PREPARE_FN|PRIMARY|PROCEDURE|PRODUCED|PTF|PURGE|RANGE|READS|RECOVER|RECURSIVE|REF|REFERENCES|REFERENCING|REFRESH|REGEXP|REGR_AVGX|REGR_AVGY|REGR_COUNT|REGR_INTERCEPT|REGR_R2REGR_SLOPE|REGR_SXX|REGR_SXY|REGR_SYY|RELEASE|RENAME|REPEATABLE|REPLACE|REPLICATION|RESTRICT|RETURNS|REVOKE|RIGHT|RLIKE|ROLE|ROLES|ROLLBACK|ROLLUP|ROW|ROWS|RUNNING|SAVEPOINT|SCHEMA|SCHEMAS|SCOPE|SCROLL|SEARCH|SEEK|SELECT|SEMI|SENSITIVE|SERDEPROPERTIES|SERIALIZE_FN|SET|SHOW|SIMILAR|SKIP|SOME|SORT|SPECIFIC|SPECIFICTYPE|SQLEXCEPTION|SQLSTATE|SQLWARNING|STATIC|STATS|STORED|STRAIGHT_JOIN|SUBMULTISET|SUBSET|SUBSTRING_REGEX|SUCCEEDS|SYMBOL|SYMMETRIC|SYSTEM_TIME|SYSTEM_USER|TABLE|TABLES|TABLESAMPLE|TBLPROPERTIES|TERMINATED|THEN|TIMEZONE_HOUR|TIMEZONE_MINUTE|TO|TRAILING|TRANSLATE_REGEX|TRANSLATION|TREAT|TRIGGER|TRIM_ARRAY|TRUNCATE|UESCAPE|UNBOUNDED|UNCACHED|UNION|UNIQUE|UNNEST|UPDATE|UPDATE_FN|UPSERT|USE|USING|VALUE_OF|VALUES|VARBINARY|VARYING|VERSIONING|VIEW|WHEN|WHENEVER|WHERE|WIDTH_BUCKET|WINDOW|WITH|WITHIN|WITHOUT"
    );

    var builtinConstants = (
        "DAY|DAYS|FALSE|HOUR|HOURS|MINUTE|MINUTES|MICROSECOND|MICROSECONDS|MILLISECOND|MILLISECONDS|MONTH|MONTHS|NANOSECOND|NANOSECONDS|NULL|SECOND|SECONDS|TRUE|UNKNOWN|WEEK|WEEKS|YEAR|YEARS"
    );

    var builtinFunctions = (
        "ABS|ACOS|ADD_MONTHS|ADDDATE|APPX_MEDIAN|ASCII|ASIN|ATAN|AVG|BIN|CAST|CEIL|CEILING|CHAR_LENGTH|CHARACTER_LENGTH|COALESCE|CONCAT|CONCAT_WS|CONV|COS|COUNT|CURRENT_DATABASE|CURRENT_TIMESTAMP|DATE_ADD|DATE_PART|DATE_SUB|DATEDIFF|DAY|DAYNAME|DAYOFMONTH|DAYOFWEEK|DAYOFYEAR|DAYS_ADD|DAYS_SUB|DECODE|DEGREES|DENSE_RANK|E|EXP|EXTRACT|FIND_IN_SET|FIRST_VALUE|FLOOR|FMOD|FNV_HASH|FROM_UNIXTIME|FROM_UTC_TIMESTAMP|GREATEST|GROUP_CONCAT|HEX|HOUR|HOURS_ADD|HOURS_SUB|IF|IFNULL|INITCAP|INSTR|IS_INF|IS_NAN|ISNULL|LAG|LAST_VALUE|LCASE|LEAD|LEAST|LENGTH|LN|LOCATE|LOG|LOG10|LOG2|LOWER|LPAD|LTRIM|MAX|MAX_BIGINT|MAX_INT|MAX_SMALLINT|MAX_TINYINT|MICROSECONDS_ADD|MICROSECONDS_SUB|MILLISECONDS_ADD|MILLISECONDS_SUB|MIN|MIN_BIGINT|MIN_INT|MIN_SMALLINT|MIN_TINYINT|MINUTE|MINUTES_ADD|MINUTES_SUB|MONTH|MONTHS_ADD|MONTHS_SUB|NANOSECONDS_ADD|NANOSECONDS_SUB|NDV|NEGATIVE|NOW|NULLIF|NULLIFZERO|NVL|PARSE_URL|PI|PID|PMOD|POSITIVE|POW|POWER|PRECISION|QUOTIENT|RADIANS|RAND|RANK|REGEXP_EXTRACT|REGEXP_REPLACE|REPEAT|REVERSE|ROUND|ROW_NUMBER|RPAD|RTRIM|SCALE|SECOND|SECONDS_ADD|SECONDS_SUB|SIGN|SIN|SPACE|SQRT|STDDEV|STDDEV_POP|STDDEV_SAMP|STRLEFT|STRRIGHT|SUBDATE|SUBSTR|SUBSTRING|SUM|TAN|TO_DATE|TO_UTC_TIMESTAMP|TRANSLATE|TRIM|TRUNC|UCASE|UNHEX|UNIX_TIMESTAMP|UPPER|USER|VAR_POP|VAR_SAMP|VARIANCE|VARIANCE_POP|VARIANCE_SAMP|VERSION|WEEKOFYEAR|WEEKS_ADD|WEEKS_SUB|YEAR|YEARS_ADD|YEARS_SUB|ZEROIFNULL"
    );

    var dataTypes = (
        "ARRAY|BIGINT|BOOLEAN|CHAR|DECIMAL|DOUBLE|FLOAT|INT|KUDU|MAP|PARQUETFILE|REAL|SEQUENCEFILE|RCFILE|SMALLINT|STRING|STRUCT|TEXTFILE|TIMESTAMP|TINYINT|VARCHAR"
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

ace.define("ace/mode/impala",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/impala_highlight_rules","ace/mode/folding/sqlserver"], function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextMode = require("./text").Mode;
var ImpalaHighlightRules = require("./impala_highlight_rules").ImpalaHighlightRules;
var FoldMode = require("./folding/sqlserver").FoldMode;

var Mode = function() {
    this.HighlightRules = ImpalaHighlightRules;
    this.foldingRules = new FoldMode();
};
oop.inherits(Mode, TextMode);

(function() {
    this.lineCommentStart = "--";
    this.$id = "ace/mode/impala";

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
