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

import { UdfCategory, UdfCategoryFunctions } from 'sql/reference/types';
import I18n from 'utils/i18n';

const EVAL_FUNCTIONS: UdfCategoryFunctions = {
  avg: {
    name: 'avg',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'AVG(%VAR%)',
    draggable: 'AVG()'
  },
  concat: {
    name: 'concat',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'CONCAT(%VAR1%, %VAR2%)',
    draggable: 'CONCAT()'
  },
  count: {
    name: 'count',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'COUNT(%VAR%)',
    draggable: 'COUNT()'
  },
  count_start: {
    name: 'count_start',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'COUNT_START(%VAR%)',
    draggable: 'COUNT_START()'
  },
  is_empty: {
    name: 'is_empty',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'IsEmpty(%VAR%)',
    draggable: 'IsEmpty()'
  },
  diff: {
    name: 'diff',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'DIFF(%VAR1%, %VAR2%)',
    draggable: 'DIFF()'
  },
  max: {
    name: 'max',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'MAX(%VAR%)',
    draggable: 'MAX()'
  },
  min: {
    name: 'min',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'MIN(%VAR%)',
    draggable: 'MIN()'
  },
  size: {
    name: 'size',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'SIZE(%VAR%)',
    draggable: 'SIZE()'
  },
  sum: {
    name: 'sum',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'SUM(%VAR%)',
    draggable: 'SUM()'
  },
  tokenize: {
    name: 'tokenize',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'TOKENIZE(%VAR%, %DELIM%)',
    draggable: 'TOKENIZE()'
  }
};

const RELATIONAL_OPERATORS: UdfCategoryFunctions = {
  cogroup: {
    name: 'cogroup',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'COGROUP %VAR% BY %VAR%',
    draggable: 'COGROUP %VAR% BY %VAR%'
  },
  cross: {
    name: 'cross',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'CROSS %VAR1%, %VAR2%;',
    draggable: 'CROSS %VAR1%, %VAR2%;'
  },
  distinct: {
    name: 'distinct',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'DISTINCT %VAR%;',
    draggable: 'DISTINCT %VAR%;'
  },
  filter: {
    name: 'filter',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'FILTER %VAR% BY %COND%',
    draggable: 'FILTER %VAR% BY %COND%'
  },
  flatten: {
    name: 'flatten',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'FLATTEN(%VAR%)',
    draggable: 'FLATTEN()'
  },
  foreach_generate: {
    name: 'foreach_generate',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'FOREACH %DATA% GENERATE %NEW_DATA%;',
    draggable: 'FOREACH %DATA% GENERATE %NEW_DATA%;'
  },
  foreach: {
    name: 'foreach',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'FOREACH %DATA% {%NESTED_BLOCK%};',
    draggable: 'FOREACH %DATA% {%NESTED_BLOCK%};'
  },
  group_by: {
    name: 'group_by',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'GROUP %VAR% BY %VAR%',
    draggable: 'GROUP %VAR% BY %VAR%'
  },
  group_all: {
    name: 'group_all',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'GROUP %VAR% ALL',
    draggable: 'GROUP %VAR% ALL'
  },
  join: {
    name: 'join',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'JOIN %VAR% BY ',
    draggable: 'JOIN %VAR% BY '
  },
  limit: {
    name: 'limit',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'LIMIT %VAR% %N%',
    draggable: 'LIMIT %VAR% %N%'
  },
  order: {
    name: 'order',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'ORDER %VAR% BY %FIELD%',
    draggable: 'ORDER %VAR% BY %FIELD%'
  },
  sample: {
    name: 'sample',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'SAMPLE %VAR% %SIZE%',
    draggable: 'SAMPLE %VAR% %SIZE%'
  },
  split: {
    name: 'split',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'SPLIT %VAR1% INTO %VAR2% IF %EXPRESSIONS%',
    draggable: 'SPLIT %VAR1% INTO %VAR2% IF %EXPRESSIONS%'
  },
  union: {
    name: 'union',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'UNION %VAR1%, %VAR2%',
    draggable: 'UNION %VAR1%, %VAR2%'
  }
};

const INPUT_OUTPUT: UdfCategoryFunctions = {
  load: {
    name: 'load',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: "LOAD '%FILE%';",
    draggable: "LOAD '%FILE%';"
  },
  dump: {
    name: 'dump',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'DUMP %VAR%;',
    draggable: 'DUMP %VAR%;'
  },
  store: {
    name: 'store',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'STORE %VAR% INTO %PATH%;',
    draggable: 'STORE %VAR% INTO %PATH%;'
  }
};

const DEBUG: UdfCategoryFunctions = {
  explain: {
    name: 'explain',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'EXPLAIN %VAR%;',
    draggable: 'EXPLAIN %VAR%;'
  },
  illustrate: {
    name: 'illustrate',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'ILLUSTRATE %VAR%;',
    draggable: 'ILLUSTRATE %VAR%;'
  },
  describe: {
    name: 'describe',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'DESCRIBE %VAR%;',
    draggable: 'DESCRIBE %VAR%;'
  }
};

const HCATALOG: UdfCategoryFunctions = {
  LOAD: {
    name: 'LOAD',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: "LOAD '%TABLE%' USING org.apache.hcatalog.pig.HCatLoader();",
    draggable: "LOAD '%TABLE%' USING org.apache.hcatalog.pig.HCatLoader();"
  }
};

