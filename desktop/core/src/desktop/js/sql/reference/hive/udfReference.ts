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
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'abs(DOUBLE a)',
    draggable: 'abs()',
    description: 'Returns the absolute value.'
  },
  acos: {
    name: 'acos',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
    signature: 'acos(DECIMAL|DOUBLE a)',
    draggable: 'acos()',
    description: 'Returns the arccosine of a if -1<=a<=1 or NULL otherwise.'
  },
  asin: {
    name: 'asin',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
    signature: 'asin(DECIMAL|DOUBLE a)',
    draggable: 'asin()',
    description: 'Returns the arc sin of a if -1<=a<=1 or NULL otherwise.'
  },
  atan: {
    name: 'atan',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
    signature: 'atan(DECIMAL|DOUBLE a)',
    draggable: 'atan()',
    description: 'Returns the arctangent of a.'
  },
  bin: {
    name: 'bin',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'BIGINT' }]],
    signature: 'bin(BIGINT a)',
    draggable: 'bin()',
    description: 'Returns the number in binary format'
  },
  bround: {
    name: 'bround',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }], [{ type: 'INT', optional: true }]],
    signature: 'bround(DOUBLE a [, INT decimals])',
    draggable: 'bround()',
    description:
      'Returns the rounded BIGINT value of a using HALF_EVEN rounding mode with optional decimal places d.'
  },
  cbrt: {
    name: 'cbrt',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'cbft(DOUBLE a)',
    draggable: 'cbft()',
    description: 'Returns the cube root of a double value.'
  },
  ceil: {
    name: 'ceil',
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'ceil(DOUBLE a)',
    draggable: 'ceil()',
    description: 'Returns the minimum BIGINT value that is equal to or greater than a.'
  },
  ceiling: {
    name: 'ceiling',
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'ceiling(DOUBLE a)',
    draggable: 'ceiling()',
    description: 'Returns the minimum BIGINT value that is equal to or greater than a.'
  },
  conv: {
    name: 'conv',
    returnTypes: ['T'],
    arguments: [[{ type: 'BIGINT' }, { type: 'STRING' }], [{ type: 'INT' }], [{ type: 'INT' }]],
    signature: 'conv(BIGINT|STRING a, INT from_base, INT to_base)',
    draggable: 'conv()',
    description: 'Converts a number from a given base to another'
  },
  cos: {
    name: 'cos',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
    signature: 'cos(DECIMAL|DOUBLE a)',
    draggable: 'cos()',
    description: 'Returns the cosine of a (a is in radians).'
  },
  degrees: {
    name: 'degrees',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
    signature: 'degrees(DECIMAL|DOUBLE a)',
    draggable: 'degrees()',
    description: 'Converts value of a from radians to degrees.'
  },
  e: {
    name: 'e',
    returnTypes: ['DOUBLE'],
    arguments: [[]],
    signature: 'e()',
    draggable: 'e()',
    description: 'Returns the value of e.'
  },
  exp: {
    name: 'exp',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
    signature: 'exp(DECIMAL|DOUBLE a)',
    draggable: 'exp()',
    description: 'Returns e^a where e is the base of the natural logarithm.'
  },
  factorial: {
    name: 'factorial',
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'INT' }]],
    signature: 'factorial(INT a)',
    draggable: 'factorial()',
    description: 'Returns the factorial of a. Valid a is [0..20].'
  },
  floor: {
    name: 'floor',
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'DOUBLE' }]],
    signature: 'floor(DOUBLE a)',
    draggable: 'floor()',
    description: 'Returns the maximum BIGINT value that is equal to or less than a.'
  },
  greatest: {
    name: 'greatest',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'greatest(T a1, T a2, ...)',
    draggable: 'greatest()',
    description:
      'Returns the greatest value of the list of values. Fixed to return NULL when one or more arguments are NULL, and strict type restriction relaxed, consistent with ">" operator.'
  },
  hex: {
    name: 'hex',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'BIGINT' }, { type: 'BINARY' }, { type: 'STRING' }]],
    signature: 'hex(BIGINT|BINARY|STRING a)',
    draggable: 'hex()',
    description:
      'If the argument is an INT or binary, hex returns the number as a STRING in hexadecimal format. Otherwise if the number is a STRING, it converts each character into its hexadecimal representation and returns the resulting STRING.'
  },
  least: {
    name: 'least',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'least(T a1, T a2, ...)',
    draggable: 'least()',
    description:
      'Returns the least value of the list of values. Fixed to return NULL when one or more arguments are NULL, and strict type restriction relaxed, consistent with "<" operator.'
  },
  ln: {
    name: 'ln',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
    signature: 'ln(DECIMAL|DOUBLE a)',
    draggable: 'ln()',
    description: 'Returns the natural logarithm of the argument a'
  },
  log: {
    name: 'log',
    returnTypes: ['DOUBLE'],
    arguments: [
      [{ type: 'DECIMAL' }, { type: 'DOUBLE' }],
      [{ type: 'DECIMAL' }, { type: 'DOUBLE' }]
    ],
    signature: 'log(DECIMAL|DOUBLE base, DECIMAL|DOUBLE a)',
    draggable: 'log()',
    description: 'Returns the base-base logarithm of the argument a.'
  },
  log10: {
    name: 'log10',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
    signature: 'log10(DECIMAL|DOUBLE a)',
    draggable: 'log10()',
    description: 'Returns the base-10 logarithm of the argument a.'
  },
  log2: {
    name: 'log2',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
    signature: 'log2(DECIMAL|DOUBLE a)',
    draggable: 'log2()',
    description: 'Returns the base-2 logarithm of the argument a.'
  },
  negative: {
    name: 'negative',
    returnTypes: ['T'],
    arguments: [[{ type: 'DOUBLE' }, { type: 'INT' }]],
    signature: 'negative(T<DOUBLE|INT> a)',
    draggable: 'negative()',
    description: 'Returns -a.'
  },
  pi: {
    name: 'pi',
    returnTypes: ['DOUBLE'],
    arguments: [],
    signature: 'pi()',
    draggable: 'pi()',
    description: 'Returns the value of pi.'
  },
  pmod: {
    name: 'pmod',
    returnTypes: ['T'],
    arguments: [[{ type: 'DOUBLE' }, { type: 'INT' }], [{ type: 'T' }]],
    signature: 'pmod(T<DOUBLE|INT> a, T b)',
    draggable: 'pmod()',
    description: 'Returns the positive value of a mod b'
  },
  positive: {
    name: 'positive',
    returnTypes: ['T'],
    arguments: [[{ type: 'DOUBLE' }, { type: 'INT' }]],
    signature: 'positive(T<DOUBLE|INT> a)',
    draggable: 'positive()',
    description: 'Returns a.'
  },
  pow: {
    name: 'pow',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }], [{ type: 'DOUBLE' }]],
    signature: 'pow(DOUBLE a, DOUBLE p)',
    draggable: 'pow()',
    description: 'Returns a^p'
  },
  power: {
    name: 'power',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }], [{ type: 'DOUBLE' }]],
    signature: 'power(DOUBLE a, DOUBLE p)',
    draggable: 'power()',
    description: 'Returns a^p'
  },
  radians: {
    name: 'radians',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
    signature: 'radians(DECIMAL|DOUBLE a)',
    draggable: 'radians()',
    description: 'Converts value of a from degrees to radians.'
  },
  rand: {
    name: 'rand',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'INT', optional: true }]],
    signature: 'rand([INT seed])',
    draggable: 'rand()',
    description:
      'Returns a random number (that changes from row to row) that is distributed uniformly from 0 to 1. Specifying the seed will make sure the generated random number sequence is deterministic.'
  },
  round: {
    name: 'round',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DOUBLE' }], [{ type: 'INT', optional: true }]],
    signature: 'round(DOUBLE a [, INT d])',
    draggable: 'round()',
    description: 'Returns the rounded BIGINT value of a or a rounded to d decimal places.'
  },
  shiftleft: {
    name: 'shiftleft',
    returnTypes: ['T'],
    arguments: [
      [{ type: 'BIGINT' }, { type: 'INT' }, { type: 'SMALLINT' }, { type: 'TINYINT' }],
      [{ type: 'INT' }]
    ],
    signature: 'shiftleft(T<BIGINT|INT|SMALLINT|TINYINT> a, INT b)',
    draggable: 'shiftleft()',
    description:
      'Bitwise left shift. Shifts a b positions to the left. Returns int for tinyint, smallint and int a. Returns bigint for bigint a.'
  },
  shiftright: {
    name: 'shiftright',
    returnTypes: ['T'],
    arguments: [
      [{ type: 'BIGINT' }, { type: 'INT' }, { type: 'SMALLINT' }, { type: 'TINYINT' }],
      [{ type: 'INT' }]
    ],
    signature: 'shiftright(T<BIGINT|INT|SMALLINT|TINYINT> a, INT b)',
    draggable: 'shiftright()',
    description:
      'Bitwise right shift. Shifts a b positions to the right. Returns int for tinyint, smallint and int a. Returns bigint for bigint a.'
  },
  shiftrightunsigned: {
    name: 'shiftrightunsigned',
    returnTypes: ['T'],
    arguments: [
      [{ type: 'BIGINT' }, { type: 'INT' }, { type: 'SMALLINT' }, { type: 'TINYINT' }],
      [{ type: 'INT' }]
    ],
    signature: 'shiftrightunsigned(T<BIGINT|INT|SMALLINT|TINYINT> a, INT b)',
    draggable: 'shiftrightunsigned()',
    description:
      'Bitwise unsigned right shift. Shifts a b positions to the right. Returns int for tinyint, smallint and int a. Returns bigint for bigint a.'
  },
  sign: {
    name: 'sign',
    returnTypes: ['T'],
    arguments: [[{ type: 'DOUBLE' }, { type: 'INT' }]],
    signature: 'sign(T<DOUBLE|INT> a)',
    draggable: 'sign()',
    description:
      "Returns the sign of a as '1.0' (if a is positive) or '-1.0' (if a is negative), '0.0' otherwise. The decimal version returns INT instead of DOUBLE."
  },
  sin: {
    name: 'sin',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
    signature: 'sin(DECIMAL|DOUBLE a)',
    draggable: 'sin()',
    description: 'Returns the sine of a (a is in radians).'
  },
  sqrt: {
    name: 'sqrt',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
    signature: 'sqrt(DECIMAL|DOUBLE a)',
    draggable: 'sqrt()',
    description: 'Returns the square root of a'
  },
  tan: {
    name: 'tan',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'DECIMAL' }, { type: 'DOUBLE' }]],
    signature: 'tan(DECIMAL|DOUBLE a)',
    draggable: 'tan()',
    description: 'Returns the tangent of a (a is in radians).'
  },
  unhex: {
    name: 'unhex',
    returnTypes: ['BINARY'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'unhex(STRING a)',
    draggable: 'unhex()',
    description:
      'Inverse of hex. Interprets each pair of characters as a hexadecimal number and converts to the byte representation of the number.'
  },
  width_bucket: {
    name: 'width_bucket',
    returnTypes: ['INT'],
    arguments: [[{ type: 'NUMBER' }, { type: 'NUMBER' }, { type: 'NUMBER' }, { type: 'INT' }]],
    signature: 'width_bucket(NUMBER expr, NUMBER min_value, NUMBER max_value, INT num_buckets)',
    draggable: 'width_bucket()',
    description:
      'Returns an integer between 0 and num_buckets+1 by mapping expr into the ith equally sized bucket. Buckets are made by dividing [min_value, max_value] into equally sized regions. If expr < min_value, return 1, if expr > max_value return num_buckets+1. (as of Hive 3.0.0)'
  }
};

