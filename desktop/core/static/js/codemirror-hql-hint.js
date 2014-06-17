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

(function () {
  function forEach(arr, f) {
    for (var i = 0, e = arr.length; i < e; ++i) f(arr[i]);
  }

  function arrayContains(arr, item) {
    if (!Array.prototype.indexOf) {
      var i = arr.length;
      while (i--) {
        if (arr[i] === item) {
          return true;
        }
      }
      return false;
    }
    return arr.indexOf(item) != -1;
  }

  function scriptHint(editor, _keywords, getToken) {
    // Find the token at the cursor
    var cur = editor.getCursor(), token = getToken(editor, cur), tprop = token;

    // If it's not a 'word-style' or dot token, ignore the token.
    if (!/^[\.\w$_]*$/.test(token.string)) {
      token = tprop = {start: cur.ch, end: cur.ch, string: "", state: token.state,
        className: token.string == "." ? "hiveql-type" : null};
    }

    if (!context) var context = [];
    context.push(tprop);

    var completionList = getCompletions(token, context);
    //prevent autocomplete for last word, instead show dropdown with one word
    if (completionList.length == 1) {
      completionList.push(" ");
    }

    return {list: completionList,
      from: CodeMirror.Pos(cur.line, token.start),
      to: CodeMirror.Pos(cur.line, token.end)};
  }

  CodeMirror.catalogTables = "";
  CodeMirror.catalogFields = "";
  CodeMirror.possibleTable = false;
  CodeMirror.possibleSoloField = false;
  CodeMirror.tableFieldMagic = false;

  CodeMirror.hiveQLHint = function (editor) {
    return scriptHint(editor, hiveQLKeywordsU, function (e, cur) {
      return e.getTokenAt(cur);
    });
  };

  var hiveQLKeywords = "ADD AFTER ALL ALTER ANALYZE AND ARCHIVE AS ASC BETWEEN BUCKET BUCKETS BY CASCADE CHANGE CLI CLUSTER CLUSTERED COALESCE COLLECTION COLUMN COLUMNS COMMENT COMPUTE CREATE CROSS DATA DATABASE DATABASES DBPROPERTIES DEFERRED DELIMITED DEPENDENCY DESC DESCRIBE DIRECTORY DISABLE DISTINCT DISTRIBUTE DOT DROP ENABLE ESCAPED EXISTS EXPLAIN EXPORT EXTENDED EXTERNAL FIELDS FILEFORMAT FIRST FORMAT FORMATTED FROM FULL FUNCTION FUNCTIONS GRANT GROUP HAVING IDXPROPERTIES IF IGNORE IMPORT IN INDEX INDEXES INPATH INSERT INTO IS ITEMS JOIN KEYS LATERAL LEFT LIKE LIMIT LINES LOAD LOCAL LOCATION LOCKS MAP MAPJOIN MSCK NOT OF OFFLINE ON OPTION ORDER OUT OUTER OVERWRITE PARTITION PARTITIONED PARTITIONS PERCENT PRIVILEGES PROTECTION REBUILD RECORDREADER RECOVER REDUCE REGEXP RENAME REPAIR REPLACE RESTRICT REVOKE RIGHT RLIKE ROLE ROW SCHEMA SCHEMAS SELECT SEMI SEPARATED SERDE SERDEPROPERTIES SET SHOW SKEWED SORT SORTED STATISTICS STORED SUM TABLE TABLES TABLESAMPLE TBLPROPERTIES TEMPORARY TERMINATED TO TOUCH TRANSFORM TRUNCATE UNARCHIVE UNION US USER USING VIEW WHERE WITH";
  var hiveQLKeywordsU = hiveQLKeywords.split(" ");
  var hiveQLKeywordsL = hiveQLKeywords.toLowerCase().split(" ");

  var hiveQLKeywordsAfterTables = "JOIN ON WHERE ORDER BY ASC DESC LIMIT COMPUTE STATISTICS";
  var hiveQLKeywordsAfterTablesU = hiveQLKeywordsAfterTables.split(" ");
  var hiveQLKeywordsAfterTablesL = hiveQLKeywordsAfterTables.toLowerCase().split(" ");

  var hiveQLTypes = "TINYINT SMALLINT INT BIGINT BOOLEAN FLOAT DOUBLE STRING BINARY TIMESTAMP DECIMAL ARRAY MAP STRUCT UNIONTYPE DELIMITED SERDE SEQUENCEFILE TEXTFILE RCFILE INPUTFORMAT OUTPUTFORMAT";
  var hiveQLTypesU = hiveQLTypes.split(" ");
  var hiveQLTypesL = hiveQLTypes.toLowerCase().split(" ");

  var hiveQLBuiltins = "ROUND FLOOR CEIL CEILING RAND EXP LN LOG10 LOG2 LOG POW POWER SQRT BIN HEX UNHEX CONV ABS PMOD SIN ASIN COS ACOS TAN ATAN DEGREES RADIANS POSITIVE NEGATIVE SIGN E PI SIZE MAP_KEYS MAP_VALUES ARRAY_CONTAINS SORT_ARRAY BINARY CAST FROM_UNIXTIME UNIX_TIMESTAMP TO_DATE YEAR MONTH DAY HOUR MINUTE SECOND WEEKOFYEAR DATEDIFF DATE_ADD DATE_SUB FROM_UTC_TIMESTAMP TO_UTC_TIMESTAMP ASCII CONCAT CONTEXT_NGRAMS CONCAT_WS FIND_IN_SET FORMAT_NUMBER GET_JSON_OBJECT IN_FILE INSTR LENGTH LOCATE LOWER LCASE LPAD LTRIM NGRAMS PARSE_URL PRINTF REGEXP_EXTRACT REGEXP_REPLACE REPEAT REVERSE RPAD RTRIM SENTENCES SPACE SPLIT STR_TO_MAP SUBSTR SUBSTRING TRANSLATE TRIM UPPER UCASE JAVA_METHOD REFLECT XPATH XPATH_SHORT XPATH_INT XPATH_LONG XPATH_FLOAT XPATH_DOUBLE XPATH_NUMBER XPATH_STRING COUNT SUM AVG MIN MAX VARIANCE VAR_SAMP STDEV_POP STDEV_SAMP COVAR_POP COVAR_SAMP CORR PERCENTILE PERCENTILE_APPROX HISTOGRAM_NUMERIC COLLECT_SET INLINE EXPLODE JSON_TUPLE PARSE_URL_TUPLE GET_JSON_OBJECT";
  var hiveQLBuiltinsU = hiveQLBuiltins.split(" ").join("() ").split(" ");
  var hiveQLBuiltinsL = hiveQLBuiltins.toLowerCase().split(" ").join("() ").split(" ");

  function getCompletions(token, context) {
    var catalogTablesL = CodeMirror.catalogTables.toLowerCase().split(" ");
    var catalogFieldsL = CodeMirror.catalogFields.toLowerCase().split(" ");

    var found = [], start = token.string, extraFound = [];

    function maybeAdd(str) {
      if (str.indexOf(start) == 0 && !arrayContains(found, str)) found.push(str);
    }

    function maybeAddToExtra(str) {
      var _match = str;
      if (_match.indexOf("fa-magic") > -1) {
        _match = _match.substring(_match.indexOf("FROM ") + 5);
      }
      if (_match.indexOf(start) == 0 && !arrayContains(found, str)) extraFound.push(str);
    }

    function gatherCompletions(obj) {
      if (obj.indexOf(".") == 0 || obj.indexOf("(") == 0) {
        forEach(catalogFieldsL, maybeAdd);
      }
      else {
        if (!CodeMirror.possibleTable) {
          if (CodeMirror.tableFieldMagic) {
            var _specialCatalogTablesL = CodeMirror.catalogTables.toLowerCase().split(" ");
            for (var i = 0; i < _specialCatalogTablesL.length; i++) {
              _specialCatalogTablesL[i] = "<i class='fa fa-magic'></i> FROM " + _specialCatalogTablesL[i];
            }
            forEach(_specialCatalogTablesL, maybeAddToExtra);
          }
          if (CodeMirror.possibleSoloField) {
            forEach(catalogFieldsL, maybeAddToExtra);
          }
          forEach(hiveQLBuiltinsU, maybeAdd);
          forEach(hiveQLBuiltinsL, maybeAdd);
          forEach(hiveQLTypesU, maybeAdd);
          forEach(hiveQLTypesL, maybeAdd);
          forEach(hiveQLKeywordsU, maybeAdd);
          forEach(hiveQLKeywordsL, maybeAdd);

        }
        else {
          forEach(catalogTablesL, maybeAddToExtra);
          forEach(hiveQLKeywordsAfterTablesU, maybeAdd);
          forEach(hiveQLKeywordsAfterTablesL, maybeAdd);
        }
      }
    }

    if (context) {
      // If this is a property, see if it belongs to some object we can
      // find in the current environment.
      var obj = context.pop(), base;
      base = obj.string;

      while (base != null && context.length)
        base = base[context.pop().string];
      if (base != null) gatherCompletions(base);
    }
    return extraFound.sort().concat(found.sort());
  }
})();
