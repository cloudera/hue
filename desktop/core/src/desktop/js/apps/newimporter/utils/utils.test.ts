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

import { ColumnProps } from 'cuix/dist/components/Table';
import { convertToAntdColumns, convertToDataSource } from './utils';
import { GuessFieldTypesColumn } from '../types';

describe('convertToAntdColumns', () => {
  it('should return an empty array when no input is provided', () => {
    expect(convertToAntdColumns()).toEqual([]);
  });

  it('should correctly convert GuessFieldTypesColumn[] to ColumnProps[]', () => {
    const input: GuessFieldTypesColumn[] = [{ name: 'name' }, { name: 'age' }];
    const expectedOutput = [
      { title: 'name', dataIndex: 'name', key: 'name', width: '100px' },
      { title: 'age', dataIndex: 'age', key: 'age', width: '100px' }
    ];

    expect(convertToAntdColumns(input)).toEqual(expectedOutput);
  });
});

describe('convertToDataSource', () => {
  const columns: ColumnProps<GuessFieldTypesColumn>[] = [
    { title: 'Name', dataIndex: 'name', key: 'name', width: '100px' },
    { title: 'Age', dataIndex: 'age', key: 'age', width: '100px' }
  ];

  it('should return an empty array when no apiResponse is provided', () => {
    expect(convertToDataSource(columns)).toEqual([]);
  });

  it('should correctly convert apiResponse to GuessFieldTypesColumn[]', () => {
    const apiResponse: string[][] = [
      ['Alice', '30'],
      ['Bob', '25']
    ];

    const expectedOutput = [
      { importerDataKey: 'Alice__0', name: 'Alice', age: '30' },
      { importerDataKey: 'Bob__1', name: 'Bob', age: '25' }
    ];

    expect(convertToDataSource(columns, apiResponse)).toEqual(expectedOutput);
  });
});
