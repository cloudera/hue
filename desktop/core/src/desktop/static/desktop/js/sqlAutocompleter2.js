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

(function (root, factory) {
  if(typeof define === "function" && define.amd) {
    define([
      'desktop/js/autocomplete/sql'
    ], factory);
  } else {
    root.SqlAutocompleter2 = factory(sql);
  }
}(this, function (sqlParser) {

  var MATHEMATICAL_FUNCTIONS = {
    hive: [
      { name: 'abs()', returnType: 'DOUBLE', signature: 'abs(DOUBLE a)', description: 'Returns the absolute value.' },
      { name: 'acos()', returnType: 'DOUBLE', signature: 'acos(DECIMAL|DOUBLE a)', description: 'Returns the arccosine of a if -1&lt;=a&lt;=1 or NULL otherwise.' },
      { name: 'asin()', returnType: 'DOUBLE', signature: 'asin(DECIMAL|DOUBLE a)', description: 'Returns the arc sin of a if -1&lt;=a&lt;=1 or NULL otherwise.' },
      { name: 'atan()', returnType: 'DOUBLE', signature: 'atan(DECIMAL|DOUBLE a)', description: 'Returns the arctangent of a.' },
      { name: 'bin()', returnType: 'STRING', signature: 'bin(BIGINT a)', description: 'Returns the number in binary format' },
      { name: 'bround()', returnType: 'DOUBLE', signature: 'bround(DOUBLE a [, INT decimals])', description: 'Returns the rounded BIGINT value of a using HALF_EVEN rounding mode with optional decimal places d.' },
      { name: 'cbrt()', returnType: 'DOUBLE', signature: 'cbft(DOUBLE a)', description: 'Returns the cube root of a double value.' },
      { name: 'ceil()', returnType: 'BIGINT', signature: 'ceil(DOUBLE a)', description: 'Returns the minimum BIGINT value that is equal to or greater than a.' },
      { name: 'ceiling()', returnType: 'BIGINT', signature: 'ceiling(DOUBLE a)', description: 'Returns the minimum BIGINT value that is equal to or greater than a.' },
      { name: 'conv()', returnType: 'T', signature: 'conv(BIGINT|STRING a, INT from_base, INT to_base)', description: 'Converts a number from a given base to another' },
      { name: 'cos()', returnType: 'DOUBLE', signature: 'cos(DECIMAL|DOUBLE a)', description: 'Returns the cosine of a (a is in radians).' },
      { name: 'degrees()', returnType: 'DOUBLE', signature: 'degrees(DECIMAL|DOUBLE a)', description: 'Converts value of a from radians to degrees.' },
      { name: 'e()', returnType: 'DOUBLE', signature: 'e()', description: 'Returns the value of e.' },
      { name: 'exp()', returnType: 'DOUBLE', signature: 'exp(DECIMAL|DOUBLE a)', description: 'Returns e^a where e is the base of the natural logarithm.' },
      { name: 'factorial()', returnType: 'BIGINT', signature: 'factorial(INT a)', description: 'Returns the factorial of a. Valid a is [0..20].' },
      { name: 'floor()', returnType: 'BIGINT', signature: '', description: 'Returns the maximum BIGINT value that is equal to or less than a.' },
      { name: 'greatest()', returnType: 'T', signature: 'greatest(T a1, T a2, ...)', description: 'Returns the greatest value of the list of values. Fixed to return NULL when one or more arguments are NULL, and strict type restriction relaxed, consistent with "&gt;" operator.' },
      { name: 'hex()', returnType: 'STRING', signature: 'hex(BIGINT|BINARY|STRING a)', description: 'If the argument is an INT or binary, hex returns the number as a STRING in hexadecimal format. Otherwise if the number is a STRING, it converts each character into its hexadecimal representation and returns the resulting STRING.' },
      { name: 'least()', returnType: 'T', signature: 'least(T a1, T a2, ...)', description: 'Returns the least value of the list of values. Fixed to return NULL when one or more arguments are NULL, and strict type restriction relaxed, consistent with "&lt;" operator.' },
      { name: 'ln()', returnType: 'DOUBLE', signature: 'ln(DECIMAL|DOUBLE a)', description: 'Returns the natural logarithm of the argument a' },
      { name: 'log()', returnType: 'DOUBLE', signature: 'log(DECIMAL|DOUBLE base, DECIMAL|DOUBLE a)', description: 'Returns the base-base logarithm of the argument a.' },
      { name: 'log10()', returnType: 'DOUBLE', signature: 'log10(DECIMAL|DOUBLE a)', description: 'Returns the base-10 logarithm of the argument a.' },
      { name: 'log2()', returnType: 'DOUBLE', signature: 'log2(DECIMAL|DOUBLE a)', description: 'Returns the base-2 logarithm of the argument a.' },
      { name: 'negative()', returnType: 'T', signature: 'negative(T&lt;DOUBLE|INT&gt; a)', description: 'Returns -a.' },
      { name: 'pi()', returnType: 'DOUBLE', signature: 'pi()', description: 'Returns the value of pi.' },
      { name: 'pmod()', returnType: 'T', signature: 'pmod(T&lt;DOUBLE|INT&gt; a, T b)', description: 'Returns the positive value of a mod b' },
      { name: 'positive()', returnType: 'T', signature: 'positive(T&lt;DOUBLE|INT&gt; a)', description: 'Returns a.' },
      { name: 'pow()', returnType: 'DOUBLE', signature: 'pow(DOUBLE a, DOUBLE p)', description: 'Returns a^p' },
      { name: 'power()', returnType: 'DOUBLE', signature: 'power(DOUBLE a, DOUBLE p)', description: 'Returns a^p' },
      { name: 'radians()', returnType: 'DOUBLE', signature: 'radians(DECIMAL|DOUBLE a)', description: 'Converts value of a from degrees to radians.' },
      { name: 'rand()', returnType: 'DOUBLE', signature: 'rand([INT seed])', description: 'Returns a random number (that changes from row to row) that is distributed uniformly from 0 to 1. Specifying the seed will make sure the generated random number sequence is deterministic.' },
      { name: 'round()', returnType: 'DOUBLE', signature: 'round(DOUBLE a [, INT d])', description: 'Returns the rounded BIGINT value of a or a rounded to d decimal places.' },
      { name: 'shiftleft()', returnType: 'T', signature: 'shiftleft(T&lt;BIGINT|INT|SMALLINT|TINYINT&gt; a, INT b)', description: 'Bitwise left shift. Shifts a b positions to the left. Returns int for tinyint, smallint and int a. Returns bigint for bigint a.' },
      { name: 'shiftright()', returnType: 'T', signature: 'shiftright(T&lt;BIGINT|INT|SMALLINT|TINYINT&gt; a, INT b)', description: 'Bitwise right shift. Shifts a b positions to the right. Returns int for tinyint, smallint and int a. Returns bigint for bigint a.' },
      { name: 'shiftrightunsigned()', returnType: 'T', signature: 'shiftrightunsigned(T&lt;BIGINT|INT|SMALLINT|TINYINT&gt; a, INT b)', description: 'Bitwise unsigned right shift. Shifts a b positions to the right. Returns int for tinyint, smallint and int a. Returns bigint for bigint a.' },
      { name: 'sign()', returnType: 'T', signature: 'sign(T&lt;DOUBLE|INT&gt; a)', description: 'Returns the sign of a as \'1.0\' (if a is positive) or \'-1.0\' (if a is negative), \'0.0\' otherwise. The decimal version returns INT instead of DOUBLE.' },
      { name: 'sin()', returnType: 'DOUBLE', signature: 'sin(DECIMAL|DOUBLE a)', description: 'Returns the sine of a (a is in radians).' },
      { name: 'sqrt()', returnType: 'DOUBLE', signature: 'sqrt(DECIMAL|DOUBLE a)', description: 'Returns the square root of a' },
      { name: 'tan()', returnType: 'DOUBLE', signature: 'tan(DECIMAL|DOUBLE a)', description: 'Returns the tangent of a (a is in radians).' },
      { name: 'unhex()', returnType: 'BINARY', signature: 'unhex(STRING a)', description: 'Inverse of hex. Interprets each pair of characters as a hexadecimal number and converts to the byte representation of the number.' }
    ],
    impala: [
      { name: 'abs()', returnType: 'T', signature: 'abs(T a)', description: 'Returns the absolute value of the argument. Use this function to ensure all return values are positive. This is different than the positive() function, which returns its argument unchanged (even if the argument was negative).' },
      { name: 'acos()', returnType: 'DOUBLE', signature: 'acos(DOUBLE a)', description: 'Returns the arccosine of the argument.' },
      { name: 'asin()', returnType: 'DOUBLE', signature: 'asin(DOUBLE a)', description: 'Returns the arcsine of the argument.' },
      { name: 'atan()', returnType: 'DOUBLE', signature: 'atan(DOUBLE a)', description: 'Returns the arctangent of the argument.' },
      { name: 'bin()', returnType: 'STRING', signature: 'bin(BIGINT a)', description: 'Returns the binary representation of an integer value, that is, a string of 0 and 1 digits.' },
      { name: 'ceil()', returnType: 'T', signature: 'ceil(T&lt;DOUBLE|DECIMAL&gt; a)', description: 'Returns the smallest integer that is greater than or equal to the argument.' },
      { name: 'ceiling()', returnType: 'T', signature: 'ceiling(T&lt;DOUBLE|DECIMAL&gt; a)', description: 'Returns the smallest integer that is greater than or equal to the argument.' },
      { name: 'conv()', returnType: 'T', signature: 'conv(T&lt;BIGINT|STRING&gt; a, INT from_base, INT to_base)', description: 'Returns a string representation of an integer value in a particular base. The input value can be a string, for example to convert a hexadecimal number such as fce2 to decimal. To use the return value as a number (for example, when converting to base 10), use CAST() to convert to the appropriate type.' },
      { name: 'cos()', returnType: 'DOUBLE', signature: 'cos(DOUBLE a)', description: 'Returns the cosine of the argument.' },
      { name: 'degrees()', returnType: 'DOUBLE', signature: 'degrees(DOUBLE a)', description: 'Converts argument value from radians to degrees.' },
      { name: 'e()', returnType: 'DOUBLE', signature: 'e()', description: 'Returns the mathematical constant e.' },
      { name: 'exp()', returnType: 'DOUBLE', signature: 'exp(DOUBLE a)', description: 'Returns the mathematical constant e raised to the power of the argument.' },
      { name: 'floor()', returnType: 'BIGINT', signature: 'floor(DOUBLE a)', description: 'Returns the largest integer that is less than or equal to the argument.' },
      { name: 'fmod()', returnType: 'T', signature: 'fmod(T&lt;DOUBLE|FLOAT&gt; a, T&lt;DOUBLE|FLOAT&gt; b)', description: 'Returns the modulus of a number.' },
      { name: 'fnv_hash()', returnType: 'BIGINT', signature: 'fnv_hash(T a)', description: 'Returns a consistent 64-bit value derived from the input argument, for convenience of implementing hashing logic in an application.' },
      { name: 'greatest()', returnType: 'T', signature: 'greatest(T a1, T a2, ...)', description: 'Returns the largest value from a list of expressions.' },
      { name: 'hex()', returnType: 'STRING', signature: 'hex(T&lt;BIGINT|STRING&gt; a)', description: 'Returns the hexadecimal representation of an integer value, or of the characters in a string.' },
      { name: 'is_inf()', returnType: 'BOOLEAN', signature: 'is_inf(DOUBLE a)', description: 'Tests whether a value is equal to the special value "inf", signifying infinity.' },
      { name: 'is_nan()', returnType: 'BOOLEAN', signature: 'is_nan(DOUBLE A)', description: 'Tests whether a value is equal to the special value "NaN", signifying "not a number".' },
      { name: 'least()', returnType: 'T', signature: 'least(T a1, T a2, ...)', description: 'Returns the smallest value from a list of expressions.' },
      { name: 'ln()', returnType: 'DOUBLE', signature: 'ln(DOUBLE a)', description: 'Returns the natural logarithm of the argument.' },
      { name: 'log()', returnType: 'DOUBLE', signature: 'log(DOUBLE base, DOUBLE a)', description: 'Returns the logarithm of the second argument to the specified base.' },
      { name: 'log10()', returnType: 'DOUBLE', signature: 'log10(DOUBLE a)', description: 'Returns the logarithm of the argument to the base 10.' },
      { name: 'log2()', returnType: 'DOUBLE', signature: 'log2(DOUBLE a)', description: 'Returns the logarithm of the argument to the base 2.' },
      { name: 'max_bigint()', returnType: 'BIGINT', signature: 'max_bigint()', description: 'Returns the largest value of the associated integral type.' },
      { name: 'max_int()', returnType: 'INT', signature: 'max_int()', description: 'Returns the largest value of the associated integral type.' },
      { name: 'max_smallint()', returnType: 'SMALLINT', signature: 'max_smallint()', description: 'Returns the largest value of the associated integral type.' },
      { name: 'max_tinyint()', returnType: 'TINYINT', signature: 'max_tinyint()', description: 'Returns the largest value of the associated integral type.' },
      { name: 'min_bigint()', returnType: 'BIGINT', signature: 'min_bigint()', description: 'Returns the smallest value of the associated integral type (a negative number).' },
      { name: 'min_int()', returnType: 'INT', signature: 'min_int()', description: 'Returns the smallest value of the associated integral type (a negative number).' },
      { name: 'min_smallint()', returnType: 'SMALLINT', signature: 'min_smallint()', description: 'Returns the smallest value of the associated integral type (a negative number).' },
      { name: 'min_tinyint()', returnType: 'TINYINT', signature: 'min_tinyint()', description: 'Returns the smallest value of the associated integral type (a negative number).' },
      { name: 'negative()', returnType: 'T', signature: 'negative(T a)', description: 'Returns the argument with the sign reversed; returns a positive value if the argument was already negative.' },
      { name: 'pi()', returnType: 'DOUBLE', signature: 'pi()', description: 'Returns the constant pi.' },
      { name: 'pmod()', returnType: 'T', signature: 'pmod(T&lt;DOUBLE|INT&gt; a, T b)', description: 'Returns the positive modulus of a number.' },
      { name: 'positive()', returnType: 'T', signature: 'positive(T a)', description: 'Returns the original argument unchanged (even if the argument is negative).' },
      { name: 'pow()', returnType: 'DOUBLE', signature: 'pow(DOUBLE a, DOUBLE p)', description: 'Returns the first argument raised to the power of the second argument.' },
      { name: 'power()', returnType: 'DOUBLE', signature: 'power(DOUBLE a, DOUBLE p)', description: 'Returns the first argument raised to the power of the second argument.' },
      { name: 'precision()', returnType: 'INT', signature: 'precision(numeric_expression)', description: 'Computes the precision (number of decimal digits) needed to represent the type of the argument expression as a DECIMAL value.' },
      { name: 'quotient()', returnType: 'INT', signature: 'quotient(INT numerator, INT denominator)', description: 'Returns the first argument divided by the second argument, discarding any fractional part. Avoids promoting arguments to DOUBLE as happens with the / SQL operator.' },
      { name: 'radians()', returnType: 'DOUBLE', signature: 'radians(DOUBLE a)', description: 'Converts argument value from degrees to radians.' },
      { name: 'rand()', returnType: 'DOUBLE', signature: 'rand([INT seed])', description: 'Returns a random value between 0 and 1. After rand() is called with a seed argument, it produces a consistent random sequence based on the seed value.' },
      { name: 'round()', returnType: 'T', signature: 'round(DOUBLE a [, INT d]), round(DECIMAL val, INT d)', description: 'Rounds a floating-point value. By default (with a single argument), rounds to the nearest integer. Values ending in .5 are rounded up for positive numbers, down for negative numbers (that is, away from zero). The optional second argument specifies how many digits to leave after the decimal point; values greater than zero produce a floating-point return value rounded to the requested number of digits to the right of the decimal point.' },
      { name: 'scale()', returnType: 'INT', signature: 'scale(numeric_expression)', description: 'Computes the scale (number of decimal digits to the right of the decimal point) needed to represent the type of the argument expression as a DECIMAL value.' },
      { name: 'sign()', returnType: 'INT', signature: 'sign(DOUBLE a)', description: 'Returns -1, 0, or 1 to indicate the signedness of the argument value.' },
      { name: 'sin()', returnType: 'DOUBLE', signature: 'sin(DOUBLE a)', description: 'Returns the sine of the argument.' },
      { name: 'sqrt()', returnType: 'DOUBLE', signature: 'sqrt(DOUBLE a)', description: 'Returns the square root of the argument.' },
      { name: 'tan()', returnType: 'DOUBLE', signature: 'tan(DOUBLE a)', description: 'Returns the tangent of the argument.' },
      { name: 'unhex()', returnType: 'STRING', signature: 'unhex(STRING a)', description: 'Returns a string of characters with ASCII values corresponding to pairs of hexadecimal digits in the argument.' }
    ]
  };

  var COMPLEX_TYPE_CONSTRUCTS = {
    hive: [
      { name: 'array()', returnType: 'ARRAY', signature: 'array(val1, val2, ...)', description: 'Creates an array with the given elements.' },
      { name: 'create_union()', returnType: 'UNION', signature: 'create_union(tag, val1, val2, ...)', description: 'Creates a union type with the value that is being pointed to by the tag parameter.' },
      { name: 'map()', returnType: 'MAP', signature: 'map(key1, value1, ...)', description: 'Creates a map with the given key/value pairs.' },
      { name: 'named_struct()', returnType: 'STRUCT', signature: 'named_struct(name1, val1, ...)', description: 'Creates a struct with the given field names and values.' },
      { name: 'struct()', returnType: 'STRUCT', signature: 'struct(val1, val2, ...)', description: 'Creates a struct with the given field values. Struct field names will be col1, col2, ....' }
    ]
  };

  var AGGREGATE_FUNCTIONS = {
    shared: [
      { name: 'var_pop()', returnType: 'DOUBLE', signature: 'var_pop(col)', description: 'Returns the variance of a numeric column in the group.' },
      { name: 'var_samp()', returnType: 'DOUBLE', signature: 'var_samp(col)', description: 'Returns the unbiased sample variance of a numeric column in the group.' }
    ],
    generic: [
      { name: 'count()', returnType: 'BIGINT', signature: 'count(col)', description: 'count(*) - Returns the total number of retrieved rows, including rows containing NULL values. count(expr) - Returns the number of rows for which the supplied expression is non-NULL.' },
      { name: 'sum()', returnType: 'DOUBLE', signature: 'sum(col)', description: 'Returns the sum of the elements in the group or the sum of the distinct values of the column in the group.' },
      { name: 'max()', returnType: 'DOUBLE', signature: 'max(col)', description: 'Returns the maximum value of the column in the group.' },
      { name: 'min()', returnType: 'DOUBLE', signature: 'min(col)', description: 'Returns the minimum of the column in the group.' }
    ],
    hive: [
      { name: 'avg()', returnType: 'DOUBLE', signature: 'avg(col)', description: 'Returns the average of the elements in the group or the average of the distinct values of the column in the group.' },
      { name: 'count()', returnType: 'BIGINT', signature: 'count([DISTINCT] col)', description: 'count(*) - Returns the total number of retrieved rows, including rows containing NULL values. count(expr) - Returns the number of rows for which the supplied expression is non-NULL. count(DISTINCT expr[, expr]) - Returns the number of rows for which the supplied expression(s) are unique and non-NULL. Execution of this can be optimized with hive.optimize.distinct.rewrite.' },
      { name: 'stddev_pop()', returnType: 'DOUBLE', signature: 'stddev_pop(col)', description: 'Returns the standard deviation of a numeric column in the group.' },
      { name: 'stddev_samp()', returnType: 'DOUBLE', signature: 'stddev_samp(col)', description: 'Returns the unbiased sample standard deviation of a numeric column in the group.' },
      { name: 'sum()', returnType: 'DOUBLE', signature: 'sum(col)', description: 'Returns the sum of the elements in the group or the sum of the distinct values of the column in the group.'},
      { name: 'max()', returnType: 'DOUBLE', signature: 'max(col)', description: 'Returns the maximum value of the column in the group.'},
      { name: 'min()', returnType: 'DOUBLE', signature: 'min(col)', description: 'Returns the minimum of the column in the group.'},
      { name: 'corr()', returnType: 'DOUBLE', signature: 'corr(col1, col2)', description: 'Returns the Pearson coefficient of correlation of a pair of a numeric columns in the group.'},
      { name: 'covar_pop()', returnType: 'DOUBLE', signature: 'covar_pop(col1, col2)', description: 'Returns the population covariance of a pair of numeric columns in the group.'},
      { name: 'covar_samp()', returnType: 'DOUBLE', signature: 'covar_samp(col1, col2)', description: 'Returns the sample covariance of a pair of a numeric columns in the group.'},
      { name: 'collect_set()', returnType: 'array', signature: 'collect_set(col)', description: 'Returns a set of objects with duplicate elements eliminated.'},
      { name: 'collect_list()', returnType: 'array', signature: 'collect_list(col)', description: 'Returns a list of objects with duplicates. (As of Hive 0.13.0.)'},
      { name: 'histogram_numeric()', returnType: 'array<struct {\'x\', \'y\'}>', signature: 'histogram_numeric(col, b)', description: 'Computes a histogram of a numeric column in the group using b non-uniformly spaced bins. The output is an array of size b of double-valued (x,y) coordinates that represent the bin centers and heights'},
      { name: 'ntile()', returnType: 'INT', signature: 'ntile(INT x)', description: 'Divides an ordered partition into x groups called buckets and assigns a bucket number to each row in the partition. This allows easy calculation of tertiles, quartiles, deciles, percentiles and other common summary statistics. (As of Hive 0.11.0.)'},
      { name: 'percentile()', returnType: 'DOUBLE|array<DOUBLE>', signature: 'percentile(BIGINT col, p), percentile(BIGINT col, array(p1 [, p2]...))', description: 'Returns the exact pth percentile (or percentiles p1, p2, ..) of a column in the group (does not work with floating point types). p must be between 0 and 1. NOTE: A true percentile can only be computed for integer values. Use PERCENTILE_APPROX if your input is non-integral.'},
      { name: 'percentile_approx()', returnType: 'DOUBLE|array<DOUBLE>', signature: 'percentile_approx(DOUBLE col, p, [, B]), percentile_approx(DOUBLE col, array(p1 [, p2]...), [, B])', description: 'Returns an approximate pth percentile (or percentiles p1, p2, ..) of a numeric column (including floating point types) in the group. The B parameter controls approximation accuracy at the cost of memory. Higher values yield better approximations, and the default is 10,000. When the number of distinct values in col is smaller than B, this gives an exact percentile value.' },
      { name: 'variance()', returnType: 'DOUBLE', signature: 'variance(col)', description: 'Returns the variance of a numeric column in the group.' }
    ],
    impala: [
      { name: 'appx_median()', returnType: 'T', signature: 'appx_median([DISTINCT|ALL] T col)', description: 'An aggregate function that returns a value that is approximately the median (midpoint) of values in the set of input values.' },
      { name: 'avg()', returnType: 'DOUBLE', signature: 'avg([DISTINCT|ALL] col)', description: 'An aggregate function that returns the average value from a set of numbers. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to AVG are NULL, AVG returns NULL.' },
      { name: 'count()', returnType: 'BIGINT', signature: 'count([DISTINCT|ALL] col)', description: 'An aggregate function that returns the number of rows, or the number of non-NULL rows.' },
      { name: 'max()', returnType: 'T', signature: 'max([DISTINCT | ALL] T col)', description: 'An aggregate function that returns the maximum value from a set of numbers. Opposite of the MIN function. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to MAX are NULL, MAX returns NULL.' },
      { name: 'min()', returnType: 'T', signature: 'min([DISTINCT | ALL] T col)', description: 'An aggregate function that returns the minimum value from a set of numbers. Opposite of the MAX function. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to MIN are NULL, MIN returns NULL.' },
      { name: 'sum()', returnType: 'BIGINT|DOUBLE', signature: 'sum([DISTINCT | ALL] col)', description: 'An aggregate function that returns the sum of a set of numbers. Its single argument can be numeric column, or the numeric result of a function or expression applied to the column value. Rows with a NULL value for the specified column are ignored. If the table is empty, or all the values supplied to MIN are NULL, SUM returns NULL.' },
      { name: 'group_concat()', returnType: 'STRING', signature: 'group_concat([ALL] col [, separator])', description: 'An aggregate function that returns a single string representing the argument value concatenated together for each row of the result set. If the optional separator string is specified, the separator is added between each pair of concatenated values. The default separator is a comma followed by a space.' },
      { name: 'ndv()', returnType: 'DOUBLE', signature: 'ndv([DISTINCT | ALL] col)', description: 'An aggregate function that returns an approximate value similar to the result of COUNT(DISTINCT col), the "number of distinct values". It is much faster than the combination of COUNT and DISTINCT, and uses a constant amount of memory and thus is less memory-intensive for columns with high cardinality.' },
      { name: 'stddev()', returnType: 'DOUBLE', signature: 'stddev([DISTINCT | ALL] col)', description: 'Returns the standard deviation of a numeric column in the group.' },
      { name: 'stddev_pop()', returnType: 'DOUBLE', signature: 'stddev_pop([DISTINCT | ALL] col)', description: 'Returns the population standard deviation of a numeric column in the group.' },
      { name: 'stddev_samp()', returnType: 'DOUBLE', signature: 'stddev_samp([DISTINCT | ALL] col)', description: 'Returns the unbiased sample standard deviation of a numeric column in the group.' },
      { name: 'variance()', returnType: 'DOUBLE', signature: 'variance([DISTINCT | ALL] col)', description: 'An aggregate function that returns the variance of a set of numbers. This is a mathematical property that signifies how far the values spread apart from the mean. The return value can be zero (if the input is a single value, or a set of identical values), or a positive number otherwise.' },
      { name: 'variance_pop()', returnType: 'DOUBLE', signature: 'variance_pop([DISTINCT | ALL] col)', description: 'An aggregate function that returns the population variance of a set of numbers. This is a mathematical property that signifies how far the values spread apart from the mean. The return value can be zero (if the input is a single value, or a set of identical values), or a positive number otherwise.' },
      { name: 'variance_samp()', returnType: 'DOUBLE', signature: 'variance_samp([DISTINCT | ALL] col)', description: 'An aggregate function that returns the sample variance of a set of numbers. This is a mathematical property that signifies how far the values spread apart from the mean. The return value can be zero (if the input is a single value, or a set of identical values), or a positive number otherwise.' }
    ]
  };

  var COLLECTION_FUNCTIONS = {
    hive: [
      { name: 'array_contains()', returnType: 'BOOLEAN', signature: 'array_contains(Array&lt;T&gt; a, val)', description: 'Returns TRUE if the array contains value.' },
      { name: 'map_keys()', returnType: 'array<K.V>', signature: 'map_keys(Map&lt;K.V&gt; a)', description: 'Returns an unordered array containing the keys of the input map.' },
      { name: 'map_values()', returnType: 'array<K.V>', signature: 'map_values(Map&lt;K.V&gt; a)', description: 'Returns an unordered array containing the values of the input map.' },
      { name: 'size()', returnType: 'INT', signature: 'size(Map&lt;K.V&gt;|Array&lt;T&gt; a)', description: 'Returns the number of elements in the map or array type.' },
      { name: 'sort_array()', returnType: 'array<T>', signature: 'sort_array(Array&lt;T&gt; a)', description: 'Sorts the input array in ascending order according to the natural ordering of the array elements and returns it.' }
    ]
  };

  var TYPE_CONVERSION_FUNCTIONS = {
    hive: [
      { name: 'binary()', returnType: 'BINARY', signature: 'binary(BINARY|STRING a)', description: 'Casts the parameter into a binary.' },
      { name: 'cast()', returnType: 'T', signature: 'cast(a as T)', description: 'Converts the results of the expression expr to type T. For example, cast(\'1\' as BIGINT) will convert the string \'1\' to its integral representation. A null is returned if the conversion does not succeed. If cast(expr as boolean) Hive returns true for a non-empty string.' }
    ],
    impala: [
      { name: 'cast()', returnType: 'T', signature: 'cast(a as T)', description: 'Converts the results of the expression expr to type T. For example, cast(\'1\' as BIGINT) will convert the string \'1\' to its integral representation. A null is returned if the conversion does not succeed. If cast(expr as boolean) Hive returns true for a non-empty string.' }
    ]
  };

  var DATE_FUNCTIONS = {
    hive: [
      { name: 'add_months()', returnType: 'STRING', signature: 'add_months(DATE|STRING|TIMESTAMP start_date, INT num_months)', description: 'Returns the date that is num_months after start_date (as of Hive 1.1.0). start_date is a string, date or timestamp. num_months is an integer. The time part of start_date is ignored. If start_date is the last day of the month or if the resulting month has fewer days than the day component of start_date, then the result is the last day of the resulting month. Otherwise, the result has the same day component as start_date.' },
      { name: 'current_date', returnType: 'DATE', signature: 'current_date', description: 'Returns the current date at the start of query evaluation (as of Hive 1.2.0). All calls of current_date within the same query return the same value.' },
      { name: 'current_timestamp', returnType: 'TIMESTAMP', signature: 'current_timestamp', description: 'Returns the current timestamp at the start of query evaluation (as of Hive 1.2.0). All calls of current_timestamp within the same query return the same value.' },
      { name: 'datediff()', returnType: 'INT', signature: 'datediff(STRING enddate, STRING startdate)', description: 'Returns the number of days from startdate to enddate: datediff(\'2009-03-01\', \'2009-02-27\') = 2.' },
      { name: 'date_add()', returnType: 'T', signature: 'date_add(STRING startdate, INT days)', description: 'Adds a number of days to startdate: date_add(\'2008-12-31\', 1) = \'2009-01-01\'. T = pre 2.1.0: STRING, 2.1.0 on: DATE' },
      { name: 'date_format()', returnType: 'STRING', signature: 'date_format(DATE|TIMESTAMP|STRING ts, STRING fmt)', description: 'Converts a date/timestamp/string to a value of string in the format specified by the date format fmt (as of Hive 1.2.0). Supported formats are Java SimpleDateFormat formats – https://docs.oracle.com/javase/7/docs/api/java/text/SimpleDateFormat.html. The second argument fmt should be constant. Example: date_format(\'2015-04-08\', \'y\') = \'2015\'.' },
      { name: 'date_sub()', returnType: 'T', signature: 'date_sub(STRING startdate, INT days)', description: 'Subtracts a number of days to startdate: date_sub(\'2008-12-31\', 1) = \'2008-12-30\'. T = pre 2.1.0: STRING, 2.1.0 on: DATE' },
      { name: 'day()', returnType: 'INT', signature: 'day(STRING date)', description: 'Returns the day part of a date or a timestamp string: day(\'1970-11-01 00:00:00\') = 1, day(\'1970-11-01\') = 1.' },
      { name: 'dayofmonth()', returnType: 'INT', signature: 'dayofmonth(STRING date)', description: 'Returns the day part of a date or a timestamp string: dayofmonth(\'1970-11-01 00:00:00\') = 1, dayofmonth(\'1970-11-01\') = 1.' },
      { name: 'from_unixtime()', returnType: 'BIGINT', signature: 'from_unixtime(BIGINT unixtime [, STRING format])', description: 'Converts time string in format yyyy-MM-dd HH:mm:ss to Unix timestamp (in seconds), using the default timezone and the default locale, return 0 if fail: unix_timestamp(\'2009-03-20 11:30:01\') = 1237573801' },
      { name: 'from_utc_timestamp()', returnType: 'TIMESTAMP', signature: 'from_utc_timestamp(TIMESTAMP a, STRING timezone)', description: 'Assumes given timestamp is UTC and converts to given timezone (as of Hive 0.8.0). For example, from_utc_timestamp(\'1970-01-01 08:00:00\',\'PST\') returns 1970-01-01 00:00:00' },
      { name: 'hour()', returnType: 'INT', signature: 'hour(STRING date)', description: 'Returns the hour of the timestamp: hour(\'2009-07-30 12:58:59\') = 12, hour(\'12:58:59\') = 12.' },
      { name: 'last_day()', returnType: 'STRING', signature: 'last_day(STRING date)', description: 'Returns the last day of the month which the date belongs to (as of Hive 1.1.0). date is a string in the format \'yyyy-MM-dd HH:mm:ss\' or \'yyyy-MM-dd\'. The time part of date is ignored.' },
      { name: 'minute()', returnType: 'INT', signature: 'minute(STRING date)', description: 'Returns the minute of the timestamp.' },
      { name: 'month()', returnType: 'INT', signature: 'month(STRING date)', description: 'Returns the month part of a date or a timestamp string: month(\'1970-11-01 00:00:00\') = 11, month(\'1970-11-01\') = 11.' },
      { name: 'months_between()', returnType: 'DOUBLE', signature: 'months_between(DATE|TIMESTAMP|STRING date1, DATE|TIMESTAMP|STRING date2)', description: 'Returns number of months between dates date1 and date2 (as of Hive 1.2.0). If date1 is later than date2, then the result is positive. If date1 is earlier than date2, then the result is negative. If date1 and date2 are either the same days of the month or both last days of months, then the result is always an integer. Otherwise the UDF calculates the fractional portion of the result based on a 31-day month and considers the difference in time components date1 and date2. date1 and date2 type can be date, timestamp or string in the format \'yyyy-MM-dd\' or \'yyyy-MM-dd HH:mm:ss\'. The result is rounded to 8 decimal places. Example: months_between(\'1997-02-28 10:30:00\', \'1996-10-30\') = 3.94959677' },
      { name: 'next_day()', returnType: 'STRING', signature: 'next_day(STRING start_date, STRING day_of_week)', description: 'Returns the first date which is later than start_date and named as day_of_week (as of Hive 1.2.0). start_date is a string/date/timestamp. day_of_week is 2 letters, 3 letters or full name of the day of the week (e.g. Mo, tue, FRIDAY). The time part of start_date is ignored. Example: next_day(\'2015-01-14\', \'TU\') = 2015-01-20.' },
      { name: 'quarter()', returnType: 'INT', signature: 'quarter(DATE|TIMESTAMP|STRING a)	', description: 'Returns the quarter of the year for a date, timestamp, or string in the range 1 to 4. Example: quarter(\'2015-04-08\') = 2.' },
      { name: 'second()', returnType: 'INT', signature: 'second(STRING date)', description: 'Returns the second of the timestamp.' },
      { name: 'to_date()', returnType: 'T', signature: 'to_date(STRING timestamp)', description: 'Returns the date part of a timestamp string, example to_date(\'1970-01-01 00:00:00\'). T = pre 2.1.0: STRING 2.1.0 on: DATE' },
      { name: 'to_utc_timestamp()', returnType: 'TIMESTAMP', signature: 'to_utc_timestamp(TIMESTAMP a, STRING timezone)', description: 'Assumes given timestamp is in given timezone and converts to UTC (as of Hive 0.8.0). For example, to_utc_timestamp(\'1970-01-01 00:00:00\',\'PST\') returns 1970-01-01 08:00:00.' },
      { name: 'trunc()', returnType: 'STRING', signature: 'trunc(STRING date, STRING format)', description: 'Returns date truncated to the unit specified by the format (as of Hive 1.2.0). Supported formats: MONTH/MON/MM, YEAR/YYYY/YY. Example: trunc(\'2015-03-17\', \'MM\') = 2015-03-01.' },
      { name: 'unix_timestamp()', returnType: 'BIGINT', signature: 'unix_timestamp(STRING date, STRING pattern)', description: 'Convert time string with given pattern to Unix time stamp (in seconds), return 0 if fail: unix_timestamp(\'2009-03-20\', \'yyyy-MM-dd\') = 1237532400.' },
      { name: 'weekofyear()', returnType: 'INT', signature: 'weekofyear(STRING date)', description: 'Returns the week number of a timestamp string: weekofyear(\'1970-11-01 00:00:00\') = 44, weekofyear(\'1970-11-01\') = 44.' },
      { name: 'year()', returnType: 'INT', signature: 'year(STRING date)', description: 'Returns the year part of a date or a timestamp string: year(\'1970-01-01 00:00:00\') = 1970, year(\'1970-01-01\') = 1970' }
    ],
    impala: [
      { name: 'add_months()', returnType: 'TIMESTAMP', signature: 'add_months(TIMESTAMP date, INT months), add_months(TIMESTAMP date, BIGINT months)', description: 'Returns the specified date and time plus some number of months.' },
      { name: 'adddate()', returnType: 'TIMESTAMP', signature: 'adddate(TIMESTAMP startdate, INT days), adddate(TIMESTAMP startdate, BIGINT days)', description: 'Adds a specified number of days to a TIMESTAMP value. Similar to date_add(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.' },
      { name: 'current_timestamp()', returnType: 'TIMESTAMP', signature: 'current_timestamp()', description: 'Alias for the now() function.' },
      { name: 'date_add()', returnType: 'TIMESTAMP', signature: 'date_add(TIMESTAMP startdate, INT days), date_add(TIMESTAMP startdate, interval_expression)', description: 'Adds a specified number of days to a TIMESTAMP value. The first argument can be a string, which is automatically cast to TIMESTAMP if it uses the recognized format. With an INTERVAL expression as the second argument, you can calculate a delta value using other units such as weeks, years, hours, seconds, and so on.' },
      { name: 'date_part()', returnType: 'TIMESTAMP', signature: 'date_part(STRING unit, TIMESTAMP timestamp)', description: 'Similar to EXTRACT(), with the argument order reversed. Supports the same date and time units as EXTRACT(). For compatibility with SQL code containing vendor extensions.' },
      { name: 'date_sub()', returnType: 'TIMESTAMP', signature: 'date_sub(TIMESTAMP startdate, INT days), date_sub(TIMESTAMP startdate, interval_expression)', description: 'ubtracts a specified number of days from a TIMESTAMP value. The first argument can be a string, which is automatically cast to TIMESTAMP if it uses the recognized format. With an INTERVAL expression as the second argument, you can calculate a delta value using other units such as weeks, years, hours, seconds, and so on.' },
      { name: 'datediff()', returnType: 'INT', signature: 'datediff(STRING enddate, STRING startdate)', description: 'Returns the number of days between two dates represented as strings.' },
      { name: 'day()', returnType: 'INT', signature: 'day(STRING date), dayofmonth(STRING date)', description: 'Returns the day field from a date represented as a string.' },
      { name: 'dayname()', returnType: 'STRING', signature: 'dayname(STRING date)', description: 'Returns the day field from a date represented as a string, converted to the string corresponding to that day name. The range of return values is \'Sunday\' to \'Saturday\'. Used in report-generating queries, as an alternative to calling dayofweek() and turning that numeric return value into a string using a CASE expression.' },
      { name: 'dayofweek()', returnType: 'INT', signature: 'dayofweek(STRING date)', description: 'Returns the day field from a date represented as a string, corresponding to the day of the week. The range of return values is 1 (Sunday) to 7 (Saturday).' },
      { name: 'dayofyear()', returnType: 'INT', signature: 'dayofyear(TIMESTAMP date)', description: 'Returns the day field from a TIMESTAMP value, corresponding to the day of the year. The range of return values is 1 (January 1) to 366 (December 31 of a leap year).' },
      { name: 'days_add()', returnType: 'TIMESTAMP', signature: 'days_add(TIMESTAMP startdate, BIGINT|INT days)', description: 'Adds a specified number of days to a TIMESTAMP value. Similar to date_add(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.' },
      { name: 'days_sub()', returnType: 'TIMESTAMP', signature: 'days_sub(TIMESTAMP startdate, BIGINT|INT days)', description: 'Subtracts a specified number of days from a TIMESTAMP value. Similar to date_sub(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.' },
      { name: 'extract()', returnType: 'INT', signature: 'extract(TIMESTAMP date, STRING unit), extract(STRING unit FROM TIMESTAMP date)', description: 'Returns one of the numeric date or time fields from a TIMESTAMP value.' },
      { name: 'from_unixtime()', returnType: 'STRING', signature: 'from_unixtime(BIGINT unixtime [, STRING format])', description: 'Converts the number of seconds from the Unix epoch to the specified time into a string in the local time zone.' },
      { name: 'from_utc_timestamp()', returnType: 'TIMESTAMP', signature: 'from_utc_timestamp(TIMESTAMP date, STRING timezone)', description: 'Converts a specified UTC timestamp value into the appropriate value for a specified time zone.' },
      { name: 'hour()', returnType: 'INT', signature: 'hour(STRING date)', description: 'Returns the hour field from a date represented as a string.' },
      { name: 'hours_add()', returnType: 'TIMESTAMP', signature: 'hours_add(TIMESTAMP date, BIGINT|INT hours)', description: 'Returns the specified date and time plus some number of hours.' },
      { name: 'hours_sub()', returnType: 'TIMESTAMP', signature: 'hours_sub(TIMESTAMP date, BIGINT|INT hours)', description: 'Returns the specified date and time minus some number of hours.' },
      { name: 'microseconds_add()', returnType: 'TIMESTAMP', signature: 'microseconds_add(TIMESTAMP date, BIGINT|INT microseconds)', description: 'Returns the specified date and time plus some number of microseconds.' },
      { name: 'microseconds_sub()', returnType: 'TIMESTAMP', signature: 'microseconds_sub(TIMESTAMP date, BIGINT|INT microseconds)', description: 'Returns the specified date and time minus some number of microseconds.' },
      { name: 'milliseconds_add()', returnType: 'TIMESTAMP', signature: 'milliseconds_add(TIMESTAMP date, BIGINT|INT milliseconds)', description: 'Returns the specified date and time plus some number of milliseconds.' },
      { name: 'milliseconds_sub()', returnType: 'TIMESTAMP', signature: 'milliseconds_sub(TIMESTAMP date, BIGINT|INT milliseconds)', description: 'Returns the specified date and time minus some number of milliseconds.' },
      { name: 'minute()', returnType: 'INT', signature: 'minute(STRING date)', description: 'Returns the minute field from a date represented as a string.' },
      { name: 'minutes_add()', returnType: 'TIMESTAMP', signature: 'minutes_add(TIMESTAMP date, BIGINT|INT minutes)', description: 'Returns the specified date and time plus some number of minutes.' },
      { name: 'minutes_sub()', returnType: 'TIMESTAMP', signature: 'minutes_sub(TIMESTAMP date, BIGINT|INT minutes)', description: 'Returns the specified date and time minus some number of minutes.' },
      { name: 'month()', returnType: 'INT', signature: 'month(STRING date)', description: 'Returns the month field from a date represented as a string.' },
      { name: 'months_add()', returnType: 'TIMESTAMP', signature: 'months_add(TIMESTAMP date, BIGINT|INT months)', description: 'Returns the specified date and time plus some number of months.' },
      { name: 'months_sub()', returnType: 'TIMESTAMP', signature: 'months_sub(TIMESTAMP date, BIGINT|INT months)', description: 'Returns the specified date and time minus some number of months.' },
      { name: 'nanoseconds_add()', returnType: 'TIMESTAMP', signature: 'nanoseconds_add(TIMESTAMP date, BIGINT|INT nanoseconds)', description: 'Returns the specified date and time plus some number of nanoseconds.' },
      { name: 'nanoseconds_sub()', returnType: 'TIMESTAMP', signature: 'nanoseconds_sub(TIMESTAMP date, BIGINT|INT nanoseconds)', description: 'Returns the specified date and time minus some number of nanoseconds.' },
      { name: 'now()', returnType: 'TIMESTAMP', signature: 'now()', description: 'Returns the current date and time (in the local time zone) as a timestamp value.' },
      { name: 'second()', returnType: 'INT', signature: 'second(STRING date)', description: 'Returns the second field from a date represented as a string.' },
      { name: 'seconds_add()', returnType: 'TIMESTAMP', signature: 'seconds_add(TIMESTAMP date, BIGINT|INT seconds)', description: 'Returns the specified date and time plus some number of seconds.' },
      { name: 'seconds_sub()', returnType: 'TIMESTAMP', signature: 'seconds_sub(TIMESTAMP date, BIGINT|INT seconds)', description: 'Returns the specified date and time minus some number of seconds.' },
      { name: 'subdate()', returnType: 'TIMESTAMP', signature: 'subdate(TIMESTAMP startdate, BIGINT|INT days)', description: 'Subtracts a specified number of days from a TIMESTAMP value. Similar to date_sub(), but starts with an actual TIMESTAMP value instead of a string that is converted to a TIMESTAMP.' },
      { name: 'to_date()', returnType: 'STRING', signature: 'to_date(TIMESTAMP date)', description: 'Returns a string representation of the date field from a timestamp value.' },
      { name: 'to_utc_timestamp()', returnType: 'TIMESTAMP', signature: 'to_utc_timestamp(TIMESTAMP date, STRING timezone)', description: 'Converts a specified timestamp value in a specified time zone into the corresponding value for the UTC time zone.' },
      { name: 'trunc()', returnType: 'TIMESTAMP', signature: 'trunc(TIMESTAMP date, STRING unit)', description: 'Strips off fields and optionally rounds a TIMESTAMP value.' },
      { name: 'unix_timestamp()', returnType: 'INT', signature: 'unix_timestamp([STRING datetime [, STRING format]]|[TIMESTAMP datetime])', description: 'Returns an integer value representing the current date and time as a delta from the Unix epoch, or converts from a specified date and time value represented as a TIMESTAMP or STRING.' },
      { name: 'weekofyear()', returnType: 'INT', signature: 'weekofyear(STRING date)', description: 'Returns the corresponding week (1-53) from a date represented as a string.' },
      { name: 'weeks_add()', returnType: 'TIMESTAMP', signature: 'weeks_add(TIMESTAMP date, BIGINT|INT weeks)', description: 'Returns the specified date and time plus some number of weeks.' },
      { name: 'weeks_sub()', returnType: 'TIMESTAMP', signature: 'weeks_sub(TIMESTAMP date, BIGINT|INT weeks)', description: 'Returns the specified date and time minus some number of weeks.' },
      { name: 'year()', returnType: 'INT', signature: 'year(STRING date)', description: 'Returns the year field from a date represented as a string.' },
      { name: 'years_add()', returnType: 'TIMESTAMP', signature: 'years_add(TIMESTAMP date, BIGINT|INT years)', description: 'Returns the specified date and time plus some number of years.' },
      { name: 'years_sub()', returnType: 'TIMESTAMP', signature: 'years_sub(TIMESTAMP date, BIGINT|INT years)', description: 'Returns the specified date and time minus some number of years.' }
    ]
  };

  var CONDITIONAL_FUNCTIONS = {
    hive: [
      { name: 'coalesce()', returnType: 'T', signature: 'coalesce(T v1, T v2, ...)', description: 'Returns the first v that is not NULL, or NULL if all v\'s are NULL.' },
      { name: 'if()', returnType: 'T', signature: 'if(BOOLEAN testCondition, T valueTrue, T valueFalseOrNull)', description: 'Returns valueTrue when testCondition is true, returns valueFalseOrNull otherwise.' },
      { name: 'isnotnull()', returnType: 'BOOLEAN', signature: 'isnotnull(a)', description: 'Returns true if a is not NULL and false otherwise.' },
      { name: 'isnull()', returnType: 'BOOLEAN', signature: 'isnull(a)', description: 'Returns true if a is NULL and false otherwise.' },
      { name: 'nvl()', returnType: 'T', signature: 'nvl(T value, T default_value)', description: 'Returns default value if value is null else returns value (as of Hive 0.11).' }
    ],
    impala: [
      { name: 'coalesce()', returnType: 'T', signature: 'coalesce(T v1, T v2, ...)', description: 'Returns the first specified argument that is not NULL, or NULL if all arguments are NULL.' },
      { name: 'decode()', returnType: 'T', signature: 'decode(T expression, T search1, T result1 [, T search2, T result2 ...] [, T default] )', description: 'Compares an expression to one or more possible values, and returns a corresponding result when a match is found.' },
      { name: 'if()', returnType: 'T', signature: 'if(BOOLEAN condition, T ifTrue, T ifFalseOrNull)', description: 'Tests an expression and returns a corresponding result depending on whether the result is true, false, or NULL.' },
      { name: 'ifnull()', returnType: 'T', signature: 'ifnull(T a, T ifNotNull)', description: 'Alias for the isnull() function, with the same behavior. To simplify porting SQL with vendor extensions to Impala.' },
      { name: 'isnull()', returnType: 'T', signature: 'isnull(T a, T ifNotNull)', description: 'Tests if an expression is NULL, and returns the expression result value if not. If the first argument is NULL, returns the second argument.' },
      { name: 'nullif()', returnType: 'T', signature: 'nullif(T expr1, T expr2)', description: 'Returns NULL if the two specified arguments are equal. If the specified arguments are not equal, returns the value of expr1. The data types of the expressions must be compatible. You cannot use an expression that evaluates to NULL for expr1; that way, you can distinguish a return value of NULL from an argument value of NULL, which would never match expr2.' },
      { name: 'nullifzero()', returnType: 'T', signature: 'nullifzero(T numeric_expr)', description: 'Returns NULL if the numeric expression evaluates to 0, otherwise returns the result of the expression.' },
      { name: 'nvl()', returnType: 'T', signature: 'nvl(T a, T ifNotNull)', description: 'Alias for the isnull() function. Tests if an expression is NULL, and returns the expression result value if not. If the first argument is NULL, returns the second argument. Equivalent to the nvl() function from Oracle Database or ifnull() from MySQL.' },
      { name: 'zeroifnull()', returnType: 'T', signature: 'zeroifnull(T numeric_expr)', description: 'Returns 0 if the numeric expression evaluates to NULL, otherwise returns the result of the expression.' }
    ]
  };

  var STRING_FUNCTIONS = {
    hive: [
      { name: 'ascii()', returnType: 'INT', signature: 'ascii(STRING str)', description: 'Returns the numeric value of the first character of str.' },
      { name: 'base64()', returnType: 'STRING', signature: 'base64(BINARY bin)', description: 'Converts the argument from binary to a base 64 string (as of Hive 0.12.0).' },
      { name: 'concat()', returnType: 'STRING', signature: 'concat(STRING|BINARY a, STRING|BINARY b...)', description: 'Returns the string or bytes resulting from concatenating the strings or bytes passed in as parameters in order. For example, concat(\'foo\', \'bar\') results in \'foobar\'. Note that this function can take any number of input strings.' },
      { name: 'concat_ws()', returnType: 'STRING', signature: 'concat_ws(STRING sep, STRING a, STRING b...), concat_ws(STRING sep, Array&lt;STRING&gt;)', description: 'Like concat(), but with custom separator SEP.' },
      { name: 'context_ngrams()', returnType: 'array<struct<STRING,DOUBLE>>', signature: 'context_ngrams(Array&lt;Array&lt;STRING&gt;&gt;, Array&lt;STRING&gt;, INT k, INT pf)', description: 'Returns the top-k contextual N-grams from a set of tokenized sentences, given a string of "context".' },
      { name: 'decode()', returnType: 'STRING', signature: 'decode(BINARY bin, STRING charset)', description: 'Decodes the first argument into a String using the provided character set (one of \'US-ASCII\', \'ISO-8859-1\', \'UTF-8\', \'UTF-16BE\', \'UTF-16LE\', \'UTF-16\'). If either argument is null, the result will also be null. (As of Hive 0.12.0.)' },
      { name: 'encode()', returnType: 'BINARY', signature: 'encode(STRING src, STRING charset)', description: 'Encodes the first argument into a BINARY using the provided character set (one of \'US-ASCII\', \'ISO-8859-1\', \'UTF-8\', \'UTF-16BE\', \'UTF-16LE\', \'UTF-16\'). If either argument is null, the result will also be null. (As of Hive 0.12.0.)' },
      { name: 'find_in_set()', returnType: 'INT', signature: 'find_in_set(STRING str, STRING strList)', description: 'Returns the first occurance of str in strList where strList is a comma-delimited string. Returns null if either argument is null. Returns 0 if the first argument contains any commas. For example, find_in_set(\'ab\', \'abc,b,ab,c,def\') returns 3.' },
      { name: 'format_number()', returnType: 'STRING', signature: 'format_number(NUMBER x, INT d)', description: 'Formats the number X to a format like \'#,###,###.##\', rounded to D decimal places, and returns the result as a string. If D is 0, the result has no decimal point or fractional part. (As of Hive 0.10.0; bug with float types fixed in Hive 0.14.0, decimal type support added in Hive 0.14.0)' },
      { name: 'get_json_object()', returnType: 'STRING', signature: 'get_json_object(STRING json_string, STRING path)', description: 'Extracts json object from a json string based on json path specified, and returns json string of the extracted json object. It will return null if the input json string is invalid. NOTE: The json path can only have the characters [0-9a-z_], i.e., no upper-case or special characters. Also, the keys *cannot start with numbers.* This is due to restrictions on Hive column names.' },
      { name: 'initcap()', returnType: 'STRING', signature: 'initcap(STRING a)', description: 'Returns string, with the first letter of each word in uppercase, all other letters in lowercase. Words are delimited by whitespace. (As of Hive 1.1.0.)' },
      { name: 'instr()', returnType: 'INT', signature: 'instr(STRING str, STRING substr)', description: 'Returns the position of the first occurrence of substr in str. Returns null if either of the arguments are null and returns 0 if substr could not be found in str. Be aware that this is not zero based. The first character in str has index 1.' },
      { name: 'in_file()', returnType: 'BOOLEAN', signature: 'in_file(STRING str, STRING filename)', description: 'Returns true if the string str appears as an entire line in filename.' },
      { name: 'length()', returnType: 'INT', signature: 'length(STRING a)', description: 'Returns the length of the string.' },
      { name: 'levenshtein()', returnType: 'INT', signature: 'levenshtein(STRING a, STRING b)', description: 'Returns the Levenshtein distance between two strings (as of Hive 1.2.0). For example, levenshtein(\'kitten\', \'sitting\') results in 3.' },
      { name: 'lcase()', returnType: 'STRING', signature: 'lcase(STRING a)', description: 'Returns the string resulting from converting all characters of B to lower case. For example, lcase(\'fOoBaR\') results in \'foobar\'.' },
      { name: 'locate()', returnType: 'INT', signature: 'locate(STRING substr, STRING str [, INT pos])', description: 'Returns the position of the first occurrence of substr in str after position pos.' },
      { name: 'lower()', returnType: 'STRING', signature: 'lower(STRING a)', description: 'Returns the string resulting from converting all characters of B to lower case. For example, lower(\'fOoBaR\') results in \'foobar\'.' },
      { name: 'lpad()', returnType: 'STRING', signature: 'lpad(STRING str, INT len, STRING pad)', description: 'Returns str, left-padded with pad to a length of len.' },
      { name: 'ltrim()', returnType: 'STRING', signature: 'ltrim(STRING a)', description: 'Returns the string resulting from trimming spaces from the beginning(left hand side) of A. For example, ltrim(\' foobar \') results in \'foobar \'.' },
      { name: 'ngrams()', returnType: 'array<struct<STRING, DOUBLE>>', signature: 'ngrams(Array&lt;Array&lt;STRING&gt;&gt; a, INT n, INT k, INT pf)', description: 'Returns the top-k N-grams from a set of tokenized sentences, such as those returned by the sentences() UDAF.' },
      { name: 'parse_url()', returnType: 'STRING', signature: 'parse_url(STRING urlString, STRING partToExtract [, STRING keyToExtract])', description: 'Returns the specified part from the URL. Valid values for partToExtract include HOST, PATH, QUERY, REF, PROTOCOL, AUTHORITY, FILE, and USERINFO. For example, parse_url(\'http://facebook.com/path1/p.php?k1=v1&k2=v2#Ref1\', \'HOST\') returns \'facebook.com\'. Also a value of a particular key in QUERY can be extracted by providing the key as the third argument, for example, parse_url(\'http://facebook.com/path1/p.php?k1=v1&k2=v2#Ref1\', \'QUERY\', \'k1\') returns \'v1\'.' },
      { name: 'printf()', returnType: 'STRING', signature: 'printf(STRING format, Obj... args)', description: 'Returns the input formatted according do printf-style format strings (as of Hive 0.9.0).' },
      { name: 'regexp_extract()', returnType: 'STRING', signature: 'regexp_extract(STRING subject, STRING pattern, INT index)', description: 'Returns the string extracted using the pattern. For example, regexp_extract(\'foothebar\', \'foo(.*?)(bar)\', 2) returns \'bar.\' Note that some care is necessary in using predefined character classes: using \'\\s\' as the second argument will match the letter s; \'\\\\s\' is necessary to match whitespace, etc. The \'index\' parameter is the Java regex Matcher group() method index.' },
      { name: 'regexp_replace()', returnType: 'STRING', signature: 'regexp_replace(STRING initial_string, STRING pattern, STRING replacement)', description: 'Returns the string resulting from replacing all substrings in INITIAL_STRING that match the java regular expression syntax defined in PATTERN with instances of REPLACEMENT. For example, regexp_replace("foobar", "oo|ar", "") returns \'fb.\' Note that some care is necessary in using predefined character classes: using \'\\s\' as the second argument will match the letter s; \'\\\\s\' is necessary to match whitespace, etc.' },
      { name: 'repeat()', returnType: 'STRING', signature: 'repeat(STRING str, INT n)', description: 'Repeats str n times.' },
      { name: 'reverse()', returnType: 'STRING', signature: 'reverse(STRING a)', description: 'Returns the reversed string.' },
      { name: 'rpad()', returnType: 'STRING', signature: 'rpad(STRING str, INT len, STRING pad)', description: 'Returns str, right-padded with pad to a length of len.' },
      { name: 'rtrim()', returnType: 'STRING', signature: 'rtrim(STRING a)', description: 'Returns the string resulting from trimming spaces from the end(right hand side) of A. For example, rtrim(\' foobar \') results in \' foobar\'.' },
      { name: 'sentences()', returnType: 'array<array<STRING>>', signature: 'sentences(STRING str, STRING lang, STRING locale)', description: 'Tokenizes a string of natural language text into words and sentences, where each sentence is broken at the appropriate sentence boundary and returned as an array of words. The \'lang\' and \'locale\' are optional arguments. For example, sentences(\'Hello there! How are you?\') returns ( ("Hello", "there"), ("How", "are", "you") ).' },
      { name: 'soundex()', returnType: 'STRING', signature: 'soundex(STRING a)', description: 'Returns soundex code of the string (as of Hive 1.2.0). For example, soundex(\'Miller\') results in M460.' },
      { name: 'space()', returnType: 'STRING', signature: 'space(INT n)', description: 'Returns a string of n spaces.' },
      { name: 'split()', returnType: 'array<STRING>', signature: 'split(STRING str, STRING pat)', description: 'Splits str around pat (pat is a regular expression).' },
      { name: 'str_to_map()', returnType: 'map<STRING,STRING>', signature: 'str_to_map(STRING [, STRING delimiter1, STRING delimiter2])', description: 'Splits text into key-value pairs using two delimiters. Delimiter1 separates text into K-V pairs, and Delimiter2 splits each K-V pair. Default delimiters are \',\' for delimiter1 and \'=\' for delimiter2.' },
      { name: 'substr()', returnType: 'STRING', signature: 'substr(STRING|BINARY A, INT start [, INT len]) ', description: 'Returns the substring or slice of the byte array of A starting from start position till the end of string A or with optional length len. For example, substr(\'foobar\', 4) results in \'bar\'' },
      { name: 'substring()', returnType: 'STRING', signature: 'substring(STRING|BINARY a, INT start [, INT len])', description: 'Returns the substring or slice of the byte array of A starting from start position till the end of string A or with optional length len. For example, substr(\'foobar\', 4) results in \'bar\'' },
      { name: 'substring_index()', returnType: 'STRING', signature: 'substring_index(STRING a, STRING delim, INT count)', description: 'Returns the substring from string A before count occurrences of the delimiter delim (as of Hive 1.3.0). If count is positive, everything to the left of the final delimiter (counting from the left) is returned. If count is negative, everything to the right of the final delimiter (counting from the right) is returned. Substring_index performs a case-sensitive match when searching for delim. Example: substring_index(\'www.apache.org\', \'.\', 2) = \'www.apache\'.' },
      { name: 'translate()', returnType: 'STRING', signature: 'translate(STRING|CHAR|VARCHAR input, STRING|CHAR|VARCHAR from, STRING|CHAR|VARCHAR to)', description: 'Translates the input string by replacing the characters present in the from string with the corresponding characters in the to string. This is similar to the translate function in PostgreSQL. If any of the parameters to this UDF are NULL, the result is NULL as well. (Available as of Hive 0.10.0, for string types) Char/varchar support added as of Hive 0.14.0.' },
      { name: 'trim()', returnType: 'STRING', signature: 'trim(STRING a)', description: 'Returns the string resulting from trimming spaces from both ends of A. For example, trim(\' foobar \') results in \'foobar\'' },
      { name: 'ucase()', returnType: 'STRING', signature: 'ucase(STRING a)', description: 'Returns the string resulting from converting all characters of A to upper case. For example, ucase(\'fOoBaR\') results in \'FOOBAR\'.' },
      { name: 'unbase64()', returnType: 'BINARY', signature: 'unbase64(STRING a)', description: 'Converts the argument from a base 64 string to BINARY. (As of Hive 0.12.0.)' },
      { name: 'upper()', returnType: 'STRING', signature: 'upper(STRING a)', description: 'Returns the string resulting from converting all characters of A to upper case. For example, upper(\'fOoBaR\') results in \'FOOBAR\'.' }
    ],
    impala: [
      { name: 'ascii', returnType: 'INT', signature: 'ascii(STRING str)', description: 'Returns the numeric ASCII code of the first character of the argument.' },
      { name: 'char_length', returnType: 'INT', signature: 'char_length(STRING a)', description: 'Returns the length in characters of the argument string. Aliases for the length() function.' },
      { name: 'character_length', returnType: 'INT', signature: 'character_length(STRING a)', description: 'Returns the length in characters of the argument string. Aliases for the length() function.' },
      { name: 'concat', returnType: 'STRING', signature: 'concat(STRING a, STRING b...)', description: 'Returns a single string representing all the argument values joined together.' },
      { name: 'concat_ws', returnType: 'STRING', signature: 'concat_ws(STRING sep, STRING a, STRING b...)', description: 'Returns a single string representing the second and following argument values joined together, delimited by a specified separator.' },
      { name: 'find_in_set', returnType: 'INT', signature: 'find_in_set(STRING str, STRING strList)', description: 'Returns the position (starting from 1) of the first occurrence of a specified string within a comma-separated string. Returns NULL if either argument is NULL, 0 if the search string is not found, or 0 if the search string contains a comma.' },
      { name: 'group_concat', returnType: 'STRING', signature: 'group_concat(STRING s [, STRING sep])', description: 'Returns a single string representing the argument value concatenated together for each row of the result set. If the optional separator string is specified, the separator is added between each pair of concatenated values.' },
      { name: 'initcap', returnType: 'STRING', signature: 'initcap(STRING str)', description: 'Returns the input string with the first letter capitalized.' },
      { name: 'instr', returnType: 'INT', signature: 'instr(STRING str, STRING substr)', description: 'Returns the position (starting from 1) of the first occurrence of a substring within a longer string.' },
      { name: 'length', returnType: 'INT', signature: 'length(STRING a)', description: 'Returns the length in characters of the argument string.' },
      { name: 'locate', returnType: 'INT', signature: 'locate(STRING substr, string str[, int pos])', description: 'Returns the position (starting from 1) of the first occurrence of a substring within a longer string, optionally after a particular position.' },
      { name: 'lower', returnType: 'STRING', signature: 'lower(STRING a)', description: 'Returns the argument string converted to all-lowercase.' },
      { name: 'lcase', returnType: 'STRING', signature: 'lcase(STRING a)', description: 'Returns the argument string converted to all-lowercase.' },
      { name: 'lpad', returnType: 'STRING', signature: 'lpad(STRING str, int len, string pad)', description: 'Returns a string of a specified length, based on the first argument string. If the specified string is too short, it is padded on the left with a repeating sequence of the characters from the pad string. If the specified string is too long, it is truncated on the right.' },
      { name: 'ltrim', returnType: 'STRING', signature: 'ltrim(STRING a)', description: 'Returns the argument string with any leading spaces removed from the left side.' },
      { name: 'parse_url', returnType: 'STRING', signature: 'parse_url(STRING urlString, STRING partToExtract [, STRING keyToExtract])', description: 'Returns the portion of a URL corresponding to a specified part. The part argument can be \'PROTOCOL\', \'HOST\', \'PATH\', \'REF\', \'AUTHORITY\', \'FILE\', \'USERINFO\', or \'QUERY\'. Uppercase is required for these literal values. When requesting the QUERY portion of the URL, you can optionally specify a key to retrieve just the associated value from the key-value pairs in the query string.' },
      { name: 'regexp_extract', returnType: 'STRING', signature: 'regexp_extract(STRING subject, STRING pattern, INT index)', description: 'Returns the specified () group from a string based on a regular expression pattern. Group 0 refers to the entire extracted string, while group 1, 2, and so on refers to the first, second, and so on (...) portion.' },
      { name: 'regexp_replace', returnType: 'STRING', signature: 'regexp_replace(STRING initial, STRING pattern, STRING replacement)', description: 'Returns the initial argument with the regular expression pattern replaced by the final argument string.' },
      { name: 'repeat', returnType: 'STRING', signature: 'repeat(STRING str, INT n)', description: 'Returns the argument string repeated a specified number of times.' },
      { name: 'reverse', returnType: 'STRING', signature: 'reverse(STRING a)', description: 'Returns the argument string with characters in reversed order.' },
      { name: 'rpad', returnType: 'STRING', signature: 'rpad(STRING str, INT len, STRING pad)', description: 'Returns a string of a specified length, based on the first argument string. If the specified string is too short, it is padded on the right with a repeating sequence of the characters from the pad string. If the specified string is too long, it is truncated on the right.' },
      { name: 'rtrim', returnType: 'STRING', signature: 'rtrim(STRING a)', description: 'Returns the argument string with any trailing spaces removed from the right side.' },
      { name: 'space', returnType: 'STRING', signature: 'space(INT n)', description: 'Returns a concatenated string of the specified number of spaces. Shorthand for repeat(\' \', n).' },
      { name: 'strleft', returnType: 'STRING', signature: 'strleft(STRING a, INT num_chars)', description: 'Returns the leftmost characters of the string. Shorthand for a call to substr() with 2 arguments.' },
      { name: 'strright', returnType: 'STRING', signature: 'strright(STRING a, INT num_chars)', description: 'Returns the rightmost characters of the string. Shorthand for a call to substr() with 2 arguments.' },
      { name: 'substr', returnType: 'STRING', signature: 'substr(STRING a, INT start [, INT len])', description: 'Returns the portion of the string starting at a specified point, optionally with a specified maximum length. The characters in the string are indexed starting at 1.' },
      { name: 'substring', returnType: 'STRING', signature: 'substring(STRING a, INT start [, INT len])', description: 'Returns the portion of the string starting at a specified point, optionally with a specified maximum length. The characters in the string are indexed starting at 1.' },
      { name: 'translate', returnType: 'STRING', signature: 'translate(STRING input, STRING from, STRING to)', description: 'Returns the input string with a set of characters replaced by another set of characters.' },
      { name: 'trim', returnType: 'STRING', signature: 'trim(STRING a)', description: 'Returns the input string with both leading and trailing spaces removed. The same as passing the string through both ltrim() and rtrim().' },
      { name: 'upper', returnType: 'STRING', signature: 'upper(STRING a)', description: 'Returns the argument string converted to all-uppercase.' },
      { name: 'ucase', returnType: 'STRING', signature: 'ucase(STRING a)', description: 'Returns the argument string converted to all-uppercase.' }
    ]
  };

  var TABLE_GENERATING_FUNCTIONS = {
    hive: [
      { name: 'explode()', returnType: 'table', signature: 'explode(Array|Array<T>|Map a)', description: '' },
      { name: 'inline()', returnType: 'table', signature: 'inline(Array<Struct [, Struct]> a)', description: 'Explodes an array of structs into a table. (As of Hive 0.10.)' },
      { name: 'json_tuple()', returnType: 'table', signature: 'json_tuple(STRING jsonStr, STRING k1, STRING k2, ...)', description: 'A new json_tuple() UDTF is introduced in Hive 0.7. It takes a set of names (keys) and a JSON string, and returns a tuple of values using one function. This is much more efficient than calling GET_JSON_OBJECT to retrieve more than one key from a single JSON string.' },
      { name: 'parse_url_tuple()', returnType: 'table', signature: 'parse_url_tuple(STRING url, STRING p1, STRING p2, ...)', description: 'The parse_url_tuple() UDTF is similar to parse_url(), but can extract multiple parts of a given URL, returning the data in a tuple. Values for a particular key in QUERY can be extracted by appending a colon and the key to the partToExtract argument.' },
      { name: 'posexplode()', returnType: 'table', signature: 'posexplode(ARRAY)', description: 'posexplode() is similar to explode but instead of just returning the elements of the array it returns the element as well as its position in the original array.' },
      { name: 'stack()', returnType: 'table', signature: 'stack(INT n, v1, v2, ..., vk)', description: 'Breaks up v1, v2, ..., vk into n rows. Each row will have k/n columns. n must be constant.' }
    ]
  };

  var MISC_FUNCTIONS = {
    hive: [
      { name: 'aes_decrypt()', returnType: 'BINARY', signature: 'aes_decrypt(BINARY input, STRING|BINARY key)', description: 'Decrypt input using AES (as of Hive 1.3.0). Key lengths of 128, 192 or 256 bits can be used. 192 and 256 bits keys can be used if Java Cryptography Extension (JCE) Unlimited Strength Jurisdiction Policy Files are installed. If either argument is NULL or the key length is not one of the permitted values, the return value is NULL. Example: aes_decrypt(unbase64(\'y6Ss+zCYObpCbgfWfyNWTw==\'), \'1234567890123456\') = \'ABC\'.' },
      { name: 'aes_encrypt()', returnType: 'BINARY', signature: 'aes_encrypt(STRING|BINARY input, STRING|BINARY key)', description: 'Encrypt input using AES (as of Hive 1.3.0). Key lengths of 128, 192 or 256 bits can be used. 192 and 256 bits keys can be used if Java Cryptography Extension (JCE) Unlimited Strength Jurisdiction Policy Files are installed. If either argument is NULL or the key length is not one of the permitted values, the return value is NULL. Example: base64(aes_encrypt(\'ABC\', \'1234567890123456\')) = \'y6Ss+zCYObpCbgfWfyNWTw==\'.' },
      { name: 'crc32()', returnType: 'BIGINT', signature: 'crc32(STRING|BINARY a)', description: 'Computes a cyclic redundancy check value for string or binary argument and returns bigint value (as of Hive 1.3.0). Example: crc32(\'ABC\') = 2743272264.' },
      { name: 'current_database()', returnType: 'STRING', signature: 'current_database()', description: 'Returns current database name (as of Hive 0.13.0).' },
      { name: 'current_user()', returnType: 'STRING', signature: 'current_user()', description: 'Returns current user name (as of Hive 1.2.0).' },
      { name: 'get_json_object()', returnType: 'STRING', signature: 'get_json_object(STRING json, STRING jsonPath)', description: 'A limited version of JSONPath is supported ($ : Root object, . : Child operator, [] : Subscript operator for array, * : Wildcard for []' },
      { name: 'hash()', returnType: 'INT', signature: 'hash(a1[, a2...])', description: 'Returns a hash value of the arguments. (As of Hive 0.4.)' },
      { name: 'java_method()', returnType: 'T', signature: 'java_method(class, method[, arg1[, arg2..]])', description: 'Calls a Java method by matching the argument signature, using reflection. (As of Hive 0.9.0.)' },
      { name: 'md5()', returnType: 'STRING', signature: 'md5(STRING|BINARY a)	', description: 'Calculates an MD5 128-bit checksum for the string or binary (as of Hive 1.3.0). The value is returned as a string of 32 hex digits, or NULL if the argument was NULL. Example: md5(\'ABC\') = \'902fbdd2b1df0c4f70b4a5d23525e932\'.' },
      { name: 'reflect()', returnType: 'T', signature: 'reflect(class, method[, arg1[, arg2..]])', description: 'Calls a Java method by matching the argument signature, using reflection. (As of Hive 0.7.0.)' },
      { name: 'sha()', returnType: 'STRING', signature: 'sha(STRING|BINARY a)', description: 'Calculates the SHA-1 digest for string or binary and returns the value as a hex string (as of Hive 1.3.0). Example: sha1(\'ABC\') = \'3c01bdbb26f358bab27f267924aa2c9a03fcfdb8\'.' },
      { name: 'sha1()', returnType: 'STRING', signature: 'sha1(STRING|BINARY a)', description: 'Calculates the SHA-1 digest for string or binary and returns the value as a hex string (as of Hive 1.3.0). Example: sha1(\'ABC\') = \'3c01bdbb26f358bab27f267924aa2c9a03fcfdb8\'.' },
      { name: 'sha2()', returnType: 'STRING', signature: 'sha2(STRING|BINARY a, INT b)', description: 'Calculates the SHA-2 family of hash functions (SHA-224, SHA-256, SHA-384, and SHA-512) (as of Hive 1.3.0). The first argument is the string or binary to be hashed. The second argument indicates the desired bit length of the result, which must have a value of 224, 256, 384, 512, or 0 (which is equivalent to 256). SHA-224 is supported starting from Java 8. If either argument is NULL or the hash length is not one of the permitted values, the return value is NULL. Example: sha2(\'ABC\', 256) = \'b5d4045c3f466fa91fe2cc6abe79232a1a57cdf104f7a26e716e0a1e2789df78\'.' },
      { name: 'xpath()', returnType: 'array<STRING>', signature: 'xpath(STRING xml, STRING xpath)', description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.' },
      { name: 'xpath_boolean()', returnType: 'BOOLEAN', signature: 'xpath_boolean(STRING xml, STRING xpath)', description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.' },
      { name: 'xpath_double()', returnType: 'DOUBLE', signature: 'xpath_double(STRING xml, STRING xpath)', description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.' },
      { name: 'xpath_float()', returnType: 'DOUBLE', signature: 'xpath_float(STRING xml, STRING xpath)', description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.' },
      { name: 'xpath_int()', returnType: 'INT', signature: 'xpath_int(STRING xml, STRING xpath)', description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.' },
      { name: 'xpath_long()', returnType: 'INT', signature: 'xpath_long(STRING xml, STRING xpath)', description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.' },
      { name: 'xpath_number()', returnType: 'DOUBLE', signature: 'xpath_number(STRING xml, STRING xpath)', description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.' },
      { name: 'xpath_short()', returnType: 'INT', signature: 'xpath_short(STRING xml, STRING xpath)', description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.' },
      { name: 'xpath_string()', returnType: 'STRING', signature: 'xpath_string(STRING xml, STRING xpath)', description: 'The xpath family of UDFs are wrappers around the Java XPath library javax.xml.xpath provided by the JDK. The library is based on the XPath 1.0 specification.' }
    ],
    impala: [
      { name: 'current_database()', returnType: 'STRING', signature: 'current_database()', description: 'Returns the database that the session is currently using, either default if no database has been selected, or whatever database the session switched to through a USE statement or the impalad -d option' },
      { name: 'pid()', returnType: 'INT', signature: 'pid()', description: 'Returns the process ID of the impalad daemon that the session is connected to. You can use it during low-level debugging, to issue Linux commands that trace, show the arguments, and so on the impalad process.' },
      { name: 'user()', returnType: 'STRING', signature: 'user()', description: 'Returns the username of the Linux user who is connected to the impalad daemon. Typically called a single time, in a query without any FROM clause, to understand how authorization settings apply in a security context; once you know the logged-in user name, you can check which groups that user belongs to, and from the list of groups you can check which roles are available to those groups through the authorization policy file. In Impala 2.0 and later, user() returns the the full Kerberos principal string, such as user@example.com, in a Kerberized environment.' },
      { name: 'version()', returnType: 'STRING', signature: 'version()', description: 'Returns information such as the precise version number and build date for the impalad daemon that you are currently connected to. Typically used to confirm that you are connected to the expected level of Impala to use a particular feature, or to connect to several nodes and confirm they are all running the same level of impalad.' }
    ]
  };

  var createDocHtml = function (funcDesc) {
    var html = '<div style="max-width: 600px; white-space: normal; overflow-y: auto; height: 100%; padding: 8px;"><p><span style="white-space: pre; font-family: monospace;">' + funcDesc.signature + '</span></p>';
    if (funcDesc.description) {
      html += '<p>' + funcDesc.description + '</p>';
    }
    html += '<div>';
    return html;
  };

  var addFunctions = function (functionIndex, dialect, completions) {
    if (typeof functionIndex.shared !== 'undefined') {
      functionIndex.shared.forEach(function (func) {
        completions.push({ value: func.name, meta: func.returnType, type: 'function', docHTML: createDocHtml(func) })
      })
    }
    if (typeof functionIndex[dialect] !== 'undefined') {
      functionIndex[dialect].forEach(function (func) {
        completions.push({ value: func.name, meta: func.returnType, type: 'function', docHTML: createDocHtml(func) })
      })
    }
  };

  /**
   * @param {Object} options
   * @param {Snippet} options.snippet
   * @param {Number} options.timeout
   * @constructor
   */
  function SqlAutocompleter2(options) {
    var self = this;
    self.snippet = options.snippet;
    self.timeout = options.timeout;
  }

  SqlAutocompleter2.prototype.autocomplete = function(beforeCursor, afterCursor, callback, editor) {
    var self = this;
    var parseResult = sqlParser.parseSql(beforeCursor, afterCursor, self.snippet.type());

    var completions = [];

    if (parseResult.suggestKeywords) {
      parseResult.suggestKeywords.forEach(function (keyword) {
        completions.push({ value: parseResult.lowerCase ? keyword.toLowerCase() : keyword, meta: 'keyword', type: 'keyword' });
      });
    }

    if (parseResult.suggestIdentifiers) {
      parseResult.suggestIdentifiers.forEach(function (identifier) {
        completions.push({ value: identifier.name, meta: identifier.type, type: 'identifier' });
      });
    }
    
    if (parseResult.suggestFunctions) {
      addFunctions(COLLECTION_FUNCTIONS, self.snippet.type(), completions);
      addFunctions(COMPLEX_TYPE_CONSTRUCTS, self.snippet.type(), completions);
      addFunctions(CONDITIONAL_FUNCTIONS, self.snippet.type(), completions);
      addFunctions(DATE_FUNCTIONS, self.snippet.type(), completions);
      addFunctions(MATHEMATICAL_FUNCTIONS, self.snippet.type(), completions);
      addFunctions(TYPE_CONVERSION_FUNCTIONS, self.snippet.type(), completions);
      addFunctions(STRING_FUNCTIONS, self.snippet.type(), completions);
      addFunctions(MISC_FUNCTIONS, self.snippet.type(), completions);
      addFunctions(TABLE_GENERATING_FUNCTIONS, self.snippet.type(), completions);
    }

    if (parseResult.suggestAggregateFunctions) {
      addFunctions(AGGREGATE_FUNCTIONS, self.snippet.type(), completions);
    }

    if (parseResult.suggestDatabases || parseResult.suggestHdfs || parseResult.suggestTables || parseResult.suggestColumns || parseResult.suggestValues) {
      var database = parseResult.useDatabase || self.snippet.database();

      var deferrals = [];

      if (parseResult.suggestDatabases) {
        var prefix = parseResult.suggestDatabases.prependQuestionMark ? '? ' : '';
        if (parseResult.suggestDatabases.prependFrom) {
          prefix += parseResult.lowerCase ? 'from ' : 'FROM ';
        }

        var databaseDeferred = $.Deferred();
        deferrals.push(databaseDeferred);

        self.snippet.getApiHelper().loadDatabases({
          sourceType: self.snippet.type(),
          successCallback: function (data) {
            data.forEach(function (db) {
              completions.push({ value: prefix + db + (parseResult.suggestDatabases.appendDot ? '.' : ''), meta: 'database', type: 'database' });
            });
            databaseDeferred.resolve();

          },
          silenceErrors: true,
          errorCallback: databaseDeferred.resolve
        })

      }

      if (parseResult.suggestHdfs) {
        var parts = parseResult.suggestHdfs.path.split('/');
        // Drop the first " or '
        parts.shift();
        // Last one is either partial name or empty
        parts.pop();

        var hdfsDeferred = $.Deferred();
        deferrals.push(hdfsDeferred);

        self.snippet.getApiHelper().fetchHdfsPath({
          pathParts: parts,
          successCallback: function (data) {
            if (!data.error) {
              data.files.forEach(function (file) {
                if (file.name !== '..' && file.name !== '.') {
                  completions.push({ value: parseResult.suggestHdfs.path === '' ? '/' + file.name : file.name, meta: file.type, type: 'HDFS' });
                }
              });
            }
            hdfsDeferred.resolve();
          },
          silenceErrors: true,
          errorCallback: hdfsDeferred.resolve,
          editor: editor,
          timeout: self.timeout
        });
      }

      if (parseResult.suggestTables) {
        var prefix = parseResult.suggestTables.prependQuestionMark ? '? ' : '';
        if (parseResult.suggestTables.prependFrom) {
          prefix += parseResult.lowerCase ? 'from ' : 'FROM ';
        }

        var tableDeferred = $.Deferred();
        deferrals.push(tableDeferred);
        self.snippet.getApiHelper().fetchTables({
          sourceType: self.snippet.type(),
          databaseName: database,
          successCallback: function (data) {
            data.tables_meta.forEach(function (tablesMeta) {
              completions.push({ value: prefix + tablesMeta.name, meta: tablesMeta.type.toLowerCase(), type: 'table' })
            });
            tableDeferred.resolve();
          },
          silenceErrors: true,
          errorCallback: tableDeferred.resolve,
          editor: editor,
          timeout: self.timeout
        });
      }

      if (parseResult.suggestColumns) {
        var columnsDeferred = $.Deferred();
        deferrals.push(columnsDeferred);

        var fields = [];
        if (parseResult.suggestColumns.identifierChain) {
          parseResult.suggestColumns.identifierChain.forEach(function (identifier) {
            var field = identifier.name;
            if (identifier.key) {
              field += '[' + identifier.key + ']';
            }
            fields.push(field);
          });
        }

        self.snippet.getApiHelper().fetchFields({
          sourceType: self.snippet.type(),
          databaseName: parseResult.suggestColumns.database || database,
          tableName: parseResult.suggestColumns.table,
          fields: fields,
          editor: editor,
          timeout: self.timeout,
          successCallback: function (data) {
            if (data.extended_columns) {
              data.extended_columns.forEach(function (column) {
                if (column.type.indexOf('map') === 0 && self.snippet.type() === 'hive') {
                  completions.push({value: column.name + '[]', meta: 'map', type: 'column' })
                } else if (column.type.indexOf('map') === 0) {
                  completions.push({value: column.name, meta: 'map', type: 'column' })
                } else if (column.type.indexOf('struct') === 0) {
                  completions.push({ value: column.name, meta: 'struct' , type: 'column' })
                } else if (column.type.indexOf('array') === 0 && self.snippet.type() === 'hive') {
                  completions.push({ value: column.name + '[]', meta: 'array', type: 'column' })
                } else if (column.type.indexOf('array') === 0) {
                  completions.push({ value: column.name, meta: 'array', type: 'column' })
                } else {
                  completions.push({ value: column.name, meta: column.type, type: 'column' })
                }
              });
            } else if (data.columns) {
              data.columns.forEach(function (column) {
                completions.push({ value: column, meta: 'column', type: 'column' })
              });
            }
            if (data.type === 'map' && self.snippet.type() === 'impala') {
              completions.push({ value: 'key', meta: 'key', type: 'column' });
              completions.push({ value: 'value', meta: 'value', type: 'column' });
            }
            if (data.type === 'struct') {
              data.fields.forEach(function (field) {
                completions.push({ value: field.name, meta: 'struct', type: 'column' })
              });
            } else if (data.type === 'map' && (data.value && data.value.fields)) {
              data.value.fields.forEach(function (field) {
                completions.push({ value: field.name, meta: field.type, type: 'column' });
              });
            } else if (data.type === 'array' && (data.item && data.item.fields)) {
              data.item.fields.forEach(function (field) {
                if ((field.type === 'array' || field.type === 'map') && self.snippet.type() === 'hive') {
                  completions.push({ value: field.name + '[]', meta: field.type, type: 'column' });
                } else {
                  completions.push({ value: field.name, meta: field.type, type: 'column' });
                }
              });
            }
            columnsDeferred.resolve();
          },
          silenceErrors: true,
          errorCallback: columnsDeferred.resolve
        });
      }

      if (parseResult.suggestValues) {
        if (self.snippet.type() === 'impala') {
          var impalaValuesDeferred = $.Deferred();
          deferrals.push(impalaValuesDeferred);
          // TODO: Fetch for each identifier in the chain, we need to add key or value for impala
          //       select a.key from customers c, c.addresses a WHERE a.zip_code = |
          // Same goes for Hive
          //       SELECT orders[].items[].| FROM customers
          self.snippet.getApiHelper().fetchFields({
            sourceType: self.snippet.type(),
            databaseName: parseResult.suggestValues.database || database,
            tableName: parseResult.suggestValues.table,
            fields: $.map(parseResult.suggestValues.identifierChain, function (value) { return value.name }),
            editor: editor,
            timeout: self.timeout,
            successCallback: function (data) {
              if (data.sample) {
                var isString = data.type === "string";
                data.sample.forEach(function (sample) {
                  completions.push({ meta: 'value', value: isString ? "'" + sample + "'" : new String(sample) })
                });
              }
              impalaValuesDeferred.resolve();
            },
            silenceErrors: true,
            errorCallback: impalaValuesDeferred.resolve
          });
        } else {
          var valuesDeferred = $.Deferred();
          deferrals.push(valuesDeferred);
          self.snippet.getApiHelper().fetchTableSample({
            sourceType: self.snippet.type(),
            databaseName: parseResult.suggestValues.database || database,
            tableName: parseResult.suggestValues.table,
            columnName: parseResult.suggestValues.identifierChain[0].name,
            editor: editor,
            timeout: self.timeout,
            successCallback: function (data) {
              if (data.status === 0 && data.headers.length === 1) {
                data.rows.forEach(function (row) {
                  completions.push({ value: typeof row[0] === 'string' ? "'" + row[0] + "'" :  '' + row[0], meta: 'sample', type: 'sample' });
                });
              }
              valuesDeferred.resolve();
            },
            silenceErrors: true,
            errorCallback: valuesDeferred.resolve
          });
        }
      }

      $.when.apply($, deferrals).done(function () {
        self.finalizeCompletions(completions, callback, editor);
      });
    } else {
      self.finalizeCompletions(completions, callback, editor);
    }
  };

  SqlAutocompleter2.prototype.finalizeCompletions = function (completions, callback, editor) {
    var self = this;
    self.sortCompletions(completions);

    var currentScore = 1000;
    completions.forEach(function (completion) {
      completion.score = currentScore;
      currentScore--;
    });

    // TODO Figure out why SELECT | FROM customers LATERAL VIEW explode(a) AS (b, c)
    if (typeof editor !== 'undefined') {
      editor.hideSpinner();
    }
    callback(completions);
  };

  var typeOrder = { 'star': 1, 'column': 2, 'table': 3, 'database': 4, 'identifier': 5, 'keyword': 6, 'function': 8, 'sample' : 9 };

  SqlAutocompleter2.prototype.sortCompletions = function (completions) {
    completions.sort(function (a, b) {
      if (typeOrder[a.value == '*' ? 'star' : a.type] !== typeOrder[b.value == '*' ? 'star' : b.type]) {
        return typeOrder[a.value == '*' ? 'star' : a.type] - typeOrder[b.value == '*' ? 'star' : b.type];
      }
      return a.value.localeCompare(b.value);
    });
  };
  
  SqlAutocompleter2.prototype.getDocTooltip = function (item) {

  };

  return SqlAutocompleter2;
}));