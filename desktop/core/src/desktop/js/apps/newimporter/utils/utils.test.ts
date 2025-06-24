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
  it('should correctly convert FilePreviewTableColumn[] to ColumnProps[]', () => {
    const input: FilePreviewTableColumn[] = [{ name: 'name' }, { name: 'age' }];
    const expectedOutput = [
      { title: 'name', dataIndex: 'name', key: 'name', width: '100px' },
      { title: 'age', dataIndex: 'age', key: 'age', width: '100px' }
    ];

    expect(convertToAntdColumns(input)).toEqual(expectedOutput);
  });

  it('should handle single column input', () => {
    const input: FilePreviewTableColumn[] = [{ name: 'singleColumn' }];
    const expectedOutput = [
      { title: 'singleColumn', dataIndex: 'singleColumn', key: 'singleColumn', width: '100px' }
    ];

    expect(convertToAntdColumns(input)).toEqual(expectedOutput);
  });

  it('should handle columns with special characters', () => {
    const input: FilePreviewTableColumn[] = [
      { name: 'first-name' },
      { name: 'email_address' },
      { name: 'phone number' }
    ];
    const expectedOutput = [
      { title: 'first-name', dataIndex: 'firstName', key: 'first-name', width: '100px' },
      { title: 'email_address', dataIndex: 'emailAddress', key: 'email_address', width: '100px' },
      { title: 'phone number', dataIndex: 'phoneNumber', key: 'phone number', width: '100px' }
    ];

    expect(convertToAntdColumns(input)).toEqual(expectedOutput);
  });

  it('should handle columns with numbers and special characters', () => {
    const input: FilePreviewTableColumn[] = [
      { name: 'column1' },
      { name: '2nd_column' },
      { name: 'column-3' }
    ];
    const expectedOutput = [
      { title: 'column1', dataIndex: 'column1', key: 'column1', width: '100px' },
      { title: '2nd_column', dataIndex: '2NdColumn', key: '2nd_column', width: '100px' },
      { title: 'column-3', dataIndex: 'column3', key: 'column-3', width: '100px' }
    ];

    expect(convertToAntdColumns(input)).toEqual(expectedOutput);
  });

  it('should handle columns with type property', () => {
    const input: FilePreviewTableColumn[] = [
      { name: 'name', type: 'string' },
      { name: 'age', type: 'number' }
    ];
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

  it('should handle uneven array lengths with null values', () => {
    const apiResponse: FilePreviewTableData = {
      name: ['Alice', 'Bob', 'Charlie'],
      age: ['30', '25'],
      city: ['New York']
    };

    const expectedOutput = [
      { importerDataKey: 'importer-row__0', name: 'Alice', age: '30', city: 'New York' },
      { importerDataKey: 'importer-row__1', name: 'Bob', age: '25', city: null },
      { importerDataKey: 'importer-row__2', name: 'Charlie', age: null, city: null }
    ];

    expect(convertToDataSource(apiResponse)).toEqual(expectedOutput);
  });

  it('should handle empty arrays in apiResponse', () => {
    const apiResponse: FilePreviewTableData = {
      name: [],
      age: []
    };

    expect(convertToDataSource(apiResponse)).toEqual([]);
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

  it('should handle LOCALFILE with complex filename', () => {
    const filePath = '/user/data/:complex-file_name.with.dots;v1.xlsx';
    const result = getDefaultTableName(filePath, ImporterFileSource.LOCAL);
    expect(result).toBe('complex_file_name_with_dots');
  });

  it('should handle LOCALFILE with special characters in filename', () => {
    const filePath = '/user/data/:file@2023#test;v1.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.LOCAL);
    expect(result).toBe('file_2023_test');
  });

  it('should handle LOCALFILE with spaces in filename', () => {
    const filePath = '/user/data/:my file name;v1.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.LOCAL);
    expect(result).toBe('my_file_name');
  });

  it('should extract file name from REMOTE path as last part of path', () => {
    const filePath = 'https://demo.gethue.com/hue/test-file.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('test_file');
  });

  it('should handle file names with multiple dots correctly', () => {
    const filePath = 'https://demo.gethue.com/hue/test.file.name.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('test_file_name');
  });

  it('should handle file names with no extension correctly', () => {
    const filePath = 'https://demo.gethue.com/hue/test-file';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('test_file');
  });

  it('should handle file names with special characters correctly', () => {
    const filePath = 'https://demo.gethue.com/hue/test-file@2023.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('test_file_2023');
  });

  it('should handle file names with spaces correctly', () => {
    const filePath = 'https://demo.gethue.com/hue/test file.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('test_file');
  });

  it('should handle REMOTE files with only extension', () => {
    const filePath = 'https://demo.gethue.com/hue/.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('');
  });

  it('should handle REMOTE files with multiple extensions', () => {
    const filePath = 'https://demo.gethue.com/hue/file.backup.tar.gz';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('file_backup_tar');
  });

  it('should handle REMOTE files with numbers and underscores', () => {
    const filePath = 'https://demo.gethue.com/hue/data_file_2023_v1.xlsx';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('data_file_2023_v1');
  });

  it('should handle S3 URLs', () => {
    const filePath = 's3://bucket-name/folder/data-file.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('data_file');
  });

  it('should handle Azure blob URLs', () => {
    const filePath = 'https://storageaccount.blob.core.windows.net/container/data.file.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('data_file');
  });

  it('should handle local file paths with forward slashes', () => {
    const filePath = 'C:/Users/Documents/data.file.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('data_file');
  });

  it('should return empty string for empty file path', () => {
    const result1 = getDefaultTableName('', ImporterFileSource.LOCAL);
    const result2 = getDefaultTableName('', ImporterFileSource.REMOTE);
    expect(result1).toBe('');
    expect(result2).toBe('');
  });

  it('should handle path with only directories (no file)', () => {
    const filePath = 'https://demo.gethue.com/hue/';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('hue');
  });

  it('should handle single character file names', () => {
    const filePath = 'https://demo.gethue.com/hue/a.csv';
    const result = getDefaultTableName(filePath, ImporterFileSource.REMOTE);
    expect(result).toBe('a');
  });
});
