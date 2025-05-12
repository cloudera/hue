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

import { convertToAntdColumns, convertToDataSource, getDefaultTableName } from './utils';
import { ImporterFileSource, FilePreviewTableColumn, FilePreviewTableData } from '../types';

describe('convertToAntdColumns', () => {
  it('should return an empty array when no input is provided', () => {
    expect(convertToAntdColumns()).toEqual([]);
  });

  it('should correctly convert FilePreviewTableColumn[] to ColumnProps[]', () => {
    const input: FilePreviewTableColumn[] = [{ name: 'name' }, { name: 'age' }];
    const expectedOutput = [
      { title: 'name', dataIndex: 'name', key: 'name', width: '100px' },
      { title: 'age', dataIndex: 'age', key: 'age', width: '100px' }
    ];

    expect(convertToAntdColumns(input)).toEqual(expectedOutput);
  });
});

describe('convertToDataSource', () => {
  it('should return an empty array when no apiResponse is provided', () => {
    expect(convertToDataSource({})).toEqual([]);
  });

  it('should correctly convert apiResponse to FilePreviewTableColumn[]', () => {
    const apiResponse: FilePreviewTableData = {
      name: ['Alice', 'Bob'],
      age: ['30', '25']
    };

    const expectedOutput = [
      { importerDataKey: 'importer-row__0', name: 'Alice', age: '30' },
      { importerDataKey: 'importer-row__1', name: 'Bob', age: '25' }
    ];

    expect(convertToDataSource(apiResponse)).toEqual(expectedOutput);
  });
});

describe('getDefaultTableName', () => {
  it('should extract file name from LOCALFILE path using pattern', () => {
    const filePath = '/user/data/:myDocument;v1.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.LOCAL);
    expect(result).toBe('myDocument');
  });

  it('should return empty string if LOCALFILE pattern does not match', () => {
    const filePath = '/user/data/myDocument.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.LOCAL);
    expect(result).toBe('');
  });

  it('should extract file name from REMOTE path as last part of path', () => {
    const filePath = 'https://demo.gethue.com/hue/test-file.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('test-file');
  });

  it('should handle file names with multiple dots correctly', () => {
    const filePath = 'https://demo.gethue.com/hue/test.file.name.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('test_file_name');
  });

  it('should handle file names with no extension correctly', () => {
    const filePath = 'https://demo.gethue.com/hue/test-file';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('test-file');
  });

  it('should handle file names with special characters correctly', () => {
    const filePath = 'https://demo.gethue.com/hue/test-file@2023.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('test-file@2023');
  });

  it('should handle file names with spaces correctly', () => {
    const filePath = 'https://demo.gethue.com/hue/test file.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('test file');
  });
});
