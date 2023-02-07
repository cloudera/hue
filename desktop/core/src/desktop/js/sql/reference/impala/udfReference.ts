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

const MATHEMATICAL_FUNCTIONS: UdfCategoryFunctions = {
  abs: {
    name: 'abs',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'abs(T a)',
    draggable: 'abs()',
    description:
      'Returns the absolute value of the argument. Use this function to ensure all return values are positive. This is different than the positive() function, which returns its argument unchanged (even if the argument was negative).'
  },
  acos: {
    name: 'acos',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'acos(DOUBLE a)',
    draggable: 'acos()',
    description: 'Returns the arccosine of the argument.'
  },
  asin: {
    name: 'asin',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'asin(DOUBLE a)',
    draggable: 'asin()',
    description: 'Returns the arcsine of the argument.'
  },
  atan: {
    name: 'atan',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'atan(DOUBLE a)',
    draggable: 'atan()',
    description: 'Returns the arctangent of the argument.'
  },
  atan2: {
    name: 'atan2',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }], [{ type: 'DOUBLE' }]],
    signature: 'atan2(DOUBLE a, DOUBLE b)',
    draggable: 'atan2()',
    description:
      'Returns the arctangent of the two arguments, with the signs of the arguments used to determine the quadrant of the result.'
  },
  bin: {
    name: 'bin',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'BIGINT' }]],
    signature: 'bin(BIGINT a)',
    draggable: 'bin()',
    description:
      'Returns the binary representation of an integer value, that is, a string of 0 and 1 digits.'
  },
  ceil: {
    name: 'ceil',
    returnTypes: ['T'],
    arguments: [[{ type: 'DOUBLE' }, { type: 'DECIMAL' }]],
    signature: 'ceil(T<DOUBLE|DECIMAL> a)',
    draggable: 'ceil()',
    description: 'Returns the smallest integer that is greater than or equal to the argument.'
  },
  ceiling: {
    name: 'ceiling',
    returnTypes: ['T'],
    arguments: [[{ type: 'DOUBLE' }, { type: 'DECIMAL' }]],
    signature: 'ceiling(T<DOUBLE|DECIMAL> a)',
    draggable: 'ceiling()',
    description: 'Returns the smallest integer that is greater than or equal to the argument.'
  },
  conv: {
    name: 'conv',
    returnTypes: ['T'],
    arguments: [[{ type: 'BIGINT' }, { type: 'STRING' }], [{ type: 'INT' }], [{ type: 'INT' }]],
    signature: 'conv(T<BIGINT|STRING> a, INT from_base, INT to_base)',
    draggable: 'conv()',
    description:
      'Returns a string representation of an integer value in a particular base. The input value can be a string, for example to convert a hexadecimal number such as fce2 to decimal. To use the return value as a number (for example, when converting to base 10), use CAST() to convert to the appropriate type.'
  },
  cos: {
    name: 'cos',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'cos(DOUBLE a)',
    draggable: 'cos()',
    description: 'Returns the cosine of the argument.'
  },
  cosh: {
    name: 'cosh',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'cosh(DOUBLE a)',
    draggable: 'cosh()',
    description: 'Returns the hyperbolic cosine of the argument.'
  },
  cot: {
    name: 'cot',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'cot(DOUBLE a)',
    draggable: 'cot()',
    description: 'Returns the cotangent of the argument.'
  },
  dceil: {
    name: 'dceil',
    returnTypes: ['T'],
    arguments: [[{ type: 'DOUBLE' }, { type: 'DECIMAL' }]],
    signature: 'dceil(T<DOUBLE|DECIMAL> a)',
    draggable: 'dceil()',
    description: 'Returns the smallest integer that is greater than or equal to the argument.'
  },
  degrees: {
    name: 'degrees',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'degrees(DOUBLE a)',
    draggable: 'degrees()',
    description: 'Converts argument value from radians to degrees.'
  },
  dexp: {
    name: 'dexp',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'dexp(DOUBLE a)',
    draggable: 'dexp()',
    description: 'Returns the mathematical constant e raised to the power of the argument.'
  },
  dfloor: {
    name: 'dfloor',
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'DOUBLE' }, { type: 'DECIMAL' }]],
    signature: 'dfloor(T<DOUBLE|DECIMAL> a)',
    draggable: 'dfloor()',
    description: 'Returns the largest integer that is less than or equal to the argument.'
  },
  dlog1: {
    name: 'dlog1',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'dlog1(DOUBLE a)',
    draggable: 'dlog1()',
    description: 'Returns the natural logarithm of the argument.'
  },
  dpow: {
    name: 'dpow',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }], [{ type: 'DOUBLE' }]],
    signature: 'dpow(DOUBLE a, DOUBLE p)',
    draggable: 'dpow()',
    description: 'Returns the first argument raised to the power of the second argument.'
  },
  dround: {
    name: 'dround',
    returnTypes: ['T'],
    arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }], [{ type: 'INT', optional: true }]],
    signature: 'dround(DOUBLE a [, INT d]), round(DECIMAL val, INT d)',
    draggable: 'dround()',
    description:
      'Rounds a floating-point value. By default (with a single argument), rounds to the nearest integer. Values ending in .5 are rounded up for positive numbers, down for negative numbers (that is, away from zero). The optional second argument specifies how many digits to leave after the decimal point; values greater than zero produce a floating-point return value rounded to the requested number of digits to the right of the decimal point.'
  },
  dsqrt: {
    name: 'dsqrt',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'dsqrt(DOUBLE a)',
    draggable: 'dsqrt()',
    description: 'Returns the square root of the argument.'
  },
  dtrunc: {
    name: 'dtrunc',
    returnTypes: ['T'],
    arguments: [[{ type: 'DOUBLE' }, { type: 'DECIMAL' }], [{ type: 'NUMBER', optional: true }]],
    signature: 'dtrunc(T<DOUBLE|DECIMAL> a, [NUMBER b])',
    draggable: 'dtrunc()',
    description:
      'Removes some or all fractional digits from a numeric value. With no argument, removes all fractional digits, leaving an integer value. The optional argument specifies the number of fractional digits to include in the return value, and only applies with the argument type is DECIMAL. truncate(), trunc() and dtrunc() are aliases for the same function.'
  },
  e: {
    name: 'e',
    returnTypes: ['DOUBLE'],
    arguments: [],
    signature: 'e()',
    draggable: 'e()',
    description: 'Returns the mathematical constant e.'
  },
  exp: {
    name: 'exp',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'exp(DOUBLE a)',
    draggable: 'exp()',
    description: 'Returns the mathematical constant e raised to the power of the argument.'
  },
  factorial: {
    name: 'factorial',
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'T' }]],
    signature: 'factorial(T a)',
    draggable: 'factorial()',
    description:
      'Computes the factorial of an integer value. It works with any integer type. You can use either the factorial() function or the ! operator. The factorial of 0 is 1. Likewise, the factorial() function returns 1 for any negative value. The maximum positive value for the input argument is 20; a value of 21 or greater overflows the range for a BIGINT and causes an error.'
  },
  floor: {
    name: 'floor',
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'DOUBLE' }, { type: 'DECIMAL' }]],
    signature: 'floor(T<DOUBLE|DECIMAL> a)',
    draggable: 'floor()',
    description: 'Returns the largest integer that is less than or equal to the argument.'
  },
  fmod: {
    name: 'fmod',
    returnTypes: ['T'],
    arguments: [
      [{ type: 'DOUBLE' }, { type: 'DOUBLE' }],
      [{ type: 'FLOAT' }, { type: 'FLOAT' }]
    ],
    signature: 'fmod(DOUBLE a, DOUBLE b), fmod(FLOAT a, FLOAT b)',
    draggable: 'fmod()',
    description: 'Returns the modulus of a floating-point number'
  },
  fpow: {
    name: 'fpow',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }], [{ type: 'DOUBLE' }]],
    signature: 'fpow(DOUBLE a, DOUBLE p)',
    draggable: 'fpow()',
    description: 'Returns the first argument raised to the power of the second argument.'
  },
  fnv_hash: {
    name: 'fnv_hash',
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'T' }]],
    signature: 'fnv_hash(T a)',
    draggable: 'fnv_hash()',
    description:
      'Returns a consistent 64-bit value derived from the input argument, for convenience of implementing hashing logic in an application.'
  },
  greatest: {
    name: 'greatest',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'greatest(T a1, T a2, ...)',
    draggable: 'greatest()',
    description: 'Returns the largest value from a list of expressions.'
  },
  hex: {
    name: 'hex',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'BIGINT' }, { type: 'STRING' }]],
    signature: 'hex(T<BIGINT|STRING> a)',
    draggable: 'hex()',
    description:
      'Returns the hexadecimal representation of an integer value, or of the characters in a string.'
  },
  is_inf: {
    name: 'is_inf',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'is_inf(DOUBLE a)',
    draggable: 'is_inf()',
    description: 'Tests whether a value is equal to the special value "inf", signifying infinity.'
  },
  is_nan: {
    name: 'is_nan',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'is_nan(DOUBLE A)',
    draggable: 'is_nan()',
    description:
      'Tests whether a value is equal to the special value "NaN", signifying "not a number".'
  },
  least: {
    name: 'least',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'least(T a1, T a2, ...)',
    draggable: 'least()',
    description: 'Returns the smallest value from a list of expressions.'
  },
  ln: {
    name: 'ln',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'ln(DOUBLE a)',
    draggable: 'ln()',
    description: 'Returns the natural logarithm of the argument.'
  },
  log: {
    name: 'log',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }], [{ type: 'DOUBLE' }]],
    signature: 'log(DOUBLE base, DOUBLE a)',
    draggable: 'log()',
    description: 'Returns the logarithm of the second argument to the specified base.'
  },
  log10: {
    name: 'log10',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'log10(DOUBLE a)',
    draggable: 'log10()',
    description: 'Returns the logarithm of the argument to the base 10.'
  },
  log2: {
    name: 'log2',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'log2(DOUBLE a)',
    draggable: 'log2()',
    description: 'Returns the logarithm of the argument to the base 2.'
  },
  max_bigint: {
    name: 'max_bigint',
    returnTypes: ['BIGINT'],
    arguments: [],
    signature: 'max_bigint()',
    draggable: 'max_bigint()',
    description: 'Returns the largest value of the associated integral type.'
  },
  max_int: {
    name: 'max_int',
    returnTypes: ['INT'],
    arguments: [],
    signature: 'max_int()',
    draggable: 'max_int()',
    description: 'Returns the largest value of the associated integral type.'
  },
  max_smallint: {
    name: 'max_smallint',
    returnTypes: ['SMALLINT'],
    arguments: [],
    signature: 'max_smallint()',
    draggable: 'max_smallint()',
    description: 'Returns the largest value of the associated integral type.'
  },
  max_tinyint: {
    name: 'max_tinyint',
    returnTypes: ['TINYINT'],
    arguments: [],
    signature: 'max_tinyint()',
    draggable: 'max_tinyint()',
    description: 'Returns the largest value of the associated integral type.'
  },
  min_bigint: {
    name: 'min_bigint',
    returnTypes: ['BIGINT'],
    arguments: [],
    signature: 'min_bigint()',
    draggable: 'min_bigint()',
    description: 'Returns the smallest value of the associated integral type (a negative number).'
  },
  min_int: {
    name: 'min_int',
    returnTypes: ['INT'],
    arguments: [],
    signature: 'min_int()',
    draggable: 'min_int()',
    description: 'Returns the smallest value of the associated integral type (a negative number).'
  },
  min_smallint: {
    name: 'min_smallint',
    returnTypes: ['SMALLINT'],
    arguments: [],
    signature: 'min_smallint()',
    draggable: 'min_smallint()',
    description: 'Returns the smallest value of the associated integral type (a negative number).'
  },
  min_tinyint: {
    name: 'min_tinyint',
    returnTypes: ['TINYINT'],
    arguments: [],
    signature: 'min_tinyint()',
    draggable: 'min_tinyint()',
    description: 'Returns the smallest value of the associated integral type (a negative number).'
  },
  mod: {
    name: 'mod',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'mod(T a, T b)',
    draggable: 'mod()',
    description:
      'Returns the modulus of a number. Equivalent to the % arithmetic operator. Works with any size integer type, any size floating-point type, and DECIMAL with any precision and scale.'
  },
  murmur_hash: {
    name: 'murmur_hash',
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'T' }]],
    signature: 'murmur_hash(T a)',
    draggable: 'murmur_hash()',
    description:
      'Returns a consistent 64-bit value derived from the input argument, for convenience of implementing MurmurHash2 non-cryptographic hash function.'
  },
  negative: {
    name: 'negative',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'negative(T a)',
    draggable: 'negative()',
    description:
      'Returns the argument with the sign reversed; returns a positive value if the argument was already negative.'
  },
  pi: {
    name: 'pi',
    returnTypes: ['DOUBLE'],
    arguments: [],
    signature: 'pi()',
    draggable: 'pi()',
    description: 'Returns the constant pi.'
  },
  pmod: {
    name: 'pmod',
    returnTypes: ['T'],
    arguments: [[{ type: 'DOUBLE' }, { type: 'INT' }], [{ type: 'T' }]],
    signature: 'pmod(T<DOUBLE|INT> a, T b)',
    draggable: 'pmod()',
    description: 'Returns the positive modulus of a number.'
  },
  positive: {
    name: 'positive',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'positive(T a)',
    draggable: 'positive()',
    description: 'Returns the original argument unchanged (even if the argument is negative).'
  },
  pow: {
    name: 'pow',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }], [{ type: 'DOUBLE' }]],
    signature: 'pow(DOUBLE a, DOUBLE p)',
    draggable: 'pow()',
    description: 'Returns the first argument raised to the power of the second argument.'
  },
  power: {
    name: 'power',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }], [{ type: 'DOUBLE' }]],
    signature: 'power(DOUBLE a, DOUBLE p)',
    draggable: 'power()',
    description: 'Returns the first argument raised to the power of the second argument.'
  },
  precision: {
    name: 'precision',
    returnTypes: ['INT'],
    arguments: [[{ type: 'NUMBER' }]],
    signature: 'precision(numeric_expression)',
    draggable: 'precision()',
    description:
      'Computes the precision (number of decimal digits) needed to represent the type of the argument expression as a DECIMAL value.'
  },
  quotient: {
    name: 'quotient',
    returnTypes: ['INT'],
    arguments: [
      [{ type: 'BIGINT' }, { type: 'DOUBLE' }],
      [{ type: 'BIGINT' }, { type: 'DOUBLE' }]
    ],
    signature:
      'quotient(BIGINT numerator, BIGINT denominator), quotient(DOUBLE numerator, DOUBLE denominator)',
    draggable: 'quotient()',
    description:
      'Returns the first argument divided by the second argument, discarding any fractional part. Avoids promoting arguments to DOUBLE as happens with the / SQL operator.'
  },
  radians: {
    name: 'radians',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'radians(DOUBLE a)',
    draggable: 'radians()',
    description: 'Converts argument value from degrees to radians.'
  },
  rand: {
    name: 'rand',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'INT', optional: true }]],
    signature: 'rand([INT seed])',
    draggable: 'rand()',
    description:
      'Returns a random value between 0 and 1. After rand() is called with a seed argument, it produces a consistent random sequence based on the seed value.'
  },
  random: {
    name: 'random',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'INT', optional: true }]],
    signature: 'random([INT seed])',
    draggable: 'random()',
    description:
      'Returns a random value between 0 and 1. After rand() is called with a seed argument, it produces a consistent random sequence based on the seed value.'
  },
  round: {
    name: 'round',
    returnTypes: ['T'],
    arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }], [{ type: 'INT', optional: true }]],
    signature: 'round(DOUBLE a [, INT d]), round(DECIMAL val, INT d)',
    draggable: 'round()',
    description:
      'Rounds a floating-point value. By default (with a single argument), rounds to the nearest integer. Values ending in .5 are rounded up for positive numbers, down for negative numbers (that is, away from zero). The optional second argument specifies how many digits to leave after the decimal point; values greater than zero produce a floating-point return value rounded to the requested number of digits to the right of the decimal point.'
  },
  scale: {
    name: 'scale',
    returnTypes: ['INT'],
    arguments: [[{ type: 'NUMBER' }]],
    signature: 'scale(numeric_expression)',
    draggable: 'scale()',
    description:
      'Computes the scale (number of decimal digits to the right of the decimal point) needed to represent the type of the argument expression as a DECIMAL value.'
  },
  sign: {
    name: 'sign',
    returnTypes: ['INT'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'sign(DOUBLE a)',
    draggable: 'sign()',
    description: 'Returns -1, 0, or 1 to indicate the signedness of the argument value.'
  },
  sin: {
    name: 'sin',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'sin(DOUBLE a)',
    draggable: 'sin()',
    description: 'Returns the sine of the argument.'
  },
  sinh: {
    name: 'sinh',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'sinh(DOUBLE a)',
    draggable: 'sinh()',
    description: 'Returns the hyperbolic sine of the argument.'
  },
  sqrt: {
    name: 'sqrt',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'sqrt(DOUBLE a)',
    draggable: 'sqrt()',
    description: 'Returns the square root of the argument.'
  },
  tan: {
    name: 'tan',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'tan(DOUBLE a)',
    draggable: 'tan()',
    description: 'Returns the tangent of the argument.'
  },
  tanh: {
    name: 'tanh',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'tanh(DOUBLE a)',
    draggable: 'tanh()',
    description: 'Returns the tangent of the argument.'
  },
  trunc: {
    name: 'trunc',
    returnTypes: ['T'],
    arguments: [[{ type: 'DOUBLE' }, { type: 'DECIMAL' }], [{ type: 'NUMBER', optional: true }]],
    signature: 'trunc(T<DOUBLE|DECIMAL> a, [NUMBER b])',
    draggable: 'trunc()',
    description:
      'Removes some or all fractional digits from a numeric value. With no argument, removes all fractional digits, leaving an integer value. The optional argument specifies the number of fractional digits to include in the return value, and only applies with the argument type is DECIMAL. truncate(), trunc() and dtrunc() are aliases for the same function.'
  },
  truncate: {
    name: 'truncate',
    returnTypes: ['T'],
    arguments: [[{ type: 'DOUBLE' }, { type: 'DECIMAL' }], [{ type: 'NUMBER', optional: true }]],
    signature: 'truncate(T<DOUBLE|DECIMAL> a, [NUMBER b])',
    draggable: 'truncate()',
    description:
      'Removes some or all fractional digits from a numeric value. With no argument, removes all fractional digits, leaving an integer value. The optional argument specifies the number of fractional digits to include in the return value, and only applies with the argument type is DECIMAL. truncate(), trunc() and dtrunc() are aliases for the same function.'
  },
  unhex: {
    name: 'unhex',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'unhex(STRING a)',
    draggable: 'unhex()',
    description:
      'Returns a string of characters with ASCII values corresponding to pairs of hexadecimal digits in the argument.'
  },
  width_bucket: {
    name: 'width_bucket',
    returnTypes: ['T'],
    arguments: [
      [{ type: 'DOUBLE' }, { type: 'DECIMAL' }],
      [{ type: 'DOUBLE' }, { type: 'DECIMAL' }],
      [{ type: 'DOUBLE' }, { type: 'DECIMAL' }],
      [{ type: 'INT' }]
    ],
    signature: 'width_bucket(DECIMAL expr, DECIMAL min_value, DECIMAL max_value, INT num_buckets)',
    draggable: 'width_bucket()',
    description:
      'Returns the bucket number in which the expr value would fall in the histogram where its range between min_value and max_value is divided into num_buckets buckets of identical sizes.'
  }
};

