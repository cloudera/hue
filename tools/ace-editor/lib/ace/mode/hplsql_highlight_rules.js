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
  
    var HplsqlHighlightRules = function () {
      // regexp must not have capturing parentheses. Use (?:) instead.
      // regexps are ordered -> the first match is used
  
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
  