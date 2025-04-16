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

import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import StorageDirectoryActions from './StorageDirectoryActions';

const mockOnActionSuccess = jest.fn();
const mockOnFilesDrop = jest.fn();
const mockOnFilePathChange = jest.fn();

describe('StorageDirectoryActions Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const mockSelectedFiles = [
    {
      name: 'file1.txt',
      size: '0 Byte',
      type: 'file',
      permission: 'rwxrwxrwx',
      mtime: '2021-01-01 00:00:00',
      path: '/user/path/.Trash/Current/file1.txt',
      user: 'test',
      group: 'test',
      replication: 1
    }
  ];

  const mockFileStats = {
    name: 'file1.txt',
    type: 'file',
    permission: 'rwxrwxrwx',
    mtime: 123,
    path: '/user/path/file1.txt',
    user: 'test',
    group: 'test',
    replication: 1,
    atime: 123,
    blockSize: 123,
    mode: 123,
    rwx: 'rwxrwxrwx',
    size: 123
  };

  const mockFileSystem = {
    name: 'hdfs',
    userHomeDirectory: '/user/hue'
  };

  const mockTrashPath = '/user/path/.Trash/Current';

  it('should render the Trash actions when path is in Trash', () => {
    const { getByRole, queryByRole } = render(
      <StorageDirectoryActions
        selectedFiles={mockSelectedFiles}
        onActionSuccess={mockOnActionSuccess}
        fileStats={{ ...mockFileStats, path: mockTrashPath }}
        fileSystem={mockFileSystem}
        onFilePathChange={mockOnFilePathChange}
        onFilesDrop={mockOnFilesDrop}
      />
    );

    expect(getByRole('button', { name: 'Restore' })).toBeInTheDocument();
    expect(getByRole('button', { name: 'Empty trash' })).toBeInTheDocument();
    expect(queryByRole('button', { name: 'Actions' })).not.toBeInTheDocument();
    expect(queryByRole('button', { name: 'New' })).not.toBeInTheDocument();
  });

  it('should render the regular actions when path is not in Trash', () => {
    const { getByRole, queryByRole } = render(
      <StorageDirectoryActions
        selectedFiles={mockSelectedFiles}
        onActionSuccess={mockOnActionSuccess}
        fileStats={mockFileStats}
        fileSystem={mockFileSystem}
        onFilePathChange={mockOnFilePathChange}
        onFilesDrop={mockOnFilesDrop}
      />
    );

    expect(getByRole('button', { name: 'Actions' })).toBeInTheDocument();
    expect(getByRole('button', { name: 'New' })).toBeInTheDocument();
    expect(queryByRole('button', { name: 'Restore' })).not.toBeInTheDocument();
    expect(queryByRole('button', { name: 'Empty trash' })).not.toBeInTheDocument();
  });
});