const AGGREGATE_FUNCTIONS: UdfCategoryFunctions = {
  appx_median: {
    name: 'appx_median',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'appx_median([DISTINCT|ALL] T col)',
    draggable: 'appx_median()',
    description:
      'An aggregate function that returns a value that is approximately the median (midpoint) of values in the set of input values.'
  },
  avg: {
    name: 'avg',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'NUMBER' }]],
    signature: 'avg([DISTINCT|ALL] col)',
    draggable: 'avg()',
    description:
      'An aggregate function that returns the average value from a set of numbers. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to AVG are NULL, AVG returns NULL.'
  },
  count: {
    name: 'count',
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'T' }]],
    signature: 'count([DISTINCT|ALL] col)',
    draggable: 'count()',
    description:
      'An aggregate function that returns the number of rows, or the number of non-NULL rows.'
  },
  group_concat: {
    name: 'group_concat',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'T' }], [{ type: 'STRING', optional: true }]],
    signature: 'group_concat([ALL] col [, separator])',
    draggable: 'group_concat()',
    description:
      'An aggregate function that returns a single string representing the argument value concatenated together for each row of the result set. If the optional separator string is specified, the separator is added between each pair of concatenated values. The default separator is a comma followed by a space.'
  },
  max: {
    name: 'max',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'max([DISTINCT | ALL] T col)',
    draggable: 'max()',
    description:
      'An aggregate function that returns the maximum value from a set of numbers. Opposite of the MIN function. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to MAX are NULL, MAX returns NULL.'
  },
  min: {
    name: 'min',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'min([DISTINCT | ALL] T col)',
    draggable: 'min()',
    description:
      'An aggregate function that returns the minimum value from a set of numbers. Opposite of the MAX function. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to MIN are NULL, MIN returns NULL.'
  },
  ndv: {
    name: 'ndv',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'ndv([DISTINCT | ALL] col)',
    draggable: 'ndv()',
    description:
      'An aggregate function that returns an approximate value similar to the result of COUNT(DISTINCT col), the "number of distinct values". It is much faster than the combination of COUNT and DISTINCT, and uses a constant amount of memory and thus is less memory-intensive for columns with high cardinality.'
  },
  stddev: {
    name: 'stddev',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'stddev([DISTINCT | ALL] col)',
    draggable: 'stddev()',
    description: 'Returns the standard deviation of a numeric column in the group.'
  },
  stddev_pop: {
    name: 'stddev_pop',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'stddev_pop([DISTINCT | ALL] col)',
    draggable: 'stddev_pop()',
    description: 'Returns the population standard deviation of a numeric column in the group.'
  },
  stddev_samp: {
    name: 'stddev_samp',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'stddev_samp([DISTINCT | ALL] col)',
    draggable: 'stddev_samp()',
    description: 'Returns the unbiased sample standard deviation of a numeric column in the group.'
  },
  sum: {
    name: 'sum',
    returnTypes: ['BIGINT', 'DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'sum([DISTINCT | ALL] col)',
    draggable: 'sum()',
    description:
      'An aggregate function that returns the sum of a set of numbers. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to MIN are NULL, SUM returns NULL.'
  },
  variance: {
    name: 'variance',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'variance([DISTINCT | ALL] col)',
    draggable: 'variance()',
    description:
      'An aggregate function that returns the variance of a set of numbers. This is a mathematical property that signifies how far the values spread apart from the mean. The return value can be zero (if the input is a single value, or a set of identical values), or a positive number otherwise.'
  },
  variance_pop: {
    name: 'variance_pop',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'variance_pop([DISTINCT | ALL] col)',
    draggable: 'variance_pop()',
    description:
      'An aggregate function that returns the population variance of a set of numbers. This is a mathematical property that signifies how far the values spread apart from the mean. The return value can be zero (if the input is a single value, or a set of identical values), or a positive number otherwise.'
  },
  variance_samp: {
    name: 'variance_samp',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'variance_samp([DISTINCT | ALL] col)',
    draggable: 'variance_samp()',
    description:
      'An aggregate function that returns the sample variance of a set of numbers. This is a mathematical property that signifies how far the values spread apart from the mean. The return value can be zero (if the input is a single value, or a set of identical values), or a positive number otherwise.'
  },
  var_pop: {
    name: 'var_pop',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'var_pop(col)',
    draggable: 'var_pop()',
    description: 'Returns the variance of a numeric column in the group.'
  },
  var_samp: {
    name: 'var_samp',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'var_samp(col)',
    draggable: 'var_samp()',
    description: 'Returns the unbiased sample variance of a numeric column in the group.'
  }
};