const COMPLEX_TYPE_CONSTRUCTS: UdfCategoryFunctions = {
  array: {
    name: 'array',
    returnTypes: ['ARRAY'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'array(val1, val2, ...)',
    draggable: 'array()',
    description: 'Creates an array with the given elements.'
  },
  create_union: {
    name: 'create_union',
    returnTypes: ['UNION'],
    arguments: [[{ type: 'T' }], [{ type: 'T', multiple: true }]],
    signature: 'create_union(tag, val1, val2, ...)',
    draggable: 'create_union()',
    description:
      'Creates a union type with the value that is being pointed to by the tag parameter.'
  },
  map: {
    name: 'map',
    returnTypes: ['MAP'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'map(key1, value1, ...)',
    draggable: 'map()',
    description: 'Creates a map with the given key/value pairs.'
  },
  named_struct: {
    name: 'named_struct',
    returnTypes: ['STRUCT'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'named_struct(name1, val1, ...)',
    draggable: 'named_struct()',
    description: 'Creates a struct with the given field names and values.'
  },
  struct: {
    name: 'struct',
    returnTypes: ['STRUCT'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'struct(val1, val2, ...)',
    draggable: 'struct()',
    description:
      'Creates a struct with the given field values. Struct field names will be col1, col2, ....'
  }
};

const AGGREGATE_FUNCTIONS: UdfCategoryFunctions = {
  avg: {
    name: 'avg',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'avg(col)',
    draggable: 'avg()',
    description:
      'Returns the average of the elements in the group or the average of the distinct values of the column in the group.'
  },
  collect_set: {
    name: 'collect_set',
    returnTypes: ['ARRAY'],
    arguments: [[{ type: 'T' }]],
    signature: 'collect_set(col)',
    draggable: 'collect_set()',
    description: 'Returns a set of objects with duplicate elements eliminated.'
  },
  collect_list: {
    name: 'collect_list',
    returnTypes: ['ARRAY'],
    arguments: [[{ type: 'T' }]],
    signature: 'collect_list(col)',
    draggable: 'collect_list()',
    description: 'Returns a list of objects with duplicates. (As of Hive 0.13.0.)'
  },
  corr: {
    name: 'corr',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'corr(col1, col2)',
    draggable: 'corr()',
    description:
      'Returns the Pearson coefficient of correlation of a pair of a numeric columns in the group.'
  },
  count: {
    name: 'count',
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'T' }]],
    signature: 'count([DISTINCT] col)',
    draggable: 'count()',
    description:
      'count(*) - Returns the total number of retrieved rows, including rows containing NULL values. count(expr) - Returns the number of rows for which the supplied expression is non-NULL. count(DISTINCT expr[, expr]) - Returns the number of rows for which the supplied expression(s) are unique and non-NULL. Execution of this can be optimized with hive.optimize.distinct.rewrite.'
  },
  covar_pop: {
    name: 'covar_pop',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'covar_pop(col1, col2)',
    draggable: 'covar_pop()',
    description: 'Returns the population covariance of a pair of numeric columns in the group.'
  },
  covar_samp: {
    name: 'covar_samp',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'covar_samp(col1, col2)',
    draggable: 'covar_samp()',
    description: 'Returns the sample covariance of a pair of a numeric columns in the group.'
  },
  histogram_numeric: {
    name: 'histogram_numeric',
    returnTypes: ['ARRAY'],
    arguments: [[{ type: 'T' }], [{ type: 'INT' }]],
    signature: 'histogram_numeric(col, b)',
    draggable: 'histogram_numeric()',
    description:
      'Computes a histogram of a numeric column in the group using b non-uniformly spaced bins. The output is an array of size b of double-valued (x,y) coordinates that represent the bin centers and heights.'
  },
  max: {
    name: 'max',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'max(col)',
    draggable: 'max()',
    description: 'Returns the maximum value of the column in the group.'
  },
  min: {
    name: 'min',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'min(col)',
    draggable: 'min()',
    description: 'Returns the minimum of the column in the group.'
  },
  ntile: {
    name: 'ntile',
    returnTypes: ['INT'],
    arguments: [[{ type: 'INT' }]],
    signature: 'ntile(INT x)',
    draggable: 'ntile()',
    description:
      'Divides an ordered partition into x groups called buckets and assigns a bucket number to each row in the partition. This allows easy calculation of tertiles, quartiles, deciles, percentiles and other common summary statistics. (As of Hive 0.11.0.)'
  },
  percentile: {
    name: 'percentile',
    returnTypes: ['DOUBLE', 'ARRAY'],
    arguments: [[{ type: 'BIGINT' }], [{ type: 'ARRAY' }, { type: 'DOUBLE' }]],
    signature:
      'percentile(BIGINT col, p), array<DOUBLE> percentile(BIGINT col, array(p1 [, p2]...))',
    draggable: 'percentile()',
    description:
      'Returns the exact pth percentile (or percentiles p1, p2, ..) of a column in the group (does not work with floating point types). p must be between 0 and 1. NOTE: A true percentile can only be computed for integer values. Use PERCENTILE_APPROX if your input is non-integral.'
  },
  percentile_approx: {
    name: 'percentile_approx',
    returnTypes: ['DOUBLE', 'ARRAY'],
    arguments: [
      [{ type: 'DOUBLE' }],
      [{ type: 'DOUBLE' }, { type: 'ARRAY' }],
      [{ type: 'BIGINT', optional: true }]
    ],
    signature:
      'percentile_approx(DOUBLE col, p, [, B]), array<DOUBLE> percentile_approx(DOUBLE col, array(p1 [, p2]...), [, B])',
    draggable: 'percentile_approx()',
    description:
      'Returns an approximate pth percentile (or percentiles p1, p2, ..) of a numeric column (including floating point types) in the group. The B parameter controls approximation accuracy at the cost of memory. Higher values yield better approximations, and the default is 10,000. When the number of distinct values in col is smaller than B, this gives an exact percentile value.'
  },
  regr_avgx: {
    name: 'regr_avgx',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'regr_avgx(T independent, T dependent)',
    draggable: 'regr_avgx()',
    description: 'Equivalent to avg(dependent). As of Hive 2.2.0.'
  },
  regr_avgy: {
    name: 'regr_avgy',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'regr_avgy(T independent, T dependent)',
    draggable: 'regr_avgy()',
    description: 'Equivalent to avg(dependent). As of Hive 2.2.0.'
  },
  regr_count: {
    name: 'regr_count',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'regr_count(T independent, T dependent)',
    draggable: 'regr_count()',
    description:
      'Returns the number of non-null pairs used to fit the linear regression line. As of Hive 2.2.0.'
  },
  regr_intercept: {
    name: 'regr_intercept',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'regr_intercept(T independent, T dependent)',
    draggable: 'regr_intercept()',
    description:
      'Returns the y-intercept of the linear regression line, i.e. the value of b in the equation dependent = a * independent + b. As of Hive 2.2.0.'
  },
  regr_r2: {
    name: 'regr_r2',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'regr_r2(T independent, T dependent)',
    draggable: 'regr_r2()',
    description: 'Returns the coefficient of determination for the regression. As of Hive 2.2.0.'
  },
  regr_slope: {
    name: 'regr_slope',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'regr_slope(T independent, T dependent)',
    draggable: 'regr_slope()',
    description:
      'Returns the slope of the linear regression line, i.e. the value of a in the equation dependent = a * independent + b. As of Hive 2.2.0.'
  },
  regr_sxx: {
    name: 'regr_sxx',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'regr_sxx(T independent, T dependent)',
    draggable: 'regr_sxx()',
    description:
      'Equivalent to regr_count(independent, dependent) * var_pop(dependent). As of Hive 2.2.0.'
  },
  regr_sxy: {
    name: 'regr_sxy',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'regr_sxy(T independent, T dependent)',
    draggable: 'regr_sxy()',
    description:
      'Equivalent to regr_count(independent, dependent) * covar_pop(independent, dependent). As of Hive 2.2.0.'
  },
  regr_syy: {
    name: 'regr_syy',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'regr_syy(T independent, T dependent)',
    draggable: 'regr_syy()',
    description:
      'Equivalent to regr_count(independent, dependent) * var_pop(independent). As of Hive 2.2.0.'
  },
  stddev_pop: {
    name: 'stddev_pop',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'stddev_pop(col)',
    draggable: 'stddev_pop()',
    description: 'Returns the standard deviation of a numeric column in the group.'
  },
  stddev_samp: {
    name: 'stddev_samp',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'stddev_samp(col)',
    draggable: 'stddev_samp()',
    description: 'Returns the unbiased sample standard deviation of a numeric column in the group.'
  },
  sum: {
    name: 'sum',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'sum(col)',
    draggable: 'sum()',
    description:
      'Returns the sum of the elements in the group or the sum of the distinct values of the column in the group.'
  },
  variance: {
    name: 'variance',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'variance(col)',
    draggable: 'variance()',
    description: 'Returns the variance of a numeric column in the group.'
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

const COLLECTION_FUNCTIONS: UdfCategoryFunctions = {
  array_contains: {
    name: 'array_contains',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'ARRAY' }], [{ type: 'T' }]],
    signature: 'array_contains(Array<T> a, val)',
    draggable: 'array_contains()',
    description: 'Returns TRUE if the array contains value.'
  },
  map_keys: {
    name: 'map_keys',
    returnTypes: ['ARRAY'],
    arguments: [[{ type: 'MAP' }]],
    signature: 'array<K.V> map_keys(Map<K.V> a)',
    draggable: 'array<K.V> map_keys()',
    description: 'Returns an unordered array containing the keys of the input map.'
  },
  map_values: {
    name: 'map_values',
    returnTypes: ['ARRAY'],
    arguments: [[{ type: 'MAP' }]],
    signature: 'array<K.V> map_values(Map<K.V> a)',
    draggable: 'array<K.V> map_values()',
    description: 'Returns an unordered array containing the values of the input map.'
  },
  size: {
    name: 'size',
    returnTypes: ['INT'],
    arguments: [[{ type: 'ARRAY' }, { type: 'MAP' }]],
    signature: 'size(Map<K.V>|Array<T> a)',
    draggable: 'size()',
    description: 'Returns the number of elements in the map or array type.'
  },
  sort_array: {
    name: 'sort_array',
    returnTypes: ['ARRAY'],
    arguments: [[{ type: 'ARRAY' }]],
    signature: 'sort_array(Array<T> a)',
    draggable: 'sort_array()',
    description:
      'Sorts the input array in ascending order according to the natural ordering of the array elements and returns it.'
  }
};

