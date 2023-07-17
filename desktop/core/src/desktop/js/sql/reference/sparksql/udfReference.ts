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

export const AGGREGATE_FUNCTIONS: UdfCategoryFunctions = {
  any: {
    name: 'any',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'any(expr)',
    draggable: 'any()',
    description: 'Returns true if at least one value of `expr` is true.'
  },
  approx_count_distinct: {
    name: 'approx_count_distinct',
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'approx_count_distinct(expr[, relativeSD])',
    draggable: 'approx_count_distinct()',
    description:
      'Returns the estimated cardinality by HyperLogLog++. `relativeSD` defines the maximum estimation error allowed.'
  },
  approx_percentile: {
    name: 'approx_percentile',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'approx_percentile(col, percentage [, accuracy])',
    draggable: 'approx_percentile()',
    description:
      'Returns the approximate percentile value of numeric column `col` at the given percentage. The value of percentage must be between 0.0 and 1.0. The `accuracy` parameter (default: 10000) is a positive numeric literal which controls approximation accuracy at the cost of memory. Higher value of `accuracy` yields better accuracy, `1.0/accuracy` is the relative error of the approximation. When `percentage` is an array, each value of the percentage array must be between 0.0 and 1.0. In this case, returns the approximate percentile array of column `col` at the given percentage array.'
  },
  array_agg: {
    name: 'array_agg',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'array_agg(expr)',
    draggable: 'array_agg()',
    description: 'Collects and returns a list of non-unique elements.'
  },
  avg: {
    name: 'avg',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'avg(expr)',
    draggable: 'avg()',
    description: 'Returns the mean calculated from values of a group.'
  },
  bit_and: {
    name: 'bit_and',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'bit_and(expr)',
    draggable: 'bit_and()',
    description: 'Returns the bitwise AND of all non-null input values, or null if none.'
  },
  bit_or: {
    name: 'bit_or',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'bit_or(expr)',
    draggable: 'bit_or()',
    description: 'Returns the bitwise OR of all non-null input values, or null if none.'
  },
  bit_xor: {
    name: 'bit_xor',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'bit_xor(expr)',
    draggable: 'bit_xor()',
    description: 'Returns the bitwise XOR of all non-null input values, or null if none.'
  },
  bool_and: {
    name: 'bool_and',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'T' }]],
    signature: 'bool_and(expr)',
    draggable: 'bool_and()',
    description: 'Returns true if all values of `expr` are true.'
  },
  bool_or: {
    name: 'bool_or',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'T' }]],
    signature: 'bool_or(expr)',
    draggable: 'bool_or()',
    description: 'Returns true if at least one value of `expr` is true.'
  },
  collect_list: {
    name: 'collect_list',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'collect_list(expr)',
    draggable: 'collect_list()',
    description: 'Collects and returns a list of non-unique elements.'
  },
  collect_set: {
    name: 'collect_set',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'collect_set(expr)',
    draggable: 'collect_set()',
    description: 'Collects and returns a set of unique elements.'
  },
  corr: {
    name: 'corr',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'corr(expr1, expr2)',
    draggable: 'corr()',
    description: 'Returns Pearson coefficient of correlation between a set of number pairs.'
  },
  count: {
    name: 'count',
    returnTypes: ['NUMBER'],
    arguments: [
      [
        { type: 'T', keywords: ['DISTINCT', '*'] },
        { type: 'T', optional: true, multiple: true }
      ]
    ],
    signature: 'count([DISTINCT]*|expr[, expr...])',
    draggable: 'count()',
    description:
      '* - Returns the total number of retrieved rows, including rows containing null.\n\nexpr[, expr] - Returns the number of rows for which the supplied expression(s) are all non-null.'
  },
  count_if: {
    name: 'count_if',
    returnTypes: ['NUMBER'],
    arguments: [[{ type: 'T' }]],
    signature: 'count_if(expr)',
    draggable: 'count_if()',
    description: 'Returns the number of `TRUE` values for the expression.'
  },
  count_min_sketch: {
    name: 'count_min_sketch',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'count_min_sketch(col, eps, confidence, seed)',
    draggable: 'count_min_sketch()',
    description:
      'Returns a count-min sketch of a column with the given esp, confidence and seed. The result is an array of bytes, which can be deserialized to a `CountMinSketch` before usage. Count-min sketch is a probabilistic data structure used for cardinality estimation using sub-linear space.'
  },
  covar_pop: {
    name: 'covar_pop',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'covar_pop(expr1, expr2)',
    draggable: 'covar_pop()',
    description: 'Returns the population covariance of a set of number pairs.'
  },
  covar_samp: {
    name: 'covar_samp',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'covar_samp(expr1, expr2)',
    draggable: 'covar_samp()',
    description: 'Returns the sample covariance of a set of number pairs.'
  },
  every: {
    name: 'every',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'T' }]],
    signature: 'every(expr)',
    draggable: 'every()',
    description: 'Returns true if all values of `expr` are true.'
  },
  first: {
    name: 'first',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'first(expr[, isIgnoreNull])',
    draggable: 'first()',
    description:
      'Returns the first value of `expr` for a group of rows. If `isIgnoreNull` is true, returns only non-null values.'
  },
  first_value: {
    name: 'first_value',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'first_value(expr[, isIgnoreNull])',
    draggable: 'first_value()',
    description:
      'Returns the first value of `expr` for a group of rows. If `isIgnoreNull` is true, returns only non-null values.'
  },
  grouping: {
    name: 'grouping',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'grouping(col)',
    draggable: 'grouping()',
    description:
      'Indicates whether a specified column in a GROUP BY is aggregated or not, returns 1 for aggregated or 0 for not aggregated in the result set.",'
  },
  grouping_id: {
    name: 'grouping_id',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', optional: true, multiple: true }]],
    signature: 'grouping_id([col1[, col2 ..]])',
    draggable: 'grouping_id()',
    description:
      'returns the level of grouping, equals to (grouping(c1) << (n-1)) + (grouping(c2) << (n-2)) + ... + grouping(cn)'
  },
  histogram_numeric: {
    name: 'histogram_numeric',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'histogram_numeric(expr, nb)',
    draggable: 'histogram_numeric()',
    description:
      "Computes a histogram on numeric 'expr' using nb bins. The return value is an array of (x,y) pairs representing the centers of the histogram's bins. As the value of 'nb' is increased, the histogram approximation gets finer-grained, but may yield artifacts around outliers. In practice, 20-40 histogram bins appear to work well, with more bins being required for skewed or smaller datasets. Note that this function creates a histogram with non-uniform bin widths. It offers no guarantees in terms of the mean-squared-error of the histogram, but in practice is comparable to the histograms produced by the R/S-Plus statistical computing packages. Note: the output type of the 'x' field in the return value is propagated from the input value consumed in the aggregate function."
  },
  kurtosis: {
    name: 'kurtosis',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'kurtosis(expr)',
    draggable: 'kurtosis()',
    description: 'Returns the kurtosis value calculated from values of a group.'
  },
  last: {
    name: 'last',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'last(expr[, isIgnoreNull])',
    draggable: 'last()',
    description:
      'Returns the last value of `expr` for a group of rows. If `isIgnoreNull` is true, returns only non-null values'
  },
  last_value: {
    name: 'last_value',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'last_value(expr[, isIgnoreNull])',
    draggable: 'last_value()',
    description:
      'Returns the last value of `expr` for a group of rows. If `isIgnoreNull` is true, returns only non-null values'
  },
  max: {
    name: 'max',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'max(expr)',
    draggable: 'max()',
    description: 'Returns the maximum value of `expr`.'
  },
  max_by: {
    name: 'max_by',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'max_by(x, y)',
    draggable: 'max_by()',
    description: 'Returns the value of `x` associated with the maximum value of `y`.'
  },
  mean: {
    name: 'mean',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'mean(expr)',
    draggable: 'mean()',
    description: 'Returns the mean calculated from values of a group.'
  },
  min: {
    name: 'min',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'min(expr)',
    draggable: 'min()',
    description: 'Returns the minimum value of `expr`.'
  },
  min_by: {
    name: 'min_by',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'min_by(x, y)',
    draggable: 'min_by()',
    description: 'Returns the value of `x` associated with the minimum value of `y`.'
  },
  percentile: {
    name: 'percentile',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'percentile(col, percentage [, frequency])',
    draggable: 'percentile()',
    description:
      'Returns the exact percentile value of numeric column `col` at the given percentage. The value of percentage must be between 0.0 and 1.0. The value of frequency should be positive integral'
  },
  percentile_approx: {
    name: 'percentile_approx',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'percentile_approx(col, percentage [, accuracy])',
    draggable: 'percentile_approx()',
    description:
      'Returns the approximate percentile value of numeric column `col` at the given percentage. The value of percentage must be between 0.0 and 1.0. The `accuracy` parameter (default: 10000) is a positive numeric literal which controls approximation accuracy at the cost of memory. Higher value of `accuracy` yields better accuracy, `1.0/accuracy` is the relative error of the approximation. When `percentage` is an array, each value of the percentage array must be between 0.0 and 1.0. In this case, returns the approximate percentile array of column `col` at the given percentage array.'
  },
  regr_avgx: {
    name: 'regr_avgx',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'regr_avgx(y, x)',
    draggable: 'regr_avgx()',
    description:
      'Returns the average of the independent variable for non-null pairs in a group, where y is the dependent variable and x is the independent variable.'
  },
  regr_avgy: {
    name: 'regr_avgy',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'regr_avgy(y, x)',
    draggable: 'regr_avgy()',
    description:
      'Returns the average of the dependent variable for non-null pairs in a group, where y is the dependent variable and x is the independent variable.'
  },
  regr_count: {
    name: 'regr_count',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'regr_count(y, x)',
    draggable: 'regr_count()',
    description:
      'Returns the number of non-null number pairs in a group, where y is the dependent variable and x is the independent variable.'
  },
  regr_r2: {
    name: 'regr_r2',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'regr_r2(y, x)',
    draggable: 'regr_r2()',
    description:
      'Returns the coefficient of determination for non-null pairs in a group, where y is the dependent variable and x is the independent variable.'
  },
  skewness: {
    name: 'skewness',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'skewness(expr)',
    draggable: 'skewness()',
    description: 'Returns the skewness value calculated from values of a group.'
  },
  some: {
    name: 'some',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'some(expr)',
    draggable: 'some()',
    description: 'Returns true if at least one value of `expr` is true.'
  },
  std: {
    name: 'std',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'std(expr)',
    draggable: 'std()',
    description: 'Returns the sample standard deviation calculated from values of a group.'
  },
  stddev: {
    name: 'stddev',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'stddev(expr)',
    draggable: 'stddev()',
    description: 'Returns the sample standard deviation calculated from values of a group.'
  },
  stddev_pop: {
    name: 'stddev_pop',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'stddev_pop(expr)',
    draggable: 'stddev_pop()',
    description: 'Returns the population standard deviation calculated from values of a group.'
  },
  stddev_samp: {
    name: 'stddev_samp',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'stddev_samp(expr)',
    draggable: 'stddev_samp()',
    description: 'Returns the sample standard deviation calculated from values of a group.'
  },
  sum: {
    name: 'sum',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'sum(expr)',
    draggable: 'sum()',
    description: 'Returns the sum calculated from values of a group.'
  },
  try_avg: {
    name: 'try_avg',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'try_avg(expr)',
    draggable: 'try_avg()',
    description:
      'Returns the mean calculated from values of a group and the result is null on overflow.'
  },
  try_sum: {
    name: 'sum',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'try_sum(expr)',
    draggable: 'try_sum()',
    description:
      'Returns the sum calculated from values of a group and the result is null on overflow.'
  },
  var_pop: {
    name: 'var_pop',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'var_pop(expr)',
    draggable: 'var_pop()',
    description: 'Returns the population variance calculated from values of a group.'
  },
  var_samp: {
    name: 'var_samp',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'var_samp(expr)',
    draggable: 'var_samp()',
    description: 'Returns the sample variance calculated from values of a group.'
  },
  variance: {
    name: 'variance',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'variance(expr)',
    draggable: 'variance()',
    description: 'Returns the sample variance calculated from values of a group.'
  }
};