const TYPE_CONVERSION_FUNCTIONS: UdfCategoryFunctions = {
  cast: {
    name: 'cast',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'cast(a as T)',
    draggable: 'cast()',
    description:
      "Converts the results of the expression expr to type T. For example, cast('1' as BIGINT) will convert the string '1' to its integral representation. A null is returned if the conversion does not succeed. If cast(expr as boolean) Hive returns true for a non-empty string."
  },
  typeof: {
    name: 'typeof',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'T' }]],
    signature: 'typeof(T a)',
    draggable: 'typeof()',
    description:
      'Returns the name of the data type corresponding to an expression. For types with extra attributes, such as length for CHAR and VARCHAR, or precision and scale for DECIMAL, includes the full specification of the type.'
  }
};

const DATE_FUNCTIONS: UdfCategoryFunctions = {
  add_months: {
    name: 'add_months',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'add_months(TIMESTAMP date, BIGINT|INT months)',
    draggable: 'add_months()',
    description: 'Returns the specified date and time plus some number of months.'
  },
  adddate: {
    name: 'adddate',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'adddate(TIMESTAMP startdate, BIGINT|INT days)',
    draggable: 'adddate()',
    description:
      'Adds a specified number of days to a TIMESTAMP value. Similar to date_add(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.'
  },
  current_timestamp: {
    name: 'current_timestamp',
    returnTypes: ['TIMESTAMP'],
    arguments: [],
    signature: 'current_timestamp()',
    draggable: 'current_timestamp()',
    description: 'Alias for the now() function.'
  },
  date_add: {
    name: 'date_add',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'INT' }]],
    signature:
      'date_add(TIMESTAMP startdate, INT days), date_add(TIMESTAMP startdate, interval_expression)',
    draggable: 'date_add()',
    description:
      'Adds a specified number of days to a TIMESTAMP value. The first argument can be a string, which is automatically cast to TIMESTAMP if it uses the recognized format. With an INTERVAL expression as the second argument, you can calculate a delta value using other units such as weeks, years, hours, seconds, and so on.'
  },
  date_part: {
    name: 'date_part',
    returnTypes: ['TIMESTAMP'],
    arguments: [
      [
        {
          type: 'STRING',
          keywords: [
            "'epoch'",
            "'year'",
            "'quarter'",
            "'month'",
            "'day'",
            "'hour'",
            "'minute'",
            "'second'",
            "'millisecond'"
          ]
        }
      ],
      [{ type: 'TIMESTAMP' }]
    ],
    signature: 'date_part(STRING unit, TIMESTAMP timestamp)',
    draggable: 'date_part()',
    description:
      'Similar to EXTRACT(), with the argument order reversed. Supports the same date and time units as EXTRACT(). For compatibility with SQL code containing vendor extensions.'
  },
  date_sub: {
    name: 'date_sub',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'INT' }]],
    signature:
      'date_sub(TIMESTAMP startdate, INT days), date_sub(TIMESTAMP startdate, interval_expression)',
    draggable: 'date_sub()',
    description:
      'Subtracts a specified number of days from a TIMESTAMP value. The first argument can be a string, which is automatically cast to TIMESTAMP if it uses the recognized format. With an INTERVAL expression as the second argument, you can calculate a delta value using other units such as weeks, years, hours, seconds, and so on.'
  },
  date_trunc: {
    name: 'date_trunc',
    returnTypes: ['TIMESTAMP'],
    arguments: [
      [
        {
          type: 'STRING',
          keywords: [
            "'microseconds'",
            "'milliseconds'",
            "'second'",
            "'minute'",
            "'hour'",
            "'day'",
            "'week'",
            "'month'",
            "'year'",
            "'decade'",
            "'century'",
            "'millennium'"
          ]
        }
      ],
      [{ type: 'TIMESTAMP' }]
    ],
    signature: 'date_trunc(STRING unit, TIMESTAMP timestamp)',
    draggable: 'date_trunc()',
    description:
      "Truncates a TIMESTAMP value to the specified precision. The unit argument value for truncating TIMESTAMP values is not case-sensitive. This argument string can be one of: 'microseconds', 'milliseconds', 'second', 'minute', 'hour', 'day', 'week', 'month', 'year', 'decade', 'century' or 'millennium'."
  },
  datediff: {
    name: 'datediff',
    returnTypes: ['INT'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'TIMESTAMP' }]],
    signature: 'datediff(TIMESTAMP enddate, TIMESTAMP startdate)',
    draggable: 'datediff()',
    description: 'Returns the number of days between two TIMESTAMP values.'
  },
  day: {
    name: 'day',
    returnTypes: ['INT'],
    arguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'day(TIMESTAMP date)',
    draggable: 'day()',
    description:
      'Returns the day field from the date portion of a TIMESTAMP. The value represents the day of the month, therefore is in the range 1-31, or less for months without 31 days.'
  },
  dayname: {
    name: 'dayname',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'dayname(TIMESTAMP date)',
    draggable: 'dayname()',
    description:
      "Returns the day field from a TIMESTAMP value, converted to the string corresponding to that day name. The range of return values is 'Sunday' to 'Saturday'. Used in report-generating queries, as an alternative to calling dayofweek() and turning that numeric return value into a string using a CASE expression."
  },
  dayofmonth: {
    name: 'dayofmonth',
    returnTypes: ['INT'],
    arguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'dayofmonth(TIMESTAMP date)',
    draggable: 'dayofmonth()',
    description:
      'Returns the day field from the date portion of a TIMESTAMP. The value represents the day of the month, therefore is in the range 1-31, or less for months without 31 days.'
  },
  dayofweek: {
    name: 'dayofweek',
    returnTypes: ['INT'],
    arguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'dayofweek(TIMESTAMP date)',
    draggable: 'dayofweek()',
    description:
      'Returns the day field from the date portion of a TIMESTAMP, corresponding to the day of the week. The range of return values is 1 (Sunday) to 7 (Saturday).'
  },
  dayofyear: {
    name: 'dayofyear',
    returnTypes: ['INT'],
    arguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'dayofyear(TIMESTAMP date)',
    draggable: 'dayofyear()',
    description:
      'Returns the day field from a TIMESTAMP value, corresponding to the day of the year. The range of return values is 1 (January 1) to 366 (December 31 of a leap year).'
  },
  days_add: {
    name: 'days_add',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'days_add(TIMESTAMP startdate, BIGINT|INT days)',
    draggable: 'days_add()',
    description:
      'Adds a specified number of days to a TIMESTAMP value. Similar to date_add(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.'
  },
  days_sub: {
    name: 'days_sub',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'days_sub(TIMESTAMP startdate, BIGINT|INT days)',
    draggable: 'days_sub()',
    description:
      'Subtracts a specified number of days from a TIMESTAMP value. Similar to date_sub(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.'
  },
  extract: {
    name: 'extract',
    returnTypes: ['INT'],
    arguments: [
      [{ type: 'TIMESTAMP' }],
      [
        {
          type: 'STRING',
          keywords: [
            "'epoch'",
            "'year'",
            "'quarter'",
            "'month'",
            "'day'",
            "'hour'",
            "'minute'",
            "'second'",
            "'millisecond'"
          ]
        }
      ]
    ],
    signature: 'extract(TIMESTAMP date, STRING unit), extract(STRING unit FROM TIMESTAMP date)',
    draggable: 'extract()',
    description: 'Returns one of the numeric date or time fields from a TIMESTAMP value.'
  },
  from_timestamp: {
    name: 'from_timestamp',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'STRING' }]],
    signature: 'from_timestamp(TIMESTAMP val, STRING format)',
    draggable: 'from_timestamp()',
    description:
      "Converts a specified timestamp to a string with the given format. Example: from_timestamp(cast('1999-01-01 10:10:10' as timestamp), 'yyyy-MM-dd')\" results in \"1999-01-01\""
  },
  from_unixtime: {
    name: 'from_unixtime',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'BIGINT' }], [{ type: 'STRING', optional: true }]],
    signature: 'from_unixtime(BIGINT unixtime [, STRING format])',
    draggable: 'from_unixtime()',
    description:
      'Converts the number of seconds from the Unix epoch to the specified time into a string in the local time zone.'
  },
  from_utc_timestamp: {
    name: 'from_utc_timestamp',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'STRING' }]],
    signature: 'from_utc_timestamp(TIMESTAMP date, STRING timezone)',
    draggable: 'from_utc_timestamp()',
    description:
      'Converts a specified UTC timestamp value into the appropriate value for a specified time zone.'
  },
  hour: {
    name: 'hour',
    returnTypes: ['INT'],
    arguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'hour(TIMESTAMP date)',
    draggable: 'hour()',
    description: 'Returns the hour field from a TIMESTAMP field.'
  },
  hours_add: {
    name: 'hours_add',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'hours_add(TIMESTAMP date, BIGINT|INT hours)',
    draggable: 'hours_add()',
    description: 'Returns the specified date and time plus some number of hours.'
  },
  hours_sub: {
    name: 'hours_sub',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'hours_sub(TIMESTAMP date, BIGINT|INT hours)',
    draggable: 'hours_sub()',
    description: 'Returns the specified date and time minus some number of hours.'
  },
  int_months_between: {
    name: 'int_months_between',
    returnTypes: ['INT'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'TIMESTAMP' }]],
    signature: 'int_months_between(TIMESTAMP newer, TIMESTAMP older)',
    draggable: 'int_months_between()',
    description:
      'Returns the number of months between the date portions of two TIMESTAMP values, as an INT representing only the full months that passed.'
  },
  last_day: {
    name: 'last_day',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'last_day(TIMESTAMP t)',
    draggable: 'last_day()',
    description:
      'Returns a TIMESTAMP corresponding to the beginning of the last calendar day in the same month as the TIMESTAMP argument.'
  },
  microseconds_add: {
    name: 'microseconds_add',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'microseconds_add(TIMESTAMP date, BIGINT|INT microseconds)',
    draggable: 'microseconds_add()',
    description: 'Returns the specified date and time plus some number of microseconds.'
  },
  microseconds_sub: {
    name: 'microseconds_sub',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'microseconds_sub(TIMESTAMP date, BIGINT|INT microseconds)',
    draggable: 'microseconds_sub()',
    description: 'Returns the specified date and time minus some number of microseconds.'
  },
  millisecond: {
    name: 'millisecond',
    returnTypes: ['INT'],
    arguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'millisecond(TIMESTAMP date)',
    draggable: 'millisecond()',
    description: 'Returns the millisecond portion of a TIMESTAMP value.'
  },
  milliseconds_add: {
    name: 'milliseconds_add',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'milliseconds_add(TIMESTAMP date, BIGINT|INT milliseconds)',
    draggable: 'milliseconds_add()',
    description: 'Returns the specified date and time plus some number of milliseconds.'
  },
  milliseconds_sub: {
    name: 'milliseconds_sub',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'milliseconds_sub(TIMESTAMP date, BIGINT|INT milliseconds)',
    draggable: 'milliseconds_sub()',
    description: 'Returns the specified date and time minus some number of milliseconds.'
  },
  minute: {
    name: 'minute',
    returnTypes: ['INT'],
    arguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'minute(TIMESTAMP date)',
    draggable: 'minute()',
    description: 'Returns the minute field from a TIMESTAMP value.'
  },
  minutes_add: {
    name: 'minutes_add',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'minutes_add(TIMESTAMP date, BIGINT|INT minutes)',
    draggable: 'minutes_add()',
    description: 'Returns the specified date and time plus some number of minutes.'
  },
  minutes_sub: {
    name: 'minutes_sub',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'minutes_sub(TIMESTAMP date, BIGINT|INT minutes)',
    draggable: 'minutes_sub()',
    description: 'Returns the specified date and time minus some number of minutes.'
  },
  month: {
    name: 'month',
    returnTypes: ['INT'],
    arguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'month(TIMESTAMP date)',
    draggable: 'month()',
    description:
      'Returns the month field, represented as an integer, from the date portion of a TIMESTAMP.'
  },
  monthname: {
    name: 'monthname',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'monthname(TIMESTAMP date)',
    draggable: 'monthname()',
    description:
      'Returns the month field from TIMESTAMP value, converted to the string corresponding to that month name.'
  },
  months_add: {
    name: 'months_add',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'months_add(TIMESTAMP date, BIGINT|INT months)',
    draggable: 'months_add()',
    description: 'Returns the specified date and time plus some number of months.'
  },
  months_between: {
    name: 'months_between',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'TIMESTAMP' }]],
    signature: 'months_between(TIMESTAMP newer, TIMESTAMP older)',
    draggable: 'months_between()',
    description:
      'Returns the number of months between the date portions of two TIMESTAMP values. Can include a fractional part representing extra days in addition to the full months between the dates. The fractional component is computed by dividing the difference in days by 31 (regardless of the month).'
  },
  months_sub: {
    name: 'months_sub',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'months_sub(TIMESTAMP date, BIGINT|INT months)',
    draggable: 'months_sub()',
    description: 'Returns the specified date and time minus some number of months.'
  },
  nanoseconds_add: {
    name: 'nanoseconds_add',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'nanoseconds_add(TIMESTAMP date, BIGINT|INT nanoseconds)',
    draggable: 'nanoseconds_add()',
    description: 'Returns the specified date and time plus some number of nanoseconds.'
  },
  nanoseconds_sub: {
    name: 'nanoseconds_sub',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'nanoseconds_sub(TIMESTAMP date, BIGINT|INT nanoseconds)',
    draggable: 'nanoseconds_sub()',
    description: 'Returns the specified date and time minus some number of nanoseconds.'
  },
  next_day: {
    name: 'next_day',
    returnTypes: ['TIMESTAMP'],
    arguments: [
      [{ type: 'TIMESTAMP' }],
      [
        {
          type: 'STRING',
          keywords: [
            "'Sunday'",
            "'Sun'",
            "'Monday'",
            "'Mon'",
            "'Tuesday'",
            "'Tue'",
            "'Wednesday'",
            "'Wed'",
            "'Thursday'",
            "'Thu'",
            "'Friday'",
            "'Fri'",
            "'Saturday'",
            "'Sat'"
          ]
        }
      ]
    ],
    signature: 'next_day(TIMESTAMP date, STRING weekday)',
    draggable: 'next_day()',
    description:
      'Returns the date of the weekday that follows the specified date. The weekday parameter is case-insensitive. The following values are accepted for weekday: "Sunday"/"Sun", "Monday"/"Mon", "Tuesday"/"Tue", "Wednesday"/"Wed", "Thursday"/"Thu", "Friday"/"Fri", "Saturday"/"Sat".'
  },
  now: {
    name: 'now',
    returnTypes: ['TIMESTAMP'],
    arguments: [],
    signature: 'now()',
    draggable: 'now()',
    description: 'Returns the current date and time (in the local time zone) as a timestamp value.'
  },
  quarter: {
    name: 'quarter',
    returnTypes: ['INT'],
    arguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'quarter(TIMESTAMP date)',
    draggable: 'quarter()',
    description:
      'Returns the quarter in the input TIMESTAMP expression as an integer value, 1, 2, 3, or 4, where 1 represents January 1 through March 31.'
  },
  second: {
    name: 'second',
    returnTypes: ['INT'],
    arguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'second(TIMESTAMP date)',
    draggable: 'second()',
    description: 'Returns the second field from a TIMESTAMP value.'
  },
  seconds_add: {
    name: 'seconds_add',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'seconds_add(TIMESTAMP date, BIGINT|INT seconds)',
    draggable: 'seconds_add()',
    description: 'Returns the specified date and time plus some number of seconds.'
  },
  seconds_sub: {
    name: 'seconds_sub',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'seconds_sub(TIMESTAMP date, BIGINT|INT seconds)',
    draggable: 'seconds_sub()',
    description: 'Returns the specified date and time minus some number of seconds.'
  },
  subdate: {
    name: 'subdate',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'subdate(TIMESTAMP startdate, BIGINT|INT days)',
    draggable: 'subdate()',
    description:
      'Subtracts a specified number of days from a TIMESTAMP value. Similar to date_sub(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.'
  },
  timeofday: {
    name: 'timeofday',
    returnTypes: ['STRING'],
    arguments: [],
    signature: 'timeofday()',
    draggable: 'timeofday()',
    description:
      'Returns a string representation of the current date and time, according to the time of the local system, including any time zone designation.'
  },
  timestamp_cmp: {
    name: 'timestamp_cmp',
    returnTypes: ['INT'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'TIMESTAMP' }]],
    signature: 'timestamp_cmp(TIMESTAMP t1, TIMESTAMP t2)',
    draggable: 'timestamp_cmp()',
    description:
      'Tests if one TIMESTAMP value is newer than, older than, or identical to another TIMESTAMP. Returns either -1, 0, 1 or NULL.'
  },
  to_date: {
    name: 'to_date',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'to_date(TIMESTAMP date)',
    draggable: 'to_date()',
    description: 'Returns a string representation of the date field from a timestamp value.'
  },
  to_timestamp: {
    name: 'to_timestamp',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    altArguments: [[{ type: 'BIGINT' }]],
    signature: 'to_timestamp([STRING val, STRING format]|[BIGINT val])',
    draggable: 'to_timestamp()',
    description:
      "Converts a bigint (delta from the Unix epoch) or a string with the specified format to a timestamp. Example: to_timestamp('1970-01-01 00:00:00', 'yyyy-MM-dd HH:mm:ss')."
  },
  to_utc_timestamp: {
    name: 'to_utc_timestamp',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'STRING' }]],
    signature: 'to_utc_timestamp(TIMESTAMP date, STRING timezone)',
    draggable: 'to_utc_timestamp()',
    description:
      'Converts a specified timestamp value in a specified time zone into the corresponding value for the UTC time zone.'
  },
  trunc: {
    name: 'trunc',
    returnTypes: ['TIMESTAMP'],
    arguments: [
      [{ type: 'TIMESTAMP' }],
      [
        {
          type: 'STRING',
          keywords: [
            "'SYYYY'",
            "'YYYY'",
            "'YEAR'",
            "'SYEAR'",
            "'YYY'",
            "'YY'",
            "'Y'",
            "'Q'",
            "'MONTH'",
            "'MON'",
            "'MM'",
            "'RM'",
            "'WW'",
            "'W'",
            "'DDD'",
            "'DD'",
            "'J'",
            "'DAY'",
            "'DY'",
            "'D'",
            "'HH'",
            "'HH12'",
            "'HH24'",
            "'MI'"
          ]
        }
      ]
    ],
    signature: 'trunc(TIMESTAMP date, STRING unit)',
    draggable: 'trunc()',
    description:
      'Strips off fields and optionally rounds a TIMESTAMP value. The unit argument value is case-sensitive. This argument string can be one of: SYYYY, YYYY, YEAR, SYEAR, YYY, YY, Y: Year. Q: Quarter. MONTH, MON, MM, RM: Month. WW, W: Same day of the week as the first day of the month. DDD, DD, J: Day. DAY, DY, D: Starting day of the week. (Not necessarily the current day.) HH, HH12, HH24: Hour. A TIMESTAMP value truncated to the hour is always represented in 24-hour notation, even for the HH12 argument string. MI: Minute.'
  },
  unix_timestamp: {
    name: 'unix_timestamp',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING', optional: true }], [{ type: 'STRING', optional: true }]],
    altArguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'unix_timestamp([STRING datetime [, STRING format]]|[TIMESTAMP datetime])',
    draggable: 'unix_timestamp()',
    description:
      'Returns an integer value representing the current date and time as a delta from the Unix epoch, or converts from a specified date and time value represented as a TIMESTAMP or STRING.'
  },
  utc_timestamp: {
    name: 'utc_timestamp',
    returnTypes: ['TIMESTAMP'],
    arguments: [],
    signature: 'utc_timestamp()',
    draggable: 'utc_timestamp()',
    description:
      'Returns a TIMESTAMP corresponding to the current date and time in the UTC time zone.'
  },
  weekofyear: {
    name: 'weekofyear',
    returnTypes: ['INT'],
    arguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'weekofyear(TIMESTAMP date)',
    draggable: 'weekofyear()',
    description: 'Returns the corresponding week (1-53) from the date portion of a TIMESTAMP.'
  },
  weeks_add: {
    name: 'weeks_add',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'weeks_add(TIMESTAMP date, BIGINT|INT weeks)',
    draggable: 'weeks_add()',
    description: 'Returns the specified date and time plus some number of weeks.'
  },
  weeks_sub: {
    name: 'weeks_sub',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'weeks_sub(TIMESTAMP date, BIGINT|INT weeks)',
    draggable: 'weeks_sub()',
    description: 'Returns the specified date and time minus some number of weeks.'
  },
  year: {
    name: 'year',
    returnTypes: ['INT'],
    arguments: [[{ type: 'TIMESTAMP' }]],
    signature: 'year(TIMESTAMP date)',
    draggable: 'year()',
    description: 'Returns the year field from the date portion of a TIMESTAMP.'
  },
  years_add: {
    name: 'years_add',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'years_add(TIMESTAMP date, BIGINT|INT years)',
    draggable: 'years_add()',
    description: 'Returns the specified date and time plus some number of years.'
  },
  years_sub: {
    name: 'years_sub',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'TIMESTAMP' }], [{ type: 'BIGINT' }, { type: 'INT' }]],
    signature: 'years_sub(TIMESTAMP date, BIGINT|INT years)',
    draggable: 'years_sub()',
    description: 'Returns the specified date and time minus some number of years.'
  }
};

