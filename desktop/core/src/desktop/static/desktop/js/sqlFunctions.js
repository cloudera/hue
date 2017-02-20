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

var PigFunctions = (function () {
  var EVAL_FUNCTIONS = {
    avg: { signature: 'AVG(%VAR%)' },
    concat: { signature: 'CONCAT(%VAR1%, %VAR2%)' },
    count: { signature: 'COUNT(%VAR%)' },
    count_start: { signature: 'COUNT_START(%VAR%)' },
    is_empty: { signature: 'IsEmpty(%VAR%)' },
    diff: { signature: 'DIFF(%VAR1%, %VAR2%)' },
    max: { signature: 'MAX(%VAR%)' },
    min: { signature: 'MIN(%VAR%)' },
    size: { signature: 'SIZE(%VAR%)' },
    sum: { signature: 'SUM(%VAR%)' },
    tokenize: { signature: 'TOKENIZE(%VAR%, %DELIM%)' }
  }

  var RELATIONAL_OPERATORS = {
    cogroup: { signature: 'COGROUP %VAR% BY %VAR%' },
    cross: { signature: 'CROSS %VAR1%, %VAR2%;' },
    distinct: { signature: 'DISTINCT %VAR%;' },
    filter: { signature: 'FILTER %VAR% BY %COND%' },
    flatten: { signature: 'FLATTEN(%VAR%)' },
    foreach_generate: { signature: 'FOREACH %DATA% GENERATE %NEW_DATA%;' },
    foreach: { signature: 'FOREACH %DATA% {%NESTED_BLOCK%};' },
    group_by: { signature: 'GROUP %VAR% BY %VAR%' },
    group_all: { signature: 'GROUP %VAR% ALL' },
    join: { signature: 'JOIN %VAR% BY ' },
    limit: { signature: 'LIMIT %VAR% %N%' },
    order: { signature: 'ORDER %VAR% BY %FIELD%' },
    sample: { signature: 'SAMPLE %VAR% %SIZE%' },
    split: { signature: 'SPLIT %VAR1% INTO %VAR2% IF %EXPRESSIONS%' },
    union: { signature: 'UNION %VAR1%, %VAR2%' }
  }

  var INPUT_OUTPUT = {
    load: { signature: 'LOAD \'%FILE%\';' },
    dump: { signature: 'DUMP %VAR%;' },
    store: { signature: 'STORE %VAR% INTO %PATH%;' }
  }

  var DEBUG = {
    explain: { signature: 'EXPLAIN %VAR%;' },
    illustrate: { signature: 'ILLUSTRATE %VAR%;' },
    describe: { signature: 'DESCRIBE %VAR%;' }
  }

  var HCATALOG = {
    LOAD: { signature: 'LOAD \'%TABLE%\' USING org.apache.hcatalog.pig.HCatLoader();' }
  }

  var MATH_FUNCTIONS = {
    abs: { signature: 'ABS(%VAR%)' },
    acos: { signature: 'ACOS(%VAR%)' },
    asin: { signature: 'ASIN(%VAR%)' },
    atan: { signature: 'ATAN(%VAR%)' },
    cbrt: { signature: 'CBRT(%VAR%)' },
    ceil: { signature: 'CEIL(%VAR%)' },
    cos: { signature: 'COS(%VAR%)' },
    cosh: { signature: 'COSH(%VAR%)' },
    exp: { signature: 'EXP(%VAR%)' },
    floor: { signature: 'FLOOR(%VAR%)' },
    log: { signature: 'LOG(%VAR%)' },
    log10: { signature: 'LOG10(%VAR%)' },
    random: { signature: 'RANDOM(%VAR%)' },
    round: { signature: 'ROUND(%VAR%)' },
    sin: { signature: 'SIN(%VAR%)' },
    sinh: { signature: 'SINH(%VAR%)' },
    sqrt: { signature: 'SQRT(%VAR%)' },
    tan: { signature: 'TAN(%VAR%)' },
    tanh: { signature: 'TANH(%VAR%)' }
  }

  var TUPLE_BAG_MAP = {
    totuple: { signature: 'TOTUPLE(%VAR%)' },
    tobag: { signature: 'TOBAG(%VAR%)' },
    tomap: { signature: 'TOMAP(%KEY%, %VALUE%)' },
    top: { signature: 'TOP(%topN%, %COLUMN%, %RELATION%)' }
  }

  var STRING_FUNCTIONS = {
    indexof: { signature: 'INDEXOF(%STRING%, \'%CHARACTER%\', %STARTINDEX%)' },
    last_index_of: { signature: 'LAST_INDEX_OF(%STRING%, \'%CHARACTER%\', %STARTINDEX%)' },
    lower: { signature: 'LOWER(%STRING%)' },
    regex_extract: { signature: 'REGEX_EXTRACT(%STRING%, %REGEX%, %INDEX%)' },
    regex_extract_all: { signature: 'REGEX_EXTRACT_ALL(%STRING%, %REGEX%)' },
    replace: { signature: 'REPLACE(%STRING%, \'%oldChar%\', \'%newChar%\')' },
    strsplit: { signature: 'STRSPLIT(%STRING%, %REGEX%, %LIMIT%)' },
    substring: { signature: 'SUBSTRING(%STRING%, %STARTINDEX%, %STOPINDEX%)' },
    trim: { signature: 'TRIM(%STRING%)' },
    ucfirst: { signature: 'UCFIRST(%STRING%)' },
    upper: { signature: 'UPPER(%STRING%)' }
  }

  var MACROS = {
    import: { signature: 'IMPORT \'%PATH_TO_MACRO%\';' }
  }

  var HBASE = {
    load: { signature: 'LOAD \'hbase://%TABLE%\' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage(\'%columnList%\')' },
    store: { signature: 'STORE %VAR% INTO \'hbase://%TABLE%\' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage(\'%columnList%\')' }
  }

  var PYTHON_UDF = {
    register: { signature: 'REGISTER \'python_udf.py\' USING jython AS myfuncs;' }
  }

  var CATEGORIZED_FUNCTIONS = [
    { name: 'Eval', functions: EVAL_FUNCTIONS },
    { name: 'Relational Operators', functions: RELATIONAL_OPERATORS },
    { name: 'Input and Output', functions: INPUT_OUTPUT },
    { name: 'Debug', functions: DEBUG },
    { name: 'HCatalog', functions: HCATALOG },
    { name: 'Math', functions: MATH_FUNCTIONS },
    { name: 'Tuple, Bag and Map', functions: TUPLE_BAG_MAP },
    { name: 'String', functions: STRING_FUNCTIONS },
    { name: 'Macros', functions: MACROS },
    { name: 'HBase', functions: HBASE },
    { name: 'Python UDF', functions: PYTHON_UDF }
  ];

  return {
    CATEGORIZED_FUNCTIONS: CATEGORIZED_FUNCTIONS
  }
})();