const TYPE_CONVERSION_FUNCTIONS: UdfCategoryFunctions = {
  binary: {
    name: 'binary',
    returnTypes: ['BINARY'],
    arguments: [[{ type: 'BINARY' }, { type: 'STRING' }]],
    signature: 'binary(BINARY|STRING a)',
    draggable: 'binary()',
    description: 'Casts the parameter into a binary.'
  },
  cast: {
    name: 'cast',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'cast(a as T)',
    draggable: 'cast()',
    description:
      "Converts the results of the expression expr to type T. For example, cast('1' as BIGINT) will convert the string '1' to its integral representation. A null is returned if the conversion does not succeed. If cast(expr as boolean) Hive returns true for a non-empty string."
  }
};

const DATE_FUNCTIONS: UdfCategoryFunctions = {
  add_months: {
    name: 'add_months',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'DATE' }, { type: 'STRING' }, { type: 'TIMESTAMP' }], [{ type: 'INT' }]],
    signature: 'add_months(DATE|STRING|TIMESTAMP start_date, INT num_months)',
    draggable: 'add_months()',
    description:
      'Returns the date that is num_months after start_date (as of Hive 1.1.0). start_date is a string, date or timestamp. num_months is an integer. The time part of start_date is ignored. If start_date is the last day of the month or if the resulting month has fewer days than the day component of start_date, then the result is the last day of the resulting month. Otherwise, the result has the same day component as start_date.'
  },
  current_date: {
    name: 'current_date',
    returnTypes: ['DATE'],
    arguments: [],
    signature: 'current_date',
    draggable: 'current_date',
    description:
      'Returns the current date at the start of query evaluation (as of Hive 1.2.0). All calls of current_date within the same query return the same value.'
  },
  current_timestamp: {
    name: 'current_timestamp',
    returnTypes: ['TIMESTAMP'],
    arguments: [],
    signature: 'current_timestamp()',
    draggable: 'current_timestamp()',
    description:
      'Returns the current timestamp at the start of query evaluation (as of Hive 1.2.0). All calls of current_timestamp within the same query return the same value.'
  },
  datediff: {
    name: 'datediff',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'datediff(STRING enddate, STRING startdate)',
    draggable: 'datediff()',
    description:
      "Returns the number of days from startdate to enddate: datediff('2009-03-01', '2009-02-27') = 2."
  },
  date_add: {
    name: 'date_add',
    returnTypes: ['T'],
    arguments: [[{ type: 'DATE' }, { type: 'STRING' }], [{ type: 'INT' }]],
    signature: 'date_add(DATE startdate, INT days)',
    draggable: 'date_add()',
    description:
      "Adds a number of days to startdate: date_add('2008-12-31', 1) = '2009-01-01'. T = pre 2.1.0: STRING, 2.1.0 on: DATE"
  },
  date_format: {
    name: 'date_format',
    returnTypes: ['STRING'],
    arguments: [
      [{ type: 'DATE' }, { type: 'STRING' }, { type: 'TIMESTAMP' }],
      [{ type: 'STRING' }]
    ],
    signature: 'date_format(DATE|TIMESTAMP|STRING ts, STRING fmt)',
    draggable: 'date_format()',
    description:
      "Converts a date/timestamp/string to a value of string in the format specified by the date format fmt (as of Hive 1.2.0). Supported formats are Java SimpleDateFormat formats - https://docs.oracle.com/javase/7/docs/api/java/text/SimpleDateFormat.html. The second argument fmt should be constant. Example: date_format('2015-04-08', 'y') = '2015'."
  },
  date_sub: {
    name: 'date_sub',
    returnTypes: ['T'],
    arguments: [[{ type: 'DATE' }, { type: 'STRING' }], [{ type: 'INT' }]],
    signature: 'date_sub(DATE startdate, INT days)',
    draggable: 'date_sub()',
    description:
      "Subtracts a number of days to startdate: date_sub('2008-12-31', 1) = '2008-12-30'. T = pre 2.1.0: STRING, 2.1.0 on: DATE"
  },
  day: {
    name: 'day',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'day(STRING date)',
    draggable: 'day()',
    description:
      "Returns the day part of a date or a timestamp string: day('1970-11-01 00:00:00') = 1, day('1970-11-01') = 1."
  },
  dayofmonth: {
    name: 'dayofmonth',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'dayofmonth(STRING date)',
    draggable: 'dayofmonth()',
    description:
      "Returns the day part of a date or a timestamp string: dayofmonth('1970-11-01 00:00:00') = 1, dayofmonth('1970-11-01') = 1."
  },
  extract: {
    name: 'extract',
    returnTypes: ['INT'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'extract(field FROM source)',
    draggable: 'extract()',
    description:
      'Retrieve fields such as days or hours from source (as of Hive 2.2.0). Source must be a date, timestamp, interval or a string that can be converted into either a date or timestamp. Supported fields include: day, dayofweek, hour, minute, month, quarter, second, week and year.'
  },
  from_unixtime: {
    name: 'from_unixtime',
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'BIGINT' }], [{ type: 'STRING', optional: true }]],
    signature: 'from_unixtime(BIGINT unixtime [, STRING format])',
    draggable: 'from_unixtime()',
    description:
      "Converts the number of seconds from unix epoch (1970-01-01 00:00:00 UTC) to a string representing the timestamp of that moment in the current system time zone in the format of '1970-01-01 00:00:00'"
  },
  from_utc_timestamp: {
    name: 'from_utc_timestamp',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'T' }], [{ type: 'STRING' }]],
    signature: 'from_utc_timestamp(T a, STRING timezone)',
    draggable: 'from_utc_timestamp()',
    description:
      "Assumes given timestamp is UTC and converts to given timezone (as of Hive 0.8.0). For example, from_utc_timestamp('1970-01-01 08:00:00','PST') returns 1970-01-01 00:00:00"
  },
  hour: {
    name: 'hour',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'hour(STRING date)',
    draggable: 'hour()',
    description:
      "Returns the hour of the timestamp: hour('2009-07-30 12:58:59') = 12, hour('12:58:59') = 12."
  },
  last_day: {
    name: 'last_day',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'last_day(STRING date)',
    draggable: 'last_day()',
    description:
      "Returns the last day of the month which the date belongs to (as of Hive 1.1.0). date is a string in the format 'yyyy-MM-dd HH:mm:ss' or 'yyyy-MM-dd'. The time part of date is ignored."
  },
  minute: {
    name: 'minute',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'minute(STRING date)',
    draggable: 'minute()',
    description: 'Returns the minute of the timestamp.'
  },
  month: {
    name: 'month',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'month(STRING date)',
    draggable: 'month()',
    description:
      "Returns the month part of a date or a timestamp string: month('1970-11-01 00:00:00') = 11, month('1970-11-01') = 11."
  },
  months_between: {
    name: 'months_between',
    returnTypes: ['DOUBLE'],
    arguments: [
      [{ type: 'DATE' }, { type: 'STRING' }, { type: 'TIMESTAMP' }],
      [{ type: 'DATE' }, { type: 'STRING' }, { type: 'TIMESTAMP' }]
    ],
    signature: 'months_between(DATE|TIMESTAMP|STRING date1, DATE|TIMESTAMP|STRING date2)',
    draggable: 'months_between()',
    description:
      "Returns number of months between dates date1 and date2 (as of Hive 1.2.0). If date1 is later than date2, then the result is positive. If date1 is earlier than date2, then the result is negative. If date1 and date2 are either the same days of the month or both last days of months, then the result is always an integer. Otherwise the UDF calculates the fractional portion of the result based on a 31-day month and considers the difference in time components date1 and date2. date1 and date2 type can be date, timestamp or string in the format 'yyyy-MM-dd' or 'yyyy-MM-dd HH:mm:ss'. The result is rounded to 8 decimal places. Example: months_between('1997-02-28 10:30:00', '1996-10-30') = 3.94959677"
  },
  next_day: {
    name: 'next_day',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'next_day(STRING start_date, STRING day_of_week)',
    draggable: 'next_day()',
    description:
      "Returns the first date which is later than start_date and named as day_of_week (as of Hive 1.2.0). start_date is a string/date/timestamp. day_of_week is 2 letters, 3 letters or full name of the day of the week (e.g. Mo, tue, FRIDAY). The time part of start_date is ignored. Example: next_day('2015-01-14', 'TU') = 2015-01-20."
  },
  quarter: {
    name: 'quarter',
    returnTypes: ['INT'],
    arguments: [[{ type: 'DATE' }, { type: 'STRING' }, { type: 'TIMESTAMP' }]],
    signature: 'quarter(DATE|TIMESTAMP|STRING a)',
    draggable: 'quarter()',
    description:
      "Returns the quarter of the year for a date, timestamp, or string in the range 1 to 4. Example: quarter('2015-04-08') = 2."
  },
  second: {
    name: 'second',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'second(STRING date)',
    draggable: 'second()',
    description: 'Returns the second of the timestamp.'
  },
  to_date: {
    name: 'to_date',
    returnTypes: ['T'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'to_date(STRING timestamp)',
    draggable: 'to_date()',
    description:
      "Returns the date part of a timestamp string, example to_date('1970-01-01 00:00:00'). T = pre 2.1.0: STRING 2.1.0 on: DATE"
  },
  to_utc_timestamp: {
    name: 'to_utc_timestamp',
    returnTypes: ['TIMESTAMP'],
    arguments: [[{ type: 'T' }], [{ type: 'STRING' }]],
    signature: 'to_utc_timestamp(T a, STRING timezone)',
    draggable: 'to_utc_timestamp()',
    description:
      "Assumes given timestamp is in given timezone and converts to UTC (as of Hive 0.8.0). For example, to_utc_timestamp('1970-01-01 00:00:00','PST') returns 1970-01-01 08:00:00."
  },
  trunc: {
    name: 'trunc',
    returnTypes: ['STRING'],
    arguments: [
      [{ type: 'STRING' }],
      [{ type: 'STRING', keywords: ["'MONTH'", "'MON'", "'MM'", "'YEAR'", "'YYYY'", "'YY'"] }]
    ],
    signature: 'trunc(STRING date, STRING format)',
    draggable: 'trunc()',
    description:
      "Returns date truncated to the unit specified by the format (as of Hive 1.2.0). Supported formats: MONTH/MON/MM, YEAR/YYYY/YY. Example: trunc('2015-03-17', 'MM') = 2015-03-01."
  },
  unix_timestamp: {
    name: 'unix_timestamp',
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'STRING', optional: true }], [{ type: 'STRING', optional: true }]],
    signature: 'unix_timestamp([STRING date [, STRING pattern]])',
    draggable: 'unix_timestamp()',
    description:
      "Convert time string with given pattern to Unix time stamp (in seconds), return 0 if fail: unix_timestamp('2009-03-20', 'yyyy-MM-dd') = 1237532400."
  },
  weekofyear: {
    name: 'weekofyear',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'weekofyear(STRING date)',
    draggable: 'weekofyear()',
    description:
      "Returns the week number of a timestamp string: weekofyear('1970-11-01 00:00:00') = 44, weekofyear('1970-11-01') = 44."
  },
  year: {
    name: 'year',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'year(STRING date)',
    draggable: 'year()',
    description:
      "Returns the year part of a date or a timestamp string: year('1970-01-01 00:00:00') = 1970, year('1970-01-01') = 1970"
  }
};