const CONDITIONAL_FUNCTIONS: UdfCategoryFunctions = {
  coalesce: {
    name: 'coalesce',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'coalesce(T v1, T v2, ...)',
    draggable: 'coalesce()',
    description:
      'Returns the first specified argument that is not NULL, or NULL if all arguments are NULL.'
  },
  decode: {
    name: 'decode',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', multiple: true }]],
    signature:
      'decode(T expression, T search1, T result1 [, T search2, T result2 ...] [, T default] )',
    draggable: 'decode()',
    description:
      'Compares an expression to one or more possible values, and returns a corresponding result when a match is found.'
  },
  if: {
    name: 'if',
    returnTypes: ['T'],
    arguments: [[{ type: 'BOOLEAN' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'if(BOOLEAN condition, T ifTrue, T ifFalseOrNull)',
    draggable: 'if()',
    description:
      'Tests an expression and returns a corresponding result depending on whether the result is true, false, or NULL.'
  },
  ifnull: {
    name: 'ifnull',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'ifnull(T a, T ifNotNull)',
    draggable: 'ifnull()',
    description:
      'Alias for the isnull() function, with the same behavior. To simplify porting SQL with vendor extensions to Impala.'
  },
  isfalse: {
    name: 'isfalse',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'BOOLEAN' }]],
    signature: 'isfalse(BOOLEAN condition)',
    draggable: 'isfalse()',
    description:
      'Tests if a Boolean expression is false or not. Returns true if so. If the argument is NULL, returns false. Identical to isnottrue(), except it returns the opposite value for a NULL argument.'
  },
  isnotfalse: {
    name: 'isnotfalse',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'BOOLEAN' }]],
    signature: 'isnotfalse(BOOLEAN condition)',
    draggable: 'isnotfalse()',
    description:
      'Tests if a Boolean expression is not false (that is, either true or NULL). Returns true if so. If the argument is NULL, returns true. Identical to istrue(), except it returns the opposite value for a NULL argument.'
  },
  isnottrue: {
    name: 'isnottrue',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'BOOLEAN' }]],
    signature: 'isnottrue(BOOLEAN condition)',
    draggable: 'isnottrue()',
    description:
      'Tests if a Boolean expression is not true (that is, either false or NULL). Returns true if so. If the argument is NULL, returns true. Identical to isfalse(), except it returns the opposite value for a NULL argument.'
  },
  isnull: {
    name: 'isnull',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'isnull(T a, T ifNotNull)',
    draggable: 'isnull()',
    description:
      'Tests if an expression is NULL, and returns the expression result value if not. If the first argument is NULL, returns the second argument.'
  },
  istrue: {
    name: 'istrue',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'BOOLEAN' }]],
    signature: 'istrue(BOOLEAN condition)',
    draggable: 'istrue()',
    description:
      'Tests if a Boolean expression is true or not. Returns true if so. If the argument is NULL, returns false. Identical to isnotfalse(), except it returns the opposite value for a NULL argument.'
  },
  nonnullvalue: {
    name: 'nonnullvalue',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'T' }]],
    signature: 'nonnullvalue(T expression)',
    draggable: 'nonnullvalue()',
    description:
      'Tests if an expression (of any type) is NULL or not. Returns false if so. The converse of nullvalue().'
  },
  nullif: {
    name: 'nullif',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'nullif(T expr1, T expr2)',
    draggable: 'nullif()',
    description:
      'Returns NULL if the two specified arguments are equal. If the specified arguments are not equal, returns the value of expr1. The data types of the expressions must be compatible. You cannot use an expression that evaluates to NULL for expr1; that way, you can distinguish a return value of NULL from an argument value of NULL, which would never match expr2.'
  },
  nullifzero: {
    name: 'nullifzero',
    returnTypes: ['T'],
    arguments: [[{ type: 'NUMBER' }]],
    signature: 'nullifzero(T numeric_expr)',
    draggable: 'nullifzero()',
    description:
      'Returns NULL if the numeric expression evaluates to 0, otherwise returns the result of the expression.'
  },
  nullvalue: {
    name: 'nullvalue',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'T' }]],
    signature: 'nullvalue(T expression)',
    draggable: 'nullvalue()',
    description:
      'Tests if an expression (of any type) is NULL or not. Returns true if so. The converse of nonnullvalue().'
  },
  nvl: {
    name: 'nvl',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'nvl(T a, T ifNotNull)',
    draggable: 'nvl()',
    description:
      'Alias for the isnull() function. Tests if an expression is NULL, and returns the expression result value if not. If the first argument is NULL, returns the second argument. Equivalent to the nvl() function from Oracle Database or ifnull() from MySQL.'
  },
  nvl2: {
    name: 'nvl2',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'nvl2(T a, T ifNull, T ifNotNull)',
    draggable: 'nvl2()',
    description:
      'Enhanced variant of the nvl() function. Tests an expression and returns different result values depending on whether it is NULL or not. If the first argument is NULL, returns the second argument. If the first argument is not NULL, returns the third argument. Equivalent to the nvl2() function from Oracle.'
  },
  zeroifnull: {
    name: 'zeroifnull',
    returnTypes: ['T'],
    arguments: [[{ type: 'NUMBER' }]],
    signature: 'zeroifnull(T numeric_expr)',
    draggable: 'zeroifnull()',
    description:
      'Returns 0 if the numeric expression evaluates to NULL, otherwise returns the result of the expression.'
  }
};

