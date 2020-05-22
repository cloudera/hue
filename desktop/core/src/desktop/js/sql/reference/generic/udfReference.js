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

export const AGGREGATE_FUNCTIONS = {
  count: {
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'T' }]],
    signature: 'count(col)',
    draggable: 'count()',
    description:
      'count(*) - Returns the total number of retrieved rows, including rows containing NULL values. count(expr) - Returns the number of rows for which the supplied expression is non-NULL.'
  },
  sum: {
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'sum(col)',
    draggable: 'sum()',
    description:
      'Returns the sum of the elements in the group or the sum of the distinct values of the column in the group.'
  },
  max: {
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'max(col)',
    draggable: 'max()',
    description: 'Returns the maximum value of the column in the group.'
  },
  min: {
    returnTypes: ['DOUBLE'],
    arguments: [[{ type: 'T' }]],
    signature: 'min(col)',
    draggable: 'min()',
    description: 'Returns the minimum of the column in the group.'
  }
};

export const UDF_CATEGORIES = [{ name: I18n('Aggregate'), functions: AGGREGATE_FUNCTIONS }];
