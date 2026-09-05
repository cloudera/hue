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

import {
  formatRowDetailsTitle,
  inferRowDetailsSourceName,
  resolveRowDetailsSourceName
} from './rowDetailsSource';

describe('formatRowDetailsTitle', () => {
  it('uses the default title when source name is missing', () => {
    expect(formatRowDetailsTitle()).toEqual('Row details');
    expect(formatRowDetailsTitle('')).toEqual('Row details');
    expect(formatRowDetailsTitle('   ')).toEqual('Row details');
  });

  it('appends the source name', () => {
    expect(formatRowDetailsTitle('default.customers')).toEqual('Row details - default.customers');
  });
});

describe('resolveRowDetailsSourceName', () => {
  it('returns trimmed strings and getter results', () => {
    expect(resolveRowDetailsSourceName('  t  ')).toEqual('t');
    expect(resolveRowDetailsSourceName(() => 'customers')).toEqual('customers');
  });

  it('returns undefined for empty, throwing, or missing values', () => {
    expect(resolveRowDetailsSourceName(undefined)).toBeUndefined();
    expect(resolveRowDetailsSourceName(() => '')).toBeUndefined();
    expect(
      resolveRowDetailsSourceName(() => {
        throw new Error('boom');
      })
    ).toBeUndefined();
  });
});

describe('inferRowDetailsSourceName', () => {
  it('returns a single qualified table from a simple select', () => {
    expect(
      inferRowDetailsSourceName({
        database: 'default',
        statement: 'SELECT * FROM customers'
      })
    ).toEqual('default.customers');
  });

  it('keeps already qualified names from the Impala editor repro', () => {
    expect(
      inferRowDetailsSourceName({
        database: 'default',
        statement: 'select * from database.table_name limit 1;'
      })
    ).toEqual('database.table_name');
  });

  it('joins multiple FROM/JOIN tables', () => {
    expect(
      inferRowDetailsSourceName({
        database: 'default',
        statement: 'SELECT * FROM customers c JOIN orders o ON c.id = o.cid'
      })
    ).toEqual('default.customers, default.orders');
  });

  it('skips subqueries after FROM (', () => {
    expect(
      inferRowDetailsSourceName({
        database: 'default',
        statement: 'SELECT * FROM (SELECT 1) t'
      })
    ).toEqual('default');
  });

  it('falls back to database when there is no table', () => {
    expect(
      inferRowDetailsSourceName({
        database: 'default',
        statement: 'SELECT 1'
      })
    ).toEqual('default');
  });

  it('returns undefined when nothing is known', () => {
    expect(inferRowDetailsSourceName({})).toBeUndefined();
  });
});