const STRING_FUNCTIONS: UdfCategoryFunctions = {
  ascii: {
    name: 'ascii',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'ascii(STRING str)',
    draggable: 'ascii()',
    description: 'Returns the numeric ASCII code of the first character of the argument.'
  },
  base64decode: {
    name: 'base64decode',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'base64decode(STRING str)',
    draggable: 'base64decode()',
    description:
      "Decodes the given string from Base64, an ACSII string format. It's typically used in combination with base64encode(), to store data in an Impala table string that is problematic to store or transmit"
  },
  base64encode: {
    name: 'base64encode',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'base64encode(STRING str)',
    draggable: 'base64encode()',
    description:
      "Encodes the given string to Base64, an ACSII string format. It's typically used in combination with base64decode(), to store data in an Impala table string that is problematic to store or transmit"
  },
  btrim: {
    name: 'btrim',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING', optional: true }]],
    signature: 'btrim(STRING str [, STRING chars_to_trim])',
    draggable: 'btrim()',
    description:
      'Removes all instances of one or more characters from the start and end of a STRING value. By default, removes only spaces. If a non-NULL optional second argument is specified, the function removes all occurrences of characters in that second argument from the beginning and end of the string.'
  },
  bytes: {
    name: 'bytes',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'bytes(STRING byte_expression)',
    draggable: 'bytes()',
    description:
      'Returns the number of bytes contained in the specified byte string. Syntax: BYTES(byte_expression) Where: byte_expression is the byte string for which the number of bytes is to be returned. The BYTES function is  similar to the LENGTH() function except that it always returns the number of bytes regardless of the status of UTF-8 mode whether it is turned ON or OFF.'
  },
  char_length: {
    name: 'char_length',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'char_length(STRING a)',
    draggable: 'char_length()',
    description:
      'Returns the length in characters of the argument string. Aliases for the length() function.'
  },
  character_length: {
    name: 'character_length',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'character_length(STRING a)',
    draggable: 'character_length()',
    description:
      'Returns the length in characters of the argument string. Aliases for the length() function.'
  },
  chr: {
    name: 'chr',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'INT' }]],
    signature: 'chr(INT character_code)',
    draggable: 'chr()',
    description:
      'Returns a character specified by a decimal code point value. The interpretation and display of the resulting character depends on your system locale. Because consistent processing of Impala string values is only guaranteed for values within the ASCII range, only use this function for values corresponding to ASCII characters. In particular, parameter values greater than 255 return an empty string.'
  },
  concat: {
    name: 'concat',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING', multiple: true }]],
    signature: 'concat(STRING a, STRING b...)',
    draggable: 'concat()',
    description: 'Returns a single string representing all the argument values joined together.'
  },
  concat_ws: {
    name: 'concat_ws',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING', multiple: true }]],
    signature: 'concat_ws(STRING sep, STRING a, STRING b...)',
    draggable: 'concat_ws()',
    description:
      'Returns a single string representing the second and following argument values joined together, delimited by a specified separator.'
  },
  find_in_set: {
    name: 'find_in_set',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'find_in_set(STRING str, STRING strList)',
    draggable: 'find_in_set()',
    description:
      'Returns the position (starting from 1) of the first occurrence of a specified string within a comma-separated string. Returns NULL if either argument is NULL, 0 if the search string is not found, or 0 if the search string contains a comma.'
  },
  group_concat: {
    name: 'group_concat',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING', optional: true }]],
    signature: 'group_concat(STRING s [, STRING sep])',
    draggable: 'group_concat()',
    description:
      'Returns a single string representing the argument value concatenated together for each row of the result set. If the optional separator string is specified, the separator is added between each pair of concatenated values.'
  },
  initcap: {
    name: 'initcap',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'initcap(STRING str)',
    draggable: 'initcap()',
    description: 'Returns the input string with the first letter capitalized.'
  },
  instr: {
    name: 'instr',
    returnTypes: ['INT'],
    arguments: [
      [{ type: 'STRING' }],
      [{ type: 'STRING' }],
      [{ type: 'BIGINT', optional: true }],
      [{ type: 'BIGINT', optional: true }]
    ],
    signature: 'instr(STRING str, STRING substr [, BIGINT position [, BIGINT occurrence]])',
    draggable: 'instr()',
    description:
      'Returns the position (starting from 1) of the first occurrence of a substring within a longer string. The optional third and fourth arguments let you find instances of the substring other than the first instance starting from the left.'
  },
  left: {
    name: 'left',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'INT' }]],
    signature: 'left(STRING a, INT num_chars)',
    draggable: 'left()',
    description: 'Returns the leftmost characters of the string. Same as strleft().'
  },
  length: {
    name: 'length',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'length(STRING a)',
    draggable: 'length()',
    description: 'Returns the length in characters of the argument string.'
  },
  levenshtein: {
    name: 'levenshtein',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'levenshtein(STRING a, STRING b)',
    draggable: 'levenshtein()',
    description:
      "Returns the Levenshtein distance between two strings. For example, levenshtein('kitten', 'sitting') results in 3."
  },
  locate: {
    name: 'locate',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'INT', optional: true }]],
    signature: 'locate(STRING substr, STRING str[, INT pos])',
    draggable: 'locate()',
    description:
      'Returns the position (starting from 1) of the first occurrence of a substring within a longer string, optionally after a particular position.'
  },
  lower: {
    name: 'lower',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'lower(STRING a)',
    draggable: 'lower()',
    description: 'Returns the argument string converted to all-lowercase.'
  },
  lcase: {
    name: 'lcase',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'lcase(STRING a)',
    draggable: 'lcase()',
    description: 'Returns the argument string converted to all-lowercase.'
  },
  lpad: {
    name: 'lpad',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'INT' }], [{ type: 'STRING' }]],
    signature: 'lpad(STRING str, INT len, STRING pad)',
    draggable: 'lpad()',
    description:
      'Returns a string of a specified length, based on the first argument string. If the specified string is too short, it is padded on the left with a repeating sequence of the characters from the pad string. If the specified string is too long, it is truncated on the right.'
  },
  ltrim: {
    name: 'ltrim',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING', optional: true }]],
    signature: 'ltrim(STRING a [, STRING charsToTrim])',
    draggable: 'ltrim()',
    description:
      'Returns the argument string with all occurrences of characters specified by the second argument removed from the left side. Removes spaces if the second argument is not specified.'
  },
  parse_url: {
    name: 'parse_url',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING', optional: true }]],
    signature: 'parse_url(STRING urlString, STRING partToExtract [, STRING keyToExtract])',
    draggable: 'parse_url()',
    description:
      "Returns the portion of a URL corresponding to a specified part. The part argument can be 'PROTOCOL', 'HOST', 'PATH', 'REF', 'AUTHORITY', 'FILE', 'USERINFO', or 'QUERY'. Uppercase is required for these literal values. When requesting the QUERY portion of the URL, you can optionally specify a key to retrieve just the associated value from the key-value pairs in the query string."
  },
  regexp_escape: {
    name: 'regexp_escape',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'regexp_escape(STRING source)',
    draggable: 'regexp_escape()',
    description:
      'The regexp_escape function returns a string escaped for the special character in RE2 library so that the special characters are interpreted literally rather than as special characters. The following special characters are escaped by the function: .\\+*?[^]$(){}=!<>|:-'
  },
  regexp_extract: {
    name: 'regexp_extract',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'INT' }]],
    signature: 'regexp_extract(STRING subject, STRING pattern, INT index)',
    draggable: 'regexp_extract()',
    description:
      'Returns the specified () group from a string based on a regular expression pattern. Group 0 refers to the entire extracted string, while group 1, 2, and so on refers to the first, second, and so on (...) portion.'
  },
  regexp_like: {
    name: 'regexp_like',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING', optional: true }]],
    signature: 'regexp_like(STRING source, STRING pattern [, STRING options])',
    draggable: 'regexp_like()',
    description:
      'Returns true or false to indicate whether the source string contains anywhere inside it the regular expression given by the pattern. The optional third argument consists of letter flags that change how the match is performed, such as i for case-insensitive matching.'
  },
  regexp_replace: {
    name: 'regexp_replace',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'regexp_replace(STRING initial, STRING pattern, STRING replacement)',
    draggable: 'regexp_replace()',
    description:
      'Returns the initial argument with the regular expression pattern replaced by the final argument string.'
  },
  repeat: {
    name: 'repeat',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'INT' }]],
    signature: 'repeat(STRING str, INT n)',
    draggable: 'repeat()',
    description: 'Returns the argument string repeated a specified number of times.'
  },
  replace: {
    name: 'replace',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'replace(STRING initial, STRING target, STRING replacement)',
    draggable: 'replace()',
    description:
      'Returns the initial argument with all occurrences of the target string replaced by the replacement string.'
  },
  reverse: {
    name: 'reverse',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'reverse(STRING a)',
    draggable: 'reverse()',
    description: 'Returns the argument string with characters in reversed order.'
  },
  right: {
    name: 'right',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'INT' }]],
    signature: 'right(STRING a, INT num_chars)',
    draggable: 'right()',
    description: 'Returns the rightmost characters of the string. Same as strright().'
  },
  rpad: {
    name: 'rpad',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'INT' }], [{ type: 'STRING' }]],
    signature: 'rpad(STRING str, INT len, STRING pad)',
    draggable: 'rpad()',
    description:
      'Returns a string of a specified length, based on the first argument string. If the specified string is too short, it is padded on the right with a repeating sequence of the characters from the pad string. If the specified string is too long, it is truncated on the right.'
  },
  rtrim: {
    name: 'rtrim',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING', optional: true }]],
    signature: 'rtrim(STRING a [, STRING charsToTrim])',
    draggable: 'rtrim()',
    description:
      'Returns the argument string with all occurrences of characters specified by the second argument removed from the right side. Removes spaces if the second argument is not specified.'
  },
  space: {
    name: 'space',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'INT' }]],
    signature: 'space(INT n)',
    draggable: 'space()',
    description:
      "Returns a concatenated string of the specified number of spaces. Shorthand for repeat(' ', n)."
  },
  split_part: {
    name: 'split_part',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'BIGINT' }]],
    signature: 'split_part(STRING source, STRING delimiter, BIGINT n)',
    draggable: 'split_part()',
    description:
      'Returns the nth field within a delimited string. The fields are numbered starting from 1. The delimiter can consist of multiple characters, not just a single character. All matching of the delimiter is done exactly, not using any regular expression patterns.'
  },
  strleft: {
    name: 'strleft',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'INT' }]],
    signature: 'strleft(STRING a, INT num_chars)',
    draggable: 'strleft()',
    description:
      'Returns the leftmost characters of the string. Shorthand for a call to substr() with 2 arguments.'
  },
  strright: {
    name: 'strright',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'INT' }]],
    signature: 'strright(STRING a, INT num_chars)',
    draggable: 'strright()',
    description:
      'Returns the rightmost characters of the string. Shorthand for a call to substr() with 2 arguments.'
  },
  substr: {
    name: 'substr',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'INT' }], [{ type: 'INT', optional: true }]],
    signature: 'substr(STRING a, INT start [, INT len])',
    draggable: 'substr()',
    description:
      'Returns the portion of the string starting at a specified point, optionally with a specified maximum length. The characters in the string are indexed starting at 1.'
  },
  substring: {
    name: 'substring',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'INT' }], [{ type: 'INT', optional: true }]],
    signature: 'substring(STRING a, INT start [, INT len])',
    draggable: 'substring()',
    description:
      'Returns the portion of the string starting at a specified point, optionally with a specified maximum length. The characters in the string are indexed starting at 1.'
  },
  translate: {
    name: 'translate',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'translate(STRING input, STRING from, STRING to)',
    draggable: 'translate()',
    description:
      'Returns the input string with a set of characters replaced by another set of characters.'
  },
  trim: {
    name: 'trim',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'trim(STRING a)',
    draggable: 'trim()',
    description:
      'Returns the input string with both leading and trailing spaces removed. The same as passing the string through both ltrim() and rtrim().'
  },
  upper: {
    name: 'upper',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'upper(STRING a)',
    draggable: 'upper()',
    description: 'Returns the argument string converted to all-uppercase.'
  },
  ucase: {
    name: 'ucase',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'ucase(STRING a)',
    draggable: 'ucase()',
    description: 'Returns the argument string converted to all-uppercase.'
  }
};