export const ARRAY_FUNCTIONS: UdfCategoryFunctions = {
  aggregate: {
    name: 'aggregate',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'aggregate(expr, start, merge, finish)',
    draggable: 'aggregate()',
    description:
      'Applies a binary operator to an initial state and all elements in the array, and reduces this to a single state. The final state is converted into the final result by applying a finish function.'
  },
  array: {
    name: 'array',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'array(expr, ...)',
    draggable: 'array()',
    description: 'Returns an array with the given elements.'
  },
  array_contains: {
    name: 'array_contains',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'array_contains(array, value)',
    draggable: 'array_contains()',
    description: 'Returns true if the array contains the value.'
  },
  array_distinct: {
    name: 'array_distinct',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'array_distinct(array)',
    draggable: 'array_distinct()',
    description: 'Removes duplicate values from the array.'
  },
  array_except: {
    name: 'array_except',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'array_except(array1, array2)',
    draggable: 'array_except()',
    description: 'Returns an array of the elements in array1 but not in array2, without duplicates.'
  },
  array_intersect: {
    name: 'array_intersect',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'array_intersect(array1, array2)',
    draggable: 'array_intersect()',
    description:
      'Returns an array of the elements in the intersection of array1 and array2, without duplicates.'
  },
  array_join: {
    name: 'array_join',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'array_join(array, delimiter[, nullReplacement])',
    draggable: 'array_join()',
    description:
      'Concatenates the elements of the given array using the delimiter and an optional string to replace nulls. If no value is set for nullReplacement, any null value is filtered.'
  },
  array_max: {
    name: 'array_max',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'array_max(array)',
    draggable: 'array_max()',
    description: 'Returns the maximum value in the array. NULL elements are skipped.'
  },
  array_min: {
    name: 'array_min',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'array_min(array)',
    draggable: 'array_min()',
    description: 'Returns the minimum value in the array. NULL elements are skipped.'
  },
  array_position: {
    name: 'array_position',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'array_position(array, element)',
    draggable: 'array_position()',
    description: 'Returns the (1-based) index of the first element of the array as long.'
  },
  array_remove: {
    name: 'array_remove',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'array_remove(array, element)',
    draggable: 'array_remove()',
    description: 'Remove all elements that equal to element from array.'
  },
  array_repeat: {
    name: 'array_repeat',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'array_repeat(element, count)',
    draggable: 'array_repeat()',
    description: 'Returns the array containing element count times.'
  },
  array_size: {
    name: 'array_size',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'array_size(expr)',
    draggable: 'array_size()',
    description: 'Returns the size of an array. The function returns null for null input.'
  },
  array_sort: {
    name: 'array_sort',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'array_sort(expr, ...)',
    draggable: 'array_sort()',
    description:
      'Sorts the input array. If func is omitted, sort in ascending order. The elements of the input array must be orderable. Null elements will be placed at the end of the returned array. Since 3.0.0 this function also sorts and returns the array based on the given comparator function. The comparator will take two arguments representing two elements of the array. It returns -1, 0, or 1 as the first element is less than, equal to, or greater than the second element. If the comparator function returns other values (including null), the function will fail and raise an error.'
  },
  array_union: {
    name: 'array_union',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'array_union(array1, array2)',
    draggable: 'array_union()',
    description:
      'Returns an array of the elements in the union of array1 and array2, without duplicates.'
  },
  arrays_overlap: {
    name: 'arrays_overlap',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'arrays_overlap(a1, a2)',
    draggable: 'arrays_overlap()',
    description:
      'Returns true if a1 contains at least a non-null element present also in a2. If the arrays have no common element and they are both non-empty and either of them contains a null element null is returned, false otherwise.'
  },
  arrays_zip: {
    name: 'arrays_zip',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'arrays_zip(a1, a2, ...))',
    draggable: 'arrays_zip()',
    description:
      'Returns a merged array of structs in which the N-th struct contains all N-th values of input arrays.'
  },
  concat: {
    name: 'concat',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'concat(col1, col2, ..., colN)',
    draggable: 'concat()',
    description: 'Returns the concatenation of col1, col2, ..., colN.'
  },
  element_at: {
    name: 'element_at',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'element_at(arrayOrMap, index)',
    draggable: 'element_at()',
    description:
      'Returns element of array at given (1-based) index. If index < 0, accesses elements from the last to the first. Returns NULL if the index exceeds the length of the array.'
  },
  filter: {
    name: 'filter',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'filter(expr, func)',
    draggable: 'filter()',
    description: 'Filters the input array using the given predicate.'
  },
  flatten: {
    name: 'flatten',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'flatten(arrayOfArrays)',
    draggable: 'flatten()',
    description: 'Transforms an array of arrays into a single array.'
  },
  reverse: {
    name: 'reverse',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'reverse(array)',
    draggable: 'reverse()',
    description: 'Returns a reversed string or an array with reverse order of elements.'
  },
  sequence: {
    name: 'sequence',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'sequence(start, stop, step)',
    draggable: 'sequence()',
    description:
      "Generates an array of elements from start to stop (inclusive), incrementing by step. The type of the returned elements is the same as the type of argument expressions. Supported types are: byte, short, integer, long, date, timestamp. The start and stop expressions must resolve to the same type. If start and stop expressions resolve to the 'date' or 'timestamp' type then the step expression must resolve to the 'interval' type, otherwise to the same type as the start and stop expressions."
  },
  shuffle: {
    name: 'shuffle',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'shuffle(array)',
    draggable: 'shuffle()',
    description: 'Returns a random permutation of the given array.'
  },
  slice: {
    name: 'slice',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'slice(x, start, length)',
    draggable: 'slice()',
    description:
      'Subsets array x starting from index start (array indices start at 1, or starting from the end if start is negative) with the specified length.'
  },
  sort_array: {
    name: 'sort_array',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'sort_array(array[, ascendingOrder])',
    draggable: 'sort_array()',
    description:
      'Sorts the input array in ascending or descending order according to the natural ordering of the array elements. Null elements will be placed at the beginning of the returned array in ascending order or at the end of the returned array in descending order.'
  },
  try_element_at: {
    name: 'try_element_at',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'try_element_at(arrayOrMap, index)',
    draggable: 'try_element_at()',
    description:
      'Returns element of array at given (1-based) index. If Index is 0, Spark will throw an error. If index < 0, accesses elements from the last to the first. The function always returns NULL if the index exceeds the length of the array.\n\nFor maps it returns value for given key. The function always returns NULL if the key is not contained in the map.'
  },
  zip_with: {
    name: 'zip_with',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'zip_with(left, right, func)',
    draggable: 'zip_with()',
    description:
      'Merges the two given arrays, element-wise, into a single array using function. If one array is shorter, nulls are appended at the end to match the length of the longer array, before applying function.'
  }
};

export const BITWISE_FUNCTIONS: UdfCategoryFunctions = {
  bit_count: {
    name: 'bit_count',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'bit_count(expr)',
    draggable: 'bit_count()',
    description:
      'Returns the number of bits that are set in the argument expr as an unsigned 64-bit integer, or NULL if the argument is NULL.'
  },
  bit_get: {
    name: 'bit_get',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'bit_get(expr, pos)',
    draggable: 'bit_get()',
    description:
      'Returns the value of the bit (0 or 1) at the specified position. The positions are numbered from right to left, starting at zero. The position argument cannot be negative.'
  },
  getbit: {
    name: 'getbit',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'getbit(expr, pos)',
    draggable: 'getbit()',
    description:
      'Returns the value of the bit (0 or 1) at the specified position. The positions are numbered from right to left, starting at zero. The position argument cannot be negative.'
  },
  shiftleft: {
    name: 'shiftleft',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'shiftleft(base, expr)',
    draggable: 'shiftleft()',
    description: 'Bitwise left shift.'
  },
  shiftright: {
    name: 'shiftright',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'shiftright(base, expr)',
    draggable: 'shiftright()',
    description: 'Bitwise (signed) right shift.'
  },
  shiftrightunsigned: {
    name: 'shiftrightunsigned',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'shiftrightunsigned(base, expr)',
    draggable: 'shiftrightunsigned()',
    description: 'Bitwise unsigned right shift.'
  }
};

export const CONDITIONAL_FUNCTIONS: UdfCategoryFunctions = {
  coalesce: {
    name: 'coalesce',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'coalesce(expr1, expr2, ...)',
    draggable: 'coalesce()',
    description: 'Returns the first non-null argument if exists. Otherwise, null.'
  },
  if: {
    name: 'if',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'if(expr1, expr2, expr3)',
    draggable: 'if()',
    description: 'If expr1 evaluates to true, then returns expr2; otherwise returns expr3.'
  },
  ifnull: {
    name: 'ifnull',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'ifnull(expr1, expr2)',
    draggable: 'ifnull()',
    description: 'Returns expr2 if expr1 is null, or expr1 otherwise.'
  },
  nanvl: {
    name: 'nanvl',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'nanvl(expr1, expr2)',
    draggable: 'nanvl()',
    description: "Returns expr1 if it's not NaN, or expr2 otherwise."
  },
  nullif: {
    name: 'nullif',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'nullif(expr1, expr2)',
    draggable: 'nullif()',
    description: 'Returns null if expr1 equals to expr2, or expr1 otherwise.'
  },
  nvl: {
    name: 'nvl',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'nvl(expr1, expr2)',
    draggable: 'nvl()',
    description: 'Returns expr2 if expr1 is null, or expr1 otherwise.'
  },
  nvl2: {
    name: 'nvl2',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'nvl2(expr1, expr2, expr3)',
    draggable: 'nvl2()',
    description: 'Returns expr2 if expr1 is not null, or expr3 otherwise.'
  }
};

export const CONVERSION_FUNCTIONS: UdfCategoryFunctions = {
  bigint: {
    name: 'bigint',
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'T' }]],
    signature: 'bigint(expr)',
    draggable: 'bigint()',
    description: 'Casts the value expr to the target data type bigint.'
  },
  binary: {
    name: 'binary',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'binary(expr)',
    draggable: 'binary()',
    description: 'Casts the value expr to the target data type binary.'
  },
  boolean: {
    name: 'boolean',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'T' }]],
    signature: 'boolean(expr)',
    draggable: 'boolean()',
    description: 'Casts the value expr to the target data type boolean.'
  },
  cast: {
    name: 'cast',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'cast(expr AS type)',
    draggable: 'cast()',
    description: 'Casts the value expr to the target data type type.'
  },
  date: {
    name: 'date',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'date(expr)',
    draggable: 'date()',
    description: 'Casts the value expr to the target data type date.'
  },
  decimal: {
    name: 'decimal',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'decimal(expr)',
    draggable: 'decimal()',
    description: 'Casts the value expr to the target data type decimal.'
  },
  double: {
    name: 'double',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'double(expr)',
    draggable: 'double()',
    description: 'Casts the value expr to the target data type double.'
  },
  float: {
    name: 'float',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'float(expr)',
    draggable: 'float()',
    description: 'Casts the value expr to the target data type float.'
  },
  int: {
    name: 'int',
    returnTypes: ['INT'],
    arguments: [[{ type: 'T' }]],
    signature: 'int(expr)',
    draggable: 'int()',
    description: 'Casts the value expr to the target data type int.'
  },
  smallint: {
    name: 'smallint',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'smallint(expr)',
    draggable: 'smallint()',
    description: 'Casts the value expr to the target data type smallint.'
  },
  string: {
    name: 'string',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'string(expr)',
    draggable: 'string()',
    description: 'Casts the value expr to the target data type string.'
  },
  timestamp: {
    name: 'timestamp',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'timestamp(expr)',
    draggable: 'timestamp()',
    description: 'Casts the value expr to the target data type timestamp.'
  },
  tinyint: {
    name: 'tinyint',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'tinyint(expr)',
    draggable: 'tinyint()',
    description: 'Casts the value expr to the target data type tinyint.'
  }
};

