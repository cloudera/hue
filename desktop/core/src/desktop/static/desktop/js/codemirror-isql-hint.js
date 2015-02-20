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
        className: token.string == "." ? "impalasql-type" : null};
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

  CodeMirror.impalaSQLHint = function (editor) {
    return scriptHint(editor, impalaSQLKeywordsU, function (e, cur) {
      return e.getTokenAt(cur);
    });
  };

  var impalaSQLKeywords = "add aggregate all and api_version as avro binary by cached case change char class close_fn column columns comment compute create cross data database databases decimal delimited describe distinct div drop else end escaped exists explain external false fields fileformat finalize_fn first format formatted from full function functions group having if init_fn inner inpath insert integer intermediate interval into invalidate join last left like limit lines load location merge_fn metadata not null nulls offset or order outer overwrite parquet partition partitioned partitions prepare_fn produced real refresh regexp rename replace returns right rlike row schema schemas select semi serdeproperties serialize_fn show stats stored straight_join symbol table tables tblproperties terminated then to true uncached union update_fn use using view when where with";
  var impalaSQLKeywordsU = impalaSQLKeywords.toUpperCase().split(" ");
  var impalaSQLKeywordsL = impalaSQLKeywords.toLowerCase().split(" ");

  var impalaSQLKeywordsAfterTables = "JOIN ON WHERE ORDER BY ASC DESC LIMIT";
  var impalaSQLKeywordsAfterTablesU = impalaSQLKeywordsAfterTables.toUpperCase().split(" ");
  var impalaSQLKeywordsAfterTablesL = impalaSQLKeywordsAfterTables.toLowerCase().split(" ");

  var impalaSQLTypes = "DATE DATETIME TINYINT SMALLINT INT BIGINT BOOLEAN FLOAT DOUBLE STRING TIMESTAMP PARQUETFILE SEQUENCEFILE TEXTFILE RCFILE";
  var impalaSQLTypesU = impalaSQLTypes.toUpperCase().split(" ");
  var impalaSQLTypesL = impalaSQLTypes.toLowerCase().split(" ");

  var impalaSQLBuiltins = "ABS ACOS ASCII ASIN ATAN AVG BIN CAST CEIL CEILING COALESCE CONCAT CONCAT_WS COUNT CONV COS DATE_ADD DATE_SUB DATEDIFF DAY DAYNAME DAYOFMONTH DAYOFWEEK DEGREES E EXP FIND_IN_SET FLOOR FNV_HASH FROM_UNIXTIME FROM_UTC_TIMESTAMP GREATEST GROUP_CONCAT HEX HOUR IF INITCAP INSTR ISNULL LCASE LEAST LENGTH LN LOCATE LOG LOG10 LOG2 LOWER LPAD LTRIM MAX MIN MINUTE MONTH NDV NEGATIVE NOW NVL PARSE_URL PI PMOD POSITIVE POW POWER QUOTIENT RADIANS RAND REGEXP_EXTRACT REPEAT REVERSE ROUND RPAD RTRIM SECOND SIGN SIN SPACE SQRT SUBSTR SUBSTRING SUM TAN TO_DATE TO_UTC_TIMESTAMP TRANSLATE TRIM UCASE UNHEX UNIX_TIMESTAMP UPPER USER WEEKOFYEAR YEAR";
  var impalaSQLBuiltinsU = impalaSQLBuiltins.toUpperCase().split(" ").join("() ").split(" ");
  var impalaSQLBuiltinsL = impalaSQLBuiltins.toLowerCase().split(" ").join("() ").split(" ");

  var impalaSQLAnalytics = "dense_rank first_value lag last_value lead over rank row_number window";
  var impalaSQLAnalyticsU = impalaSQLAnalytics.toUpperCase().split(" ").join("() ").split(" ");
  var impalaSQLAnalyticsL = impalaSQLAnalytics.toLowerCase().split(" ").join("() ").split(" ");

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
          forEach(impalaSQLBuiltinsU, maybeAdd);
          forEach(impalaSQLBuiltinsL, maybeAdd);
          forEach(impalaSQLTypesU, maybeAdd);
          forEach(impalaSQLTypesL, maybeAdd);
          forEach(impalaSQLKeywordsU, maybeAdd);
          forEach(impalaSQLKeywordsL, maybeAdd);
          forEach(impalaSQLAnalyticsU, maybeAdd);
          forEach(impalaSQLAnalyticsL, maybeAdd);
        }
        else {
          forEach(catalogTablesL, maybeAddToExtra);
          forEach(impalaSQLKeywordsAfterTablesU, maybeAdd);
          forEach(impalaSQLKeywordsAfterTablesL, maybeAdd);
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
