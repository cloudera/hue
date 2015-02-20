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

  var keywords, keywordsU, keywordsL;

  function getKeywords(editor) {
    var mode = editor.doc.modeOption;
    if (mode === "sql") mode = "text/x-sql";
    var _keywordsObj = CodeMirror.resolveMode(mode).keywords;
    var _keywords = "";
    for (var keyword in _keywordsObj) {
      _keywords += keyword.toUpperCase() + " ";
    }
    return _keywords;
  }

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

  CodeMirror.sqlHint = function (editor) {
    keywords = getKeywords(editor);
    keywordsU = keywords.split(" ");
    keywordsL = keywords.toLowerCase().split(" ");
    return scriptHint(editor, keywords, function (e, cur) {
      return e.getTokenAt(cur);
    });
  };

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
      if (obj.indexOf(".") == 0) {
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
          forEach(keywordsU, maybeAdd);
          forEach(keywordsL, maybeAdd);

        }
        else {
          forEach(catalogTablesL, maybeAddToExtra);
          forEach(keywordsU, maybeAdd);
          forEach(keywordsL, maybeAdd);
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