export const CSV_FUNCTIONS: UdfCategoryFunctions = {
  from_csv: {
    name: 'from_csv',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'from_csv(csvStr, schema[, options])',
    draggable: 'from_csv()',
    description: 'Returns a struct value with the given csvStr and schema.'
  },
  schema_of_csv: {
    name: 'schema_of_csv',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'schema_of_csv(csv[, options])',
    draggable: 'schema_of_csv()',
    description: 'Returns schema in the DDL format of CSV string.'
  },
  to_csv: {
    name: 'to_csv',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'to_csv(expr[, options])',
    draggable: 'to_csv()',
    description: 'Returns a CSV string with a given struct value.'
  }
};

export const DATE_AND_TIME_FUNCTIONS: UdfCategoryFunctions = {
  add_months: {
    name: 'add_months',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'add_months(start_date, num_months)',
    draggable: 'add_months()',
    description: 'Returns the date that is `num_months` after `start_date`.'
  },
  current_date: {
    name: 'current_date',
    returnTypes: ['T'],
    arguments: [],
    signature: 'current_date()',
    draggable: 'current_date()',
    description: 'Returns the current date at the start of query evaluation.'
  },
  current_timestamp: {
    name: 'current_timestamp',
    returnTypes: ['T'],
    arguments: [],
    signature: 'current_timestamp()',
    draggable: 'current_timestamp()',
    description: 'Returns the current timestamp at the start of query evaluation.'
  },
  current_timezone: {
    name: 'current_timezone',
    returnTypes: ['T'],
    arguments: [],
    signature: 'current_timestamp()',
    draggable: 'current_timezone()',
    description: 'Returns the current session local timezone.'
  },
  date_add: {
    name: 'date_add',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'date_add(start_date, num_days)',
    draggable: 'date_add()',
    description: 'Returns the date that is `num_days` after `start_date`.'
  },
  date_format: {
    name: 'date_format',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'date_format(timestamp, fmt)',
    draggable: 'date_format()',
    description:
      'Converts `timestamp` to a value of string in the format specified by the date format `fmt`.'
  },
  date_from_unix_date: {
    name: 'date_from_unix_date',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'date_from_unix_date(days)',
    draggable: 'date_from_unix_date()',
    description: 'Create date from the number of days since 1970-01-01.'
  },
  date_part: {
    name: 'date_part',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'date_part(field, source)',
    draggable: 'date_part()',
    description: 'Extracts a part of the date/timestamp or interval source.'
  },
  date_sub: {
    name: 'date_sub',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'date_sub(start_date, num_days)',
    draggable: 'date_sub()',
    description: 'Returns the date that is `num_days` before `start_date`.'
  },
  date_trunc: {
    name: 'date_trunc',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'date_trunc(fmt, ts)',
    draggable: 'date_trunc()',
    description: 'Returns timestamp `ts` truncated to the unit specified by the format model `fmt`.'
  },
  datediff: {
    name: 'datediff',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'datediff(endDate, startDate)',
    draggable: 'datediff()',
    description: 'Returns the number of days from `startDate` to `endDate`.'
  },
  day: {
    name: 'day',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'day(expr)',
    draggable: 'day()',
    description: 'Returns the day of month of the date/timestamp.'
  },
  dayofmonth: {
    name: 'dayofmonth',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'dayofmonth(date)',
    draggable: 'dayofmonth()',
    description: 'Returns the day of month of the date/timestamp.'
  },
  dayofweek: {
    name: 'dayofweek',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'dayofweek(date)',
    draggable: 'dayofweek()',
    description:
      'Returns the day of the week for date/timestamp (1 = Sunday, 2 = Monday, ..., 7 = Saturday).'
  },
  dayofyear: {
    name: 'dayofyear',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'dayofyear(date)',
    draggable: 'dayofyear()',
    description: 'Returns the day of year of the date/timestamp.'
  },
  extract: {
    name: 'extract',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'extract(field FROM source)',
    draggable: 'extract()',
    description:
      'Extracts a part of the date/timestamp or interval source.\n\nArguments:\n' +
      '\n' +
      'field - selects which part of the source should be extracted.\n' +
      '  Supported string values of field for dates and timestamps are(case insensitive):\n' +
      '    "YEAR", ("Y", "YEARS", "YR", "YRS") - the year field\n' +
      '    "YEAROFWEEK" - the ISO 8601 week-numbering year that the datetime falls in. For example, 2005-01-02 is part of the 53rd week of year 2004, so the result is 2004\n' +
      '    "QUARTER", ("QTR") - the quarter (1 - 4) of the year that the datetime falls in\n' +
      '    "MONTH", ("MON", "MONS", "MONTHS") - the month field (1 - 12)\n' +
      '    "WEEK", ("W", "WEEKS") - the number of the ISO 8601 week-of-week-based-year. A week is considered to start on a Monday and week 1 is the first week with >3 days. In the ISO week-numbering system, it is   possible for early-January dates to be part of the 52nd or 53rd week of the previous year, and for late-December dates to be part of the first week of the next year. For example, 2005-01-02 is part of   the 53rd week of year 2004, while 2012-12-31 is part of the first week of 2013\n' +
      '    "DAY", ("D", "DAYS") - the day of the month field (1 - 31)\n' +
      '    "DAYOFWEEK",("DOW") - the day of the week for datetime as Sunday(1) to Saturday(7)\n' +
      '    "DAYOFWEEK_ISO",("DOW_ISO") - ISO 8601 based day of the week for datetime as Monday(1) to Sunday(7)\n' +
      '    "DOY" - the day of the year (1 - 365/366)\n' +
      '    "HOUR", ("H", "HOURS", "HR", "HRS") - The hour field (0 - 23)\n' +
      '    "MINUTE", ("M", "MIN", "MINS", "MINUTES") - the minutes field (0 - 59)\n' +
      '    "SECOND", ("S", "SEC", "SECONDS", "SECS") - the seconds field, including fractional parts\n' +
      '  Supported string values of field for interval(which consists of months, days, microseconds) are(case insensitive):\n' +
      '    "YEAR", ("Y", "YEARS", "YR", "YRS") - the total months / 12\n' +
      '    "MONTH", ("MON", "MONS", "MONTHS") - the total months % 12\n' +
      '    "DAY", ("D", "DAYS") - the days part of interval\n' +
      '    "HOUR", ("H", "HOURS", "HR", "HRS") - how many hours the microseconds contains\n' +
      '    "MINUTE", ("M", "MIN", "MINS", "MINUTES") - how many minutes left after taking hours from microseconds\n' +
      '    "SECOND", ("S", "SEC", "SECONDS", "SECS") - how many second with fractions left after taking hours and minutes from microseconds\n' +
      'source - a date/timestamp or interval column from where field should be extracted'
  },
  from_unixtime: {
    name: 'from_unixtime',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'from_unixtime(unix_time, format)',
    draggable: 'from_unixtime()',
    description: 'Returns `unix_time` in the specified `format`.'
  },
  from_utc_timestamp: {
    name: 'from_utc_timestamp',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'from_utc_timestamp(timestamp, timezone)',
    draggable: 'from_utc_timestamp()',
    description:
      "Given a timestamp like '2017-07-14 02:40:00.0', interprets it as a time in UTC, and renders that time as a timestamp in the given time zone. For example, 'GMT+1' would yield '2017-07-14 03:40:00.0'."
  },
  hour: {
    name: 'hour',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'hour(timestamp)',
    draggable: 'hour()',
    description: 'Returns the hour component of the string/timestamp.'
  },
  last_day: {
    name: 'last_day',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'last_day(date)',
    draggable: 'last_day()',
    description: 'Returns the last day of the month which the date belongs to.'
  },
  make_date: {
    name: 'make_date',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'make_date(year, month, day)',
    draggable: 'make_date()',
    description:
      'Create date from year, month and day fields.\n' +
      '\n' +
      'Arguments:\n' +
      '\n' +
      'year - the year to represent, from 1 to 9999\n' +
      'month - the month-of-year to represent, from 1 (January) to 12 (December)\n' +
      'day - the day-of-month to represent, from 1 to 31'
  },
  make_dt_interval: {
    name: 'make_dt_interval',
    returnTypes: ['T'],
    arguments: [
      [{ type: 'T' }],
      [{ type: 'T', optional: true }],
      [{ type: 'T', optional: true }],
      [{ type: 'T', optional: true }]
    ],
    signature: 'make_dt_interval([days[, hours[, mins[, secs]]]])',
    draggable: 'make_dt_interval()',
    description:
      'Make DayTimeIntervalType duration from days, hours, mins and secs.\n' +
      '\n' +
      'Arguments:\n' +
      '\n' +
      'days - the number of days, positive or negative\n' +
      'hours - the number of hours, positive or negative\n' +
      'mins - the number of minutes, positive or negative\n' +
      'secs - the number of seconds with the fractional part in microsecond precision.'
  },
  make_interval: {
    name: 'make_interval',
    returnTypes: ['T'],
    arguments: [
      [{ type: 'T' }],
      [{ type: 'T' }],
      [{ type: 'T' }],
      [{ type: 'T' }],
      [{ type: 'T' }],
      [{ type: 'T' }],
      [{ type: 'T' }]
    ],
    signature: 'make_interval(years, months, weeks, days, hours, mins, secs)',
    draggable: 'make_interval()',
    description:
      'Make interval from years, months, weeks, days, hours, mins and secs.\n' +
      '\n' +
      'Arguments:\n' +
      '\n' +
      'years - the number of years, positive or negative\n' +
      'months - the number of months, positive or negative\n' +
      'weeks - the number of weeks, positive or negative\n' +
      'days - the number of days, positive or negative\n' +
      'hours - the number of hours, positive or negative\n' +
      'mins - the number of minutes, positive or negative\n' +
      'secs - the number of seconds with the fractional part in microsecond precision.'
  },
  make_timestamp: {
    name: 'make_timestamp',
    returnTypes: ['T'],
    arguments: [
      [{ type: 'T' }],
      [{ type: 'T' }],
      [{ type: 'T' }],
      [{ type: 'T' }],
      [{ type: 'T' }],
      [{ type: 'T' }],
      [{ type: 'T', optional: true }]
    ],
    signature: 'make_timestamp(year, month, day, hour, min, sec[, timezone])',
    draggable: 'make_timestamp()',
    description: 'Create timestamp from year, month, day, hour, min, sec and timezone fields.'
  },
  make_ym_interval: {
    name: 'make_ym_interval',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'make_ym_interval([years[, months]])',
    draggable: 'make_ym_interval()',
    description: 'Make year-month interval from years, months.'
  },
  minute: {
    name: 'minute',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'minute(timestamp)',
    draggable: 'minute()',
    description: 'Returns the minute component of the string/timestamp.'
  },
  month: {
    name: 'month',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'month(date)',
    draggable: 'month()',
    description: 'Returns the month component of the date/timestamp.'
  },
  months_between: {
    name: 'months_between',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'months_between(timestamp1, timestamp2[, roundOff])',
    draggable: 'months_between()',
    description:
      'If `timestamp1` is later than `timestamp2`, then the result is positive. If `timestamp1` and `timestamp2` are on the same day of month, or both are the last day of month, time of day will be ignored. Otherwise, the difference is calculated based on 31 days per month, and rounded to 8 digits unless roundOff=false.'
  },
  next_day: {
    name: 'next_day',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'next_day(start_date, day_of_week)',
    draggable: 'next_day()',
    description: 'Returns the first date which is later than `start_date` and named as indicated.'
  },
  now: {
    name: 'now',
    returnTypes: ['T'],
    arguments: [],
    signature: 'now()',
    draggable: 'now()',
    description: 'Returns the current timestamp at the start of query evaluation.'
  },
  quarter: {
    name: 'quarter',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'quarter(date)',
    draggable: 'quarter()',
    description: 'Returns the quarter of the year for date, in the range 1 to 4.'
  },
  second: {
    name: 'second',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'second(timestamp)',
    draggable: 'second()',
    description: 'Returns the second component of the string/timestamp.'
  },
  session_window: {
    name: 'session_window',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'session_window(time_column, gap_duration)',
    draggable: 'session_window()',
    description:
      "Generates session window given a timestamp specifying column and gap duration. See 'Types of time windows' in Structured Streaming guide doc for detailed explanation and examples."
  },
  timestamp_micros: {
    name: 'timestamp_micros',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'timestamp_micros(microseconds)',
    draggable: 'timestamp_micros()',
    description: 'Creates timestamp from the number of microseconds since UTC epoch.'
  },
  timestamp_millis: {
    name: 'timestamp_millis',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'timestamp_millis(milliseconds)',
    draggable: 'timestamp_millis()',
    description: 'Creates timestamp from the number of milliseconds since UTC epoch.'
  },
  timestamp_seconds: {
    name: 'timestamp_seconds',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'timestamp_seconds(seconds)',
    draggable: 'timestamp_seconds()',
    description: 'Creates timestamp from the number of seconds (can be fractional) since UTC epoch.'
  },
  to_date: {
    name: 'to_date',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'to_date(date_str[, fmt])',
    draggable: 'to_date()',
    description:
      'Parses the `date_str` expression with the `fmt` expression to a date. Returns null with invalid input. By default, it follows casting rules to a date if the `fmt` is omitted.'
  },
  to_timestamp: {
    name: 'to_timestamp',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'to_timestamp(timestamp_str[, fmt])',
    draggable: 'to_timestamp()',
    description:
      'Parses the `timestamp_str` expression with the `fmt` expression to a timestamp. Returns null with invalid input. By default, it follows casting rules to a timestamp if the `fmt` is omitted.'
  },
  to_unix_timestamp: {
    name: 'to_unix_timestamp',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'to_unix_timestamp(timeExp[, format])',
    draggable: 'to_unix_timestamp()',
    description: 'Returns the UNIX timestamp of the given time.'
  },
  to_utc_timestamp: {
    name: 'to_utc_timestamp',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'to_utc_timestamp(timestamp, timezone)',
    draggable: 'to_utc_timestamp()',
    description:
      "Given a timestamp like '2017-07-14 02:40:00.0', interprets it as a time in the given time zone, and renders that time as a timestamp in UTC. For example, 'GMT+1' would yield '2017-07-14 01:40:00.0'."
  },
  trunc: {
    name: 'trunc',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'trunc(date, fmt)',
    draggable: 'trunc()',
    description:
      'Returns `date` with the time portion of the day truncated to the unit specified by the format model `fmt`.'
  },
  unix_date: {
    name: 'unix_date',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'unix_date(date)',
    draggable: 'unix_date()',
    description: 'Returns the number of days since 1970-01-01.'
  },
  unix_micros: {
    name: 'unix_micros',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'unix_micros(timestamp)',
    draggable: 'unix_micros()',
    description: 'Returns the number of microseconds since 1970-01-01 00:00:00 UTC.'
  },
  unix_millis: {
    name: 'unix_millis',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'unix_millis(timestamp)',
    draggable: 'unix_millis()',
    description: 'Returns the number of microseconds since 1970-01-01 00:00:00 UTC.'
  },
  unix_seconds: {
    name: 'unix_seconds',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'unix_seconds(timestamp)',
    draggable: 'unix_seconds()',
    description:
      'Returns the number of seconds since 1970-01-01 00:00:00 UTC. Truncates higher levels of precision.'
  },
  unix_timestamp: {
    name: 'unix_timestamp',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', optional: true }], [{ type: 'T', optional: true }]],
    signature: 'unix_timestamp([timeExp[, format]])',
    draggable: 'unix_timestamp()',
    description:
      'Returns the number of milliseconds since 1970-01-01 00:00:00 UTC. Truncates higher levels of precision.'
  },
  weekday: {
    name: 'weekday',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'weekday(date)',
    draggable: 'weekday()',
    description:
      'Returns the day of the week for date/timestamp (0 = Monday, 1 = Tuesday, ..., 6 = Sunday).'
  },
  weekofyear: {
    name: 'weekofyear',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'weekofyear(date)',
    draggable: 'weekofyear()',
    description:
      'Returns the week of the year of the given date. A week is considered to start on a Monday and week 1 is the first week with >3 days.'
  },
  window: {
    name: 'window',
    returnTypes: ['T'],
    arguments: [
      [{ type: 'T' }],
      [{ type: 'T' }],
      [{ type: 'T', optional: true }],
      [{ type: 'T', optional: true }]
    ],
    signature: 'window(time_column, window_duration[, slide_duration[, start_time]])',
    draggable: 'window()',
    description:
      "Bucketize rows into one or more time windows given a timestamp specifying column. Window starts are inclusive but the window ends are exclusive, e.g. 12:05 will be in the window [12:05,12:10) but not in [12:00,12:05). Windows can support microsecond precision. Windows in the order of months are not supported. See 'Window Operations on Event Time' in Structured Streaming guide doc for detailed explanation and examples."
  },
  year: {
    name: 'year',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'year(date)',
    draggable: 'year()',
    description: 'Returns the year component of the date/timestamp.'
  }
};

