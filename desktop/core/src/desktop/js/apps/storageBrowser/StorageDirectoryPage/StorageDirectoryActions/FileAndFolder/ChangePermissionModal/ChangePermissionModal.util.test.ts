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

import { getInitialPermissions } from './ChangePermissionModal.util';
import { StorageDirectoryTableData } from '../../../../types';

describe('getInitialPermissions', () => {
  const mockFiles: StorageDirectoryTableData[] = [
    {
      name: 'file1.txt',
      size: '0 Byte',
      type: 'file',
      permission: '-rwxr-xr--',
      mtime: '2021-01-01 00:00:00',
      path: 'test/path/file1.txt',
      user: 'user1',
      group: 'group1',
      replication: 1
    },
    {
      name: 'file2.txt',
      size: '0 Byte',
      type: 'file',
      permission: '-r-xr-xr--',
      mtime: '2021-01-01 00:00:00',
      path: 'test/path/file2.txt',
      user: 'user1',
      group: 'group1',
      replication: 1
    }
  ];

  it('should correctly initialize permissions for multiple files', () => {
    const result = getInitialPermissions(mockFiles);

    const expectedPermissions = [
      { key: 'read', user: true, group: true, other: true },
      { key: 'write', user: true, group: false, other: false },
      { key: 'execute', user: true, group: true, other: false },
      { key: 'sticky', common: false },
      { key: 'recursive', common: false }
    ];

    expect(result).toEqual(expectedPermissions);
  });

  it('should correctly initialize permissions for a single file', () => {
    const result = getInitialPermissions([mockFiles[0]]);

    const expectedPermissions = [
      { key: 'read', user: true, group: true, other: true },
      { key: 'write', user: true, group: false, other: false },
      { key: 'execute', user: true, group: true, other: false },
      { key: 'sticky', common: false },
      { key: 'recursive', common: false }
    ];

    expect(result).toEqual(expectedPermissions);
  });

  it('should correctly set initialize sticky to true', () => {
    const expectedPermissions = [
      { key: 'read', user: true, group: true, other: true },
      { key: 'write', user: true, group: true, other: true },
      { key: 'execute', user: true, group: true, other: true },
      { key: 'sticky', common: true },
      { key: 'recursive', common: false }
    ];

    const result = getInitialPermissions([
      {
        ...mockFiles[0],
        permission: '-rwxrwxrwxt'
      }
    ]);

    expect(result).toEqual(expectedPermissions);
  });

  it('should correctly set initialize sticky to false', () => {
    const expectedPermissions = [
      { key: 'read', user: true, group: true, other: true },
      { key: 'write', user: true, group: true, other: true },
      { key: 'execute', user: true, group: true, other: true },
      { key: 'sticky', common: false },
      { key: 'recursive', common: false }
    ];

    const result = getInitialPermissions([
      {
        ...mockFiles[0],
        permission: '-rwxrwxrwx'
      }
    ]);
    expect(result).toEqual(expectedPermissions);
  });
});