const CONDITIONAL_FUNCTIONS: UdfCategoryFunctions = {
  assert_true: {
    name: 'assert_true',
    returnTypes: ['T'],
    arguments: [[{ type: 'BOOLEAN' }]],
    signature: 'assert_true(BOOLEAN condition)',
    draggable: 'assert_true()',
    description:
      "Throw an exception if 'condition' is not true, otherwise return null (as of Hive 0.8.0). For example, select assert_true (2<1)."
  },
  coalesce: {
    name: 'coalesce',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'coalesce(T v1, T v2, ...)',
    draggable: 'coalesce()',
    description: "Returns the first v that is not NULL, or NULL if all v's are NULL."
  },
  if: {
    name: 'if',
    returnTypes: ['T'],
    arguments: [[{ type: 'BOOLEAN' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'if(BOOLEAN testCondition, T valueTrue, T valueFalseOrNull)',
    draggable: 'if()',
    description: 'Returns valueTrue when testCondition is true, returns valueFalseOrNull otherwise.'
  },
  isnotnull: {
    name: 'isnotnull',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'T' }]],
    signature: 'isnotnull(a)',
    draggable: 'isnotnull()',
    description: 'Returns true if a is not NULL and false otherwise.'
  },
  isnull: {
    name: 'isnull',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'T' }]],
    signature: 'isnull(a)',
    draggable: 'isnull()',
    description: 'Returns true if a is NULL and false otherwise.'
  },
  nullif: {
    name: 'nullif',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'nullif(a, b)',
    draggable: 'nullif()',
    description: 'Returns NULL if a=b; otherwise returns a (as of Hive 2.2.0).'
  },
  nvl: {
    name: 'nvl',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'nvl(T value, T default_value)',
    draggable: 'nvl()',
    description: 'Returns default value if value is null else returns value (as of Hive 0.11).'
  }
};