export const GENERATOR_FUNCTIONS: UdfCategoryFunctions = {
  explode: {
    name: 'explode',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'explode(exprOrMap)',
    draggable: 'explode()',
    description:
      'Separates the elements of array expr into multiple rows, or the elements of map expr into multiple rows and columns. Unless specified otherwise, uses the default column name col for elements of the array or key and value for the elements of the map.'
  },
  explode_outer: {
    name: 'explode_outer',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'explode_outer(exprOrMap)',
    draggable: 'explode_outer()',
    description:
      'Separates the elements of array expr into multiple rows, or the elements of map expr into multiple rows and columns. Unless specified otherwise, uses the default column name col for elements of the array or key and value for the elements of the map.'
  },
  inline: {
    name: 'inline',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'inline(expr)',
    draggable: 'inline()',
    description:
      'Explodes an array of structs into a table. Uses column names col1, col2, etc. by default unless specified otherwise.'
  },
  inline_outer: {
    name: 'inline_outer',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'inline_outer(expr)',
    draggable: 'inline_outer()',
    description:
      'Explodes an array of structs into a table. Uses column names col1, col2, etc. by default unless specified otherwise.'
  },
  posexplode: {
    name: 'posexplode',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'posexplode(expr)',
    draggable: 'posexplode()',
    description:
      'Separates the elements of array expr into multiple rows with positions, or the elements of map expr into multiple rows and columns with positions. Unless specified otherwise, uses the column name pos for position, col for elements of the array or key and value for elements of the map.'
  },
  posexplode_outer: {
    name: 'posexplode_outer',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'posexplode_outer(expr)',
    draggable: 'posexplode_outer()',
    description:
      'Separates the elements of array expr into multiple rows with positions, or the elements of map expr into multiple rows and columns with positions. Unless specified otherwise, uses the column name pos for position, col for elements of the array or key and value for elements of the map.'
  },
  stack: {
    name: 'stack',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', multiple: true }]],
    signature: 'stack(n, expr1, ..., exprk)',
    draggable: 'stack()',
    description:
      'Separates expr1, ..., exprk into n rows. Uses column names col0, col1, etc. by default unless specified otherwise.'
  }
};

export const JSON_FUNCTIONS: UdfCategoryFunctions = {
  from_json: {
    name: 'from_json',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'from_json(jsonStr, schema[, options])',
    draggable: 'from_json()',
    description: 'Returns a struct value with the given `jsonStr` and `schema`.'
  },
  get_json_object: {
    name: 'get_json_object',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'get_json_object(json_txt, path)',
    draggable: 'get_json_object()',
    description: 'Extracts a json object from `path`.'
  },
  json_array_length: {
    name: 'json_array_length',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'json_array_length(jsonArray)',
    draggable: 'json_array_length()',
    description: 'Returns the number of elements in the outermost JSON array.'
  },
  json_object_keys: {
    name: 'json_object_keys',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'json_object_keys(jsonObject)',
    draggable: 'json_object_keys()',
    description: 'Returns all the keys of the outermost JSON object as an array.'
  },
  json_tuple: {
    name: 'json_tuple',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', multiple: true }]],
    signature: 'json_tuple(jsonStr, p1, p2, ..., pn)',
    draggable: 'json_tuple()',
    description:
      'Returns a tuple like the function get_json_object, but it takes multiple names. All the input parameters and output column types are string.'
  },
  schema_of_json: {
    name: 'schema_of_json',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'schema_of_json(json[, options])',
    draggable: 'schema_of_json()',
    description: 'Returns schema in the DDL format of JSON string.'
  },
  to_json: {
    name: 'to_json',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'to_json(expr[, options])',
    draggable: 'to_json()',
    description: 'Returns a JSON string with a given struct value'
  }
};

export const MAP_FUNCTIONS: UdfCategoryFunctions = {
  map: {
    name: 'map',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'map(key0, value0, key1, value1, ...)',
    draggable: 'map()',
    description: 'Creates a map with the given key/value pairs.'
  },
  map_concat: {
    name: 'map_concat',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'map_concat(map, ...)',
    draggable: 'map_concat()',
    description: 'Returns the union of all the given maps.'
  },
  map_contains_key: {
    name: 'map_contains_key',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'map_contains_key(map, key)',
    draggable: 'map_contains_key()',
    description: 'Returns true if the map contains the key.'
  },
  map_entries: {
    name: 'map_entries',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'map_entries(map)',
    draggable: 'map_entries()',
    description: 'Returns an unordered array of all entries in the given map.'
  },
  map_filter: {
    name: 'map_filter',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'map_filter(expr, func)',
    draggable: 'map_filter()',
    description: 'Filters entries in a map using the function.'
  },
  map_from_arrays: {
    name: 'map_from_arrays',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'map_from_arrays(keys, values)',
    draggable: 'map_from_arrays()',
    description:
      'Creates a map with a pair of the given key/value arrays. All elements in keys should not be null.'
  },
  map_from_entries: {
    name: 'map_from_entries',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'map_from_entries(arrayOfEntries)',
    draggable: 'map_from_entries()',
    description: 'Returns a map created from the given array of entries.'
  },
  map_keys: {
    name: 'map_keys',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'map_keys(map)',
    draggable: 'map_keys()',
    description: 'Returns an unordered array containing the keys of the map.'
  },
  map_values: {
    name: 'map_values',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'map_values(map)',
    draggable: 'map_values()',
    description: 'Returns an unordered array containing the values of the map.'
  },
  map_zip_with: {
    name: 'map_zip_with',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'map_zip_with(map1, map2, function)',
    draggable: 'map_zip_with()',
    description:
      'Merges two given maps into a single map by applying function to the pair of values with the same key. For keys only presented in one map, NULL will be passed as the value for the missing key. If an input map contains duplicated keys, only the first entry of the duplicated key is passed into the lambda function.'
  },
  str_to_map: {
    name: 'str_to_map',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }], [{ type: 'T', optional: true }]],
    signature: 'str_to_map(text[, pairDelim[, keyValueDelim]])',
    draggable: 'str_to_map()',
    description:
      "Creates a map after splitting the text into key/value pairs using delimiters. Default delimiters are ',' for pairDelim and ':' for keyValueDelim. Both pairDelim and keyValueDelim are treated as regular expressions."
  },
  transform_keys: {
    name: 'transform_keys',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'transform_keys(expr, func)',
    draggable: 'transform_keys()',
    description: 'Transforms keys in a map using the function.'
  },
  transform_values: {
    name: 'transform_values',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'transform_values(expr, func)',
    draggable: 'transform_values()',
    description: 'Transforms values in the map using the function.'
  }
};

