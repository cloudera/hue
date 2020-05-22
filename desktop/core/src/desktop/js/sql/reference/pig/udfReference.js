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

import I18n from 'utils/i18n';

const EVAL_FUNCTIONS = {
  avg: { signature: 'AVG(%VAR%)', draggable: 'AVG()' },
  concat: { signature: 'CONCAT(%VAR1%, %VAR2%)', draggable: 'CONCAT()' },
  count: { signature: 'COUNT(%VAR%)', draggable: 'COUNT()' },
  count_start: { signature: 'COUNT_START(%VAR%)', draggable: 'COUNT_START()' },
  is_empty: { signature: 'IsEmpty(%VAR%)', draggable: 'IsEmpty()' },
  diff: { signature: 'DIFF(%VAR1%, %VAR2%)', draggable: 'DIFF()' },
  max: { signature: 'MAX(%VAR%)', draggable: 'MAX()' },
  min: { signature: 'MIN(%VAR%)', draggable: 'MIN()' },
  size: { signature: 'SIZE(%VAR%)', draggable: 'SIZE()' },
  sum: { signature: 'SUM(%VAR%)', draggable: 'SUM()' },
  tokenize: { signature: 'TOKENIZE(%VAR%, %DELIM%)', draggable: 'TOKENIZE()' }
};

const RELATIONAL_OPERATORS = {
  cogroup: { signature: 'COGROUP %VAR% BY %VAR%', draggable: 'COGROUP %VAR% BY %VAR%' },
  cross: { signature: 'CROSS %VAR1%, %VAR2%;', draggable: 'CROSS %VAR1%, %VAR2%;' },
  distinct: { signature: 'DISTINCT %VAR%;', draggable: 'DISTINCT %VAR%;' },
  filter: { signature: 'FILTER %VAR% BY %COND%', draggable: 'FILTER %VAR% BY %COND%' },
  flatten: { signature: 'FLATTEN(%VAR%)', draggable: 'FLATTEN()' },
  foreach_generate: {
    signature: 'FOREACH %DATA% GENERATE %NEW_DATA%;',
    draggable: 'FOREACH %DATA% GENERATE %NEW_DATA%;'
  },
  foreach: {
    signature: 'FOREACH %DATA% {%NESTED_BLOCK%};',
    draggable: 'FOREACH %DATA% {%NESTED_BLOCK%};'
  },
  group_by: { signature: 'GROUP %VAR% BY %VAR%', draggable: 'GROUP %VAR% BY %VAR%' },
  group_all: { signature: 'GROUP %VAR% ALL', draggable: 'GROUP %VAR% ALL' },
  join: { signature: 'JOIN %VAR% BY ', draggable: 'JOIN %VAR% BY ' },
  limit: { signature: 'LIMIT %VAR% %N%', draggable: 'LIMIT %VAR% %N%' },
  order: { signature: 'ORDER %VAR% BY %FIELD%', draggable: 'ORDER %VAR% BY %FIELD%' },
  sample: { signature: 'SAMPLE %VAR% %SIZE%', draggable: 'SAMPLE %VAR% %SIZE%' },
  split: {
    signature: 'SPLIT %VAR1% INTO %VAR2% IF %EXPRESSIONS%',
    draggable: 'SPLIT %VAR1% INTO %VAR2% IF %EXPRESSIONS%'
  },
  union: { signature: 'UNION %VAR1%, %VAR2%', draggable: 'UNION %VAR1%, %VAR2%' }
};

const INPUT_OUTPUT = {
  load: { signature: "LOAD '%FILE%';", draggable: "LOAD '%FILE%';" },
  dump: { signature: 'DUMP %VAR%;', draggable: 'DUMP %VAR%;' },
  store: { signature: 'STORE %VAR% INTO %PATH%;', draggable: 'STORE %VAR% INTO %PATH%;' }
};

const DEBUG = {
  explain: { signature: 'EXPLAIN %VAR%;', draggable: 'EXPLAIN %VAR%;' },
  illustrate: { signature: 'ILLUSTRATE %VAR%;', draggable: 'ILLUSTRATE %VAR%;' },
  describe: { signature: 'DESCRIBE %VAR%;', draggable: 'DESCRIBE %VAR%;' }
};

const HCATALOG = {
  LOAD: {
    signature: "LOAD '%TABLE%' USING org.apache.hcatalog.pig.HCatLoader();",
    draggable: "LOAD '%TABLE%' USING org.apache.hcatalog.pig.HCatLoader();"
  }
};

