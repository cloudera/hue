ace.define("ace/mode/sparksql_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"], function (require, exports, module) {
  "use strict";

  var oop = require("../lib/oop");
  var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;

  var SparksqlHighlightRules = function () {

    var keywords =
      'ADD|AFTER|ALL|ALTER|ANALYZE|AND|ANTI|ANY|ARCHIVE|AS|ASC|AT|AUTHORIZATION|BETWEEN|BOTH|BUCKET|BUCKETS|BY|CACHE|' +
      'CASCADE|CASE|CAST|CATALOG|CATALOGS|CHANGE|CHECK|CLEAR|CLUSTER|CLUSTERED|CODEGEN|COLLATE|COLLECTION|COLUMN|' +
      'COLUMNS|COMMENT|COMMIT|COMPACT|COMPACTIONS|COMPUTE|CONCATENATE|CONSTRAINT|COST|CREATE|CROSS|CUBE|CURRENT|' +
      'CURRENT_DATE|CURRENT_TIME|CURRENT_TIMESTAMP|CURRENT_USER|DATA|DATABASE|DATABASES|DATEADD|DATEDIFF|DAYOFYEAR|' +
      'DBPROPERTIES|DEFINED|DELETE|DELIMITED|DESC|DESCRIBE|DFS|DIRECTORIES|DIRECTORY|DISTINCT|DISTRIBUTE|DIV|DROP|' +
      'ELSE|END|ESCAPE|ESCAPED|EXCEPT|EXCHANGE|EXISTS|EXPLAIN|EXPORT|EXTENDED|EXTERNAL|EXTRACT|FETCH|FIELDS|' +
      'FILEFORMAT|FILTER|FIRST|FOLLOWING|FOR|FOREIGN|FORMAT|FORMATTED|FROM|FULL|FUNCTION|FUNCTIONS|GLOBAL|GRANT|' +
      'GROUP|GROUPING|HAVING|IF|IGNORE|ILIKE|IMPORT|IN|INDEX|INDEXES|INNER|INPATH|INPUTFORMAT|INSERT|INTERSECT|' +
      'INTERVAL|INTO|IS|ITEMS|JOIN|KEYS|LAST|LATERAL|LAZY|LEADING|LEFT|LIKE|LIMIT|LINES|LIST|LOAD|LOCAL|LOCATION|' +
      'LOCK|LOCKS|LOGICAL|MACRO|MATCHED|MERGE|MICROSECOND|MILLISECOND|MINUS|MSCK|NAMESPACE|NAMESPACES|NATURAL|NO|NOT|' +
      'NULLS|OF|ON|ONLY|OPTION|OPTIONS|OR|ORDER|OUT|OUTER|OUTPUTFORMAT|OVER|OVERLAPS|OVERLAY|OVERWRITE|PARTITION|' +
      'PARTITIONED|PARTITIONS|PERCENT|PERCENTILE_CONT|PERCENTILE_DISC|PIVOT|PLACING|POSITION|PRECEDING|PRIMARY|' +
      'PRINCIPALS|PROPERTIES|PURGE|QUARTER|QUERY|RANGE|RECORDREADER|RECORDWRITER|RECOVER|REDUCE|REFERENCES|REFRESH|' +
      'REGEXP|RENAME|REPAIR|REPEATABLE|REPLACE|RESET|RESPECT|RESTRICT|REVOKE|RIGHT|RLIKE|ROLE|ROLES|ROLLBACK|ROLLUP|' +
      'ROW|ROWS|SCHEMA|SCHEMAS|SELECT|SEMI|SEPARATED|SERDE|SERDEPROPERTIES|SESSION_USER|SET|SETS|SHOW|SKEWED|SOME|' +
      'SORT|SORTED|START|STATISTICS|STORED|STRATIFY|SUBSTR|SUBSTRING|SYNC|SYSTEM_TIME|SYSTEM_VERSION|TABLE|TABLES|' +
      'TABLESAMPLE|TBLPROPERTIES|TEMP|TEMPORARY|TERMINATED|THEN|TIME|TIMESTAMPADD|TIMESTAMPDIFF|TO|TOUCH|TRAILING|' +
      'TRANSACTION|TRANSACTIONS|TRANSFORM|TRIM|TRUNCATE|TRY_CAST|TYPE|UNARCHIVE|UNBOUNDED|UNCACHE|UNION|UNIQUE|' +
      'UNKNOWN|UNLOCK|UNSET|UPDATE|USE|USER|USING|VALUES|VERSION|VIEW|VIEWS|WEEK|WHEN|WHERE|WINDOW|WITH|WITHIN|ZONE';

    var builtinConstants =
      'AVRO|DAY|FALSE|HOUR|KUDU|MINUTE|MONTH|NULL|ORC|PARQUET|RCFILE|SECOND|SEQUENCEFILE|TEXTFILE|TRUE|YEAR';

    var builtinFunctions =
      'ABS|ACOS|ACOSH|ADD_MONTHS|AES_DECRYPT|AES_ENCRYPT|ANY|APPROX_COUNT_DISTINCT|APPROX_PERCENTILE|ARRAY|ARRAY_AGG|' +
      'ARRAY_CONTAINS|ARRAY_DISTINCT|ARRAY_EXCEPT|ARRAY_INTERSECT|ARRAY_JOIN|ARRAY_MAX|ARRAY_MIN|ARRAY_POSITION|' +
      'ARRAY_REMOVE|ARRAY_REPEAT|ARRAY_UNION|ARRAYS_OVERLAP|ARRAYS_ZIP|ASCII|ASIN|ASINH|ASSERT_TRUE|ATAN|ATAN2|ATANH|' +
      'AVG|BASE64|BIGINT|BIN|BINARY|BIT_AND|BIT_COUNT|BIT_GET|BIT_LENGTH|BIT_OR|BIT_XOR|BOOL_AND|BOOL_OR|BOOLEAN|' +
      'BROUND|BTRIM|CAST|CBRT|CEIL|CEILING|CHAR|CHAR_LENGTH|CHARACTER_LENGTH|CHR|COALESCE|COLLECT_LIST|COLLECT_SET|' +
      'CONCAT_WS|CONTAINS|CONV|CORR|COS|COSH|COT|COUNT|COUNT_MIN_SKETCH|COVAR_POP|COVAR_SAMP|CSC|CUME_DIST|' +
      'CURRENT_CATALOG|CURRENT_DATABASE|CURRENT_DATE|CURRENT_TIMESTAMP|CURRENT_TIMEZONE|CURRENT_USER|DATE|DATE_ADD|' +
      'DATE_FORMAT|DATE_FROM_UNIX_DATE|DATE_PART|DATE_SUB|DATE_TRUNC|DATEDIFF|DAY|DAYOFMONTH|DAYOFWEEK|DAYOFYEAR|' +
      'DECIMAL|DECODE|DEGREES|DENSE_RANK|DOUBLE|E|ELEMENT_AT|ELT|ENCODE|ENDSWITH|EVERY|EXP|EXPLODE|EXPLODE_OUTER|' +
      'EXPM1|EXPR1|EXTRACT|FACTORIAL|FIND_IN_SET|FIRST|FIRST_VALUE|FLATTEN|FLOAT|FLOOR|FORMAT_NUMBER|FORMAT_STRING|' +
      'FROM_JSON|FROM_UNIXTIME|FROM_UTC_TIMESTAMP|GET_JSON_OBJECT|GETBIT|GREATEST|GROUPING|GROUPING_ID|HEX|' +
      'HISTOGRAM_NUMERIC|HOUR|HYPOT|IF|IFNULL|INITCAP|INLINE|INLINE_OUTER|INPUT_FILE_BLOCK_LENGTH|' +
      'INPUT_FILE_BLOCK_START|INPUT_FILE_NAME|INSTR|INT|ISNAN|ISNOTNULL|ISNULL|JAVA_METHOD|JSON_ARRAY_LENGTH|' +
      'JSON_OBJECT_KEYS|JSON_TUPLE|KURTOSIS|LAG|LAST|LAST_DAY|LAST_VALUE|LCASE|LEAD|LEAST|LEFT|LENGTH|LEVENSHTEIN|LN|' +
      'LOCATE|LOG|LOG10|LOG1P|LOG2|LOWER|LPAD|LTRIM|MAKE_DATE|MAKE_DT_INTERVAL|MAKE_INTERVAL|MAKE_TIMESTAMP|' +
      'MAKE_YM_INTERVAL|MAP|MAP_CONCAT|MAP_CONTAINS_KEY|MAP_ENTRIES|MAP_FROM_ARRAYS|MAP_FROM_ENTRIES|MAP_KEYS|' +
      'MAP_VALUES|MAX|MAX_BY|MEAN|MIN|MIN_BY|MINUTE|MONOTONICALLY_INCREASING_ID|MONTH|MONTHS_BETWEEN|NANVL|NEGATIVE|' +
      'NEXT_DAY|NOW|NTH_VALUE|NTILE|NULLIF|NVL|NVL2|OCTET_LENGTH|OVERLAY|PARSE_URL|PERCENT_RANK|PERCENTILE|' +
      'PERCENTILE_APPROX|PI|PMOD|POSEXPLODE|POSEXPLODE_OUTER|POSITION|POSITIVE|POW|POWER|PRINTF|QUARTER|RADIANS|RAND|' +
      'RANDN|RANDOM|RANK|REFLECT|REGEXP|REGEXP_EXTRACT|REGEXP_EXTRACT_ALL|REGEXP_LIKE|REGEXP_REPLACE|REGR_AVGX|' +
      'REGR_AVGY|REGR_COUNT|REGR_R2|REPEAT|REPLACE|RIGHT|RINT|RLIKE|ROUND|ROW_NUMBER|RPAD|RTRIM|SCHEMA_OF_JSON|SEC|' +
      'SECOND|SENTENCES|SEQUENCE|SESSION_WINDOW|SHIFTLEFT|SHIFTRIGHT|SHIFTRIGHTUNSIGNED|SHUFFLE|SIGN|SIGNUM|SIN|SINH|' +
      'SKEWNESS|SLICE|SMALLINT|SOME|SORT_ARRAY|SOUNDEX|SPACE|SPARK_PARTITION_ID|SPLIT|SPLIT_PART|SQRT|STACK|' +
      'STARTSWITH|STD|STDDEV|STDDEV_POP|STDDEV_SAMP|STR_TO_MAP|STRING|SUBSTR|SUBSTRING|SUBSTRING_INDEX|SUM|TAN|TANH|' +
      'TIMESTAMP|TIMESTAMP_MICROS|TIMESTAMP_MILLIS|TIMESTAMP_SECONDS|TINYINT|TO_BINARY|TO_DATE|TO_JSON|TO_NUMBER|' +
      'TO_TIMESTAMP|TO_UNIX_TIMESTAMP|TO_UTC_TIMESTAMP|TRANSLATE|TRIM|TRUNC|TRY_ADD|TRY_AVG|TRY_DIVIDE|' +
      'TRY_ELEMENT_AT|TRY_MULTIPLY|TRY_SUBTRACT|TRY_SUM|TRY_TO_BINARY|TRY_TO_NUMBER|TYPEOF|UCASE|UNBASE64|UNHEX|' +
      'UNIX_DATE|UNIX_MICROS|UNIX_MILLIS|UNIX_SECONDS|UNIX_TIMESTAMP|UPPER|UUID|VAR_POP|VAR_SAMP|VARIANCE|VERSION|' +
      'WEEKDAY|WEEKOFYEAR|WIDTH_BUCKET|WINDOW|YEAR';

    var dataTypes =
      'ARRAY|BIGINT|BINARY|BOOLEAN|BYTE|DATE|DEC|DECIMAL|DOUBLE|FLOAT|INT|INTEGER|LONG|MAP|NUMERIC|REAL|SHORT|' +
      'SMALLINT|STRING|STRUCT|TIMESTAMP|TINYINT';

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

  SparksqlHighlightRules.metaData = {
    fileTypes: ["hql", "q", "ql"],
    name: "Sparksql",
    scopeName: "source.sparksql"
  };

  oop.inherits(SparksqlHighlightRules, TextHighlightRules);

  exports.SparksqlHighlightRules = SparksqlHighlightRules;
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

ace.define("ace/mode/sparksql",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/sparksql_highlight_rules","ace/mode/folding/sqlserver"], function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextMode = require("./text").Mode;
var SparksqlHighlightRules = require("./sparksql_highlight_rules").SparksqlHighlightRules;
var FoldMode = require("./folding/sqlserver").FoldMode;

var Mode = function() {
    this.HighlightRules = SparksqlHighlightRules;
    this.foldingRules = new FoldMode();
};
oop.inherits(Mode, TextMode);

(function() {
    this.lineCommentStart = "--";
    this.$id = "ace/mode/sparksql"

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