export const MATHEMATICAL_FUNCTIONS: UdfCategoryFunctions = {
  abs: {
    name: 'abs',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'abs(expr)',
    draggable: 'abs()',
    description: 'Returns the absolute value of the numeric value.'
  },
  acos: {
    name: 'acos',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'acos(expr)',
    draggable: 'acos()',
    description:
      'Returns the inverse cosine (a.k.a. arc cosine) of expr, as if computed by java.lang.Math.acos.'
  },
  acosh: {
    name: 'acosh',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'acosh(expr)',
    draggable: 'acosh()',
    description: 'Returns inverse hyperbolic cosine of expr.'
  },
  asin: {
    name: 'asin',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'asin(expr)',
    draggable: 'asin()',
    description:
      'Returns the inverse sine (a.k.a. arc sine) the arc sin of expr, as if computed by java.lang.Math.asin.'
  },
  asinh: {
    name: 'asinh',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'asinh(expr)',
    draggable: 'asinh()',
    description: 'Returns inverse hyperbolic sine of expr.'
  },
  atan: {
    name: 'atan',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'atan(expr)',
    draggable: 'atan()',
    description:
      'Returns the inverse tangent (a.k.a. arc tangent) of expr, as if computed by java.lang.Math.atan.'
  },
  atan2: {
    name: 'atan2',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'atan2(exprY, exprX)',
    draggable: 'atan2()',
    description:
      'Returns the angle in radians between the positive x-axis of a plane and the point given by the coordinates (exprX, exprY), as if computed by java.lang.Math.atan2.'
  },
  atanh: {
    name: 'atanh',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'atanh(expr)',
    draggable: 'atanh()',
    description: 'Returns inverse hyperbolic tangent of expr.'
  },
  bin: {
    name: 'bin',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'bin(expr)',
    draggable: 'bin()',
    description: 'Returns the string representation of the long value expr represented in binary.'
  },
  bround: {
    name: 'bround',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'bround(expr)',
    draggable: 'bround()',
    description: 'Returns expr rounded to d decimal places using HALF_EVEN rounding mode.'
  },
  cbrt: {
    name: 'cbrt',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'cbrt(expr)',
    draggable: 'cbrt()',
    description: 'Returns the cube root of expr.'
  },
  ceil: {
    name: 'ceil',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'ceil(expr)',
    draggable: 'ceil()',
    description: 'Returns the smallest integer not smaller than expr.'
  },
  ceiling: {
    name: 'ceiling',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'ceiling(expr)',
    draggable: 'ceiling()',
    description: 'Returns the smallest integer not smaller than expr.'
  },
  conv: {
    name: 'conv',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'conv(num, from_base, to_base)',
    draggable: 'conv()',
    description: 'Convert num from from_base to to_base.'
  },
  cos: {
    name: 'cos',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'cos(expr)',
    draggable: 'cos()',
    description: 'Returns the cosine of expr, as if computed by java.lang.Math.cos.'
  },
  cosh: {
    name: 'cosh',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'cosh(expr)',
    draggable: 'cosh()',
    description: 'Returns the hyperbolic cosine of expr, as if computed by java.lang.Math.cosh.'
  },
  cot: {
    name: 'cot',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'cot(expr)',
    draggable: 'cot()',
    description: 'Returns the cotangent of expr, as if computed by 1/java.lang.Math.cot.'
  },
  csc: {
    name: 'csc',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'csc(expr)',
    draggable: 'csc()',
    description: 'Returns the cosecant of expr, as if computed by 1/java.lang.Math.sin.'
  },
  div: {
    name: 'div',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'div(expr1, expr2)',
    draggable: 'div()',
    description:
      'Divide `expr1` by `expr2`. It returns NULL if an operand is NULL or `expr2` is 0. The result is casted to long.'
  },
  degrees: {
    name: 'degrees',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'degrees(expr)',
    draggable: 'degrees()',
    description: 'Converts radians to degrees.'
  },
  e: {
    name: 'e',
    returnTypes: ['T'],
    arguments: [],
    signature: 'e()',
    draggable: 'e()',
    description: "Returns Euler's number, e."
  },
  exp: {
    name: 'exp',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'exp(expr)',
    draggable: 'exp()',
    description: 'Returns e to the power of expr.'
  },
  expm1: {
    name: 'expm1',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'expm1(expr)',
    draggable: 'expm1()',
    description: 'Returns exp(expr) - 1.'
  },
  factorial: {
    name: 'factorial',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'factorial(expr)',
    draggable: 'factorial()',
    description: 'Returns the factorial of expr. expr is [0..20]. Otherwise, null.'
  },
  floor: {
    name: 'floor',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'floor(expr)',
    draggable: 'floor()',
    description: 'Returns the largest integer not greater than expr.'
  },
  greatest: {
    name: 'greatest',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'greatest(expr, ...)',
    draggable: 'greatest()',
    description: 'Returns the greatest value of all parameters, skipping null values.'
  },
  hex: {
    name: 'hex',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'hex(expr)',
    draggable: 'hex()',
    description: 'Converts expr to hexadecimal.'
  },
  hypot: {
    name: 'hypot',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'hypot(expr1, expr2)',
    draggable: 'hypot()',
    description: 'Returns sqrt(expr12 + expr22).'
  },
  least: {
    name: 'least',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'least(expr, ...)',
    draggable: 'least()',
    description: 'Returns the least value of all parameters, skipping null values.'
  },
  ln: {
    name: 'ln',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'ln(expr)',
    draggable: 'ln()',
    description: 'Returns the natural logarithm (base e) of expr.'
  },
  log: {
    name: 'log',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'log(base, expr)',
    draggable: 'log()',
    description: 'Returns the logarithm of expr with base.'
  },
  log10: {
    name: 'log10',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'log10(expr)',
    draggable: 'log10()',
    description: 'Returns the logarithm of expr with base 10.'
  },
  log1p: {
    name: 'log1p',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'log1p(expr)',
    draggable: 'log1p()',
    description: 'Returns log(1 + expr).'
  },
  log2: {
    name: 'log2',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'log2(expr)',
    draggable: 'log2()',
    description: 'Returns the logarithm of expr with base 2.'
  },
  mod: {
    name: 'mod',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'mod(expr1, expr2)',
    draggable: 'mod()',
    description: 'Returns the remainder after expr1/expr2'
  },
  negative: {
    name: 'negative',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'negative(expr)',
    draggable: 'negative()',
    description: 'Returns the negated value of expr.'
  },
  pi: {
    name: 'pi',
    returnTypes: ['T'],
    arguments: [],
    signature: 'pi()',
    draggable: 'pi()',
    description: 'Returns pi.'
  },
  pmod: {
    name: 'pmod',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'pmod(expr1, expr2)',
    draggable: 'pmod()',
    description: 'Returns the positive value of expr1 mod expr2.'
  },
  positive: {
    name: 'positive',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'positive(expr)',
    draggable: 'position()',
    description: 'Returns the value of expr'
  },
  pow: {
    name: 'pow',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'pow(expr1, expr2)',
    draggable: 'pow()',
    description: 'Raises expr1 to the power of expr2.'
  },
  power: {
    name: 'power',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'power(expr1, expr2)',
    draggable: 'power()',
    description: 'Raises expr1 to the power of expr2.'
  },
  radians: {
    name: 'radians',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'radians(expr)',
    draggable: 'radians()',
    description: 'Converts degrees to radians.'
  },
  rand: {
    name: 'rand',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', optional: true }]],
    signature: 'rand([seed])',
    draggable: 'rand()',
    description:
      'Returns a random value with independent and identically distributed (i.i.d.) uniformly distributed values in [0, 1).'
  },
  randn: {
    name: 'randn',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', optional: true }]],
    signature: 'randn([seed])',
    draggable: 'randn()',
    description:
      'Returns a random value with independent and identically distributed (i.i.d.) values drawn from the standard normal distribution.'
  },
  random: {
    name: 'random',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', optional: true }]],
    signature: 'random([seed])',
    draggable: 'random()',
    description:
      'Returns a random value with independent and identically distributed (i.i.d.) uniformly distributed values in [0, 1).'
  },
  rint: {
    name: 'rint',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'rint(expr)',
    draggable: 'rint()',
    description:
      'Returns the double value that is closest in value to the argument and is equal to a mathematical integer.'
  },
  round: {
    name: 'round',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'round(expr, d)',
    draggable: 'round()',
    description: 'Returns expr rounded to d decimal places using HALF_UP rounding mode.'
  },
  sec: {
    name: 'sec',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'sec(expr)',
    draggable: 'sec()',
    description: 'Returns the secant of expr, as if computed by 1/java.lang.Math.cos.'
  },
  sign: {
    name: 'sign',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'sign(expr)',
    draggable: 'sign()',
    description: 'Returns -1.0, 0.0 or 1.0 as expr is negative, 0 or positive.'
  },
  signum: {
    name: 'signum',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'signum(expr)',
    draggable: 'signum()',
    description: 'Returns -1.0, 0.0 or 1.0 as expr is negative, 0 or positive.'
  },
  sin: {
    name: 'sin',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'sin(expr)',
    draggable: 'sin()',
    description: 'Returns the sine of expr, as if computed by java.lang.Math.sin.'
  },
  sinh: {
    name: 'sinh',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'sinh(expr)',
    draggable: 'sinh()',
    description: 'Returns hyperbolic sine of expr, as if computed by java.lang.Math.sinh.'
  },
  sqrt: {
    name: 'sqrt',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'sqrt(expr)',
    draggable: 'sqrt()',
    description: 'Returns the square root of expr.'
  },
  tan: {
    name: 'tan',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'tan(expr)',
    draggable: 'tan()',
    description: 'Returns the tangent of expr, as if computed by java.lang.Math.tan.'
  },
  tanh: {
    name: 'tanh',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'tanh(expr)',
    draggable: 'tanh()',
    description: 'Returns the hyperbolic tangent of expr, as if computed by java.lang.Math.tanh.'
  },
  try_add: {
    name: 'try_add',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'try_add(expr1, expr2)',
    draggable: 'try_add()',
    description:
      'Returns the sum of expr1and expr2 and the result is null on overflow. The acceptable input types are the same with the + operator.'
  },
  try_divide: {
    name: 'try_divide',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'try_divide(dividend, divisor)',
    draggable: 'try_divide()',
    description:
      'Returns dividend/divisor. It always performs floating point division. Its result is always null if expr2 is 0. dividend must be a numeric or an interval. divisor must be a numeric.'
  },
  try_multiply: {
    name: 'try_multiply',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'try_multiply(expr1, expr2)',
    draggable: 'try_multiply()',
    description:
      'Returns expr1*expr2 and the result is null on overflow. The acceptable input types are the same with the * operator.'
  },
  try_subtract: {
    name: 'try_subtract',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'try_subtract(expr1, expr2)',
    draggable: 'try_subtract()',
    description:
      'Returns expr1-expr2 and the result is null on overflow. The acceptable input types are the same with the - operator.'
  },
  unhex: {
    name: 'unhex',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'unhex(expr)',
    draggable: 'unhex()',
    description: 'Converts hexadecimal expr to binary.'
  },
  width_bucket: {
    name: 'width_bucket',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'width_bucket(value, min_value, max_value, num_bucket)',
    draggable: 'width_bucket()',
    description:
      'Returns the bucket number to which value would be assigned in an equiwidth histogram with num_bucket buckets, in the range min_value to max_value."'
  }
};

