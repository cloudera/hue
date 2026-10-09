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

import { splitStatementTitle } from './statementTitle';

describe('statementTitle.ts', () => {
  it('should use the leading line comment as the title', () => {
    expect(splitStatementTitle('-- Top salaries\nSELECT * FROM employees')).toEqual({
      title: 'Top salaries',
      statement: 'SELECT * FROM employees'
    });
  });

  it('should join consecutive leading line comments', () => {
    expect(splitStatementTitle('-- Top salaries\n-- in 2007\nSELECT * FROM employees')).toEqual({
      title: 'Top salaries\nin 2007',
      statement: 'SELECT * FROM employees'
    });
  });

  it('should ignore the indentation of a leading line comment', () => {
    expect(splitStatementTitle('\n   -- Top salaries\nSELECT * FROM employees')).toEqual({
      title: 'Top salaries',
      statement: 'SELECT * FROM employees'
    });
  });

  it('should leave a statement without leading line comments untouched', () => {
    expect(splitStatementTitle('SELECT * FROM employees -- all of them')).toEqual({
      title: '',
      statement: 'SELECT * FROM employees -- all of them'
    });
  });

  it('should not use line comments that follow the statement as the title', () => {
    expect(splitStatementTitle('SELECT * FROM employees\n-- all of them')).toEqual({
      title: '',
      statement: 'SELECT * FROM employees\n-- all of them'
    });
  });

  it('should handle an empty statement', () => {
    expect(splitStatementTitle('')).toEqual({ title: '', statement: '' });
  });
});