const STRING_FUNCTIONS: UdfCategoryFunctions = {
  ascii: {
    name: 'ascii',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'ascii(STRING str)',
    draggable: 'ascii()',
    description: 'Returns the numeric value of the first character of str.'
  },
  base64: {
    name: 'base64',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'BINARY' }]],
    signature: 'base64(BINARY bin)',
    draggable: 'base64()',
    description: 'Converts the argument from binary to a base 64 string (as of Hive 0.12.0).'
  },
  chr: {
    name: 'chr',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'BIGINT' }, { type: 'DOUBLE' }]],
    signature: 'chr(BIGINT|DOUBLE a)',
    draggable: 'chr()',
    description:
      'Returns the ASCII character having the binary equivalent to a (as of Hive 1.3.0 and 2.1.0). If a is larger than 256 the result is equivalent to chr(a % 256). Example: select chr(88); returns "X".'
  },
  char_length: {
    name: 'char_length',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'char_length(STRING a)',
    draggable: 'char_length()',
    description:
      'Returns the number of UTF-8 characters contained in str (as of Hive 2.2.0). This is shorthand for character_length.'
  },
  character_length: {
    name: 'character_length',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'character_length(STRING a)',
    draggable: 'character_length()',
    description:
      'Returns the number of UTF-8 characters contained in str (as of Hive 2.2.0). The function char_length is shorthand for this function.'
  },
  concat: {
    name: 'concat',
    returnTypes: ['STRING'],
    arguments: [
      [
        { type: 'STRING', multiple: true },
        { type: 'BINARY', multiple: true }
      ]
    ],
    signature: 'concat(STRING|BINARY a, STRING|BINARY b...)',
    draggable: 'concat()',
    description:
      "Returns the string or bytes resulting from concatenating the strings or bytes passed in as parameters in order. For example, concat('foo', 'bar') results in 'foobar'. Note that this function can take any number of input strings."
  },
  concat_ws: {
    name: 'concat_ws',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING', multiple: true }]],
    altArguments: [[{ type: 'STRING' }], [{ type: 'ARRAY' }]],
    signature: 'concat_ws(STRING sep, STRING a, STRING b...), concat_ws(STRING sep, Array<STRING>)',
    draggable: 'concat_ws()',
    description: 'Like concat(), but with custom separator SEP.'
  },
  context_ngrams: {
    name: 'context_ngrams',
    returnTypes: ['ARRAY'],
    arguments: [[{ type: 'ARRAY' }], [{ type: 'ARRAY' }], [{ type: 'INT' }], [{ type: 'INT' }]],
    signature:
      'array<struct<STRING,DOUBLE>> context_ngrams(Array<Array<STRING>>, Array<STRING>, INT k, INT pf)',
    draggable: 'array<struct<STRING,DOUBLE>> context_ngrams()',
    description:
      'Returns the top-k contextual N-grams from a set of tokenized sentences, given a string of "context".'
  },
  decode: {
    name: 'decode',
    returnTypes: ['STRING'],
    arguments: [
      [{ type: 'BINARY' }],
      [
        {
          type: 'STRING',
          keywords: [
            "'US-ASCII'",
            "'ISO-8859-1'",
            "'UTF-8'",
            "'UTF-16BE'",
            "'UTF-16LE'",
            "'UTF-16'"
          ]
        }
      ]
    ],
    signature: 'decode(BINARY bin, STRING charset)',
    draggable: 'decode()',
    description:
      "Decodes the first argument into a String using the provided character set (one of 'US-ASCII', 'ISO-8859-1', 'UTF-8', 'UTF-16BE', 'UTF-16LE', 'UTF-16'). If either argument is null, the result will also be null. (As of Hive 0.12.0.)"
  },
  elt: {
    name: 'elt',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'INT' }], [{ type: 'STRING', multiple: true }]],
    signature: 'elt(INT n, STRING str, STRING str1, ...])',
    draggable: 'elt()',
    description:
      "Return string at index number. For example elt(2,'hello','world') returns 'world'. Returns NULL if N is less than 1 or greater than the number of arguments."
  },
  encode: {
    name: 'encode',
    returnTypes: ['BINARY'],
    arguments: [
      [{ type: 'STRING' }],
      [
        {
          type: 'STRING',
          keywords: [
            "'US-ASCII'",
            "'ISO-8859-1'",
            "'UTF-8'",
            "'UTF-16BE'",
            "'UTF-16LE'",
            "'UTF-16'"
          ]
        }
      ]
    ],
    signature: 'encode(STRING src, STRING charset)',
    draggable: 'encode()',
    description:
      "Encodes the first argument into a BINARY using the provided character set (one of 'US-ASCII', 'ISO-8859-1', 'UTF-8', 'UTF-16BE', 'UTF-16LE', 'UTF-16'). If either argument is null, the result will also be null. (As of Hive 0.12.0.)"
  },
  field: {
    name: 'field',
    returnTypes: ['INT'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'field(T val, T val1, ...])',
    draggable: 'field()',
    description:
      "Returns the index of val in the val1,val2,val3,... list or 0 if not found. For example field('world','say','hello','world') returns 3. All primitive types are supported, arguments are compared using str.equals(x). If val is NULL, the return value is 0."
  },
  find_in_set: {
    name: 'find_in_set',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'find_in_set(STRING str, STRING strList)',
    draggable: 'find_in_set()',
    description:
      "Returns the first occurance of str in strList where strList is a comma-delimited string. Returns null if either argument is null. Returns 0 if the first argument contains any commas. For example, find_in_set('ab', 'abc,b,ab,c,def') returns 3."
  },
  format_number: {
    name: 'format_number',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'NUMBER' }], [{ type: 'INT' }]],
    signature: 'format_number(NUMBER x, INT d)',
    draggable: 'format_number()',
    description:
      "Formats the number X to a format like '#,###,###.##', rounded to D decimal places, and returns the result as a string. If D is 0, the result has no decimal point or fractional part. (As of Hive 0.10.0; bug with float types fixed in Hive 0.14.0, decimal type support added in Hive 0.14.0)"
  },
  get_json_object: {
    name: 'get_json_object',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'get_json_object(STRING json_string, STRING path)',
    draggable: 'get_json_object()',
    description:
      'Extracts json object from a json string based on json path specified, and returns json string of the extracted json object. It will return null if the input json string is invalid. NOTE: The json path can only have the characters [0-9a-z_], i.e., no upper-case or special characters. Also, the keys *cannot start with numbers.* This is due to restrictions on Hive column names.'
  },
  initcap: {
    name: 'initcap',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'initcap(STRING a)',
    draggable: 'initcap()',
    description:
      'Returns string, with the first letter of each word in uppercase, all other letters in lowercase. Words are delimited by whitespace. (As of Hive 1.1.0.)'
  },
  instr: {
    name: 'instr',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'instr(STRING str, STRING substr)',
    draggable: 'instr()',
    description:
      'Returns the position of the first occurrence of substr in str. Returns null if either of the arguments are null and returns 0 if substr could not be found in str. Be aware that this is not zero based. The first character in str has index 1.'
  },
  in_file: {
    name: 'in_file',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'in_file(STRING str, STRING filename)',
    draggable: 'in_file()',
    description: 'Returns true if the string str appears as an entire line in filename.'
  },
  length: {
    name: 'length',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'length(STRING a)',
    draggable: 'length()',
    description: 'Returns the length of the string.'
  },
  levenshtein: {
    name: 'levenshtein',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'levenshtein(STRING a, STRING b)',
    draggable: 'levenshtein()',
    description:
      "Returns the Levenshtein distance between two strings (as of Hive 1.2.0). For example, levenshtein('kitten', 'sitting') results in 3."
  },
  lcase: {
    name: 'lcase',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'lcase(STRING a)',
    draggable: 'lcase()',
    description:
      "Returns the string resulting from converting all characters of B to lower case. For example, lcase('fOoBaR') results in 'foobar'."
  },
  locate: {
    name: 'locate',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'INT', optional: true }]],
    signature: 'locate(STRING substr, STRING str [, INT pos])',
    draggable: 'locate()',
    description: 'Returns the position of the first occurrence of substr in str after position pos.'
  },
  lower: {
    name: 'lower',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'lower(STRING a)',
    draggable: 'lower()',
    description:
      "Returns the string resulting from converting all characters of B to lower case. For example, lower('fOoBaR') results in 'foobar'."
  },
  lpad: {
    name: 'lpad',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'INT' }], [{ type: 'STRING' }]],
    signature: 'lpad(STRING str, INT len, STRING pad)',
    draggable: 'lpad()',
    description: 'Returns str, left-padded with pad to a length of len.'
  },
  ltrim: {
    name: 'ltrim',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'ltrim(STRING a)',
    draggable: 'ltrim()',
    description:
      "Returns the string resulting from trimming spaces from the beginning(left hand side) of A. For example, ltrim(' foobar ') results in 'foobar '."
  },
  ngrams: {
    name: 'ngrams',
    returnTypes: ['ARRAY'],
    arguments: [[{ type: 'ARRAY' }], [{ type: 'INT' }], [{ type: 'INT' }], [{ type: 'INT' }]],
    signature: 'array<struct<STRING, DOUBLE>> ngrams(Array<Array<STRING>> a, INT n, INT k, INT pf)',
    draggable: 'array<struct<STRING, DOUBLE>> ngrams()',
    description:
      'Returns the top-k N-grams from a set of tokenized sentences, such as those returned by the sentences() UDAF.'
  },
  octet_length: {
    name: 'octet_length',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'octet_length(STRING a)',
    draggable: 'octet_length()',
    description:
      'Returns the number of octets required to hold the string str in UTF-8 encoding (since Hive 2.2.0). Note that octet_length(str) can be larger than character_length(str).'
  },
  parse_url: {
    name: 'parse_url',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING', optional: true }]],
    signature: 'parse_url(STRING urlString, STRING partToExtract [, STRING keyToExtract])',
    draggable: 'parse_url()',
    description:
      "Returns the specified part from the URL. Valid values for partToExtract include HOST, PATH, QUERY, REF, PROTOCOL, AUTHORITY, FILE, and USERINFO. For example, parse_url('http://facebook.com/path1/p.php?k1=v1&k2=v2#Ref1', 'HOST') returns 'facebook.com'. Also a value of a particular key in QUERY can be extracted by providing the key as the third argument, for example, parse_url('http://facebook.com/path1/p.php?k1=v1&k2=v2#Ref1', 'QUERY', 'k1') returns 'v1'."
  },
  printf: {
    name: 'printf',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'T', multiple: true }]],
    signature: 'printf(STRING format, Obj... args)',
    draggable: 'printf()',
    description:
      'Returns the input formatted according do printf-style format strings (as of Hive 0.9.0).'
  },
  regexp_extract: {
    name: 'regexp_extract',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'INT' }]],
    signature: 'regexp_extract(STRING subject, STRING pattern, INT index)',
    draggable: 'regexp_extract()',
    description:
      "Returns the string extracted using the pattern. For example, regexp_extract('foothebar', 'foo(.*?)(bar)', 2) returns 'bar.' Note that some care is necessary in using predefined character classes: using '\\s' as the second argument will match the letter s; '\\\\s' is necessary to match whitespace, etc. The 'index' parameter is the Java regex Matcher group() method index."
  },
  regexp_replace: {
    name: 'regexp_replace',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'regexp_replace(STRING initial_string, STRING pattern, STRING replacement)',
    draggable: 'regexp_replace()',
    description:
      'Returns the string resulting from replacing all substrings in INITIAL_STRING that match the java regular expression syntax defined in PATTERN with instances of REPLACEMENT. For example, regexp_replace("foobar", "oo|ar", "") returns \'fb.\' Note that some care is necessary in using predefined character classes: using \'\\s\' as the second argument will match the letter s; \'\\\\s\' is necessary to match whitespace, etc.'
  },
  repeat: {
    name: 'repeat',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'INT' }]],
    signature: 'repeat(STRING str, INT n)',
    draggable: 'repeat()',
    description: 'Repeats str n times.'
  },
  replace: {
    name: 'replace',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'replace(STRING a, STRING old, STRING new)',
    draggable: 'replace()',
    description:
      'Returns the string a with all non-overlapping occurrences of old replaced with new (as of Hive 1.3.0 and 2.1.0). Example: select replace("ababab", "abab", "Z"); returns "Zab".'
  },
  reverse: {
    name: 'reverse',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'reverse(STRING a)',
    draggable: 'reverse()',
    description: 'Returns the reversed string.'
  },
  rpad: {
    name: 'rpad',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'INT' }], [{ type: 'STRING' }]],
    signature: 'rpad(STRING str, INT len, STRING pad)',
    draggable: 'rpad()',
    description: 'Returns str, right-padded with pad to a length of len.'
  },
  rtrim: {
    name: 'rtrim',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'rtrim(STRING a)',
    draggable: 'rtrim()',
    description:
      "Returns the string resulting from trimming spaces from the end(right hand side) of A. For example, rtrim(' foobar ') results in ' foobar'."
  },
  sentences: {
    name: 'sentences',
    returnTypes: ['ARRAY'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'array<array<STRING>> sentences(STRING str, STRING lang, STRING locale)',
    draggable: 'array<array<STRING>> sentences()',
    description:
      'Tokenizes a string of natural language text into words and sentences, where each sentence is broken at the appropriate sentence boundary and returned as an array of words. The \'lang\' and \'locale\' are optional arguments. For example, sentences(\'Hello there! How are you?\') returns ( ("Hello", "there"), ("How", "are", "you") ).'
  },
  soundex: {
    name: 'soundex',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'soundex(STRING a)',
    draggable: 'soundex()',
    description:
      "Returns soundex code of the string (as of Hive 1.2.0). For example, soundex('Miller') results in M460."
  },
  space: {
    name: 'space',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'INT' }]],
    signature: 'space(INT n)',
    draggable: 'space()',
    description: 'Returns a string of n spaces.'
  },
  split: {
    name: 'split',
    returnTypes: ['ARRAY'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'array<STRING> split(STRING str, STRING pat)',
    draggable: 'array<STRING> split()',
    description: 'Splits str around pat (pat is a regular expression).'
  },
  str_to_map: {
    name: 'str_to_map',
    returnTypes: ['MAP'],
    arguments: [
      [{ type: 'STRING' }],
      [{ type: 'STRING', optional: true }],
      [{ type: 'STRING', optional: true }]
    ],
    signature: 'map<STRING,STRING> str_to_map(STRING [, STRING delimiter1, STRING delimiter2])',
    draggable: 'map<STRING,STRING> str_to_map()',
    description:
      "Splits text into key-value pairs using two delimiters. Delimiter1 separates text into K-V pairs, and Delimiter2 splits each K-V pair. Default delimiters are ',' for delimiter1 and '=' for delimiter2."
  },
  substr: {
    name: 'substr',
    returnTypes: ['STRING'],
    arguments: [
      [{ type: 'STRING' }, { type: 'BINARY' }],
      [{ type: 'INT' }],
      [{ type: 'INT', optional: true }]
    ],
    signature: 'substr(STRING|BINARY A, INT start [, INT len]) ',
    draggable: 'substr()',
    description:
      "Returns the substring or slice of the byte array of A starting from start position till the end of string A or with optional length len. For example, substr('foobar', 4) results in 'bar'"
  },
  substring: {
    name: 'substring',
    returnTypes: ['STRING'],
    arguments: [
      [{ type: 'STRING' }, { type: 'BINARY' }],
      [{ type: 'INT' }],
      [{ type: 'INT', optional: true }]
    ],
    signature: 'substring(STRING|BINARY a, INT start [, INT len])',
    draggable: 'substring()',
    description:
      "Returns the substring or slice of the byte array of A starting from start position till the end of string A or with optional length len. For example, substr('foobar', 4) results in 'bar'"
  },
  substring_index: {
    name: 'substring_index',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }], [{ type: 'INT' }]],
    signature: 'substring_index(STRING a, STRING delim, INT count)',
    draggable: 'substring_index()',
    description:
      "Returns the substring from string A before count occurrences of the delimiter delim (as of Hive 1.3.0). If count is positive, everything to the left of the final delimiter (counting from the left) is returned. If count is negative, everything to the right of the final delimiter (counting from the right) is returned. Substring_index performs a case-sensitive match when searching for delim. Example: substring_index('www.apache.org', '.', 2) = 'www.apache'."
  },
  translate: {
    name: 'translate',
    returnTypes: ['STRING'],
    arguments: [
      [{ type: 'STRING' }, { type: 'CHAR' }, { type: 'VARCHAR' }],
      [{ type: 'STRING' }, { type: 'CHAR' }, { type: 'VARCHAR' }],
      [{ type: 'STRING' }, { type: 'CHAR' }, { type: 'VARCHAR' }]
    ],
    signature:
      'translate(STRING|CHAR|VARCHAR input, STRING|CHAR|VARCHAR from, STRING|CHAR|VARCHAR to)',
    draggable: 'translate()',
    description:
      'Translates the input string by replacing the characters present in the from string with the corresponding characters in the to string. This is similar to the translate function in PostgreSQL. If any of the parameters to this UDF are NULL, the result is NULL as well. (Available as of Hive 0.10.0, for string types) Char/varchar support added as of Hive 0.14.0.'
  },
  trim: {
    name: 'trim',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'trim(STRING a)',
    draggable: 'trim()',
    description:
      "Returns the string resulting from trimming spaces from both ends of A. For example, trim(' foobar ') results in 'foobar'"
  },
  ucase: {
    name: 'ucase',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'ucase(STRING a)',
    draggable: 'ucase()',
    description:
      "Returns the string resulting from converting all characters of A to upper case. For example, ucase('fOoBaR') results in 'FOOBAR'."
  },
  unbase64: {
    name: 'unbase64',
    returnTypes: ['BINARY'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'unbase64(STRING a)',
    draggable: 'unbase64()',
    description: 'Converts the argument from a base 64 string to BINARY. (As of Hive 0.12.0.)'
  },
  upper: {
    name: 'upper',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }]],
    signature: 'upper(STRING a)',
    draggable: 'upper()',
    description:
      "Returns the string resulting from converting all characters of A to upper case. For example, upper('fOoBaR') results in 'FOOBAR'."
  }
};