export const MISC_FUNCTIONS: UdfCategoryFunctions = {
  aes_decrypt: {
    name: 'aes_decrypt',
    returnTypes: ['T'],
    arguments: [
      [{ type: 'T' }],
      [{ type: 'T' }],
      [{ type: 'T', optional: true }],
      [{ type: 'T', optional: true }]
    ],
    signature: 'aes_decrypt(expr, key[, mode[, padding]])',
    draggable: 'aes_decrypt()',
    description:
      "Returns a decrypted value of expr using AES in mode with padding. Key lengths of 16, 24 and 32 bits are supported. Supported combinations of (mode, padding) are ('ECB', 'PKCS') and ('GCM', 'NONE'). The default mode is GCM.\n" +
      '\n' +
      'Arguments:\n' +
      '\n' +
      'expr - The binary value to decrypt.\n' +
      'key - The passphrase to use to decrypt the data.\n' +
      'mode - Specifies which block cipher mode should be used to decrypt messages. Valid modes: ECB, GCM.\n' +
      'padding - Specifies how to pad messages whose length is not a multiple of the block size. Valid values: PKCS, NONE, DEFAULT. The DEFAULT padding means PKCS for ECB and NONE for GCM.'
  },
  aes_encrypt: {
    name: 'aes_encrypt',
    returnTypes: ['T'],
    arguments: [
      [{ type: 'T' }],
      [{ type: 'T' }],
      [{ type: 'T', optional: true }],
      [{ type: 'T', optional: true }]
    ],
    signature: 'aes_encrypt(expr, key[, mode[, padding]])',
    draggable: 'aes_encrypt()',
    description:
      "Returns an encrypted value of expr using AES in given mode with the specified padding. Key lengths of 16, 24 and 32 bits are supported. Supported combinations of (mode, padding) are ('ECB', 'PKCS') and ('GCM', 'NONE'). The default mode is GCM.\n" +
      '\n' +
      'Arguments:\n' +
      '\n' +
      'expr - The binary value to encrypt.\n' +
      'key - The passphrase to use to encrypt the data.\n' +
      'mode - Specifies which block cipher mode should be used to encrypt messages. Valid modes: ECB, GCM.\n' +
      'padding - Specifies how to pad messages whose length is not a multiple of the block size. Valid values: PKCS, NONE, DEFAULT. The DEFAULT padding means PKCS for ECB and NONE for GCM.'
  },
  assert_true: {
    name: 'assert_true',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'assert_true(expr)',
    draggable: 'assert_true()',
    description: 'Throws an exception if expr is not true.'
  },
  bool_and: {
    name: 'bool_and',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'T' }]],
    signature: 'bool_and(expr)',
    draggable: 'bool_and()',
    description: 'Returns true if all values of expr are true.'
  },
  bool_or: {
    name: 'bool_or',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'T' }]],
    signature: 'bool_or(expr)',
    draggable: 'bool_or()',
    description: 'Returns true if at least one value of expr is true.'
  },
  cardinality: {
    name: 'cardinality',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'cardinality(expr)',
    draggable: 'cardinality()',
    description:
      'Returns the size of an array or a map. The function returns null for null input if spark.sql.legacy.sizeOfNull is set to false or spark.sql.ansi.enabled is set to true. Otherwise, the function returns -1 for null input. With the default settings, the function returns -1 for null input.'
  },
  crc32: {
    name: 'crc32',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'crc32(expr)',
    draggable: 'crc32()',
    description: 'Returns a cyclic redundancy check value of the expr as a bigint.'
  },
  cube: {
    name: 'cube',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', optional: true, multiple: true }]],
    signature: 'cube([col1[, col2 ..]])',
    draggable: 'cube()',
    description:
      'Create a multi-dimensional cube using the specified columns so that we can run aggregation on them.'
  },
  current_catalog: {
    name: 'current_catalog',
    returnTypes: ['T'],
    arguments: [],
    signature: 'current_catalog()',
    draggable: 'current_catalog()',
    description: 'Returns the current catalog.'
  },
  current_database: {
    name: 'current_database',
    returnTypes: ['T'],
    arguments: [],
    signature: 'current_database()',
    draggable: 'current_database()',
    description: 'Returns the current database.'
  },
  current_user: {
    name: 'current_user',
    returnTypes: ['T'],
    arguments: [],
    signature: 'current_user()',
    draggable: 'current_user()',
    description: 'Returns the user name of the current execution context.'
  },
  exists: {
    name: 'exists',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'exists(expr, pred)',
    draggable: 'exists()',
    description: 'Tests whether a predicate holds for one or more elements in the array.'
  },
  find_in_set: {
    name: 'find_in_set',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'find_in_set(str, str_array)',
    draggable: 'find_in_set()',
    description:
      'Returns the index (1-based) of the given string (str) in the comma-delimited list (str_array). Returns 0, if the string was not found or if the given string (str) contains a comma.'
  },
  forall: {
    name: 'forall',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'forall(expr, pred)',
    draggable: 'forall()',
    description: 'Tests whether a predicate holds for all elements in the array.'
  },
  hash: {
    name: 'hash',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'hash(expr1, expr2, ...)',
    draggable: 'hash()',
    description: 'Returns a hash value of the arguments.'
  },
  input_file_block_length: {
    name: 'input_file_block_length',
    returnTypes: ['T'],
    arguments: [],
    signature: 'input_file_block_length()',
    draggable: 'input_file_block_length()',
    description: 'Returns the length of the block being read, or -1 if not available.'
  },
  input_file_block_start: {
    name: 'input_file_block_start',
    returnTypes: ['T'],
    arguments: [],
    signature: 'input_file_block_start()',
    draggable: 'input_file_block_start()',
    description: 'Returns the start offset of the block being read, or -1 if not available.'
  },
  input_file_name: {
    name: 'input_file_name',
    returnTypes: ['T'],
    arguments: [],
    signature: 'input_file_name()',
    draggable: 'input_file_name()',
    description: 'Returns the name of the file being read, or empty string if not available.'
  },
  java_method: {
    name: 'java_method',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true, multiple: true }]],
    signature: 'java_method(class, method[, arg1[, arg2 ..]])',
    draggable: 'java_method()',
    description: 'Calls a method with reflection.'
  },
  md5: {
    name: 'md5',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'md5(expr)',
    draggable: 'md5()',
    description: 'Returns an MD5 128-bit checksum as a hex string of expr.'
  },
  monotonically_increasing_id: {
    name: 'monotonically_increasing_id',
    returnTypes: ['T'],
    arguments: [],
    signature: 'monotonically_increasing_id()',
    draggable: 'monotonically_increasing_id()',
    description:
      'Returns monotonically increasing 64-bit integers. The generated ID is guaranteed to be monotonically increasing and unique, but not consecutive. The current implementation puts the partition ID in the upper 31 bits, and the lower 33 bits represent the record number within each partition. The assumption is that the data frame has less than 1 billion partitions, and each partition has less than 8 billion records. The function is non-deterministic because its result depends on partition IDs.'
  },
  named_struct: {
    name: 'named_struct',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'named_struct(name1, val1, name2, val2, ...)',
    draggable: 'named_struct()',
    description: 'Creates a struct with the given field names and values.'
  },
  nth_value: {
    name: 'nth_value',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'nth_value(input[, offset])',
    draggable: 'nth_value()',
    description:
      'Returns the value of input at the row that is the offsetth row from beginning of the window frame. Offset starts at 1. If ignoreNulls=true, we will skip nulls when finding the offsetth row. Otherwise, every row counts for the offset. If there is no such an offsetth row (e.g., when the offset is 10, size of the window frame is less than 10), null is returned.'
  },
  raise_error: {
    name: 'raise_error',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'raise_error(expr)',
    draggable: 'raise_error()',
    description: 'Throws an exception with expr.'
  },
  rank: {
    name: 'rank',
    returnTypes: ['T'],
    arguments: [],
    signature: 'rank()',
    draggable: 'rank()',
    description:
      'Computes the rank of a value in a group of values. The result is one plus the number of rows preceding or equal to the current row in the ordering of the partition. The values will produce gaps in the sequence.'
  },
  reflect: {
    name: 'reflect',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true, multiple: true }]],
    signature: 'reflect(class, method[, arg1[, arg2 ..]])',
    draggable: 'reflect()',
    description: 'Calls a method with reflection.'
  },
  regexp_replace: {
    name: 'regexp_replace',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'regexp_replace(str, regexp, rep)',
    draggable: 'regexp_replace()',
    description: 'Replaces all substrings of str that match regexp with rep.'
  },
  rlike: {
    name: 'rlike',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'rlike(str, regexp)',
    draggable: 'rlike()',
    description: 'Returns true if str matches regexp, or false otherwise.'
  },
  rollup: {
    name: 'rollup',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', optional: true, multiple: true }]],
    signature: 'rollup([col1[, col2 ..]])',
    draggable: 'rollup()',
    description:
      'Create a multi-dimensional rollup using the specified columns so that we can run aggregation on them.'
  },
  sha: {
    name: 'sha',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'sha(expr)',
    draggable: 'sha()',
    description: 'Returns a sha1 hash value as a hex string of the expr.'
  },
  sha1: {
    name: 'sha1',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'sha1(expr)',
    draggable: 'sha1()',
    description: 'Returns a sha1 hash value as a hex string of the expr.'
  },
  sha2: {
    name: 'sha2',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'sha2(expr, bitLength)',
    draggable: 'sha2()',
    description:
      'Returns a checksum of SHA-2 family as a hex string of expr. SHA-224, SHA-256, SHA-384, and SHA-512 are supported. Bit length of 0 is equivalent to 256.'
  },
  size: {
    name: 'size',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'size(expr)',
    draggable: 'size()',
    description:
      'Returns the size of an array or a map. The function returns null for null input if spark.sql.legacy.sizeOfNull is set to false or spark.sql.ansi.enabled is set to true. Otherwise, the function returns -1 for null input. With the default settings, the function returns -1 for null input.'
  },
  spark_partition_id: {
    name: 'spark_partition_id',
    returnTypes: ['T'],
    arguments: [],
    signature: 'spark_partition_id()',
    draggable: 'spark_partition_id()',
    description: 'Returns the current partition id.'
  },
  struct: {
    name: 'struct',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'struct(col1, col2, col3, ...)',
    draggable: 'struct()',
    description: 'Creates a struct with the given field values.'
  },
  transform: {
    name: 'transform',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'transform(expr, func)',
    draggable: 'transform()',
    description: 'Transforms elements in an array using the function.'
  },
  typeof: {
    name: 'typeof',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'typeof(expr)',
    draggable: 'typeof()',
    description: 'Return DDL-formatted type string for the data type of the input.'
  },
  uuid: {
    name: 'uuid',
    returnTypes: ['T'],
    arguments: [],
    signature: 'uuid()',
    draggable: 'uuid()',
    description:
      'Returns an universally unique identifier (UUID) string. The value is returned as a canonical UUID 36-character string.'
  },
  version: {
    name: 'version',
    returnTypes: ['T'],
    arguments: [],
    signature: 'version()',
    draggable: 'version()',
    description:
      'Returns the Spark version. The string contains 2 fields, the first being a release version and the second being a git revision.'
  },
  xpath: {
    name: 'xpath',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'xpath(xml, xpath)',
    draggable: 'xpath()',
    description:
      'Returns a string array of values within the nodes of xml that match the XPath expression.'
  },
  xpath_boolean: {
    name: 'xpath_boolean',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'xpath_boolean(xml, xpath)',
    draggable: 'xpath_boolean()',
    description:
      'Returns true if the XPath expression evaluates to true, or if a matching node is found.'
  },
  xpath_double: {
    name: 'xpath_double',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'xpath_double(xml, xpath)',
    draggable: 'xpath_double()',
    description:
      'Returns a double value, the value zero if no match is found, or NaN if a match is found but the value is non-numeric.'
  },
  xpath_float: {
    name: 'xpath_float',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'xpath_float(xml, xpath)',
    draggable: 'xpath_float()',
    description:
      'Returns a float value, the value zero if no match is found, or NaN if a match is found but the value is non-numeric.'
  },
  xpath_int: {
    name: 'xpath_int',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'xpath_int(xml, xpath)',
    draggable: 'xpath_int()',
    description:
      'Returns an integer value, or the value zero if no match is found, or a match is found but the value is non-numeric.'
  },
  xpath_long: {
    name: 'xpath_long',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'xpath_long(xml, xpath)',
    draggable: 'xpath_long()',
    description:
      'Returns a long integer value, or the value zero if no match is found, or a match is found but the value is non-numeric.'
  },
  xpath_number: {
    name: 'xpath_number',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'xpath_number(xml, xpath)',
    draggable: 'xpath_number()',
    description:
      'Returns a double value, the value zero if no match is found, or NaN if a match is found but the value is non-numeric.'
  },
  xpath_short: {
    name: 'xpath_short',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'xpath_short(xml, xpath)',
    draggable: 'xpath_short()',
    description:
      'Returns a short integer value, or the value zero if no match is found, or a match is found but the value is non-numeric.'
  },
  xpath_string: {
    name: 'xpath_string',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'xpath_string(xml, xpath)',
    draggable: 'xpath_string()',
    description:
      'Returns the text contents of the first xml node that matches the XPath expression.'
  },
  xxhash64: {
    name: 'xxhash64',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'xxhash64(expr1, expr2, ...)',
    draggable: 'xxhash64()',
    description: 'Returns a 64-bit hash value of the arguments.'
  }
};