const MISC_FUNCTIONS: UdfCategoryFunctions = {
  coordinator: {
    name: 'coordinator',
    returnTypes: ['STRING'],
    arguments: [],
    signature: 'coordinator()',
    draggable: 'coordinator()',
    description:
      'Returns the name of the host which is running the impalad daemon that is acting as the coordinator for the current query.'
  },
  current_database: {
    name: 'current_database',
    returnTypes: ['STRING'],
    arguments: [],
    signature: 'current_database()',
    draggable: 'current_database()',
    description:
      'Returns the database that the session is currently using, either default if no database has been selected, or whatever database the session switched to through a USE statement or the impalad - d option'
  },
  effective_user: {
    name: 'effective_user',
    returnTypes: ['STRING'],
    arguments: [],
    signature: 'effective_user()',
    draggable: 'effective_user()',
    description:
      'Typically returns the same value as user(), except if delegation is enabled, in which case it returns the ID of the delegated user.'
  },
  logged_in_user: {
    name: 'logged_in_user',
    returnTypes: ['STRING'],
    arguments: [],
    signature: 'logged_in_user()',
    draggable: 'logged_in_user()',
    description:
      'Purpose: Typically returns the same value as USER(). If delegation is enabled, it returns the ID of the delegated user. LOGGED_IN_USER() is an alias of EFFECTIVE_USER().'
  },
  pid: {
    name: 'pid',
    returnTypes: ['INT'],
    arguments: [],
    signature: 'pid()',
    draggable: 'pid()',
    description:
      'Returns the process ID of the impalad daemon that the session is connected to.You can use it during low - level debugging, to issue Linux commands that trace, show the arguments, and so on the impalad process.'
  },
  sleep: {
    name: 'sleep',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'INT' }]],
    signature: 'sleep(INT ms)',
    draggable: 'sleep()',
    description:
      'Pauses the query for a specified number of milliseconds. For slowing down queries with small result sets enough to monitor runtime execution, memory usage, or other factors that otherwise would be difficult to capture during the brief interval of query execution.'
  },
  user: {
    name: 'user',
    returnTypes: ['STRING'],
    arguments: [],
    signature: 'user()',
    draggable: 'user()',
    description:
      'Returns the username of the Linux user who is connected to the impalad daemon.Typically called a single time, in a query without any FROM clause, to understand how authorization settings apply in a security context; once you know the logged - in user name, you can check which groups that user belongs to, and from the list of groups you can check which roles are available to those groups through the authorization policy file.In Impala 2.0 and later, user() returns the the full Kerberos principal string, such as user@example.com, in a Kerberized environment.'
  },
  uuid: {
    name: 'uuid',
    returnTypes: ['STRING'],
    arguments: [],
    signature: 'uuid()',
    draggable: 'uuid()',
    description:
      'Returns a universal unique identifier, a 128-bit value encoded as a string with groups of hexadecimal digits separated by dashes.'
  },
  version: {
    name: 'version',
    returnTypes: ['STRING'],
    arguments: [],
    signature: 'version()',
    draggable: 'version()',
    description:
      'Returns information such as the precise version number and build date for the impalad daemon that you are currently connected to.Typically used to confirm that you are connected to the expected level of Impala to use a particular feature, or to connect to several nodes and confirm they are all running the same level of impalad.'
  }
};