const DATA_MASKING_FUNCTIONS: UdfCategoryFunctions = {
  mask: {
    name: 'mask',
    returnTypes: ['STRING'],
    arguments: [
      [{ type: 'STRING' }],
      [{ type: 'STRING', optional: true }],
      [{ type: 'STRING', optional: true }],
      [{ type: 'STRING', optional: true }]
    ],
    signature: 'mask(STRING str [, STRING upper [, STRING lower [, STRING number]]])',
    draggable: 'mask()',
    description:
      'Returns a masked version of str (as of Hive 2.1.0). By default, upper case letters are converted to "X", lower case letters are converted to "x" and numbers are converted to "n". For example mask("abcd-EFGH-8765-4321") results in xxxx-XXXX-nnnn-nnnn. You can override the characters used in the mask by supplying additional arguments: the second argument controls the mask character for upper case letters, the third argument for lower case letters and the fourth argument for numbers. For example, mask("abcd-EFGH-8765-4321", "U", "l", "#") results in llll-UUUU-####-####.'
  },
  mask_first_n: {
    name: 'mask_first_n',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'INT', optional: true }]],
    signature: 'mask_first_n(STRING str [, INT n])',
    draggable: 'mask_first_n()',
    description:
      'Returns a masked version of str with the first n values masked (as of Hive 2.1.0). Upper case letters are converted to "X", lower case letters are converted to "x" and numbers are converted to "n". For example, mask_first_n("1234-5678-8765-4321", 4) results in nnnn-5678-8765-4321.'
  },
  mask_last_n: {
    name: 'mask_last_n',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'INT', optional: true }]],
    signature: 'mask_last_n(STRING str [, INT n])',
    draggable: 'mask_last_n()',
    description:
      'Returns a masked version of str with the last n values masked (as of Hive 2.1.0). Upper case letters are converted to "X", lower case letters are converted to "x" and numbers are converted to "n". For example, mask_last_n("1234-5678-8765-4321", 4) results in 1234-5678-8765-nnnn.'
  },
  mask_show_first_n: {
    name: 'mask_show_first_n',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'INT', optional: true }]],
    signature: 'mask_show_first_n(STRING str [, INT n])',
    draggable: 'mask_show_first_n()',
    description:
      'Returns a masked version of str, showing the first n characters unmasked (as of Hive 2.1.0). Upper case letters are converted to "X", lower case letters are converted to "x" and numbers are converted to "n". For example, mask_show_first_n("1234-5678-8765-4321", 4) results in 1234-nnnn-nnnn-nnnn.'
  },
  mask_show_last_n: {
    name: 'mask_show_last_n',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'INT', optional: true }]],
    signature: 'mask_show_last_n(STRING str [, INT n])',
    draggable: 'mask_show_last_n()',
    description:
      'Returns a masked version of str, showing the last n characters unmasked (as of Hive 2.1.0). Upper case letters are converted to "X", lower case letters are converted to "x" and numbers are converted to "n". For example, mask_show_last_n("1234-5678-8765-4321", 4) results in nnnn-nnnn-nnnn-4321.'
  },
  mask_hash: {
    name: 'mask_hash',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }, { type: 'CHAR' }, { type: 'VARCHAR' }]],
    signature: 'mask_hash(STRING|CHAR|VARCHAR str)',
    draggable: 'mask_hash()',
    description:
      'Returns a hashed value based on str (as of Hive 2.1.0). The hash is consistent and can be used to join masked values together across tables. This function returns null for non-string types.'
  }
};