export const PREDICATE_FUNCTIONS: UdfCategoryFunctions = {
  ilike: {
    name: 'ilike',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'ilike(str, pattern)',
    draggable: 'ilike()',
    description:
      'Returns true if str matches pattern with case-insensitively, null if any arguments are null, false otherwise.'
  },
  isnan: {
    name: 'isnan',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'T' }]],
    signature: 'isnan(expr)',
    draggable: 'isnan()',
    description: 'Returns true if expr is NaN, or false otherwise.'
  },
  isnotnull: {
    name: 'isnotnull',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'T' }]],
    signature: 'isnotnull(expr)',
    draggable: 'isnotnull()',
    description: 'Returns true if expr is not null, or false otherwise.'
  },
  isnull: {
    name: 'isnull',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'T' }]],
    signature: 'isnull(expr)',
    draggable: 'isnull()',
    description: 'Returns true if expr is null, or false otherwise.'
  },
  like: {
    name: 'like',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'like(str, pattern)',
    draggable: 'like()',
    description:
      'Returns true if str matches pattern with escape, null if any arguments are null, false otherwise.'
  },
  regexp: {
    name: 'regexp',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'regexp(str, regexp)',
    draggable: 'regexp()',
    description: 'Returns true if str matches regexp, or false otherwise.'
  },
  regexp_like: {
    name: 'regexp_like',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'regexp_like(str, regexp)',
    draggable: 'regexp_like()',
    description: 'Returns true if str matches regexp, or false otherwise.'
  }
};

