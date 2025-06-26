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
  it('should extract file name from LOCAL file metadata with fileName provided', () => {
    const fileMetaData = {
      path: '/user/data/myDocument.csv',
      fileName: 'myDocument.csv',
      source: ImporterFileSource.LOCAL
    };
    const result = getDefaultTableName(fileMetaData);
    expect(result).toBe('myDocument');
  });

  it('should return empty string if LOCAL file has no fileName property', () => {
    const fileMetaData = {
      path: '/user/data/myDocument.csv',
      source: ImporterFileSource.LOCAL
    };
    const result = getDefaultTableName(fileMetaData);
    expect(result).toBe('');
  });

  it('should handle LOCAL file with complex filename', () => {
    const fileMetaData = {
      path: '/user/data/complex-file_name.with.dots.xlsx',
      fileName: 'complex-file_name.with.dots.xlsx',
      source: ImporterFileSource.LOCAL
    };
    const result = getDefaultTableName(fileMetaData);
    expect(result).toBe('complex_file_name_with_dots');
  });

  it('should handle LOCAL file with special characters in filename', () => {
    const fileMetaData = {
      path: '/user/data/file@2023#test.csv',
      fileName: 'file@2023#test.csv',
      source: ImporterFileSource.LOCAL
    };
    const result = getDefaultTableName(fileMetaData);
    expect(result).toBe('file_2023_test');
  });

  it('should handle LOCAL file with spaces in filename', () => {
    const fileMetaData = {
      path: '/user/data/my file name.csv',
      fileName: 'my file name.csv',
      source: ImporterFileSource.LOCAL
    };
    const result = getDefaultTableName(fileMetaData);
    expect(result).toBe('my_file_name');
  });

  it('should extract file name from REMOTE path as last part of path', () => {
    const fileMetaData = {
      path: '/user/data/test-file.csv',
      source: ImporterFileSource.REMOTE
    };
    const result = getDefaultTableName(fileMetaData);
    expect(result).toBe('test_file');
  });

  it('should handle file names with multiple dots correctly', () => {
    const fileMetaData = {
      path: '/user/data/test.file.name.csv',
      source: ImporterFileSource.REMOTE
    };
    const result = getDefaultTableName(fileMetaData);
    expect(result).toBe('test_file_name');
  });

  it('should handle file names with no extension correctly', () => {
    const fileMetaData = {
      path: '/user/data/test-file',
      source: ImporterFileSource.REMOTE
    };
    const result = getDefaultTableName(fileMetaData);
    expect(result).toBe('test_file');
  });

  it('should handle file names with special characters correctly', () => {
    const fileMetaData = {
      path: '/user/data/test-file@2023.csv',
      source: ImporterFileSource.REMOTE
    };
    const result = getDefaultTableName(fileMetaData);
    expect(result).toBe('test_file_2023');
  });

  it('should handle file names with spaces correctly', () => {
    const fileMetaData = {
      path: '/user/data/test file.csv',
      source: ImporterFileSource.REMOTE
    };
    const result = getDefaultTableName(fileMetaData);
    expect(result).toBe('test_file');
  });

  it('should handle REMOTE files with only extension', () => {
    const fileMetaData = {
      path: '/user/data/.csv',
      source: ImporterFileSource.REMOTE
    };
    const result = getDefaultTableName(fileMetaData);
    expect(result).toBe('');
  });

  it('should handle REMOTE files with multiple extensions', () => {
    const fileMetaData = {
      path: '/user/data/file.backup.tar.gz',
      source: ImporterFileSource.REMOTE
    };
    const result = getDefaultTableName(fileMetaData);
    expect(result).toBe('file_backup_tar');
  });

  it('should handle REMOTE files with numbers and underscores', () => {
    const fileMetaData = {
      path: '/user/data/data_file_2023_v1.xlsx',
      source: ImporterFileSource.REMOTE
    };
    const result = getDefaultTableName(fileMetaData);
    expect(result).toBe('data_file_2023_v1');
  });

  it('should handle S3 URLs', () => {
    const fileMetaData = {
      path: 's3://bucket-name/folder/data-file.csv',
      source: ImporterFileSource.REMOTE
    };
    const result = getDefaultTableName(fileMetaData);
    expect(result).toBe('data_file');
  });

  it('should handle Azure blob URLs', () => {
    const fileMetaData = {
      path: 'abfs://container/data.file.csv',
      source: ImporterFileSource.REMOTE
    };
    const result = getDefaultTableName(fileMetaData);
    expect(result).toBe('data_file');
  });

  it('should return empty string for empty file paths', () => {
    const localFileMetaData = {
      path: '',
      fileName: '',
      source: ImporterFileSource.LOCAL
    };
    const remoteFileMetaData = {
      path: '',
      source: ImporterFileSource.REMOTE
    };
    expect(getDefaultTableName(localFileMetaData)).toBe('');
    expect(getDefaultTableName(remoteFileMetaData)).toBe('');
  });

  it('should handle single character file names', () => {
    const fileMetaData = {
      path: '/user/data/a.csv',
      source: ImporterFileSource.REMOTE
    };
    const result = getDefaultTableName(fileMetaData);
    expect(result).toBe('a');
  });
});