var SqlFunctions = (function () {

  var MATHEMATICAL_FUNCTIONS = {
    hive: {
      abs: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'abs(DOUBLE a)',
        description: 'Returns the absolute value.'
      },
      acos: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'acos(DECIMAL|DOUBLE a)',
        description: 'Returns the arccosine of a if -1<=a<=1 or NULL otherwise.'
      },
      asin: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'asin(DECIMAL|DOUBLE a)',
        description: 'Returns the arc sin of a if -1<=a<=1 or NULL otherwise.'
      },
      atan: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'atan(DECIMAL|DOUBLE a)',
        description: 'Returns the arctangent of a.'
      },
      bin: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'BIGINT'}]],
        signature: 'bin(BIGINT a)',
        description: 'Returns the number in binary format'
      },
      bround: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'INT', optional: true}]],
        signature: 'bround(DOUBLE a [, INT decimals])',
        description: 'Returns the rounded BIGINT value of a using HALF_EVEN rounding mode with optional decimal places d.'
      },
      cbrt: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'cbft(DOUBLE a)',
        description: 'Returns the cube root of a double value.'
      },
      ceil: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'ceil(DOUBLE a)',
        description: 'Returns the minimum BIGINT value that is equal to or greater than a.'
      },
      ceiling: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'ceiling(DOUBLE a)',
        description: 'Returns the minimum BIGINT value that is equal to or greater than a.'
      },
      conv: {
        returnTypes: ['T'],
        arguments: [[{type: 'BIGINT'}, {type: 'STRING'}], [{type: 'INT'}], [{type: 'INT'}]],
        signature: 'conv(BIGINT|STRING a, INT from_base, INT to_base)',
        description: 'Converts a number from a given base to another'
      },
      cos: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'cos(DECIMAL|DOUBLE a)',
        description: 'Returns the cosine of a (a is in radians).'
      },
      degrees: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'degrees(DECIMAL|DOUBLE a)',
        description: 'Converts value of a from radians to degrees.'
      },
      e: {
        returnTypes: ['DOUBLE'], arguments: [[]], signature: 'e()', description: 'Returns the value of e.'
      },
      exp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'exp(DECIMAL|DOUBLE a)',
        description: 'Returns e^a where e is the base of the natural logarithm.'
      },
      factorial: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'INT'}]],
        signature: 'factorial(INT a)',
        description: 'Returns the factorial of a. Valid a is [0..20].'
      },
      floor: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'floor(DOUBLE a)',
        description: 'Returns the maximum BIGINT value that is equal to or less than a.'
      },
      greatest: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'greatest(T a1, T a2, ...)',
        description: 'Returns the greatest value of the list of values. Fixed to return NULL when one or more arguments are NULL, and strict type restriction relaxed, consistent with ">" operator.'
      },
      hex: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'BIGINT'}, {type: 'BINARY'}, {type: 'STRING'}]],
        signature: 'hex(BIGINT|BINARY|STRING a)',
        description: 'If the argument is an INT or binary, hex returns the number as a STRING in hexadecimal format. Otherwise if the number is a STRING, it converts each character into its hexadecimal representation and returns the resulting STRING.'
      },
      least: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'least(T a1, T a2, ...)',
        description: 'Returns the least value of the list of values. Fixed to return NULL when one or more arguments are NULL, and strict type restriction relaxed, consistent with "<" operator.'
      },
      ln: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'ln(DECIMAL|DOUBLE a)',
        description: 'Returns the natural logarithm of the argument a'
      },
      log: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}], [{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'log(DECIMAL|DOUBLE base, DECIMAL|DOUBLE a)',
        description: 'Returns the base-base logarithm of the argument a.'
      },
      log10: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'log10(DECIMAL|DOUBLE a)',
        description: 'Returns the base-10 logarithm of the argument a.'
      },
      log2: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'log2(DECIMAL|DOUBLE a)',
        description: 'Returns the base-2 logarithm of the argument a.'
      },
      negative: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'INT'}]],
        signature: 'negative(T<DOUBLE|INT> a)',
        description: 'Returns -a.'
      },
      pi: {
        returnTypes: ['DOUBLE'], arguments: [], signature: 'pi()', description: 'Returns the value of pi.'
      },
      pmod: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'INT'}], [{type: 'T'}]],
        signature: 'pmod(T<DOUBLE|INT> a, T b)',
        description: 'Returns the positive value of a mod b'
      },
      positive: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'INT'}]],
        signature: 'positive(T<DOUBLE|INT> a)',
        description: 'Returns a.'
      },
      pow: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'DOUBLE'}]],
        signature: 'pow(DOUBLE a, DOUBLE p)',
        description: 'Returns a^p'
      },
      power: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'DOUBLE'}]],
        signature: 'power(DOUBLE a, DOUBLE p)',
        description: 'Returns a^p'
      },
      radians: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'radians(DECIMAL|DOUBLE a)',
        description: 'Converts value of a from degrees to radians.'
      },
      rand: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'INT', optional: true}]],
        signature: 'rand([INT seed])',
        description: 'Returns a random number (that changes from row to row) that is distributed uniformly from 0 to 1. Specifying the seed will make sure the generated random number sequence is deterministic.'
      },
      round: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'INT', optional: true}]],
        signature: 'round(DOUBLE a [, INT d])',
        description: 'Returns the rounded BIGINT value of a or a rounded to d decimal places.'
      },
      shiftleft: {
        returnTypes: ['T'],
        arguments: [[{type: 'BIGINT'}, {type: 'INT'}, {type: 'SMALLINT'}, {type: 'TINYINT'}], [{type: 'INT'}]],
        signature: 'shiftleft(T<BIGINT|INT|SMALLINT|TINYINT> a, INT b)',
        description: 'Bitwise left shift. Shifts a b positions to the left. Returns int for tinyint, smallint and int a. Returns bigint for bigint a.'
      },
      shiftright: {
        returnTypes: ['T'],
        arguments: [[{type: 'BIGINT'}, {type: 'INT'}, {type: 'SMALLINT'}, {type: 'TINYINT'}], [{type: 'INT'}]],
        signature: 'shiftright(T<BIGINT|INT|SMALLINT|TINYINT> a, INT b)',
        description: 'Bitwise right shift. Shifts a b positions to the right. Returns int for tinyint, smallint and int a. Returns bigint for bigint a.'
      },
      shiftrightunsigned: {
        returnTypes: ['T'],
        arguments: [[{type: 'BIGINT'}, {type: 'INT'}, {type: 'SMALLINT'}, {type: 'TINYINT'}], [{type: 'INT'}]],
        signature: 'shiftrightunsigned(T<BIGINT|INT|SMALLINT|TINYINT> a, INT b)',
        description: 'Bitwise unsigned right shift. Shifts a b positions to the right. Returns int for tinyint, smallint and int a. Returns bigint for bigint a.'
      },
      sign: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'INT'}]],
        signature: 'sign(T<DOUBLE|INT> a)',
        description: 'Returns the sign of a as \'1.0\' (if a is positive) or \'-1.0\' (if a is negative), \'0.0\' otherwise. The decimal version returns INT instead of DOUBLE.'
      },
      sin: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'sin(DECIMAL|DOUBLE a)',
        description: 'Returns the sine of a (a is in radians).'
      },
      sqrt: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'sqrt(DECIMAL|DOUBLE a)',
        description: 'Returns the square root of a'
      },
      tan: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}]],
        signature: 'tan(DECIMAL|DOUBLE a)',
        description: 'Returns the tangent of a (a is in radians).'
      },
      unhex: {
        returnTypes: ['BINARY'],
        arguments: [[{type: 'STRING'}]],
        signature: 'unhex(STRING a)',
        description: 'Inverse of hex. Interprets each pair of characters as a hexadecimal number and converts to the byte representation of the number.'
      }
    },
    impala: {
      abs: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'abs(T a)',
        description: 'Returns the absolute value of the argument. Use this function to ensure all return values are positive. This is different than the positive() function, which returns its argument unchanged (even if the argument was negative).'
      },
      acos: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'acos(DOUBLE a)',
        description: 'Returns the arccosine of the argument.'
      },
      asin: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'asin(DOUBLE a)',
        description: 'Returns the arcsine of the argument.'
      },
      atan: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'atan(DOUBLE a)',
        description: 'Returns the arctangent of the argument.'
      },
      bin: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'BIGINT'}]],
        signature: 'bin(BIGINT a)',
        description: 'Returns the binary representation of an integer value, that is, a string of 0 and 1 digits.'
      },
      ceil: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'DECIMAL'}]],
        signature: 'ceil(T<DOUBLE|DECIMAL> a)',
        description: 'Returns the smallest integer that is greater than or equal to the argument.'
      },
      ceiling: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'DECIMAL'}]],
        signature: 'ceiling(T<DOUBLE|DECIMAL> a)',
        description: 'Returns the smallest integer that is greater than or equal to the argument.'
      },
      conv: {
        returnTypes: ['T'],
        arguments: [[{type: 'BIGINT'}, {type: 'STRING'}], [{type: 'INT'}], [{type: 'INT'}]],
        signature: 'conv(T<BIGINT|STRING> a, INT from_base, INT to_base)',
        description: 'Returns a string representation of an integer value in a particular base. The input value can be a string, for example to convert a hexadecimal number such as fce2 to decimal. To use the return value as a number (for example, when converting to base 10), use CAST() to convert to the appropriate type.'
      },
      cos: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'cos(DOUBLE a)',
        description: 'Returns the cosine of the argument.'
      },
      degrees: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'degrees(DOUBLE a)',
        description: 'Converts argument value from radians to degrees.'
      },
      e: {
        returnTypes: ['DOUBLE'], arguments: [], signature: 'e()', description: 'Returns the mathematical constant e.'
      },
      exp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'exp(DOUBLE a)',
        description: 'Returns the mathematical constant e raised to the power of the argument.'
      },
      floor: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'floor(DOUBLE a)',
        description: 'Returns the largest integer that is less than or equal to the argument.'
      },
      fmod: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'FLOAT'}], [{type: 'DOUBLE'}, {type: 'FLOAT'}]],
        signature: 'fmod(T<DOUBLE|FLOAT> a, T<DOUBLE|FLOAT> b)',
        description: 'Returns the modulus of a number.'
      },
      fnv_hash: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'T'}]],
        signature: 'fnv_hash(T a)',
        description: 'Returns a consistent 64-bit value derived from the input argument, for convenience of implementing hashing logic in an application.'
      },
      greatest: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'greatest(T a1, T a2, ...)',
        description: 'Returns the largest value from a list of expressions.'
      },
      hex: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'BIGINT'}, {type: 'STRING'}]],
        signature: 'hex(T<BIGINT|STRING> a)',
        description: 'Returns the hexadecimal representation of an integer value, or of the characters in a string.'
      },
      is_inf: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'is_inf(DOUBLE a)',
        description: 'Tests whether a value is equal to the special value "inf", signifying infinity.'
      },
      is_nan: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'is_nan(DOUBLE A)',
        description: 'Tests whether a value is equal to the special value "NaN", signifying "not a number".'
      },
      least: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'least(T a1, T a2, ...)',
        description: 'Returns the smallest value from a list of expressions.'
      },
      ln: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'ln(DOUBLE a)',
        description: 'Returns the natural logarithm of the argument.'
      },
      log: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'DOUBLE'}]],
        signature: 'log(DOUBLE base, DOUBLE a)',
        description: 'Returns the logarithm of the second argument to the specified base.'
      },
      log10: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'log10(DOUBLE a)',
        description: 'Returns the logarithm of the argument to the base 10.'
      },
      log2: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'log2(DOUBLE a)',
        description: 'Returns the logarithm of the argument to the base 2.'
      },
      max_bigint: {
        returnTypes: ['BIGINT'],
        arguments: [],
        signature: 'max_bigint()',
        description: 'Returns the largest value of the associated integral type.'
      },
      max_int: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'max_int()',
        description: 'Returns the largest value of the associated integral type.'
      },
      max_smallint: {
        returnTypes: ['SMALLINT'],
        arguments: [],
        signature: 'max_smallint()',
        description: 'Returns the largest value of the associated integral type.'
      },
      max_tinyint: {
        returnTypes: ['TINYINT'],
        arguments: [],
        signature: 'max_tinyint()',
        description: 'Returns the largest value of the associated integral type.'
      },
      min_bigint: {
        returnTypes: ['BIGINT'],
        arguments: [],
        signature: 'min_bigint()',
        description: 'Returns the smallest value of the associated integral type (a negative number).'
      },
      min_int: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'min_int()',
        description: 'Returns the smallest value of the associated integral type (a negative number).'
      },
      min_smallint: {
        returnTypes: ['SMALLINT'],
        arguments: [],
        signature: 'min_smallint()',
        description: 'Returns the smallest value of the associated integral type (a negative number).'
      },
      min_tinyint: {
        returnTypes: ['TINYINT'],
        arguments: [],
        signature: 'min_tinyint()',
        description: 'Returns the smallest value of the associated integral type (a negative number).'
      },
      negative: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'negative(T a)',
        description: 'Returns the argument with the sign reversed; returns a positive value if the argument was already negative.'
      },
      pi: {
        returnTypes: ['DOUBLE'], arguments: [], signature: 'pi()', description: 'Returns the constant pi.'
      },
      pmod: {
        returnTypes: ['T'],
        arguments: [[{type: 'DOUBLE'}, {type: 'INT'}], [{type: 'T'}]],
        signature: 'pmod(T<DOUBLE|INT> a, T b)',
        description: 'Returns the positive modulus of a number.'
      },
      positive: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'positive(T a)',
        description: 'Returns the original argument unchanged (even if the argument is negative).'
      },
      pow: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'DOUBLE'}]],
        signature: 'pow(DOUBLE a, DOUBLE p)',
        description: 'Returns the first argument raised to the power of the second argument.'
      },
      power: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'DOUBLE'}]],
        signature: 'power(DOUBLE a, DOUBLE p)',
        description: 'Returns the first argument raised to the power of the second argument.'
      },
      precision: {
        returnTypes: ['INT'],
        arguments: [[{type: 'NUMBER'}]],
        signature: 'precision(numeric_expression)',
        description: 'Computes the precision (number of decimal digits) needed to represent the type of the argument expression as a DECIMAL value.'
      },
      quotient: {
        returnTypes: ['INT'],
        arguments: [[{type: 'INT'}], [{type: 'INT'}]],
        signature: 'quotient(INT numerator, INT denominator)',
        description: 'Returns the first argument divided by the second argument, discarding any fractional part. Avoids promoting arguments to DOUBLE as happens with the / SQL operator.'
      },
      radians: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'radians(DOUBLE a)',
        description: 'Converts argument value from degrees to radians.'
      },
      rand: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'INT', optinal: true}]],
        signature: 'rand([INT seed])',
        description: 'Returns a random value between 0 and 1. After rand() is called with a seed argument, it produces a consistent random sequence based on the seed value.'
      },
      round: {
        returnTypes: ['T'],
        arguments: [[{type: 'DECIMAL'}, {type: 'DOUBLE'}], [{type: 'INT', optional: true}]],
        signature: 'round(DOUBLE a [, INT d]), round(DECIMAL val, INT d)',
        description: 'Rounds a floating-point value. By default (with a single argument), rounds to the nearest integer. Values ending in .5 are rounded up for positive numbers, down for negative numbers (that is, away from zero). The optional second argument specifies how many digits to leave after the decimal point; values greater than zero produce a floating-point return value rounded to the requested number of digits to the right of the decimal point.'
      },
      scale: {
        returnTypes: ['INT'],
        arguments: [[{type: 'NUMBER'}]],
        signature: 'scale(numeric_expression)',
        description: 'Computes the scale (number of decimal digits to the right of the decimal point) needed to represent the type of the argument expression as a DECIMAL value.'
      },
      sign: {
        returnTypes: ['INT'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'sign(DOUBLE a)',
        description: 'Returns -1, 0, or 1 to indicate the signedness of the argument value.'
      },
      sin: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'sin(DOUBLE a)',
        description: 'Returns the sine of the argument.'
      },
      sqrt: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'sqrt(DOUBLE a)',
        description: 'Returns the square root of the argument.'
      },
      tan: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DOUBLE'}]],
        signature: 'tan(DOUBLE a)',
        description: 'Returns the tangent of the argument.'
      },
      unhex: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'unhex(STRING a)',
        description: 'Returns a string of characters with ASCII values corresponding to pairs of hexadecimal digits in the argument.'
      }
    }
  };

  var COMPLEX_TYPE_CONSTRUCTS = {
    hive: {
      array: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'array(val1, val2, ...)',
        description: 'Creates an array with the given elements.'
      },
      create_union: {
        returnTypes: ['UNION'],
        arguments: [[{type: 'T'}], [{type: 'T', multiple: true}]],
        signature: 'create_union(tag, val1, val2, ...)',
        description: 'Creates a union type with the value that is being pointed to by the tag parameter.'
      },
      map: {
        returnTypes: ['MAP'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'map(key1, value1, ...)',
        description: 'Creates a map with the given key/value pairs.'
      },
      named_struct: {
        returnTypes: ['STRUCT'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'named_struct(name1, val1, ...)',
        description: 'Creates a struct with the given field names and values.'
      },
      struct: {
        returnTypes: ['STRUCT'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'struct(val1, val2, ...)',
        description: 'Creates a struct with the given field values. Struct field names will be col1, col2, ....'
      }
    },
    impala: {}
  };

  var AGGREGATE_FUNCTIONS = {
    generic: {
      count: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'T'}]],
        signature: 'count(col)',
        description: 'count(*) - Returns the total number of retrieved rows, including rows containing NULL values. count(expr) - Returns the number of rows for which the supplied expression is non-NULL.'
      },
      sum: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'sum(col)',
        description: 'Returns the sum of the elements in the group or the sum of the distinct values of the column in the group.'
      },
      max: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'max(col)',
        description: 'Returns the maximum value of the column in the group.'
      },
      min: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'min(col)',
        description: 'Returns the minimum of the column in the group.'
      }
    },
    hive: {
      avg: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'avg(col)',
        description: 'Returns the average of the elements in the group or the average of the distinct values of the column in the group.'
      },
      count: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'T'}]],
        signature: 'count([DISTINCT] col)',
        description: 'count(*) - Returns the total number of retrieved rows, including rows containing NULL values. count(expr) - Returns the number of rows for which the supplied expression is non-NULL. count(DISTINCT expr[, expr]) - Returns the number of rows for which the supplied expression(s) are unique and non-NULL. Execution of this can be optimized with hive.optimize.distinct.rewrite.'
      },
      stddev_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'stddev_pop(col)',
        description: 'Returns the standard deviation of a numeric column in the group.'
      },
      stddev_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'stddev_samp(col)',
        description: 'Returns the unbiased sample standard deviation of a numeric column in the group.'
      },
      sum: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'sum(col)',
        description: 'Returns the sum of the elements in the group or the sum of the distinct values of the column in the group.'
      },
      max: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'max(col)',
        description: 'Returns the maximum value of the column in the group.'
      },
      min: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'min(col)',
        description: 'Returns the minimum of the column in the group.'
      },
      corr: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'corr(col1, col2)',
        description: 'Returns the Pearson coefficient of correlation of a pair of a numeric columns in the group.'
      },
      covar_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'covar_pop(col1, col2)',
        description: 'Returns the population covariance of a pair of numeric columns in the group.'
      },
      covar_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'covar_samp(col1, col2)',
        description: 'Returns the sample covariance of a pair of a numeric columns in the group.'
      },
      collect_set: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'T'}]],
        signature: 'collect_set(col)',
        description: 'Returns a set of objects with duplicate elements eliminated.'
      },
      collect_list: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'T'}]],
        signature: 'collect_list(col)',
        description: 'Returns a list of objects with duplicates. (As of Hive 0.13.0.)'
      },
      histogram_numeric: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'T'}], [{type: 'INT'}]],
        signature: 'array<struct {\'x\', \'y\'}> histogram_numeric(col, b)',
        description: 'Computes a histogram of a numeric column in the group using b non-uniformly spaced bins. The output is an array of size b of double-valued (x,y) coordinates that represent the bin centers and heights'
      },
      ntile: {
        returnTypes: ['INT'],
        arguments: [[{type: 'INT'}]],
        signature: 'ntile(INT x)',
        description: 'Divides an ordered partition into x groups called buckets and assigns a bucket number to each row in the partition. This allows easy calculation of tertiles, quartiles, deciles, percentiles and other common summary statistics. (As of Hive 0.11.0.)'
      },
      percentile: {
        returnTypes: ['DOUBLE', 'ARRAY'],
        arguments: [[{type: 'BIGINT'}], [{type: 'ARRAY'}, {type: 'DOUBLE'}]],
        signature: 'percentile(BIGINT col, p), array<DOUBLE> percentile(BIGINT col, array(p1 [, p2]...))',
        description: 'Returns the exact pth percentile (or percentiles p1, p2, ..) of a column in the group (does not work with floating point types). p must be between 0 and 1. NOTE: A true percentile can only be computed for integer values. Use PERCENTILE_APPROX if your input is non-integral.'
      },
      percentile_approx: {
        returnTypes: ['DOUBLE', 'ARRAY'],
        arguments: [[{type: 'DOUBLE'}], [{type: 'DOUBLE'}, {type: 'ARRAY'}], [{type: 'BIGINT', optional: true}]],
        signature: 'percentile_approx(DOUBLE col, p, [, B]), array<DOUBLE> percentile_approx(DOUBLE col, array(p1 [, p2]...), [, B])',
        description: 'Returns an approximate pth percentile (or percentiles p1, p2, ..) of a numeric column (including floating point types) in the group. The B parameter controls approximation accuracy at the cost of memory. Higher values yield better approximations, and the default is 10,000. When the number of distinct values in col is smaller than B, this gives an exact percentile value.'
      },
      variance: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'variance(col)',
        description: 'Returns the variance of a numeric column in the group.'
      },
      var_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'var_pop(col)',
        description: 'Returns the variance of a numeric column in the group.'
      },
      var_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'var_samp(col)',
        description: 'Returns the unbiased sample variance of a numeric column in the group.'
      }
    },
    impala: {
      appx_median: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'appx_median([DISTINCT|ALL] T col)',
        description: 'An aggregate function that returns a value that is approximately the median (midpoint) of values in the set of input values.'
      },
      avg: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'NUMBER'}]],
        signature: 'avg([DISTINCT|ALL] col)',
        description: 'An aggregate function that returns the average value from a set of numbers. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to AVG are NULL, AVG returns NULL.'
      },
      count: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'T'}]],
        signature: 'count([DISTINCT|ALL] col)',
        description: 'An aggregate function that returns the number of rows, or the number of non-NULL rows.'
      },
      max: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'max([DISTINCT | ALL] T col)',
        description: 'An aggregate function that returns the maximum value from a set of numbers. Opposite of the MIN function. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to MAX are NULL, MAX returns NULL.'
      },
      min: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'min([DISTINCT | ALL] T col)',
        description: 'An aggregate function that returns the minimum value from a set of numbers. Opposite of the MAX function. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to MIN are NULL, MIN returns NULL.'
      },
      sum: {
        returnTypes: ['BIGINT', 'DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'sum([DISTINCT | ALL] col)',
        description: 'An aggregate function that returns the sum of a set of numbers. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to MIN are NULL, SUM returns NULL.'
      },
      group_concat: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'T'}], [{type: 'STRING', optional: true}]],
        signature: 'group_concat([ALL] col [, separator])',
        description: 'An aggregate function that returns a single string representing the argument value concatenated together for each row of the result set. If the optional separator string is specified, the separator is added between each pair of concatenated values. The default separator is a comma followed by a space.'
      },
      ndv: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'ndv([DISTINCT | ALL] col)',
        description: 'An aggregate function that returns an approximate value similar to the result of COUNT(DISTINCT col), the "number of distinct values". It is much faster than the combination of COUNT and DISTINCT, and uses a constant amount of memory and thus is less memory-intensive for columns with high cardinality.'
      },
      stddev: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'stddev([DISTINCT | ALL] col)',
        description: 'Returns the standard deviation of a numeric column in the group.'
      },
      stddev_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'stddev_pop([DISTINCT | ALL] col)',
        description: 'Returns the population standard deviation of a numeric column in the group.'
      },
      stddev_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'stddev_samp([DISTINCT | ALL] col)',
        description: 'Returns the unbiased sample standard deviation of a numeric column in the group.'
      },
      variance: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'variance([DISTINCT | ALL] col)',
        description: 'An aggregate function that returns the variance of a set of numbers. This is a mathematical property that signifies how far the values spread apart from the mean. The return value can be zero (if the input is a single value, or a set of identical values), or a positive number otherwise.'
      },
      variance_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'variance_pop([DISTINCT | ALL] col)',
        description: 'An aggregate function that returns the population variance of a set of numbers. This is a mathematical property that signifies how far the values spread apart from the mean. The return value can be zero (if the input is a single value, or a set of identical values), or a positive number otherwise.'
      },
      variance_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'variance_samp([DISTINCT | ALL] col)',
        description: 'An aggregate function that returns the sample variance of a set of numbers. This is a mathematical property that signifies how far the values spread apart from the mean. The return value can be zero (if the input is a single value, or a set of identical values), or a positive number otherwise.'
      },
      var_pop: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'var_pop(col)',
        description: 'Returns the variance of a numeric column in the group.'
      },
      var_samp: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'T'}]],
        signature: 'var_samp(col)',
        description: 'Returns the unbiased sample variance of a numeric column in the group.'
      }
    }
  };

  var COLLECTION_FUNCTIONS = {
    hive: {
      array_contains: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'ARRAY'}], [{type: 'T'}]],
        signature: 'array_contains(Array<T> a, val)',
        description: 'Returns TRUE if the array contains value.'
      },
      map_keys: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'MAP'}]],
        signature: 'array<K.V> map_keys(Map<K.V> a)',
        description: 'Returns an unordered array containing the keys of the input map.'
      },
      map_values: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'MAP'}]],
        signature: 'array<K.V> map_values(Map<K.V> a)',
        description: 'Returns an unordered array containing the values of the input map.'
      },
      size: {
        returnTypes: ['INT'],
        arguments: [[{type: 'ARRAY'}, {type: 'MAP'}]],
        signature: 'size(Map<K.V>|Array<T> a)',
        description: 'Returns the number of elements in the map or array type.'
      },
      sort_array: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'ARRAY'}]],
        signature: 'sort_array(Array<T> a)',
        description: 'Sorts the input array in ascending order according to the natural ordering of the array elements and returns it.'
      }
    },
    impala: {}
  };

  var TYPE_CONVERSION_FUNCTIONS = {
    hive: {
      binary: {
        returnTypes: ['BINARY'],
        arguments: [[{type: 'BINARY'}, {type: 'STRING'}]],
        signature: 'binary(BINARY|STRING a)',
        description: 'Casts the parameter into a binary.'
      },
      cast: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'cast(a as T)',
        description: 'Converts the results of the expression expr to type T. For example, cast(\'1\' as BIGINT) will convert the string \'1\' to its integral representation. A null is returned if the conversion does not succeed. If cast(expr as boolean) Hive returns true for a non-empty string.'
      }
    },
    impala: {
      cast: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'cast(a as T)',
        description: 'Converts the results of the expression expr to type T. For example, cast(\'1\' as BIGINT) will convert the string \'1\' to its integral representation. A null is returned if the conversion does not succeed. If cast(expr as boolean) Hive returns true for a non-empty string.'
      }
    }
  };

  var DATE_FUNCTIONS = {
    hive: {
      add_months: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'DATE'}, {type: 'STRING'}, {type: 'TIMESTAMP'}], [{type: 'INT'}]],
        signature: 'add_months(DATE|STRING|TIMESTAMP start_date, INT num_months)',
        description: 'Returns the date that is num_months after start_date (as of Hive 1.1.0). start_date is a string, date or timestamp. num_months is an integer. The time part of start_date is ignored. If start_date is the last day of the month or if the resulting month has fewer days than the day component of start_date, then the result is the last day of the resulting month. Otherwise, the result has the same day component as start_date.'
      },
      current_date: {
        returnTypes: ['DATE'],
        arguments: [],
        signature: 'current_date',
        description: 'Returns the current date at the start of query evaluation (as of Hive 1.2.0). All calls of current_date within the same query return the same value.'
      },
      current_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [],
        signature: 'current_timestamp()',
        description: 'Returns the current timestamp at the start of query evaluation (as of Hive 1.2.0). All calls of current_timestamp within the same query return the same value.'
      },
      datediff: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'datediff(STRING enddate, STRING startdate)',
        description: 'Returns the number of days from startdate to enddate: datediff(\'2009-03-01\', \'2009-02-27\') = 2.'
      },
      date_add: {
        returnTypes: ['T'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}]],
        signature: 'date_add(STRING startdate, INT days)',
        description: 'Adds a number of days to startdate: date_add(\'2008-12-31\', 1) = \'2009-01-01\'. T = pre 2.1.0: STRING, 2.1.0 on: DATE'
      },
      date_format: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'DATE'}, {type: 'STRING'}, {type: 'TIMESTAMP'}], [{type: 'STRING'}]],
        signature: 'date_format(DATE|TIMESTAMP|STRING ts, STRING fmt)',
        description: 'Converts a date/timestamp/string to a value of string in the format specified by the date format fmt (as of Hive 1.2.0). Supported formats are Java SimpleDateFormat formats – https://docs.oracle.com/javase/7/docs/api/java/text/SimpleDateFormat.html. The second argument fmt should be constant. Example: date_format(\'2015-04-08\', \'y\') = \'2015\'.'
      },
      date_sub: {
        returnTypes: ['T'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}]],
        signature: 'date_sub(STRING startdate, INT days)',
        description: 'Subtracts a number of days to startdate: date_sub(\'2008-12-31\', 1) = \'2008-12-30\'. T = pre 2.1.0: STRING, 2.1.0 on: DATE'
      },
      day: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'day(STRING date)',
        description: 'Returns the day part of a date or a timestamp string: day(\'1970-11-01 00:00:00\') = 1, day(\'1970-11-01\') = 1.'
      },
      dayofmonth: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'dayofmonth(STRING date)',
        description: 'Returns the day part of a date or a timestamp string: dayofmonth(\'1970-11-01 00:00:00\') = 1, dayofmonth(\'1970-11-01\') = 1.'
      },
      from_unixtime: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'BIGINT'}], [{type: 'STRING', optional: true}]],
        signature: 'from_unixtime(BIGINT unixtime [, STRING format])',
        description: 'Converts time string in format yyyy-MM-dd HH:mm:ss to Unix timestamp (in seconds), using the default timezone and the default locale, return 0 if fail: unix_timestamp(\'2009-03-20 11:30:01\') = 1237573801'
      },
      from_utc_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'STRING'}]],
        signature: 'from_utc_timestamp(TIMESTAMP a, STRING timezone)',
        description: 'Assumes given timestamp is UTC and converts to given timezone (as of Hive 0.8.0). For example, from_utc_timestamp(\'1970-01-01 08:00:00\',\'PST\') returns 1970-01-01 00:00:00'
      },
      hour: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'hour(STRING date)',
        description: 'Returns the hour of the timestamp: hour(\'2009-07-30 12:58:59\') = 12, hour(\'12:58:59\') = 12.'
      },
      last_day: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'last_day(STRING date)',
        description: 'Returns the last day of the month which the date belongs to (as of Hive 1.1.0). date is a string in the format \'yyyy-MM-dd HH:mm:ss\' or \'yyyy-MM-dd\'. The time part of date is ignored.'
      },
      minute: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'minute(STRING date)',
        description: 'Returns the minute of the timestamp.'
      },
      month: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'month(STRING date)',
        description: 'Returns the month part of a date or a timestamp string: month(\'1970-11-01 00:00:00\') = 11, month(\'1970-11-01\') = 11.'
      },
      months_between: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'DATE'}, {type: 'STRING'}, {type: 'TIMESTAMP'}], [{type: 'DATE'}, {type: 'STRING'}, {type: 'TIMESTAMP'}]],
        signature: 'months_between(DATE|TIMESTAMP|STRING date1, DATE|TIMESTAMP|STRING date2)',
        description: 'Returns number of months between dates date1 and date2 (as of Hive 1.2.0). If date1 is later than date2, then the result is positive. If date1 is earlier than date2, then the result is negative. If date1 and date2 are either the same days of the month or both last days of months, then the result is always an integer. Otherwise the UDF calculates the fractional portion of the result based on a 31-day month and considers the difference in time components date1 and date2. date1 and date2 type can be date, timestamp or string in the format \'yyyy-MM-dd\' or \'yyyy-MM-dd HH:mm:ss\'. The result is rounded to 8 decimal places. Example: months_between(\'1997-02-28 10:30:00\', \'1996-10-30\') = 3.94959677'
      },
      next_day: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'next_day(STRING start_date, STRING day_of_week)',
        description: 'Returns the first date which is later than start_date and named as day_of_week (as of Hive 1.2.0). start_date is a string/date/timestamp. day_of_week is 2 letters, 3 letters or full name of the day of the week (e.g. Mo, tue, FRIDAY). The time part of start_date is ignored. Example: next_day(\'2015-01-14\', \'TU\') = 2015-01-20.'
      },
      quarter: {
        returnTypes: ['INT'],
        arguments: [[{type: 'DATE'}, {type: 'STRING'}, {type: 'TIMESTAMP'}]],
        signature: 'quarter(DATE|TIMESTAMP|STRING a)	',
        description: 'Returns the quarter of the year for a date, timestamp, or string in the range 1 to 4. Example: quarter(\'2015-04-08\') = 2.'
      },
      second: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'second(STRING date)',
        description: 'Returns the second of the timestamp.'
      },
      to_date: {
        returnTypes: ['T'],
        arguments: [[{type: 'STRING'}]],
        signature: 'to_date(STRING timestamp)',
        description: 'Returns the date part of a timestamp string, example to_date(\'1970-01-01 00:00:00\'). T = pre 2.1.0: STRING 2.1.0 on: DATE'
      },
      to_utc_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}]],
        signature: 'to_utc_timestamp(TIMESTAMP a, STRING timezone)',
        description: 'Assumes given timestamp is in given timezone and converts to UTC (as of Hive 0.8.0). For example, to_utc_timestamp(\'1970-01-01 00:00:00\',\'PST\') returns 1970-01-01 08:00:00.'
      },
      trunc: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'trunc(STRING date, STRING format)',
        description: 'Returns date truncated to the unit specified by the format (as of Hive 1.2.0). Supported formats: MONTH/MON/MM, YEAR/YYYY/YY. Example: trunc(\'2015-03-17\', \'MM\') = 2015-03-01.'
      },
      unix_timestamp: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'unix_timestamp(STRING date, STRING pattern)',
        description: 'Convert time string with given pattern to Unix time stamp (in seconds), return 0 if fail: unix_timestamp(\'2009-03-20\', \'yyyy-MM-dd\') = 1237532400.'
      },
      weekofyear: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'weekofyear(STRING date)',
        description: 'Returns the week number of a timestamp string: weekofyear(\'1970-11-01 00:00:00\') = 44, weekofyear(\'1970-11-01\') = 44.'
      },
      year: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'year(STRING date)',
        description: 'Returns the year part of a date or a timestamp string: year(\'1970-01-01 00:00:00\') = 1970, year(\'1970-01-01\') = 1970'
      }
    },
    impala: {
      add_months: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'add_months(TIMESTAMP date, BIGINT|INT months)',
        description: 'Returns the specified date and time plus some number of months.'
      },
      adddate: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'adddate(TIMESTAMP startdate, BIGINT|INT days)',
        description: 'Adds a specified number of days to a TIMESTAMP value. Similar to date_add(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.'
      },
      current_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [],
        signature: 'current_timestamp()',
        description: 'Alias for the now() function.'
      },
      date_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'INT'}]],
        signature: 'date_add(TIMESTAMP startdate, INT days), date_add(TIMESTAMP startdate, interval_expression)',
        description: 'Adds a specified number of days to a TIMESTAMP value. The first argument can be a string, which is automatically cast to TIMESTAMP if it uses the recognized format. With an INTERVAL expression as the second argument, you can calculate a delta value using other units such as weeks, years, hours, seconds, and so on.'
      },
      date_part: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'STRING'}], [{type: 'TIMESTAMP'}]],
        signature: 'date_part(STRING unit, TIMESTAMP timestamp)',
        description: 'Similar to EXTRACT(), with the argument order reversed. Supports the same date and time units as EXTRACT(). For compatibility with SQL code containing vendor extensions.'
      },
      date_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'INT'}]],
        signature: 'date_sub(TIMESTAMP startdate, INT days), date_sub(TIMESTAMP startdate, interval_expression)',
        description: 'Subtracts a specified number of days from a TIMESTAMP value. The first argument can be a string, which is automatically cast to TIMESTAMP if it uses the recognized format. With an INTERVAL expression as the second argument, you can calculate a delta value using other units such as weeks, years, hours, seconds, and so on.'
      },
      datediff: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'datediff(STRING enddate, STRING startdate)',
        description: 'Returns the number of days between two dates represented as strings.'
      },
      day: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'day(STRING date)',
        description: 'Returns the day field from a date represented as a string.'
      },
      dayname: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'dayname(STRING date)',
        description: 'Returns the day field from a date represented as a string, converted to the string corresponding to that day name. The range of return values is \'Sunday\' to \'Saturday\'. Used in report-generating queries, as an alternative to calling dayofweek() and turning that numeric return value into a string using a CASE expression.'
      },
      dayofmonth: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'dayofmonth(STRING date)',
        description: 'Returns the day field from a date represented as a string.'
      },
      dayofweek: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'dayofweek(STRING date)',
        description: 'Returns the day field from a date represented as a string, corresponding to the day of the week. The range of return values is 1 (Sunday) to 7 (Saturday).'
      },
      dayofyear: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}]],
        signature: 'dayofyear(TIMESTAMP date)',
        description: 'Returns the day field from a TIMESTAMP value, corresponding to the day of the year. The range of return values is 1 (January 1) to 366 (December 31 of a leap year).'
      },
      days_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'days_add(TIMESTAMP startdate, BIGINT|INT days)',
        description: 'Adds a specified number of days to a TIMESTAMP value. Similar to date_add(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.'
      },
      days_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'days_sub(TIMESTAMP startdate, BIGINT|INT days)',
        description: 'Subtracts a specified number of days from a TIMESTAMP value. Similar to date_sub(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.'
      },
      extract: {
        returnTypes: ['INT'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'STRING'}]],
        signature: 'extract(TIMESTAMP date, STRING unit), extract(STRING unit FROM TIMESTAMP date)',
        description: 'Returns one of the numeric date or time fields from a TIMESTAMP value.'
      },
      from_unixtime: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'BIGINT'}], [{type: 'STRING', optional: true}]],
        signature: 'from_unixtime(BIGINT unixtime [, STRING format])',
        description: 'Converts the number of seconds from the Unix epoch to the specified time into a string in the local time zone.'
      },
      from_utc_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'STRING'}]],
        signature: 'from_utc_timestamp(TIMESTAMP date, STRING timezone)',
        description: 'Converts a specified UTC timestamp value into the appropriate value for a specified time zone.'
      },
      hour: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'hour(STRING date)',
        description: 'Returns the hour field from a date represented as a string.'
      },
      hours_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'hours_add(TIMESTAMP date, BIGINT|INT hours)',
        description: 'Returns the specified date and time plus some number of hours.'
      },
      hours_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'hours_sub(TIMESTAMP date, BIGINT|INT hours)',
        description: 'Returns the specified date and time minus some number of hours.'
      },
      microseconds_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'microseconds_add(TIMESTAMP date, BIGINT|INT microseconds)',
        description: 'Returns the specified date and time plus some number of microseconds.'
      },
      microseconds_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'microseconds_sub(TIMESTAMP date, BIGINT|INT microseconds)',
        description: 'Returns the specified date and time minus some number of microseconds.'
      },
      milliseconds_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'milliseconds_add(TIMESTAMP date, BIGINT|INT milliseconds)',
        description: 'Returns the specified date and time plus some number of milliseconds.'
      },
      milliseconds_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'milliseconds_sub(TIMESTAMP date, BIGINT|INT milliseconds)',
        description: 'Returns the specified date and time minus some number of milliseconds.'
      },
      minute: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'minute(STRING date)',
        description: 'Returns the minute field from a date represented as a string.'
      },
      minutes_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'minutes_add(TIMESTAMP date, BIGINT|INT minutes)',
        description: 'Returns the specified date and time plus some number of minutes.'
      },
      minutes_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'minutes_sub(TIMESTAMP date, BIGINT|INT minutes)',
        description: 'Returns the specified date and time minus some number of minutes.'
      },
      month: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'month(STRING date)',
        description: 'Returns the month field from a date represented as a string.'
      },
      months_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'months_add(TIMESTAMP date, BIGINT|INT months)',
        description: 'Returns the specified date and time plus some number of months.'
      },
      months_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'months_sub(TIMESTAMP date, BIGINT|INT months)',
        description: 'Returns the specified date and time minus some number of months.'
      },
      nanoseconds_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'nanoseconds_add(TIMESTAMP date, BIGINT|INT nanoseconds)',
        description: 'Returns the specified date and time plus some number of nanoseconds.'
      },
      nanoseconds_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'nanoseconds_sub(TIMESTAMP date, BIGINT|INT nanoseconds)',
        description: 'Returns the specified date and time minus some number of nanoseconds.'
      },
      now: {
        returnTypes: ['TIMESTAMP'],
        arguments: [],
        signature: 'now()',
        description: 'Returns the current date and time (in the local time zone) as a timestamp value.'
      },
      second: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'second(STRING date)',
        description: 'Returns the second field from a date represented as a string.'
      },
      seconds_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'seconds_add(TIMESTAMP date, BIGINT|INT seconds)',
        description: 'Returns the specified date and time plus some number of seconds.'
      },
      seconds_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'seconds_sub(TIMESTAMP date, BIGINT|INT seconds)',
        description: 'Returns the specified date and time minus some number of seconds.'
      },
      subdate: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'subdate(TIMESTAMP startdate, BIGINT|INT days)',
        description: 'Subtracts a specified number of days from a TIMESTAMP value. Similar to date_sub(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.'
      },
      to_date: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'TIMESTAMP'}]],
        signature: 'to_date(TIMESTAMP date)',
        description: 'Returns a string representation of the date field from a timestamp value.'
      },
      to_utc_timestamp: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'STRING'}]],
        signature: 'to_utc_timestamp(TIMESTAMP date, STRING timezone)',
        description: 'Converts a specified timestamp value in a specified time zone into the corresponding value for the UTC time zone.'
      },
      trunc: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'STRING'}]],
        signature: 'trunc(TIMESTAMP date, STRING unit)',
        description: 'Strips off fields and optionally rounds a TIMESTAMP value. The unit argument value is case-sensitive. This argument string can be one of: SYYYY, YYYY, YEAR, SYEAR, YYY, YY, Y: Year. Q: Quarter. MONTH, MON, MM, RM: Month. WW, W: Same day of the week as the first day of the month. DDD, DD, J: Day. DAY, DY, D: Starting day of the week. (Not necessarily the current day.) HH, HH12, HH24: Hour. A TIMESTAMP value truncated to the hour is always represented in 24-hour notation, even for the HH12 argument string. MI: Minute.'
      },
      unix_timestamp: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING', optional: true}]],
        altArguments: [[{type: 'TIMESTAMP'}]],
        signature: 'unix_timestamp([STRING datetime [, STRING format]]|[TIMESTAMP datetime])',
        description: 'Returns an integer value representing the current date and time as a delta from the Unix epoch, or converts from a specified date and time value represented as a TIMESTAMP or STRING.'
      },
      weekofyear: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'weekofyear(STRING date)',
        description: 'Returns the corresponding week (1-53) from a date represented as a string.'
      },
      weeks_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'weeks_add(TIMESTAMP date, BIGINT|INT weeks)',
        description: 'Returns the specified date and time plus some number of weeks.'
      },
      weeks_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'weeks_sub(TIMESTAMP date, BIGINT|INT weeks)',
        description: 'Returns the specified date and time minus some number of weeks.'
      },
      year: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'year(STRING date)',
        description: 'Returns the year field from a date represented as a string.'
      },
      years_add: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'years_add(TIMESTAMP date, BIGINT|INT years)',
        description: 'Returns the specified date and time plus some number of years.'
      },
      years_sub: {
        returnTypes: ['TIMESTAMP'],
        arguments: [[{type: 'TIMESTAMP'}], [{type: 'BIGINT'}, {type: 'INT'}]],
        signature: 'years_sub(TIMESTAMP date, BIGINT|INT years)',
        description: 'Returns the specified date and time minus some number of years.'
      }
    }
  };

  var CONDITIONAL_FUNCTIONS = {
    hive: {
      coalesce: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'coalesce(T v1, T v2, ...)',
        description: 'Returns the first v that is not NULL, or NULL if all v\'s are NULL.'
      },
      if: {
        returnTypes: ['T'],
        arguments: [[{type: 'BOOLEAN'}], [{type: 'T'}], [{type: 'T'}]],
        signature: 'if(BOOLEAN testCondition, T valueTrue, T valueFalseOrNull)',
        description: 'Returns valueTrue when testCondition is true, returns valueFalseOrNull otherwise.'
      },
      isnotnull: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'T'}]],
        signature: 'isnotnull(a)',
        description: 'Returns true if a is not NULL and false otherwise.'
      },
      isnull: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'T'}]],
        signature: 'isnull(a)',
        description: 'Returns true if a is NULL and false otherwise.'
      },
      nvl: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'nvl(T value, T default_value)',
        description: 'Returns default value if value is null else returns value (as of Hive 0.11).'
      }
    },
    impala: {
      coalesce: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'coalesce(T v1, T v2, ...)',
        description: 'Returns the first specified argument that is not NULL, or NULL if all arguments are NULL.'
      },
      decode: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'T'}], [{type: 'T', multiple: true}]],
        signature: 'decode(T expression, T search1, T result1 [, T search2, T result2 ...] [, T default] )',
        description: 'Compares an expression to one or more possible values, and returns a corresponding result when a match is found.'
      },
      if: {
        returnTypes: ['T'],
        arguments: [[{type: 'BOOLEAN'}], [{type: 'T'}], [{type: 'T'}]],
        signature: 'if(BOOLEAN condition, T ifTrue, T ifFalseOrNull)',
        description: 'Tests an expression and returns a corresponding result depending on whether the result is true, false, or NULL.'
      },
      ifnull: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'ifnull(T a, T ifNotNull)',
        description: 'Alias for the isnull() function, with the same behavior. To simplify porting SQL with vendor extensions to Impala.'
      },
      isnull: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'isnull(T a, T ifNotNull)',
        description: 'Tests if an expression is NULL, and returns the expression result value if not. If the first argument is NULL, returns the second argument.'
      },
      nullif: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'nullif(T expr1, T expr2)',
        description: 'Returns NULL if the two specified arguments are equal. If the specified arguments are not equal, returns the value of expr1. The data types of the expressions must be compatible. You cannot use an expression that evaluates to NULL for expr1; that way, you can distinguish a return value of NULL from an argument value of NULL, which would never match expr2.'
      },
      nullifzero: {
        returnTypes: ['T'],
        arguments: [[{type: 'NUMBER'}]],
        signature: 'nullifzero(T numeric_expr)',
        description: 'Returns NULL if the numeric expression evaluates to 0, otherwise returns the result of the expression.'
      },
      nvl: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'T'}]],
        signature: 'nvl(T a, T ifNotNull)',
        description: 'Alias for the isnull() function. Tests if an expression is NULL, and returns the expression result value if not. If the first argument is NULL, returns the second argument. Equivalent to the nvl() function from Oracle Database or ifnull() from MySQL.'
      },
      zeroifnull: {
        returnTypes: ['T'],
        arguments: [[{type: 'NUMBER'}]],
        signature: 'zeroifnull(T numeric_expr)',
        description: 'Returns 0 if the numeric expression evaluates to NULL, otherwise returns the result of the expression.'
      }
    }
  };

  var STRING_FUNCTIONS = {
    hive: {
      ascii: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'ascii(STRING str)',
        description: 'Returns the numeric value of the first character of str.'
      },
      base64: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'BINARY'}]],
        signature: 'base64(BINARY bin)',
        description: 'Converts the argument from binary to a base 64 string (as of Hive 0.12.0).'
      },
      concat: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING', multiple: true}, {type: 'BINARY', multiple: true}]],
        signature: 'concat(STRING|BINARY a, STRING|BINARY b...)',
        description: 'Returns the string or bytes resulting from concatenating the strings or bytes passed in as parameters in order. For example, concat(\'foo\', \'bar\') results in \'foobar\'. Note that this function can take any number of input strings.'
      },
      concat_ws: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING', multiple: true}]],
        altArguments: [[{type: 'STRING'}], [{type: 'ARRAY'}]],
        signature: 'concat_ws(STRING sep, STRING a, STRING b...), concat_ws(STRING sep, Array<STRING>)',
        description: 'Like concat(), but with custom separator SEP.'
      },
      context_ngrams: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'ARRAY'}], [{type: 'ARRAY'}], [{type: 'INT'}], [{type: 'INT'}]],
        signature: 'array<struct<STRING,DOUBLE>> context_ngrams(Array<Array<STRING>>, Array<STRING>, INT k, INT pf)',
        description: 'Returns the top-k contextual N-grams from a set of tokenized sentences, given a string of "context".'
      },
      decode: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'BINARY'}], [{type: 'STRING'}]],
        signature: 'decode(BINARY bin, STRING charset)',
        description: 'Decodes the first argument into a String using the provided character set (one of \'US-ASCII\', \'ISO-8859-1\', \'UTF-8\', \'UTF-16BE\', \'UTF-16LE\', \'UTF-16\'). If either argument is null, the result will also be null. (As of Hive 0.12.0.)'
      },
      encode: {
        returnTypes: ['BINARY'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'encode(STRING src, STRING charset)',
        description: 'Encodes the first argument into a BINARY using the provided character set (one of \'US-ASCII\', \'ISO-8859-1\', \'UTF-8\', \'UTF-16BE\', \'UTF-16LE\', \'UTF-16\'). If either argument is null, the result will also be null. (As of Hive 0.12.0.)'
      },
      find_in_set: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'find_in_set(STRING str, STRING strList)',
        description: 'Returns the first occurance of str in strList where strList is a comma-delimited string. Returns null if either argument is null. Returns 0 if the first argument contains any commas. For example, find_in_set(\'ab\', \'abc,b,ab,c,def\') returns 3.'
      },
      format_number: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'NUMBER'}], [{type: 'INT'}]],
        signature: 'format_number(NUMBER x, INT d)',
        description: 'Formats the number X to a format like \'#,###,###.##\', rounded to D decimal places, and returns the result as a string. If D is 0, the result has no decimal point or fractional part. (As of Hive 0.10.0; bug with float types fixed in Hive 0.14.0, decimal type support added in Hive 0.14.0)'
      },
      get_json_object: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'get_json_object(STRING json_string, STRING path)',
        description: 'Extracts json object from a json string based on json path specified, and returns json string of the extracted json object. It will return null if the input json string is invalid. NOTE: The json path can only have the characters [0-9a-z_], i.e., no upper-case or special characters. Also, the keys *cannot start with numbers.* This is due to restrictions on Hive column names.'
      },
      initcap: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'initcap(STRING a)',
        description: 'Returns string, with the first letter of each word in uppercase, all other letters in lowercase. Words are delimited by whitespace. (As of Hive 1.1.0.)'
      },
      instr: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'instr(STRING str, STRING substr)',
        description: 'Returns the position of the first occurrence of substr in str. Returns null if either of the arguments are null and returns 0 if substr could not be found in str. Be aware that this is not zero based. The first character in str has index 1.'
      },
      in_file: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'in_file(STRING str, STRING filename)',
        description: 'Returns true if the string str appears as an entire line in filename.'
      },
      length: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'length(STRING a)',
        description: 'Returns the length of the string.'
      },
      levenshtein: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'levenshtein(STRING a, STRING b)',
        description: 'Returns the Levenshtein distance between two strings (as of Hive 1.2.0). For example, levenshtein(\'kitten\', \'sitting\') results in 3.'
      },
      lcase: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'lcase(STRING a)',
        description: 'Returns the string resulting from converting all characters of B to lower case. For example, lcase(\'fOoBaR\') results in \'foobar\'.'
      },
      locate: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'INT', optional: true}]],
        signature: 'locate(STRING substr, STRING str [, INT pos])',
        description: 'Returns the position of the first occurrence of substr in str after position pos.'
      },
      lower: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'lower(STRING a)',
        description: 'Returns the string resulting from converting all characters of B to lower case. For example, lower(\'fOoBaR\') results in \'foobar\'.'
      },
      lpad: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}], [{type: 'STRING'}]],
        signature: 'lpad(STRING str, INT len, STRING pad)',
        description: 'Returns str, left-padded with pad to a length of len.'
      },
      ltrim: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'ltrim(STRING a)',
        description: 'Returns the string resulting from trimming spaces from the beginning(left hand side) of A. For example, ltrim(\' foobar \') results in \'foobar \'.'
      },
      ngrams: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'ARRAY'}], [{type: 'INT'}], [{type: 'INT'}], [{type: 'INT'}]],
        signature: 'array<struct<STRING, DOUBLE>> ngrams(Array<Array<STRING>> a, INT n, INT k, INT pf)',
        description: 'Returns the top-k N-grams from a set of tokenized sentences, such as those returned by the sentences() UDAF.'
      },
      parse_url: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING', optional: true}]],
        signature: 'parse_url(STRING urlString, STRING partToExtract [, STRING keyToExtract])',
        description: 'Returns the specified part from the URL. Valid values for partToExtract include HOST, PATH, QUERY, REF, PROTOCOL, AUTHORITY, FILE, and USERINFO. For example, parse_url(\'http://facebook.com/path1/p.php?k1=v1&k2=v2#Ref1\', \'HOST\') returns \'facebook.com\'. Also a value of a particular key in QUERY can be extracted by providing the key as the third argument, for example, parse_url(\'http://facebook.com/path1/p.php?k1=v1&k2=v2#Ref1\', \'QUERY\', \'k1\') returns \'v1\'.'
      },
      printf: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'T', multiple: true}]],
        signature: 'printf(STRING format, Obj... args)',
        description: 'Returns the input formatted according do printf-style format strings (as of Hive 0.9.0).'
      },
      regexp_extract: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'INT'}]],
        signature: 'regexp_extract(STRING subject, STRING pattern, INT index)',
        description: 'Returns the string extracted using the pattern. For example, regexp_extract(\'foothebar\', \'foo(.*?)(bar)\', 2) returns \'bar.\' Note that some care is necessary in using predefined character classes: using \'\\s\' as the second argument will match the letter s; \'\\\\s\' is necessary to match whitespace, etc. The \'index\' parameter is the Java regex Matcher group() method index.'
      },
      regexp_replace: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'regexp_replace(STRING initial_string, STRING pattern, STRING replacement)',
        description: 'Returns the string resulting from replacing all substrings in INITIAL_STRING that match the java regular expression syntax defined in PATTERN with instances of REPLACEMENT. For example, regexp_replace("foobar", "oo|ar", "") returns \'fb.\' Note that some care is necessary in using predefined character classes: using \'\\s\' as the second argument will match the letter s; \'\\\\s\' is necessary to match whitespace, etc.'
      },
      repeat: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}]],
        signature: 'repeat(STRING str, INT n)',
        description: 'Repeats str n times.'
      },
      reverse: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'reverse(STRING a)',
        description: 'Returns the reversed string.'
      },
      rpad: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}], [{type: 'STRING'}]],
        signature: 'rpad(STRING str, INT len, STRING pad)',
        description: 'Returns str, right-padded with pad to a length of len.'
      },
      rtrim: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'rtrim(STRING a)',
        description: 'Returns the string resulting from trimming spaces from the end(right hand side) of A. For example, rtrim(\' foobar \') results in \' foobar\'.'
      },
      sentences: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'array<array<STRING>> sentences(STRING str, STRING lang, STRING locale)',
        description: 'Tokenizes a string of natural language text into words and sentences, where each sentence is broken at the appropriate sentence boundary and returned as an array of words. The \'lang\' and \'locale\' are optional arguments. For example, sentences(\'Hello there! How are you?\') returns ( ("Hello", "there"), ("How", "are", "you") ).'
      },
      soundex: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'soundex(STRING a)',
        description: 'Returns soundex code of the string (as of Hive 1.2.0). For example, soundex(\'Miller\') results in M460.'
      },
      space: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'INT'}]],
        signature: 'space(INT n)',
        description: 'Returns a string of n spaces.'
      },
      split: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'array<STRING> split(STRING str, STRING pat)',
        description: 'Splits str around pat (pat is a regular expression).'
      },
      str_to_map: {
        returnTypes: ['MAP'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING', optional: true}], [{type: 'STRING', optional: true}]],
        signature: 'map<STRING,STRING> str_to_map(STRING [, STRING delimiter1, STRING delimiter2])',
        description: 'Splits text into key-value pairs using two delimiters. Delimiter1 separates text into K-V pairs, and Delimiter2 splits each K-V pair. Default delimiters are \',\' for delimiter1 and \'=\' for delimiter2.'
      },
      substr: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}, {type: 'BINARY'}], [{type: 'INT'}], [{type: 'INT', optional: true}]],
        signature: 'substr(STRING|BINARY A, INT start [, INT len]) ',
        description: 'Returns the substring or slice of the byte array of A starting from start position till the end of string A or with optional length len. For example, substr(\'foobar\', 4) results in \'bar\''
      },
      substring: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}, {type: 'BINARY'}], [{type: 'INT'}], [{type: 'INT', optional: true}]],
        signature: 'substring(STRING|BINARY a, INT start [, INT len])',
        description: 'Returns the substring or slice of the byte array of A starting from start position till the end of string A or with optional length len. For example, substr(\'foobar\', 4) results in \'bar\''
      },
      substring_index: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'INT'}]],
        signature: 'substring_index(STRING a, STRING delim, INT count)',
        description: 'Returns the substring from string A before count occurrences of the delimiter delim (as of Hive 1.3.0). If count is positive, everything to the left of the final delimiter (counting from the left) is returned. If count is negative, everything to the right of the final delimiter (counting from the right) is returned. Substring_index performs a case-sensitive match when searching for delim. Example: substring_index(\'www.apache.org\', \'.\', 2) = \'www.apache\'.'
      },
      translate: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}, {type: 'CHAR'}, {type: 'VARCHAR'}], [{type: 'STRING'}, {type: 'CHAR'}, {type: 'VARCHAR'}], [{type: 'STRING'}, {type: 'CHAR'}, {type: 'VARCHAR'}]],
        signature: 'translate(STRING|CHAR|VARCHAR input, STRING|CHAR|VARCHAR from, STRING|CHAR|VARCHAR to)',
        description: 'Translates the input string by replacing the characters present in the from string with the corresponding characters in the to string. This is similar to the translate function in PostgreSQL. If any of the parameters to this UDF are NULL, the result is NULL as well. (Available as of Hive 0.10.0, for string types) Char/varchar support added as of Hive 0.14.0.'
      },
      trim: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'trim(STRING a)',
        description: 'Returns the string resulting from trimming spaces from both ends of A. For example, trim(\' foobar \') results in \'foobar\''
      },
      ucase: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'ucase(STRING a)',
        description: 'Returns the string resulting from converting all characters of A to upper case. For example, ucase(\'fOoBaR\') results in \'FOOBAR\'.'
      },
      unbase64: {
        returnTypes: ['BINARY'],
        arguments: [[{type: 'STRING'}]],
        signature: 'unbase64(STRING a)',
        description: 'Converts the argument from a base 64 string to BINARY. (As of Hive 0.12.0.)'
      },
      upper: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'upper(STRING a)',
        description: 'Returns the string resulting from converting all characters of A to upper case. For example, upper(\'fOoBaR\') results in \'FOOBAR\'.'
      }
    },
    impala: {
      ascii: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'ascii(STRING str)',
        description: 'Returns the numeric ASCII code of the first character of the argument.'
      },
      char_length: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'char_length(STRING a)',
        description: 'Returns the length in characters of the argument string. Aliases for the length() function.'
      },
      character_length: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'character_length(STRING a)',
        description: 'Returns the length in characters of the argument string. Aliases for the length() function.'
      },
      concat: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING', multiple: true}]],
        signature: 'concat(STRING a, STRING b...)',
        description: 'Returns a single string representing all the argument values joined together.'
      },
      concat_ws: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING', multiple: true}]],
        signature: 'concat_ws(STRING sep, STRING a, STRING b...)',
        description: 'Returns a single string representing the second and following argument values joined together, delimited by a specified separator.'
      },
      find_in_set: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'find_in_set(STRING str, STRING strList)',
        description: 'Returns the position (starting from 1) of the first occurrence of a specified string within a comma-separated string. Returns NULL if either argument is NULL, 0 if the search string is not found, or 0 if the search string contains a comma.'
      },
      group_concat: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING', optional: true}]],
        signature: 'group_concat(STRING s [, STRING sep])',
        description: 'Returns a single string representing the argument value concatenated together for each row of the result set. If the optional separator string is specified, the separator is added between each pair of concatenated values.'
      },
      initcap: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'initcap(STRING str)',
        description: 'Returns the input string with the first letter capitalized.'
      },
      instr: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'instr(STRING str, STRING substr)',
        description: 'Returns the position (starting from 1) of the first occurrence of a substring within a longer string.'
      },
      length: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}]],
        signature: 'length(STRING a)',
        description: 'Returns the length in characters of the argument string.'
      },
      locate: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'INT', optional: true}]],
        signature: 'locate(STRING substr, STRING str[, INT pos])',
        description: 'Returns the position (starting from 1) of the first occurrence of a substring within a longer string, optionally after a particular position.'
      },
      lower: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'lower(STRING a)',
        description: 'Returns the argument string converted to all-lowercase.'
      },
      lcase: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'lcase(STRING a)',
        description: 'Returns the argument string converted to all-lowercase.'
      },
      lpad: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}], [{type: 'STRING'}]],
        signature: 'lpad(STRING str, INT len, STRING pad)',
        description: 'Returns a string of a specified length, based on the first argument string. If the specified string is too short, it is padded on the left with a repeating sequence of the characters from the pad string. If the specified string is too long, it is truncated on the right.'
      },
      ltrim: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'ltrim(STRING a)',
        description: 'Returns the argument string with any leading spaces removed from the left side.'
      },
      parse_url: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING', optional: true}]],
        signature: 'parse_url(STRING urlString, STRING partToExtract [, STRING keyToExtract])',
        description: 'Returns the portion of a URL corresponding to a specified part. The part argument can be \'PROTOCOL\', \'HOST\', \'PATH\', \'REF\', \'AUTHORITY\', \'FILE\', \'USERINFO\', or \'QUERY\'. Uppercase is required for these literal values. When requesting the QUERY portion of the URL, you can optionally specify a key to retrieve just the associated value from the key-value pairs in the query string.'
      },
      regexp_extract: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'INT'}]],
        signature: 'regexp_extract(STRING subject, STRING pattern, INT index)',
        description: 'Returns the specified () group from a string based on a regular expression pattern. Group 0 refers to the entire extracted string, while group 1, 2, and so on refers to the first, second, and so on (...) portion.'
      },
      regexp_replace: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'regexp_replace(STRING initial, STRING pattern, STRING replacement)',
        description: 'Returns the initial argument with the regular expression pattern replaced by the final argument string.'
      },
      repeat: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}]],
        signature: 'repeat(STRING str, INT n)',
        description: 'Returns the argument string repeated a specified number of times.'
      },
      reverse: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'reverse(STRING a)',
        description: 'Returns the argument string with characters in reversed order.'
      },
      rpad: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}], [{type: 'STRING'}]],
        signature: 'rpad(STRING str, INT len, STRING pad)',
        description: 'Returns a string of a specified length, based on the first argument string. If the specified string is too short, it is padded on the right with a repeating sequence of the characters from the pad string. If the specified string is too long, it is truncated on the right.'
      },
      rtrim: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'rtrim(STRING a)',
        description: 'Returns the argument string with any trailing spaces removed from the right side.'
      },
      space: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'INT'}]],
        signature: 'space(INT n)',
        description: 'Returns a concatenated string of the specified number of spaces. Shorthand for repeat(\' \', n).'
      },
      strleft: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}]],
        signature: 'strleft(STRING a, INT num_chars)',
        description: 'Returns the leftmost characters of the string. Shorthand for a call to substr() with 2 arguments.'
      },
      strright: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}]],
        signature: 'strright(STRING a, INT num_chars)',
        description: 'Returns the rightmost characters of the string. Shorthand for a call to substr() with 2 arguments.'
      },
      substr: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}], [{type: 'INT', optional: true}]],
        signature: 'substr(STRING a, INT start [, INT len])',
        description: 'Returns the portion of the string starting at a specified point, optionally with a specified maximum length. The characters in the string are indexed starting at 1.'
      },
      substring: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'INT'}], [{type: 'INT', optional: true}]],
        signature: 'substring(STRING a, INT start [, INT len])',
        description: 'Returns the portion of the string starting at a specified point, optionally with a specified maximum length. The characters in the string are indexed starting at 1.'
      },
      translate: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'translate(STRING input, STRING from, STRING to)',
        description: 'Returns the input string with a set of characters replaced by another set of characters.'
      },
      trim: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'trim(STRING a)',
        description: 'Returns the input string with both leading and trailing spaces removed. The same as passing the string through both ltrim() and rtrim().'
      },
      upper: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'upper(STRING a)',
        description: 'Returns the argument string converted to all-uppercase.'
      },
      ucase: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}]],
        signature: 'ucase(STRING a)',
        description: 'Returns the argument string converted to all-uppercase.'
      }
    }
  };

  var TABLE_GENERATING_FUNCTIONS = {
    hive: {
      explode: {
        returnTypes: ['table'],
        arguments: [[{type: 'ARRAY'}, {type: 'MAP'}]],
        signature: 'explode(Array|Array<T>|Map a)',
        description: ''
      },
      inline: {
        returnTypes: ['table'],
        arguments: [[{type: 'ARRAY'}]],
        signature: 'inline(Array<Struct [, Struct]> a)',
        description: 'Explodes an array of structs into a table. (As of Hive 0.10.)'
      },
      json_tuple: {
        returnTypes: ['table'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING', multiple: true}]],
        signature: 'json_tuple(STRING jsonStr, STRING k1, STRING k2, ...)',
        description: 'A new json_tuple() UDTF is introduced in Hive 0.7. It takes a set of names (keys) and a JSON string, and returns a tuple of values using one function. This is much more efficient than calling GET_JSON_OBJECT to retrieve more than one key from a single JSON string.'
      },
      parse_url_tuple: {
        returnTypes: ['table'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING', multiple: true}]],
        signature: 'parse_url_tuple(STRING url, STRING p1, STRING p2, ...)',
        description: 'The parse_url_tuple() UDTF is similar to parse_url(), but can extract multiple parts of a given URL, returning the data in a tuple. Values for a particular key in QUERY can be extracted by appending a colon and the key to the partToExtract argument.'
      },
      posexplode: {
        returnTypes: ['table'],
        arguments: [[{type: 'ARRAY'}]],
        signature: 'posexplode(ARRAY) ',
        description: 'posexplode() is similar to explode but instead of just returning the elements of the array it returns the element as well as its position  in the original array.'
      },
      stack: {
        returnTypes: ['table'],
        arguments: [[{type: 'INT'}], [{type: 'T', multiple: true}]],
        signature: 'stack(INT n, v1, v2, ..., vk)',
        description: 'Breaks up v1, v2, ..., vk into n rows. Each row will have k/n columns. n must be constant.'
      }
    },
    impala: {}
  };

  var MISC_FUNCTIONS = {
    hive: {
      aes_decrypt: {
        returnTypes: ['BINARY'],
        arguments: [[{type: 'BINARY'}], [{type: 'BINARY'}, {type: 'STRING'}]],
        signature: 'aes_decrypt(BINARY input, STRING|BINARY key)',
        description: 'Decrypt input using AES (as of Hive 1.3.0). Key lengths of 128, 192 or 256 bits can be used. 192 and 256 bits keys can be used if Java Cryptography Extension (JCE) Unlimited Strength Jurisdiction Policy Files are installed. If either argument is NULL or the key length is not one of the permitted values, the return value is NULL. Example: aes_decrypt(unbase64(\'y6Ss+zCYObpCbgfWfyNWTw==\'), \'1234567890123456\') = \'ABC\'.'
      },
      aes_encrypt: {
        returnTypes: ['BINARY'],
        arguments: [[{type: 'STRING'}, {type: 'BINARY'}], [{type: 'STRING'}, {type: 'BINARY'}]],
        signature: 'aes_encrypt(STRING|BINARY input, STRING|BINARY key)',
        description: 'Encrypt input using AES (as of Hive 1.3.0). Key lengths of 128, 192 or 256 bits can be used. 192 and 256 bits keys can be used if Java Cryptography Extension (JCE) Unlimited Strength Jurisdiction Policy Files are installed. If either argument is NULL or the key length is not one of the permitted values, the return value is NULL. Example: base64(aes_encrypt(\'ABC\', \'1234567890123456\')) = \'y6Ss+zCYObpCbgfWfyNWTw==\'.'
      },
      crc32: {
        returnTypes: ['BIGINT'],
        arguments: [[{type: 'STRING'}, {type: 'BINARY'}]],
        signature: 'crc32(STRING|BINARY a)',
        description: 'Computes a cyclic redundancy check value for string or binary argument and returns bigint value (as of Hive 1.3.0). Example: crc32(\'ABC\') = 2743272264.'
      },
      current_database: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'current_database()',
        description: 'Returns current database name (as of Hive 0.13.0).'
      },
      current_user: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'current_user()',
        description: 'Returns current user name (as of Hive 1.2.0).'
      },
      get_json_object: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'get_json_object(STRING json, STRING jsonPath)',
        description: 'A limited version of JSONPath is supported ($ : Root object, . : Child operator, [] : Subscript operator for array, * : Wildcard for []'
      },
      hash: {
        returnTypes: ['INT'],
        arguments: [[{type: 'T', multiple: true}]],
        signature: 'hash(a1[, a2...])',
        description: 'Returns a hash value of the arguments. (As of Hive 0.4.)'
      },
      java_method: {
        returnTypes: ['T'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'T', multiple: true, optional: true}]],
        signature: 'java_method(class, method[, arg1[, arg2..]])',
        description: 'Calls a Java method by matching the argument signature, using reflection. (As of Hive 0.9.0.)'
      },
      md5: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}, {type: 'BINARY'}]],
        signature: 'md5(STRING|BINARY a)	',
        description: 'Calculates an MD5 128-bit checksum for the string or binary (as of Hive 1.3.0). The value is returned as a string of 32 hex digits, or NULL if the argument was NULL. Example: md5(\'ABC\') = \'902fbdd2b1df0c4f70b4a5d23525e932\'.'
      },
      reflect: {
        returnTypes: ['T'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}], [{type: 'T', multiple: true, optional: true}]],
        signature: 'reflect(class, method[, arg1[, arg2..]])',
        description: 'Calls a Java method by matching the argument signature, using reflection. (As of Hive 0.7.0.)'
      },
      sha: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}, {type: 'BINARY'}]],
        signature: 'sha(STRING|BINARY a)',
        description: 'Calculates the SHA-1 digest for string or binary and returns the value as a hex string (as of Hive 1.3.0). Example: sha1(\'ABC\') = \'3c01bdbb26f358bab27f267924aa2c9a03fcfdb8\'.'
      },
      sha1: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}, {type: 'BINARY'}]],
        signature: 'sha1(STRING|BINARY a)',
        description: 'Calculates the SHA-1 digest for string or binary and returns the value as a hex string (as of Hive 1.3.0). Example: sha1(\'ABC\') = \'3c01bdbb26f358bab27f267924aa2c9a03fcfdb8\'.'
      },
      sha2: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}, {type: 'BINARY'}], [{type: 'INT'}]],
        signature: 'sha2(STRING|BINARY a, INT b)',
        description: 'Calculates the SHA-2 family of hash functions (SHA-224, SHA-256, SHA-384, and SHA-512) (as of Hive 1.3.0). The first argument is the string or binary to be hashed. The second argument indicates the desired bit length of the result, which must have a value of 224, 256, 384, 512, or 0 (which is equivalent to 256). SHA-224 is supported starting from Java 8. If either argument is NULL or the hash length is not one of the permitted values, the return value is NULL. Example: sha2(\'ABC\', 256) = \'b5d4045c3f466fa91fe2cc6abe79232a1a57cdf104f7a26e716e0a1e2789df78\'.'
      },
      xpath: {
        returnTypes: ['ARRAY'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'array<STRING> xpath(STRING xml, STRING xpath)',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_boolean: {
        returnTypes: ['BOOLEAN'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'xpath_boolean(STRING xml, STRING xpath)',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_double: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'xpath_double(STRING xml, STRING xpath)',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_float: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'xpath_float(STRING xml, STRING xpath)',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_int: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'xpath_int(STRING xml, STRING xpath)',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_long: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'xpath_long(STRING xml, STRING xpath)',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_number: {
        returnTypes: ['DOUBLE'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'xpath_number(STRING xml, STRING xpath)',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_short: {
        returnTypes: ['INT'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'xpath_short(STRING xml, STRING xpath)',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      },
      xpath_string: {
        returnTypes: ['STRING'],
        arguments: [[{type: 'STRING'}], [{type: 'STRING'}]],
        signature: 'xpath_string(STRING xml, STRING xpath)',
        description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
      }
    },
    impala: {
      current_database: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'current_database()',
        description: 'Returns the database that the session is currently using, either default if no database has been selected, or whatever database the session switched to through a USE statement or the impalad - d option'
      },
      pid: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'pid()',
        description: 'Returns the process ID of the impalad daemon that the session is connected to.You can use it during low - level debugging, to issue Linux commands that trace, show the arguments, and so on the impalad process.'
      },
      user: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'user()',
        description: 'Returns the username of the Linux user who is connected to the impalad daemon.Typically called a single time, in a query without any FROM clause, to understand how authorization settings apply in a security context; once you know the logged - in user name, you can check which groups that user belongs to, and from the list of groups you can check which roles are available to those groups through the authorization policy file.In Impala 2.0 and later, user() returns the the full Kerberos principal string, such as user@example.com, in a Kerberized environment.'
      },
      version: {
        returnTypes: ['STRING'],
        arguments: [],
        signature: 'version()',
        description: 'Returns information such as the precise version number and build date for the impalad daemon that you are currently connected to.Typically used to confirm that you are connected to the expected level of Impala to use a particular feature, or to connect to several nodes and confirm they are all running the same level of impalad.'
      }
    }
  };

  var ANALYTIC_FUNCTIONS = {
    hive: {
      cume_dist: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true, optional: true }]],
        signature: 'cume_dist()',
        description: ''
      },
      dense_rank: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'dense_rank() OVER([partition_by_clause] order_by_clause)',
        description: 'Returns an ascending sequence of integers, starting with 1. The output sequence produces duplicate integers for duplicate values of the ORDER BY expressions.'
      },
      first_value: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'first_value(expr) OVER([partition_by_clause] order_by_clause [window_clause])',
        description: 'Returns the expression value from the first row in the window. The return value is NULL if the input expression is NULL.'
      },
      lag: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'INT', optional: true}], [{type: 'T', optional: true}]],
        signature: 'lag(expr [, offset] [, default]) OVER ([partition_by_clause] order_by_clause)',
        description: 'This function returns the value of an expression using column values from a preceding row. You specify an integer offset, which designates a row position some number of rows previous to the current row. Any column references in the expression argument refer to column values from that prior row.'
      },
      last_value: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'last_value(expr) OVER([partition_by_clause] order_by_clause [window_clause])',
        description: 'Returns the expression value from the last row in the window. The return value is NULL if the input expression is NULL.'
      },
      lead: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'INT', optional: true}], [{type: 'T', optional: true}]],
        signature: 'lead(expr [, offset] [, default]) OVER ([partition_by_clause] order_by_clause)',
        description: 'This function returns the value of an expression using column values from a following row. You specify an integer offset, which designates a row position some number of rows after to the current row. Any column references in the expression argument refer to column values from that later row.'
      },
      ntile: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true, optional: true }]],
        signature: 'ntile()',
        description: ''
      },
      percent_rank: {
        returnTypes: ['T'],
        arguments: [[{type: 'T', multiple: true, optional: true }]],
        signature: 'percent_rank()',
        description: ''
      },
      rank: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'rank() OVER([partition_by_clause] order_by_clause)',
        description: 'Returns an ascending sequence of integers, starting with 1. The output sequence produces duplicate integers for duplicate values of the ORDER BY expressions. After generating duplicate output values for the "tied" input values, the function increments the sequence by the number of tied values.'
      },
      row_number: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'row_number() OVER([partition_by_clause] order_by_clause)',
        description: 'Returns an ascending sequence of integers, starting with 1. Starts the sequence over for each group produced by the PARTITIONED BY clause. The output sequence includes different values for duplicate input values. Therefore, the sequence never contains any duplicates or gaps, regardless of duplicate input values.'
      }
    },
    impala: {
      dense_rank: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'dense_rank() OVER([partition_by_clause] order_by_clause)',
        description: 'Returns an ascending sequence of integers, starting with 1. The output sequence produces duplicate integers for duplicate values of the ORDER BY expressions.'
      },
      first_value: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'first_value(expr) OVER([partition_by_clause] order_by_clause [window_clause])',
        description: 'Returns the expression value from the first row in the window. The return value is NULL if the input expression is NULL.'
      },
      lag: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'INT', optional: true}], [{type: 'T', optional: true}]],
        signature: 'lag(expr [, offset] [, default]) OVER ([partition_by_clause] order_by_clause)',
        description: 'This function returns the value of an expression using column values from a preceding row. You specify an integer offset, which designates a row position some number of rows previous to the current row. Any column references in the expression argument refer to column values from that prior row.'
      },
      last_value: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}]],
        signature: 'last_value(expr) OVER([partition_by_clause] order_by_clause [window_clause])',
        description: 'Returns the expression value from the last row in the window. The return value is NULL if the input expression is NULL.'
      },
      lead: {
        returnTypes: ['T'],
        arguments: [[{type: 'T'}], [{type: 'INT', optional: true}], [{type: 'T', optional: true}]],
        signature: 'lead(expr [, offset] [, default]) OVER ([partition_by_clause] order_by_clause)',
        description: 'This function returns the value of an expression using column values from a following row. You specify an integer offset, which designates a row position some number of rows after to the current row. Any column references in the expression argument refer to column values from that later row.'
      },
      rank: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'rank() OVER([partition_by_clause] order_by_clause)',
        description: 'Returns an ascending sequence of integers, starting with 1. The output sequence produces duplicate integers for duplicate values of the ORDER BY expressions. After generating duplicate output values for the "tied" input values, the function increments the sequence by the number of tied values.'
      },
      row_number: {
        returnTypes: ['INT'],
        arguments: [],
        signature: 'row_number() OVER([partition_by_clause] order_by_clause)',
        description: 'Returns an ascending sequence of integers, starting with 1. Starts the sequence over for each group produced by the PARTITIONED BY clause. The output sequence includes different values for duplicate input values. Therefore, the sequence never contains any duplicates or gaps, regardless of duplicate input values.'
      }
    }
  };

  var CATEGORIZED_FUNCTIONS = {
    hive: [
      { name: 'Aggregate', functions: AGGREGATE_FUNCTIONS['hive'] },
      { name: 'Analytic', functions: ANALYTIC_FUNCTIONS['hive'] },
      { name: 'Collection', functions: COLLECTION_FUNCTIONS['hive'] },
      { name: 'Complex Type', functions: COMPLEX_TYPE_CONSTRUCTS['hive'] },
      { name: 'Conditional', functions: CONDITIONAL_FUNCTIONS['hive'] },
      { name: 'Date', functions: DATE_FUNCTIONS['hive'] },
      { name: 'Mathematical', functions: MATHEMATICAL_FUNCTIONS['hive'] },
      { name: 'Misc', functions: MISC_FUNCTIONS['hive'] },
      { name: 'String', functions: STRING_FUNCTIONS['hive'] },
      { name: 'Table Generating', functions: TABLE_GENERATING_FUNCTIONS['hive'] },
      { name: 'Type Conversion', functions: TYPE_CONVERSION_FUNCTIONS['hive'] }
    ],
    impala: [
      { name: 'Aggregate', functions: AGGREGATE_FUNCTIONS['impala'] },
      { name: 'Analytic', functions: ANALYTIC_FUNCTIONS['impala'] },
      { name: 'Conditional', functions: CONDITIONAL_FUNCTIONS['impala'] },
      { name: 'Date', functions: DATE_FUNCTIONS['impala'] },
      { name: 'Mathematical', functions: MATHEMATICAL_FUNCTIONS['impala'] },
      { name: 'Misc', functions: MISC_FUNCTIONS['impala'] },
      { name: 'String', functions: STRING_FUNCTIONS['impala'] },
      { name: 'Type Conversion', functions: TYPE_CONVERSION_FUNCTIONS['impala'] }
    ]
  };

  var typeImplicitConversion = {
    hive: {
      BOOLEAN: {
        BOOLEAN: true, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, FLOAT: false, DOUBLE: false, DECIMAL: false, NUMBER: false, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      TIMESTAMP: {
        BOOLEAN: false, TIMESTAMP: true, DATE: false, BINARY: false, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, FLOAT: false, DOUBLE: false, DECIMAL: false, NUMBER: false, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      DATE: {
        BOOLEAN: false, TIMESTAMP: false, DATE: true, BINARY: false, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, FLOAT: false, DOUBLE: false, DECIMAL: false, NUMBER: false, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      BINARY: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: true, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, FLOAT: false, DOUBLE: false, DECIMAL: false, NUMBER: false, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      TINYINT: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: true, SMALLINT: false, INT: false, BIGINT: false, FLOAT: false, DOUBLE: false, DECIMAL: false, NUMBER: true, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      SMALLINT: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: true, SMALLINT: true, INT: false, BIGINT: false, FLOAT: false, DOUBLE: false, DECIMAL: false, NUMBER: true, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      INT: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: false, FLOAT: false, DOUBLE: false, DECIMAL: false, NUMBER: true, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      BIGINT: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: false, DOUBLE: false, DECIMAL: false, NUMBER: true, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      FLOAT: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: true, DOUBLE: false, DECIMAL: false, NUMBER: true, STRING: false, CHAR: false, VARCHAR: false, T: true
      },
      DOUBLE: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: true, DOUBLE: true, DECIMAL: false, NUMBER: true, STRING: true, CHAR: true, VARCHAR: true, T: true
      },
      DECIMAL: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: true, DOUBLE: true, DECIMAL: true, NUMBER: true, STRING: true, CHAR: true, VARCHAR: true, T: true
      },
      NUMBER: {
        BOOLEAN: false, TIMESTAMP: false, DATE: false, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: true, DOUBLE: true, DECIMAL: true, NUMBER: true, STRING: true, CHAR: true, VARCHAR: true, T: true
      },
      STRING: {
        BOOLEAN: false, TIMESTAMP: true, DATE: true, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: true, DOUBLE: true, DECIMAL: true, NUMBER: true, STRING: true, CHAR: true, VARCHAR: true, T: true
      },
      CHAR: {
        BOOLEAN: false, TIMESTAMP: true, DATE: true, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: true, DOUBLE: true, DECIMAL: true, NUMBER: true, STRING: true, CHAR: true, VARCHAR: true, T: true
      },
      VARCHAR: {
        BOOLEAN: false, TIMESTAMP: true, DATE: true, BINARY: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: true, DOUBLE: true, DECIMAL: true, NUMBER: true, STRING: true, CHAR: true, VARCHAR: true, T: true
      },
      T: {
        BOOLEAN: true, TIMESTAMP: true, DATE: true, BINARY: true, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, FLOAT: true, DOUBLE: true, DECIMAL: true, NUMBER: true, STRING: true, CHAR: true, VARCHAR: true, T: true
      }
    },
    impala: {
      BOOLEAN: {
        BOOLEAN: true, TIMESTAMP: false, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: false, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      TIMESTAMP :{
        BOOLEAN: false, TIMESTAMP: true, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: false, CHAR: false, VARCHAR: false, STRING: true, T: true
      },
      TINYINT: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: false, INT: false, BIGINT: false, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      SMALLINT: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: true, INT: false, BIGINT: false, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      INT: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: false, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      BIGINT: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      DOUBLE: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, DOUBLE: true, REAL: true, DECIMAL: false, FLOAT: true, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      REAL: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, DOUBLE: true, REAL: true, DECIMAL: false, FLOAT: true, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      DECIMAL: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, DOUBLE: true, REAL: true, DECIMAL: true, FLOAT: true, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      FLOAT: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: true, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      NUMBER: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, DOUBLE: true, REAL: true, DECIMAL: true, FLOAT: true, NUMBER: true, CHAR: false, VARCHAR: false, STRING: false, T: true
      },
      CHAR: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: false, CHAR: true, VARCHAR: false, STRING: false, T: true
      },
      VARCHAR: {
        BOOLEAN: false, TIMESTAMP: false, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: false, CHAR: true, VARCHAR: true, STRING: false, T: true
      },
      STRING: {
        BOOLEAN: false, TIMESTAMP: true, TINYINT: false, SMALLINT: false, INT: false, BIGINT: false, DOUBLE: false, REAL: false, DECIMAL: false, FLOAT: false, NUMBER: false, CHAR: true, VARCHAR: false, STRING: true, T: true
      },
      T: {
        BOOLEAN: true, TIMESTAMP: true, TINYINT: true, SMALLINT: true, INT: true, BIGINT: true, DOUBLE: true, REAL: true, DECIMAL: true, FLOAT: true, NUMBER: true, CHAR: true, VARCHAR: true, STRING: true, T: true
      }
    }
  };

  var createDocHtml = function (funcDesc) {
    var html = '<div style="max-width: 600px; white-space: normal; overflow-y: auto; height: 100%; padding: 8px;"><p><span style="white-space: pre; font-family: monospace;">' + funcDesc.signature + '</span></p>';
    if (funcDesc.description) {
      html += '<p>' + funcDesc.description.replace(/[<]/g, "&lt;").replace(/[>]/g, "&gt;") + '</p>';
    }
    html += '<div>';
    return html;
  };

  var stripPrecision = function (types) {
    var result = [];
    types.forEach(function (type) {
      if (type.indexOf('(') > -1) {
        result.push(type.substring(0, type.indexOf('(')))
      } else {
        result.push(type);
      }
    });
    return result;
  };

  /**
   * Matches types based on implicit conversion i.e. if you expect a BIGINT then INT is ok but not BOOLEAN etc.
   *
   * @param dialect
   * @param expectedTypes
   * @param actualTypes
   * @returns {boolean}
   */
  var matchesType = function (dialect, expectedTypes, actualRawTypes) {
    if (dialect !== 'hive') {
      dialect = 'impala';
    }
    var actualTypes = stripPrecision(actualRawTypes);
    if (actualTypes.indexOf('ARRAY') !== -1 || actualTypes.indexOf('MAP') !== -1 || actualTypes.indexOf('STRUCT') !== -1) {
      return true;
    }
    for (var i = 0; i < expectedTypes.length; i++) {
      for (var j = 0; j < actualTypes.length; j++) {
        // To support future unknown types
        if (typeof typeImplicitConversion[dialect][expectedTypes[i]] === 'undefined' || typeof typeImplicitConversion[dialect][expectedTypes[i]][actualTypes[j]] == 'undefined') {
          return true;
        }
        if (typeImplicitConversion[dialect][expectedTypes[i]] && typeImplicitConversion[dialect][expectedTypes[i]][actualTypes[j]]) {
          return true;
        }
      }
    }
    return false;
  };

  var addFunctions = function (functionIndex, dialect, returnTypes, result) {
    var indexForDialect = functionIndex[dialect || 'generic'];
    if (indexForDialect) {
      Object.keys(indexForDialect).forEach(function (funcName) {
        var func = indexForDialect[funcName];
        if (typeof returnTypes === 'undefined' || matchesType(dialect, returnTypes, func.returnTypes)) {
          result[funcName] = func;
        }
      });
    }
    if (functionIndex.shared) {
      Object.keys(functionIndex.shared).forEach(function (funcName) {
        var func = functionIndex.shared[funcName];
        if (typeof returnTypes === 'undefined' || matchesType(dialect, returnTypes, func.returnTypes)) {
          result[funcName] = func;
        }
      });
    }
  };

  var getFunctionsWithReturnTypes = function (dialect, returnTypes, includeAggregate, includeAnalytic) {
    var result = {};
    addFunctions(COLLECTION_FUNCTIONS, dialect, returnTypes, result);
    addFunctions(CONDITIONAL_FUNCTIONS, dialect, returnTypes, result);
    addFunctions(COMPLEX_TYPE_CONSTRUCTS, dialect, returnTypes, result);
    addFunctions(DATE_FUNCTIONS, dialect, returnTypes, result);
    addFunctions(MATHEMATICAL_FUNCTIONS, dialect, returnTypes, result);
    addFunctions(TYPE_CONVERSION_FUNCTIONS, dialect, returnTypes, result);
    addFunctions(STRING_FUNCTIONS, dialect, returnTypes, result);
    addFunctions(MISC_FUNCTIONS, dialect, returnTypes, result);
    addFunctions(TABLE_GENERATING_FUNCTIONS, dialect, returnTypes, result);
    if (includeAggregate) {
      addFunctions(AGGREGATE_FUNCTIONS, dialect, returnTypes, result);
    }
    if (includeAnalytic) {
      addFunctions(ANALYTIC_FUNCTIONS, dialect, returnTypes, result);
    }
    return result;
  };

  var suggestFunctions = function (dialect, returnTypes, includeAggregate, includeAnalytic, completions, weight) {
    var functionsToSuggest = getFunctionsWithReturnTypes(dialect, returnTypes, includeAggregate, includeAnalytic);
    Object.keys(functionsToSuggest).forEach(function (name) {
      completions.push({
        value: name + '()',
        meta: functionsToSuggest[name].returnTypes.join('|'),
        weight: returnTypes.filter(function (type) {
          return functionsToSuggest[name].returnTypes.filter(
              function (otherType) {
                return otherType === type;
              }).length > 0
        }).length > 0 ? weight + 1 : weight,
        docHTML: createDocHtml(functionsToSuggest[name])
      })
    });
  };

  var findFunction = function (dialect, functionName) {
    return COLLECTION_FUNCTIONS[dialect][functionName] ||
        CONDITIONAL_FUNCTIONS[dialect][functionName] ||
        COMPLEX_TYPE_CONSTRUCTS[dialect][functionName] ||
        DATE_FUNCTIONS[dialect][functionName] ||
        MATHEMATICAL_FUNCTIONS[dialect][functionName] ||
        TYPE_CONVERSION_FUNCTIONS[dialect][functionName] ||
        STRING_FUNCTIONS[dialect][functionName] ||
        MISC_FUNCTIONS[dialect][functionName] ||
        TABLE_GENERATING_FUNCTIONS[dialect][functionName] ||
        AGGREGATE_FUNCTIONS[dialect][functionName];
  };

  var getArgumentTypes = function (dialect, functionName, argumentPosition) {
    if (dialect !== 'hive' && dialect !== 'impala') {
      return ['T'];
    }
    var foundFunction = findFunction(dialect, functionName);
    if (!foundFunction) {
      return ['T'];
    }
    var arguments = foundFunction.arguments;
    if (argumentPosition > arguments.length) {
      var multiples = arguments[arguments.length - 1].filter(function (type) {
        return type.multiple;
      });
      if (multiples.length > 0) {
        return multiples.map(function (argument) {
          return argument.type;
        }).sort();
      }
      return [];
    }
    return arguments[argumentPosition - 1].map(function (argument) {
      return argument.type;
    }).sort();
  };

  var getReturnTypes = function (dialect, functionName) {
    if (dialect !== 'hive' && dialect !== 'impala') {
      return ['T'];
    }
    var foundFunction = findFunction(dialect, functionName);
    if (!foundFunction) {
      return ['T'];
    }
    return foundFunction.returnTypes;
  };

  return {
    suggestFunctions: suggestFunctions,
    getArgumentTypes: getArgumentTypes,
    CATEGORIZED_FUNCTIONS: CATEGORIZED_FUNCTIONS,
    getFunctionsWithReturnTypes: getFunctionsWithReturnTypes,
    getReturnTypes: getReturnTypes,
    matchesType: matchesType,
    findFunction: findFunction
  };
})();