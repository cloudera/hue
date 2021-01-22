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
  count: {
    name: 'count',
    returnTypes: ['BIGINT'],
    arguments: [[{ type: 'T' }]],
    signature: 'count(col)',
    draggable: 'count()',
    description:
      'count(*) - Returns the total number of retrieved rows, including rows containing NULL values. count(expr) - Returns the number of rows for which the supplied expression is non-NULL.'
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
  }
};

const AUXILIARY_FUNCTIONS: UdfCategoryFunctions = {
  hop: {
    name: 'hop',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'hop(time_attr, interval, interval)',
    draggable: 'hop(time_attr, interval, interval)',
    description: 'Defines a hopping time window (called sliding window in the Table API). A hopping time window has a fixed duration (second interval parameter) and hops by a specified hop interval (first interval parameter)'
  },
  hop_start: {
    name: 'hop_start',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'hop_start(time_attr, interval, interval)',
    draggable: 'hop_start(time_attr, interval, interval)',
    description: 'Returns the timestamp of the inclusive lower bound of the corresponding hopping window.'
  },
  hop_end: {
    name: 'hop_end',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'hop_end(time_attr, interval, interval)',
    draggable: 'hop_end(time_attr, interval, interval)',
    description: 'Returns the timestamp of the inclusive upper bound of the corresponding hopping window.'
  },
  hop_rowtime: {
    name: 'hop_rowtime',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'hop_rowtime(time_attr, interval, interval)',
    draggable: 'hop_rowtime(time_attr, interval, interval)',
    description: 'Returns the timestamp of the inclusive upper bound of the corresponding hopping window.'
  },
  hop_proctime: {
    name: 'hop_proctime',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }], [{ type: 'T' }]],
    signature: 'hop_proctime(time_attr, interval, interval)',
    draggable: 'hop_proctime(time_attr, interval, interval)',
    description: 'Returns a proctime attribute that can be used in subsequent time-based operations such as interval joins and group window or over window aggregations.'
  },
  session: {
    name: 'session',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'session(time_attr, interval)',
    draggable: 'session(time_attr, interval)',
    description: 'Defines a session time window. Session time windows do not have a fixed duration but their bounds are defined by a time interval of inactivity, i.e., a session window is closed if no event appears for a defined gap period.'
  },
  session_start: {
    name: 'session_start',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'session_start(time_attr, interval)',
    draggable: 'session_start(time_attr, interval)',
    description: 'Returns the timestamp of the inclusive lower bound of the corresponding session window.'
  },
  session_end: {
    name: 'session_end',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'session_end(time_attr, interval)',
    draggable: 'session_end(time_attr, interval)',
    description: 'Returns the timestamp of the inclusive upper bound of the corresponding session window.'
  },
  session_rowtime: {
    name: 'session_rowtime',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'session_rowtime(time_attr, interval)',
    draggable: 'session_rowtime(time_attr, interval)',
    description: 'Returns the timestamp of the inclusive upper bound of the corresponding session window.'
  },
  session_proctime: {
    name: 'session_proctime',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'session_proctime(time_attr, interval)',
    draggable: 'session_proctime(time_attr, interval)',
    description: 'Returns a proctime attribute that can be used in subsequent time-based operations such as interval joins and group window or over window aggregations.'
  },
  tumble: {
    name: 'tumble',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'tumble(time_attr, interval)',
    draggable: 'tumble(time_attr, interval)',
    description: 'Defines a tumbling time window. A tumbling time window assigns rows to non-overlapping, continuous windows with a fixed duration (interval). For example, a tumbling window of 5 minutes groups rows in 5 minutes intervals. Tumbling windows can be defined on event-time (stream + batch) or processing-time (stream).'

  },
  tumble_start: {
    name: 'tumble_start',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'tumble_start(time_attr, interval)',
    draggable: 'tumble_start(time_attr, interval)',
    description: 'Returns the timestamp of the inclusive lower bound of the corresponding tumbling window.'
  },
  tumble_end: {
    name: 'tumble_end',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'tumble_end(time_attr, interval)',
    draggable: 'tumble_end(time_attr, interval)',
    description: 'Returns the timestamp of the exclusive upper bound of the corresponding tumbling window.'
  },
  tumble_rowtime: {
    name: 'tumble_rowtime',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'tumble_rowtime(time_attr, interval)',
    draggable: 'tumble_rowtime(time_attr, interval)',
    description: 'Returns the timestamp of the inclusive upper bound of the corresponding session window.'
  },
  tumble_proctime: {
    name: 'tumble_proctime',
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }], [{ type: 'T' }]],
    signature: 'tumble_proctime(time_attr, interval)',
    draggable: 'tumble_proctime(time_attr, interval)',
    description: 'Returns a proctime attribute that can be used in subsequent time-based operations such as interval joins and group window or over window aggregations.'
  },
};

export const UDF_CATEGORIES: UdfCategory[] = [
  { name: I18n('Aggregate'), isAggregate: true, functions: AGGREGATE_FUNCTIONS },
  { name: I18n('Misc'), functions: AUXILIARY_FUNCTIONS }
];