const ANALYTIC_FUNCTIONS: UdfCategoryFunctions = {
  cume_dist: {
    name: 'cume_dist',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'cume_dist(T expr) OVER([partition_by_clause] order_by_clause)',
    draggable: 'cume_dist() OVER()',
    description:
      'Returns the cumulative distribution of a value. The value for each row in the result set is greater than 0 and less than or equal to 1.'
  },
  dense_rank: {
    name: 'dense_rank',
    returnTypes: ['INT'],
    arguments: [],
    signature: 'dense_rank() OVER([partition_by_clause] order_by_clause)',
    draggable: 'dense_rank() OVER()',
    description:
      'Returns an ascending sequence of integers, starting with 1. The output sequence produces duplicate integers for duplicate values of the ORDER BY expressions.'
  },
  first_value: {
    name: 'first_value',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'first_value(expr) OVER([partition_by_clause] order_by_clause [window_clause])',
    draggable: 'first_value() OVER()',
    description:
      'Returns the expression value from the first row in the window. The return value is NULL if the input expression is NULL.'
  },
  lag: {
    name: 'lag',
    returnTypes: ['T'],
    arguments: [
      [{ type: 'T' }],
      [{ type: 'INT', optional: true }],
      [{ type: 'T', optional: true }]
    ],
    signature: 'lag(expr [, offset] [, default]) OVER ([partition_by_clause] order_by_clause)',
    draggable: 'lag() OVER()',
    description:
      'This function returns the value of an expression using column values from a preceding row. You specify an integer offset, which designates a row position some number of rows previous to the current row. Any column references in the expression argument refer to column values from that prior row.'
  },
  last_value: {
    name: 'last_value',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'last_value(expr) OVER([partition_by_clause] order_by_clause [window_clause])',
    draggable: 'last_value() OVER()',
    description:
      'Returns the expression value from the last row in the window. The return value is NULL if the input expression is NULL.'
  },
  lead: {
    name: 'lead',
    returnTypes: ['T'],
    arguments: [
      [{ type: 'T' }],
      [{ type: 'INT', optional: true }],
      [{ type: 'T', optional: true }]
    ],
    signature: 'lead(expr [, offset] [, default]) OVER ([partition_by_clause] order_by_clause)',
    draggable: 'lead() OVER()',
    description:
      'This function returns the value of an expression using column values from a following row. You specify an integer offset, which designates a row position some number of rows after to the current row. Any column references in the expression argument refer to column values from that later row.'
  },
  ntile: {
    name: 'ntile',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', multiple: true, optional: true }]],
    signature: 'ntile(T expr [, T offset ...])',
    draggable: 'ntile()',
    description:
      'Returns the "bucket number" associated with each row, between 1 and the value of an expression. For example, creating 100 buckets puts the lowest 1% of values in the first bucket, while creating 10 buckets puts the lowest 10% of values in the first bucket. Each partition can have a different number of buckets.'
  },
  percent_rank: {
    name: 'percent_rank',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'percent_rank(T expr) OVER ([partition_by_clause] order_by_clause)',
    draggable: 'percent_rank() OVER()',
    description:
      'Calculates the rank, expressed as a percentage, of each row within a group of rows. If rank is the value for that same row from the RANK() function (from 1 to the total number of rows in the partition group), then the PERCENT_RANK() value is calculated as (rank - 1) / (rows_in_group - 1) . If there is only a single item in the partition group, its PERCENT_RANK() value is 0. The ORDER BY clause is required. The PARTITION BY clause is optional. The window clause is not allowed.'
  },
  rank: {
    name: 'rank',
    returnTypes: ['INT'],
    arguments: [],
    signature: 'rank() OVER([partition_by_clause] order_by_clause)',
    draggable: 'rank() OVER()',
    description:
      'Returns an ascending sequence of integers, starting with 1. The output sequence produces duplicate integers for duplicate values of the ORDER BY expressions. After generating duplicate output values for the "tied" input values, the function increments the sequence by the number of tied values.'
  },
  row_number: {
    name: 'row_number',
    returnTypes: ['INT'],
    arguments: [],
    signature: 'row_number() OVER([partition_by_clause] order_by_clause)',
    draggable: 'row_number() OVER()',
    description:
      'Returns an ascending sequence of integers, starting with 1. Starts the sequence over for each group produced by the PARTITIONED BY clause. The output sequence includes different values for duplicate input values. Therefore, the sequence never contains any duplicates or gaps, regardless of duplicate input values.'
  }
};