const TABLE_GENERATING_FUNCTIONS: UdfCategoryFunctions = {
  explode: {
    name: 'explode',
    returnTypes: ['table'],
    arguments: [[{ type: 'ARRAY' }, { type: 'MAP' }]],
    signature: 'explode(Array|Array<T>|Map a)',
    draggable: 'explode()',
    description: ''
  },
  inline: {
    name: 'inline',
    returnTypes: ['table'],
    arguments: [[{ type: 'ARRAY' }]],
    signature: 'inline(Array<Struct [, Struct]> a)',
    draggable: 'inline()',
    description: 'Explodes an array of structs into a table. (As of Hive 0.10.)'
  },
  json_tuple: {
    name: 'json_tuple',
    returnTypes: ['table'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING', multiple: true }]],
    signature: 'json_tuple(STRING jsonStr, STRING k1, STRING k2, ...)',
    draggable: 'json_tuple()',
    description:
      'A new json_tuple() UDTF is introduced in Hive 0.7. It takes a set of names (keys) and a JSON string, and returns a tuple of values using one function. This is much more efficient than calling GET_JSON_OBJECT to retrieve more than one key from a single JSON string.'
  },
  parse_url_tuple: {
    name: 'parse_url_tuple',
    returnTypes: ['table'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING', multiple: true }]],
    signature: 'parse_url_tuple(STRING url, STRING p1, STRING p2, ...)',
    draggable: 'parse_url_tuple()',
    description:
      'The parse_url_tuple() UDTF is similar to parse_url(), but can extract multiple parts of a given URL, returning the data in a tuple. Values for a particular key in QUERY can be extracted by appending a colon and the key to the partToExtract argument.'
  },
  posexplode: {
    name: 'posexplode',
    returnTypes: ['table'],
    arguments: [[{ type: 'ARRAY' }]],
    signature: 'posexplode(ARRAY)',
    draggable: 'posexplode()',
    description:
      'posexplode() is similar to explode but instead of just returning the elements of the array it returns the element as well as its position  in the original array.'
  },
  stack: {
    name: 'stack',
    returnTypes: ['table'],
    arguments: [[{ type: 'INT' }], [{ type: 'T', multiple: true }]],
    signature: 'stack(INT n, v1, v2, ..., vk)',
    draggable: 'stack()',
    description:
      'Breaks up v1, v2, ..., vk into n rows. Each row will have k/n columns. n must be constant.'
  }
};

const MISC_FUNCTIONS: UdfCategoryFunctions = {
  crc32: {
    name: 'crc32',
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'STRING' }, { type: 'BINARY' }]],
    signature: 'crc32(STRING|BINARY a)',
    draggable: 'crc32()',
    description:
      "Computes a cyclic redundancy check value for string or binary argument and returns bigint value (as of Hive 1.3.0). Example: crc32('ABC') = 2743272264."
  },
  current_database: {
    name: 'current_database',
    returnTypes: ['STRING'],
    arguments: [],
    signature: 'current_database()',
    draggable: 'current_database()',
    description: 'Returns current database name (as of Hive 0.13.0).'
  },
  current_user: {
    name: 'current_user',
    returnTypes: ['STRING'],
    arguments: [],
    signature: 'current_user()',
    draggable: 'current_user()',
    description: 'Returns current user name (as of Hive 1.2.0).'
  },
  get_json_object: {
    name: 'get_json_object',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'get_json_object(STRING json, STRING jsonPath)',
    draggable: 'get_json_object()',
    description:
      'A limited version of JSONPath is supported ($ : Root object, . : Child operator, [] : Subscript operator for array, * : Wildcard for []'
  },
  hash: {
    name: 'hash',
    returnTypes: ['INT'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'hash(a1[, a2...])',
    draggable: 'hash()',
    description: 'Returns a hash value of the arguments. (As of Hive 0.4.)'
  },
  java_method: {
    name: 'java_method',
    returnTypes: ['T'],
    arguments: [
      [{ type: 'STRING' }],
      [{ type: 'STRING' }],
      [{ type: 'T', multiple: true, optional: true }]
    ],
    signature: 'java_method(class, method[, arg1[, arg2..]])',
    draggable: 'java_method()',
    description:
      'Calls a Java method by matching the argument signature, using reflection. (As of Hive 0.9.0.)'
  },
  logged_in_user: {
    name: 'logged_in_user',
    returnTypes: ['STRING'],
    arguments: [],
    signature: 'logged_in_user()',
    draggable: 'logged_in_user()',
    description:
      'Returns current user name from the session state (as of Hive 2.2.0). This is the username provided when connecting to Hive.'
  },
  md5: {
    name: 'md5',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }, { type: 'BINARY' }]],
    signature: 'md5(STRING|BINARY a)',
    draggable: 'md5()',
    description:
      "Calculates an MD5 128-bit checksum for the string or binary (as of Hive 1.3.0). The value is returned as a string of 32 hex digits, or NULL if the argument was NULL. Example: md5('ABC') = '902fbdd2b1df0c4f70b4a5d23525e932'."
  },
  reflect: {
    name: 'reflect',
    returnTypes: ['T'],
    arguments: [
      [{ type: 'STRING' }],
      [{ type: 'STRING' }],
      [{ type: 'T', multiple: true, optional: true }]
    ],
    signature: 'reflect(class, method[, arg1[, arg2..]])',
    draggable: 'reflect()',
    description:
      'Calls a Java method by matching the argument signature, using reflection. (As of Hive 0.7.0.)'
  },
  sha: {
    name: 'sha',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }, { type: 'BINARY' }]],
    signature: 'sha(STRING|BINARY a)',
    draggable: 'sha()',
    description:
      "Calculates the SHA-1 digest for string or binary and returns the value as a hex string (as of Hive 1.3.0). Example: sha1('ABC') = '3c01bdbb26f358bab27f267924aa2c9a03fcfdb8'."
  },
  sha1: {
    name: 'sha1',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }, { type: 'BINARY' }]],
    signature: 'sha1(STRING|BINARY a)',
    draggable: 'sha1()',
    description:
      "Calculates the SHA-1 digest for string or binary and returns the value as a hex string (as of Hive 1.3.0). Example: sha1('ABC') = '3c01bdbb26f358bab27f267924aa2c9a03fcfdb8'."
  },
  sha2: {
    name: 'sha2',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }, { type: 'BINARY' }], [{ type: 'INT' }]],
    signature: 'sha2(STRING|BINARY a, INT b)',
    draggable: 'sha2()',
    description:
      "Calculates the SHA-2 family of hash functions (SHA-224, SHA-256, SHA-384, and SHA-512) (as of Hive 1.3.0). The first argument is the string or binary to be hashed. The second argument indicates the desired bit length of the result, which must have a value of 224, 256, 384, 512, or 0 (which is equivalent to 256). SHA-224 is supported starting from Java 8. If either argument is NULL or the hash length is not one of the permitted values, the return value is NULL. Example: sha2('ABC', 256) = 'b5d4045c3f466fa91fe2cc6abe79232a1a57cdf104f7a26e716e0a1e2789df78'."
  },
  version: {
    name: 'version',
    returnTypes: ['STRING'],
    arguments: [],
    signature: 'version()',
    draggable: 'version()',
    description:
      'Returns the Hive version (as of Hive 2.1.0). The string contains 2 fields, the first being a build number and the second being a build hash. Example: "select version();" might return "2.1.0.2.5.0.0-1245 r027527b9c5ce1a3d7d0b6d2e6de2378fb0c39232". Actual results will depend on your build.'
  },
  xpath: {
    name: 'xpath',
    returnTypes: ['ARRAY'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'array<STRING> xpath(STRING xml, STRING xpath)',
    draggable: 'array<STRING> xpath()',
    description:
      'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
  },
  xpath_boolean: {
    name: 'xpath_boolean',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'xpath_boolean(STRING xml, STRING xpath)',
    draggable: 'xpath_boolean()',
    description:
      'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
  },
  xpath_double: {
    name: 'xpath_double',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'xpath_double(STRING xml, STRING xpath)',
    draggable: 'xpath_double()',
    description:
      'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
  },
  xpath_float: {
    name: 'xpath_float',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'xpath_float(STRING xml, STRING xpath)',
    draggable: 'xpath_float()',
    description:
      'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
  },
  xpath_int: {
    name: 'xpath_int',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'xpath_int(STRING xml, STRING xpath)',
    draggable: 'xpath_int()',
    description:
      'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
  },
  xpath_long: {
    name: 'xpath_long',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'xpath_long(STRING xml, STRING xpath)',
    draggable: 'xpath_long()',
    description:
      'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
  },
  xpath_number: {
    name: 'xpath_number',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'xpath_number(STRING xml, STRING xpath)',
    draggable: 'xpath_number()',
    description:
      'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
  },
  xpath_short: {
    name: 'xpath_short',
    returnTypes: ['INT'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'xpath_short(STRING xml, STRING xpath)',
    draggable: 'xpath_short()',
    description:
      'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
  },
  xpath_string: {
    name: 'xpath_string',
    returnTypes: ['STRING'],
    arguments: [[{ type: 'STRING' }], [{ type: 'STRING' }]],
    signature: 'xpath_string(STRING xml, STRING xpath)',
    draggable: 'xpath_string()',
    description:
      'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.'
  }
};

const ANALYTIC_FUNCTIONS: UdfCategoryFunctions = {
  cume_dist: {
    name: 'cume_dist',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true, optional: true }]],
    signature: 'cume_dist()',
    draggable: 'cume_dist()',
    description: ''
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
    signature: 'lead(expr [, offset] [, default]) OVER([partition_by_clause] order_by_clause)',
    draggable: 'lead() OVER()',
    description:
      'This function returns the value of an expression using column values from a following row. You specify an integer offset, which designates a row position some number of rows after to the current row. Any column references in the expression argument refer to column values from that later row.'
  },
  ntile: {
    name: 'ntile',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true, optional: true }]],
    signature: 'ntile()',
    draggable: 'ntile()',
    description: ''
  },
  percent_rank: {
    name: 'percent_rank',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true, optional: true }]],
    signature: 'percent_rank()',
    draggable: 'percent_rank()',
    description: ''
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

export const UDF_CATEGORIES: UdfCategory[] = [
  { name: I18n('Aggregate'), isAggregate: true, functions: AGGREGATE_FUNCTIONS },
  { name: I18n('Analytic'), isAnalytic: true, functions: ANALYTIC_FUNCTIONS },
  { name: I18n('Collection'), functions: COLLECTION_FUNCTIONS },
  { name: I18n('Complex Type'), functions: COMPLEX_TYPE_CONSTRUCTS },
  { name: I18n('Conditional'), functions: CONDITIONAL_FUNCTIONS },
  { name: I18n('Date'), functions: DATE_FUNCTIONS },
  { name: I18n('Mathematical'), functions: MATHEMATICAL_FUNCTIONS },
  { name: I18n('Misc'), functions: MISC_FUNCTIONS },
  { name: I18n('String'), functions: STRING_FUNCTIONS },
  { name: I18n('Data Masking'), functions: DATA_MASKING_FUNCTIONS },
  { name: I18n('Table Generating'), functions: TABLE_GENERATING_FUNCTIONS },
  { name: I18n('Type Conversion'), functions: TYPE_CONVERSION_FUNCTIONS }
];