const MATH_FUNCTIONS = {
  abs: { signature: 'ABS(%VAR%)', draggable: 'ABS()' },
  acos: { signature: 'ACOS(%VAR%)', draggable: 'ACOS()' },
  asin: { signature: 'ASIN(%VAR%)', draggable: 'ASIN()' },
  atan: { signature: 'ATAN(%VAR%)', draggable: 'ATAN()' },
  cbrt: { signature: 'CBRT(%VAR%)', draggable: 'CBRT()' },
  ceil: { signature: 'CEIL(%VAR%)', draggable: 'CEIL()' },
  cos: { signature: 'COS(%VAR%)', draggable: 'COS()' },
  cosh: { signature: 'COSH(%VAR%)', draggable: 'COSH()' },
  exp: { signature: 'EXP(%VAR%)', draggable: 'EXP()' },
  floor: { signature: 'FLOOR(%VAR%)', draggable: 'FLOOR()' },
  log: { signature: 'LOG(%VAR%)', draggable: 'LOG()' },
  log10: { signature: 'LOG10(%VAR%)', draggable: 'LOG10()' },
  random: { signature: 'RANDOM(%VAR%)', draggable: 'RANDOM()' },
  round: { signature: 'ROUND(%VAR%)', draggable: 'ROUND()' },
  sin: { signature: 'SIN(%VAR%)', draggable: 'SIN()' },
  sinh: { signature: 'SINH(%VAR%)', draggable: 'SINH()' },
  sqrt: { signature: 'SQRT(%VAR%)', draggable: 'SQRT()' },
  tan: { signature: 'TAN(%VAR%)', draggable: 'TAN()' },
  tanh: { signature: 'TANH(%VAR%)', draggable: 'TANH()' }
};

const TUPLE_BAG_MAP = {
  totuple: { signature: 'TOTUPLE(%VAR%)', draggable: 'TOTUPLE()' },
  tobag: { signature: 'TOBAG(%VAR%)', draggable: 'TOBAG()' },
  tomap: { signature: 'TOMAP(%KEY%, %VALUE%)', draggable: 'TOMAP()' },
  top: { signature: 'TOP(%topN%, %COLUMN%, %RELATION%)', draggable: 'TOP()' }
};

const STRING_FUNCTIONS = {
  indexof: {
    signature: "INDEXOF(%STRING%, '%CHARACTER%', %STARTINDEX%)",
    draggable: 'INDEXOF()'
  },
  last_index_of: {
    signature: "LAST_INDEX_OF(%STRING%, '%CHARACTER%', %STARTINDEX%)",
    draggable: 'LAST_INDEX_OF()'
  },
  lower: { signature: 'LOWER(%STRING%)', draggable: 'LOWER()' },
  regex_extract: {
    signature: 'REGEX_EXTRACT(%STRING%, %REGEX%, %INDEX%)',
    draggable: 'REGEX_EXTRACT()'
  },
  regex_extract_all: {
    signature: 'REGEX_EXTRACT_ALL(%STRING%, %REGEX%)',
    draggable: 'REGEX_EXTRACT_ALL()'
  },
  replace: { signature: "REPLACE(%STRING%, '%oldChar%', '%newChar%')", draggable: 'REPLACE()' },
  strsplit: { signature: 'STRSPLIT(%STRING%, %REGEX%, %LIMIT%)', draggable: 'STRSPLIT()' },
  substring: {
    signature: 'SUBSTRING(%STRING%, %STARTINDEX%, %STOPINDEX%)',
    draggable: 'SUBSTRING()'
  },
  trim: { signature: 'TRIM(%STRING%)', draggable: 'TRIM()' },
  ucfirst: { signature: 'UCFIRST(%STRING%)', draggable: 'UCFIRST()' },
  upper: { signature: 'UPPER(%STRING%)', draggable: 'UPPER()' }
};

const MACROS = {
  import: { signature: "IMPORT '%PATH_TO_MACRO%';", draggable: "IMPORT '%PATH_TO_MACRO%';" }
};

const HBASE = {
  load: {
    signature:
      "LOAD 'hbase://%TABLE%' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage('%columnList%')",
    draggable:
      "LOAD 'hbase://%TABLE%' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage('%columnList%')"
  },
  store: {
    signature:
      "STORE %VAR% INTO 'hbase://%TABLE%' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage('%columnList%')",
    draggable:
      "STORE %VAR% INTO 'hbase://%TABLE%' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage('%columnList%')"
  }
};

const PYTHON_UDF = {
  register: {
    signature: "REGISTER 'python_udf.py' USING jython AS myfuncs;",
    draggable: "REGISTER 'python_udf.py' USING jython AS myfuncs;"
  }
};

export const UDF_CATEGORIES = [
  { name: I18n('Eval'), functions: EVAL_FUNCTIONS },
  { name: I18n('Relational Operators'), functions: RELATIONAL_OPERATORS },
  { name: I18n('Input and Output'), functions: INPUT_OUTPUT },
  { name: I18n('Debug'), functions: DEBUG },
  { name: I18n('HCatalog'), functions: HCATALOG },
  { name: I18n('Math'), functions: MATH_FUNCTIONS },
  { name: I18n('Tuple, Bag and Map'), functions: TUPLE_BAG_MAP },
  { name: I18n('String'), functions: STRING_FUNCTIONS },
  { name: I18n('Macros'), functions: MACROS },
  { name: I18n('HBase'), functions: HBASE },
  { name: I18n('Python UDF'), functions: PYTHON_UDF }
];