const MATH_FUNCTIONS: UdfCategoryFunctions = {
  abs: {
    name: 'abs',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'ABS(%VAR%)',
    draggable: 'ABS()'
  },
  acos: {
    name: 'acos',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'ACOS(%VAR%)',
    draggable: 'ACOS()'
  },
  asin: {
    name: 'asin',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'ASIN(%VAR%)',
    draggable: 'ASIN()'
  },
  atan: {
    name: 'atan',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'ATAN(%VAR%)',
    draggable: 'ATAN()'
  },
  cbrt: {
    name: 'cbrt',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'CBRT(%VAR%)',
    draggable: 'CBRT()'
  },
  ceil: {
    name: 'ceil',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'CEIL(%VAR%)',
    draggable: 'CEIL()'
  },
  cos: {
    name: 'cos',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'COS(%VAR%)',
    draggable: 'COS()'
  },
  cosh: {
    name: 'cosh',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'COSH(%VAR%)',
    draggable: 'COSH()'
  },
  exp: {
    name: 'exp',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'EXP(%VAR%)',
    draggable: 'EXP()'
  },
  floor: {
    name: 'floor',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'FLOOR(%VAR%)',
    draggable: 'FLOOR()'
  },
  log: {
    name: 'log',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'LOG(%VAR%)',
    draggable: 'LOG()'
  },
  log10: {
    name: 'log10',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'LOG10(%VAR%)',
    draggable: 'LOG10()'
  },
  random: {
    name: 'random',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'RANDOM(%VAR%)',
    draggable: 'RANDOM()'
  },
  round: {
    name: 'round',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'ROUND(%VAR%)',
    draggable: 'ROUND()'
  },
  sin: {
    name: 'sin',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'SIN(%VAR%)',
    draggable: 'SIN()'
  },
  sinh: {
    name: 'sinh',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'SINH(%VAR%)',
    draggable: 'SINH()'
  },
  sqrt: {
    name: 'sqrt',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'SQRT(%VAR%)',
    draggable: 'SQRT()'
  },
  tan: {
    name: 'tan',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'TAN(%VAR%)',
    draggable: 'TAN()'
  },
  tanh: {
    name: 'tanh',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'TANH(%VAR%)',
    draggable: 'TANH()'
  }
};

const TUPLE_BAG_MAP: UdfCategoryFunctions = {
  totuple: {
    name: 'totuple',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'TOTUPLE(%VAR%)',
    draggable: 'TOTUPLE()'
  },
  tobag: {
    name: 'tobag',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'TOBAG(%VAR%)',
    draggable: 'TOBAG()'
  },
  tomap: {
    name: 'tomap',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'TOMAP(%KEY%, %VALUE%)',
    draggable: 'TOMAP()'
  },
  top: {
    name: 'top',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'TOP(%topN%, %COLUMN%, %RELATION%)',
    draggable: 'TOP()'
  }
};

const STRING_FUNCTIONS: UdfCategoryFunctions = {
  indexof: {
    name: 'indexof',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: "INDEXOF(%STRING%, '%CHARACTER%', %STARTINDEX%)",
    draggable: 'INDEXOF()'
  },
  last_index_of: {
    name: 'last_index_of',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: "LAST_INDEX_OF(%STRING%, '%CHARACTER%', %STARTINDEX%)",
    draggable: 'LAST_INDEX_OF()'
  },
  lower: {
    name: 'lower',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'LOWER(%STRING%)',
    draggable: 'LOWER()'
  },
  regex_extract: {
    name: 'regex_extract',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'REGEX_EXTRACT(%STRING%, %REGEX%, %INDEX%)',
    draggable: 'REGEX_EXTRACT()'
  },
  regex_extract_all: {
    name: 'regex_extract_all',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'REGEX_EXTRACT_ALL(%STRING%, %REGEX%)',
    draggable: 'REGEX_EXTRACT_ALL()'
  },
  replace: {
    name: 'replace',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: "REPLACE(%STRING%, '%oldChar%', '%newChar%')",
    draggable: 'REPLACE()'
  },
  strsplit: {
    name: 'strsplit',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'STRSPLIT(%STRING%, %REGEX%, %LIMIT%)',
    draggable: 'STRSPLIT()'
  },
  substring: {
    name: 'substring',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'SUBSTRING(%STRING%, %STARTINDEX%, %STOPINDEX%)',
    draggable: 'SUBSTRING()'
  },
  trim: {
    name: 'trim',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'TRIM(%STRING%)',
    draggable: 'TRIM()'
  },
  ucfirst: {
    name: 'ucfirst',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'UCFIRST(%STRING%)',
    draggable: 'UCFIRST()'
  },
  upper: {
    name: 'upper',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'UPPER(%STRING%)',
    draggable: 'UPPER()'
  }
};

const MACROS: UdfCategoryFunctions = {
  import: {
    name: 'import',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: "IMPORT '%PATH_TO_MACRO%';",
    draggable: "IMPORT '%PATH_TO_MACRO%';"
  }
};

const HBASE: UdfCategoryFunctions = {
  load: {
    name: 'load',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature:
      "LOAD 'hbase://%TABLE%' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage('%columnList%')",
    draggable:
      "LOAD 'hbase://%TABLE%' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage('%columnList%')"
  },
  store: {
    name: 'store',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature:
      "STORE %VAR% INTO 'hbase://%TABLE%' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage('%columnList%')",
    draggable:
      "STORE %VAR% INTO 'hbase://%TABLE%' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage('%columnList%')"
  }
};

const PYTHON_UDF: UdfCategoryFunctions = {
  register: {
    name: 'register',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: "REGISTER 'python_udf.py' USING jython AS myfuncs;",
    draggable: "REGISTER 'python_udf.py' USING jython AS myfuncs;"
  }
};

export const UDF_CATEGORIES: UdfCategory[] = [
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