export const STRING_FUNCTIONS: UdfCategoryFunctions = {
  ascii: {
    name: 'ascii',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'ascii(str)',
    draggable: 'ascii()',
    description: 'Returns the numeric value of the first character of str.'
  },
  base64: {
    name: 'base64',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'base64(bin)',
    draggable: 'base64()',
    description: 'Converts the argument from a binary bin to a base 64 string.'
  },
  bit_length: {
    name: 'bit_length',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'bit_length(expr)',
    draggable: 'bit_length()',
    description: 'Returns the bit length of string data or number of bits of binary data.'
  },
  btrim: {
    name: 'btrim',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'btrim(str[, trimStr])',
    draggable: 'btrim()',
    description: 'Removes the leading and trailing space characters or trimStr from str.'
  },
  char: {
    name: 'char',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'char(expr)',
    draggable: 'char()',
    description:
      'Returns the ASCII character having the binary equivalent to expr. If n is larger than 256 the result is equivalent to chr(n % 256)'
  },
  char_length: {
    name: 'char_length',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'char_length(expr)',
    draggable: 'char_length()',
    description:
      'Returns the character length of string data or number of bytes of binary data. The length of string data includes the trailing spaces. The length of binary data includes binary zeros.'
  },
  character_length: {
    name: 'character_length',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'character_length(expr)',
    draggable: 'character_length()',
    description:
      'Returns the character length of string data or number of bytes of binary data. The length of string data includes the trailing spaces. The length of binary data includes binary zeros.'
  },
  chr: {
    name: 'chr',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'chr(expr)',
    draggable: 'chr()',
    description:
      'Returns the ASCII character having the binary equivalent to expr. If n is larger than 256 the result is equivalent to chr(n % 256)'
  },
  concat_ws: {
    name: 'concat_ws',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true, multiple: true }]],
    signature: 'concat_ws(sep, [str | array(str)]+)',
    draggable: 'concat_ws()',
    description: 'Returns the concatenation of the strings separated by sep.'
  },
  contains: {
    name: 'contains',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'contains(left, right)',
    draggable: 'contains()',
    description:
      'Returns a boolean. The value is True if right is found inside left. Returns NULL if either input expression is NULL. Otherwise, returns False. Both left or right must be of STRING or BINARY type.'
  },
  decode: {
    name: 'decode',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true, multiple: true }]],
    signature:
      'decode(bin, charset), decode(expr, search, result [, search, result ] ... [, default])',
    draggable: 'decode()',
    description:
      'Decodes the first argument using the second argument character set.\n\nFor expr: Compares expr to each search value in order. If expr is equal to a search value, decode returns the corresponding result. If no match is found, then it returns default. If default is omitted, it returns null.'
  },
  elt: {
    name: 'elt',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', multiple: true }]],
    signature: 'elt(n, input1, input2, ...)',
    draggable: 'elt()',
    description: 'Returns the n-th input, e.g., returns input2 when n is 2.'
  },
  encode: {
    name: 'encode',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'encode(str, charset)',
    draggable: 'encode()',
    description: 'Encodes the first argument using the second argument character set.'
  },
  endswith: {
    name: 'endswith',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'endswith(left, right)',
    draggable: 'endswith()',
    description:
      'Returns a boolean. The value is True if left ends with right. Returns NULL if either input expression is NULL. Otherwise, returns False. Both left or right must be of STRING or BINARY type.'
  },
  format_number: {
    name: 'format_number',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'format_number(expr1, expr2)',
    draggable: 'format_number()',
    description:
      "Formats the number expr1 like '#,###,###.##', rounded to expr2 decimal places. If expr2 is 0, the result has no decimal point or fractional part. expr2 also accept a user specified format. This is supposed to function like MySQL's FORMAT."
  },
  format_string: {
    name: 'format_string',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', multiple: true }]],
    signature: 'format_string(strfmt, obj, ...)',
    draggable: 'format_string()',
    description: 'Returns a formatted string from printf-style format strings.'
  },
  initcap: {
    name: 'initcap',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'initcap(str)',
    draggable: 'initcap()',
    description:
      'Returns str with the first letter of each word in uppercase. All other letters are in lowercase. Words are delimited by white space.'
  },
  instr: {
    name: 'instr',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'instr(str, substr)',
    draggable: 'instr()',
    description: 'Returns the (1-based) index of the first occurrence of substr in str.'
  },
  lcase: {
    name: 'lcase',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'lcase(str)',
    draggable: 'lcase()',
    description: 'Returns str with all characters changed to lowercase.'
  },
  left: {
    name: 'left',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'NUMBER' }]],
    signature: 'left(str, len)',
    draggable: 'left()',
    description:
      'Returns the leftmost len(len can be string type) characters from the string str,if len is less or equal than 0 the result is an empty string.'
  },
  length: {
    name: 'length',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'length(expr)',
    draggable: 'length()',
    description:
      'Returns the character length of string data or number of bytes of binary data. The length of string data includes the trailing spaces. The length of binary data includes binary zeros.'
  },
  levenshtein: {
    name: 'levenshtein',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'levenshtein(str1, str2)',
    draggable: 'levenshtein()',
    description: 'Returns the Levenshtein distance between the two given strings.'
  },
  locate: {
    name: 'locate',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'locate(substr, str[, pos])',
    draggable: 'locate()',
    description:
      'Returns the position of the first occurrence of substr in str after position pos. The given pos and return value are 1-based.'
  },
  lower: {
    name: 'lower',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'lower(str)',
    draggable: 'lower()',
    description: 'Returns str with all characters changed to lowercase.'
  },
  lpad: {
    name: 'lpad',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'lpad(str, len[, pad])',
    draggable: 'lpad()',
    description:
      'Returns str, left-padded with pad to a length of len. If str is longer than len, the return value is shortened to len characters. If pad is not specified, str will be padded to the left with space characters.'
  },
  ltrim: {
    name: 'ltrim',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'ltrim(str)',
    draggable: 'ltrim()',
    description: 'Removes the leading space characters from str.'
  },
  octet_length: {
    name: 'octet_length',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'octet_length(expr)',
    draggable: 'octet_length()',
    description: 'Returns the byte length of string data or number of bytes of binary data.'
  },
  overlay: {
    name: 'overlay',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'overlay(input, replace, pos[, len])',
    draggable: 'overlay()',
    description: 'Replace input with replace that starts at pos and is of length.'
  },
  parse_url: {
    name: 'parse_url',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'parse_url(url, partToExtract[, key])',
    draggable: 'parse_url()',
    description: 'Extracts a part from a URL.'
  },
  position: {
    name: 'position',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'position(substr, str[, pos])',
    draggable: 'position()',
    description:
      'Returns the position of the first occurrence of substr in str after position pos. The given pos and return value are 1-based.'
  },
  printf: {
    name: 'printf',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', multiple: true }]],
    signature: 'printf(strfmt, obj, ...)',
    draggable: 'printf()',
    description: 'Returns a formatted string from printf-style format strings.'
  },
  regexp_extract: {
    name: 'regexp_extract',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'regexp_extract(str, regexp[, idx])',
    draggable: 'regexp_extract()',
    description: 'Extracts a group that matches regexp.'
  },
  regexp_extract_all: {
    name: 'regexp_extract_all',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'regexp_extract_all(str, regexp[, idx])',
    draggable: 'regexp_extract_all()',
    description:
      'Extract all strings in the str that match the regexp expression and corresponding to the regex group index.'
  },
  repeat: {
    name: 'repeat',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'repeat(str, n)',
    draggable: 'repeat()',
    description: 'Returns the string which repeats the given string value n times.'
  },
  replace: {
    name: 'replace',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'replace(str, search[, replace])',
    draggable: 'replace()',
    description:
      'Replaces all occurrences of search with replace.\n' +
      '\n' +
      'Arguments:\n' +
      '\n' +
      'str - a string expression\n' +
      'search - a string expression. If search is not found in str, str is returned unchanged.\n' +
      'replace - a string expression. If replace is not specified or is an empty string, nothing replaces the string that is removed from str.'
  },
  right: {
    name: 'right',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'right(str, len)',
    draggable: 'right()',
    description:
      'Returns the rightmost len(len can be string type) characters from the string str,if len is less or equal than 0 the result is an empty string.'
  },
  rpad: {
    name: 'rpad',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'rpad(str, len[, pad])',
    draggable: 'rpad()',
    description:
      'Returns str, right-padded with pad to a length of len. If str is longer than len, the return value is shortened to len characters. If pad is not specified, str will be padded to the right with space characters.'
  },
  rtrim: {
    name: 'rtrim',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'rtrim(str)',
    draggable: 'rtrim()',
    description: 'Removes the trailing space characters from str.'
  },
  sentences: {
    name: 'sentences',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }], [{ type: 'T', optional: true }]],
    signature: 'sentences(str[, lang, country])',
    draggable: 'sentences()',
    description: 'Splits str into an array of array of words.'
  },
  soundex: {
    name: 'soundex',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'soundex(str)',
    draggable: 'soundex()',
    description: 'Returns Soundex code of the string.'
  },
  space: {
    name: 'space',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'space(n)',
    draggable: 'space()',
    description: 'Returns a string consisting of n spaces.'
  },
  split: {
    name: 'split',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'split(str, regex, limit)',
    draggable: 'split()',
    description:
      'Splits str around occurrences that match regex and returns an array with a length of at most limit.'
  },
  split_part: {
    name: 'split_part',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'split_part(str, delimiter, partNum)',
    draggable: 'split_part()',
    description:
      'Splits str by delimiter and return requested part of the split (1-based). If any input is null, returns null. if partNum is out of range of split parts, returns empty string. If partNum is 0, throws an error. If partNum is negative, the parts are counted backward from the end of the string. If the delimiter is an empty string, the str is not split.'
  },
  startswith: {
    name: 'startswith',
    returnTypes: ['BOOLEAN'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'startswith(left, right)',
    draggable: 'startswith()',
    description:
      'Returns a boolean. The value is True if left starts with right. Returns NULL if either input expression is NULL. Otherwise, returns False. Both left or right must be of STRING or BINARY type.'
  },
  substr: {
    name: 'substr',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'substr(str, pos[, len]',
    draggable: 'substr()',
    description:
      'Returns the substring of str that starts at pos and is of length len, or the slice of byte array that starts at pos and is of length len.\n' +
      '\n' +
      'substr(str FROM pos[ FOR len]]) - Returns the substring of str that starts at pos and is of length len, or the slice of byte array that starts at pos and is of length len.'
  },
  substring: {
    name: 'substring',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'substring(str, pos[, len]',
    draggable: 'substring()',
    description:
      'Returns the substring of str that starts at pos and is of length len, or the slice of byte array that starts at pos and is of length len.\n' +
      '\n' +
      'substr(str FROM pos[ FOR len]]) - Returns the substring of str that starts at pos and is of length len, or the slice of byte array that starts at pos and is of length len.'
  },
  substring_index: {
    name: 'substring_index',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'substring_index(str, delim, count)',
    draggable: 'substring_index()',
    description:
      'Returns the substring from str before count occurrences of the delimiter delim. If count is positive, everything to the left of the final delimiter (counting from the left) is returned. If count is negative, everything to the right of the final delimiter (counting from the right) is returned. The function substring_index performs a case-sensitive match when searching for delim.'
  },
  to_binary: {
    name: 'to_binary',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'to_binary(str[, fmt])',
    draggable: 'to_binary()',
    description:
      'Converts the input str to a binary value based on the supplied fmt. fmt can be a case-insensitive string literal of "hex", "utf-8", or "base64". By default, the binary format for conversion is "hex" if fmt is omitted. The function returns NULL if at least one of the input parameters is NULL.'
  },
  to_number: {
    name: 'to_number',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'to_number(expr, fmt)',
    draggable: 'to_number()',
    description:
      "Convert string 'expr' to a number based on the string format 'fmt'. Throws an exception if the conversion fails. The format can consist of the following characters, case insensitive: '0' or '9': Specifies an expected digit between 0 and 9. A sequence of 0 or 9 in the format string matches a sequence of digits in the input string. If the 0/9 sequence starts with 0 and is before the decimal point, it can only match a digit sequence of the same size. Otherwise, if the sequence starts with 9 or is after the decimal poin, it can match a digit sequence that has the same or smaller size. '.' or 'D': Specifies the position of the decimal point (optional, only allowed once). ',' or 'G': Specifies the position of the grouping (thousands) separator (,). There must be one or more 0 or 9 to the left of the rightmost grouping separator. 'expr' must match the grouping separator relevant for the size of the number. '$': Specifies the location of the $ currency sign. This character may only be specified once. 'S' or 'MI': Specifies the position of a '-' or '+' sign (optional, only allowed once at the beginning or end of the format string). Note that 'S' allows '-' but 'MI' does not. 'PR': Only allowed at the end of the format string; specifies that 'expr' indicates a negative number with wrapping angled brackets. ('<1>')."
  },
  translate: {
    name: 'translate',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'translate(input, from, to)',
    draggable: 'translate()',
    description:
      'Translates the input string by replacing the characters present in the from string with the corresponding characters in the to string.'
  },
  trim: {
    name: 'trim',
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'trim([BOTH|LEADING|TRAILING] [trimstr] [FROM] str)',
    draggable: 'trim()',
    description:
      'trim(str) - Removes the leading and trailing space characters from str.\n' +
      'trim(BOTH FROM str) - Removes the leading and trailing space characters from str.\n' +
      'trim(LEADING FROM str) - Removes the leading space characters from str.\n' +
      'trim(TRAILING FROM str) - Removes the trailing space characters from str.\n' +
      'trim(trimStr FROM str) - Remove the leading and trailing trimStr characters from str.\n' +
      'trim(BOTH trimStr FROM str) - Remove the leading and trailing trimStr characters from str.\n' +
      'trim(LEADING trimStr FROM str) - Remove the leading trimStr characters from str.\n' +
      'trim(TRAILING trimStr FROM str) - Remove the trailing trimStr characters from str.'
  },
  try_to_binary: {
    name: 'try_to_binary',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }]],
    signature: 'try_to_binary(str[, fmt])',
    draggable: 'try_to_binary()',
    description:
      'This is a special version of to_binary that performs the same operation, but returns a NULL value instead of raising an error if the conversion cannot be performed.'
  },
  try_to_number: {
    name: 'try_to_number',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'try_to_number(expr, fmt)',
    draggable: 'try_to_number()',
    description:
      "Convert string 'expr' to a number based on the string format fmt. Returns NULL if the string 'expr' does not match the expected format. The format follows the same semantics as the to_number function."
  },
  ucase: {
    name: 'ucase',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'ucase(str)',
    draggable: 'ucase()',
    description: 'Returns str with all characters changed to uppercase.'
  },
  unbase64: {
    name: 'unbase64',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'unbase64(str)',
    draggable: 'unbase64()',
    description: 'Converts the argument from a base 64 string str to a binary.'
  },
  upper: {
    name: 'upper',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'upper(str)',
    draggable: 'upper()',
    description: 'Returns str with all characters changed to uppercase.'
  }
};

export const WINDOW_FUNCTIONS: UdfCategoryFunctions = {
  cume_dist: {
    name: 'cume_dist',
    returnTypes: ['T'],
    arguments: [],
    signature: 'cume_dist()',
    draggable: 'cume_dist()',
    description: 'Computes the position of a value relative to all values in the partition.'
  },
  dense_rank: {
    name: 'dense_rank',
    returnTypes: ['T'],
    arguments: [],
    signature: 'dense_rank(expr)',
    draggable: 'dense_rank()',
    description:
      'Computes the rank of a value in a group of values. The result is one plus the previously assigned rank value. Unlike the function rank, dense_rank will not produce gaps in the ranking sequence.'
  },
  lag: {
    name: 'lag',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }], [{ type: 'T', optional: true }]],
    signature: 'lag(input[, offset[, default]])',
    draggable: 'lag()',
    description:
      'Returns the value of `input` at the `offset`th row before the current row in the window. The default value of `offset` is 1 and the default value of `default` is null. If the value of `input` at the `offset`th row is null, null is returned. If there is no such offset row (e.g., when the offset is 1, the first row of the window does not have any previous row), `default` is returned.'
  },
  lead: {
    name: 'lead',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T', optional: true }], [{ type: 'T', optional: true }]],
    signature: 'lead(input[, offset[, default]])',
    draggable: 'lead()',
    description:
      'Returns the value of `input` at the `offset`th row after the current row in the window. The default value of `offset` is 1 and the default value of `default` is null. If the value of `input` at the `offset`th row is null, null is returned. If there is no such an offset row (e.g., when the offset is 1, the last row of the window does not have any subsequent row), `default` is returned.'
  },
  ntile: {
    name: 'ntile',
    returnTypes: ['T'],
    arguments: [[{ type: 'NUMBER' }]],
    signature: 'ntile(n)',
    draggable: 'ntile()',
    description:
      'Divides the rows for each window partition into `n` buckets ranging from 1 to at most `n`.'
  },
  percent_rank: {
    name: 'percent_rank',
    returnTypes: ['T'],
    arguments: [],
    signature: 'percent_rank()',
    draggable: 'percent_rank()',
    description: 'Computes the percentage ranking of a value in a group of values.'
  },
  row_number: {
    name: 'row_number',
    returnTypes: ['T'],
    arguments: [],
    signature: 'row_number()',
    draggable: 'row_number()',
    description:
      'Assigns a unique, sequential number to each row, starting with one, according to the ordering of rows within the window partition.'
  }
};

export const UDF_CATEGORIES: UdfCategory[] = [
  { name: I18n('Aggregate'), isAggregate: true, functions: AGGREGATE_FUNCTIONS },
  { name: I18n('Array'), functions: ARRAY_FUNCTIONS },
  { name: I18n('Bitwise'), functions: BITWISE_FUNCTIONS },
  { name: I18n('Conditional'), functions: CONDITIONAL_FUNCTIONS },
  { name: I18n('Conversion'), functions: CONVERSION_FUNCTIONS },
  { name: I18n('CSV'), functions: CSV_FUNCTIONS },
  { name: I18n('Date and Time'), functions: DATE_AND_TIME_FUNCTIONS },
  { name: I18n('Generator'), functions: GENERATOR_FUNCTIONS },
  { name: I18n('JSON'), functions: JSON_FUNCTIONS },
  { name: I18n('Map'), functions: MAP_FUNCTIONS },
  { name: I18n('Mathematical'), functions: MATHEMATICAL_FUNCTIONS },
  { name: I18n('Misc'), functions: MISC_FUNCTIONS },
  { name: I18n('Predicate'), functions: PREDICATE_FUNCTIONS },
  { name: I18n('String'), functions: STRING_FUNCTIONS },
  { name: I18n('Window'), isAnalytic: true, functions: WINDOW_FUNCTIONS }
];