const BIT_FUNCTIONS: UdfCategoryFunctions = {
  bitand: {
    name: 'bitand',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'bitand(T<integer_type> a, T<integer_type> b)',
    draggable: 'bitand()',
    description:
      'Returns an integer value representing the bits that are set to 1 in both of the arguments. If the arguments are of different sizes, the smaller is promoted to the type of the larger.'
  },
  bitnot: {
    name: 'bitnot',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'bitnot(T<integer_type> a)',
    draggable: 'bitnot()',
    description: 'Inverts all the bits of the input argument.'
  },
  bitor: {
    name: 'bitor',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'bitor(T<integer_type> a, T<integer_type> b)',
    draggable: 'bitor()',
    description:
      'Returns an integer value representing the bits that are set to 1 in either of the arguments. If the arguments are of different sizes, the smaller is promoted to the type of the larger.'
  },
  bitxor: {
    name: 'bitxor',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'bitxor(T<integer_type> a, T<integer_type> b)',
    draggable: 'bitxor()',
    description:
      'Returns an integer value representing the bits that are set to 1 in one but not both of the arguments. If the arguments are of different sizes, the smaller is promoted to the type of the larger.'
  },
  countset: {
    name: 'countset',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'INT', optional: true, keywords: ['0', '1'] }]],
    signature: 'countset(T<integer_type> a [, INT b])',
    draggable: 'countset()',
    description:
      'By default, returns the number of 1 bits in the specified integer value. If the optional second argument is set to zero, it returns the number of 0 bits instead.'
  },
  getbit: {
    name: 'getbit',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
    signature: 'getbit(T<integer_type> a, INT b)',
    draggable: 'getbit()',
    description:
      'Returns a 0 or 1 representing the bit at a specified position. The positions are numbered right to left, starting at zero. The position argument (b) cannot be negative.'
  },
  rotateleft: {
    name: 'rotateleft',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
    signature: 'rotateleft(T<integer_type> a, INT b)',
    draggable: 'rotateleft()',
    description:
      'Rotates an integer value left by a specified number of bits. As the most significant bit is taken out of the original value, if it is a 1 bit, it is "rotated" back to the least significant bit. Therefore, the final value has the same number of 1 bits as the original value, just in different positions. In computer science terms, this operation is a "circular shift".'
  },
  rotateright: {
    name: 'rotateright',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
    signature: 'rotateright(T<integer_type> a, INT b)',
    draggable: 'rotateright()',
    description:
      'Rotates an integer value right by a specified number of bits. As the least significant bit is taken out of the original value, if it is a 1 bit, it is "rotated" back to the most significant bit. Therefore, the final value has the same number of 1 bits as the original value, just in different positions. In computer science terms, this operation is a "circular shift".'
  },
  setbit: {
    name: 'setbit',
    returnTypes: ['T'],
    arguments: [
      [{ type: 'T' }],
      [{ type: 'INT' }],
      [{ type: 'INT', optional: true, keywords: ['0', '1'] }]
    ],
    signature: 'setbit(T<integer_type> a, INT b [, INT c])',
    draggable: 'setbit()',
    description:
      'By default, changes a bit at a specified position (b) to a 1, if it is not already. If the optional third argument is set to zero, the specified bit is set to 0 instead.'
  },
  shiftleft: {
    name: 'shiftleft',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
    signature: 'shiftleft(T<integer_type> a, INT b)',
    draggable: 'shiftleft()',
    description:
      'Shifts an integer value left by a specified number of bits. As the most significant bit is taken out of the original value, it is discarded and the least significant bit becomes 0. In computer science terms, this operation is a "logical shift".'
  },
  shiftright: {
    name: 'shiftright',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
    signature: 'shiftright(T<integer_type> a, INT b)',
    draggable: 'shiftright()',
    description:
      'Shifts an integer value right by a specified number of bits. As the least significant bit is taken out of the original value, it is discarded and the most significant bit becomes 0. In computer science terms, this operation is a "logical shift".'
  }
};

export const UDF_CATEGORIES: UdfCategory[] = [
  { name: I18n('Aggregate'), isAggregate: true, functions: AGGREGATE_FUNCTIONS },
  { name: I18n('Analytic'), isAnalytic: true, functions: ANALYTIC_FUNCTIONS },
  { name: I18n('Bit'), functions: BIT_FUNCTIONS },
  { name: I18n('Conditional'), functions: CONDITIONAL_FUNCTIONS },
  { name: I18n('Date'), functions: DATE_FUNCTIONS },
  { name: I18n('Mathematical'), functions: MATHEMATICAL_FUNCTIONS },
  { name: I18n('Misc'), functions: MISC_FUNCTIONS },
  { name: I18n('String'), functions: STRING_FUNCTIONS },
  { name: I18n('Type Conversion'), functions: TYPE_CONVERSION_FUNCTIONS }
];
