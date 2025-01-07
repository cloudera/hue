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
import { render, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import CompressAction from './Compress';
import { StorageDirectoryTableData } from '../../../../../reactComponents/FileChooser/types';
import { COMPRESS_API_URL } from '../../../../../reactComponents/FileChooser/api';

const mockFiles: StorageDirectoryTableData[] = [
  {
    name: 'file1.txt',
    size: '0 Byte',
    type: 'file',
    permission: 'rwxrwxrwx',
    mtime: '2021-01-01 00:00:00',
    path: 'test/path/file1.txt',
    user: 'test',
    group: 'test',
    replication: 1
  },
  {
    name: 'file2.txt',
    size: '0 Byte',
    type: 'file',
    permission: 'rwxrwxrwx',
    mtime: '2021-01-01 00:00:00',
    path: 'test/path/file2.txt',
    user: 'test',
    group: 'test',
    replication: 1
  }
];

const mockSave = jest.fn();
jest.mock('../../../../../utils/hooks/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: mockSave,
    loading: false
  }))
}));

describe('CompressAction Component', () => {
  const mockOnSuccess = jest.fn();
  const mockOnError = jest.fn();
  const mockOnClose = jest.fn();
  const setLoading = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the Compress modal with the correct title and buttons', () => {
    const { getByText, getByRole } = render(
      <CompressAction
        isOpen={true}
        files={mockFiles}
        setLoading={setLoading}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        currentPath="test/path"
      />
    );

    expect(getByText('Compress files and folders')).toBeInTheDocument();
    expect(getByText('Compressed file name')).toBeInTheDocument();
    expect(getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
    expect(getByRole('button', { name: 'Compress' })).toBeInTheDocument();
  });

  it('should display the correct list of files to be compressed', () => {
    const { getByText } = render(
      <CompressAction
        isOpen={true}
        files={mockFiles}
        setLoading={setLoading}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        currentPath="test/path"
      />
    );

    expect(getByText('Following files and folders will be compressed:')).toBeInTheDocument();
    expect(getByText('file1.txt')).toBeInTheDocument();
    expect(getByText('file2.txt')).toBeInTheDocument();
  });

  it('should call handleCompress with the correct data when "Compress" is clicked', async () => {
    const { getByText } = render(
      <CompressAction
        isOpen={true}
        files={mockFiles}
        setLoading={setLoading}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        currentPath="test/path"
      />
    );

    const formData = new FormData();
    mockFiles.forEach(file => {
      formData.append('file_name', file.name);
    });
    formData.append('upload_path', 'test/path');
    formData.append('archive_name', 'path.zip');

    fireEvent.click(getByText('Compress'));

    expect(mockSave).toHaveBeenCalledWith(formData, { url: COMPRESS_API_URL });
  });

  it('should update the compressed file name when input value changes', () => {
    const { getByRole } = render(
      <CompressAction
        isOpen={true}
        files={mockFiles}
        setLoading={setLoading}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        currentPath="test/path"
      />
    );

    const input = getByRole('textbox');
    fireEvent.change(input, { target: { value: 'new-compressed-file.zip' } });

    expect(input).toHaveValue('new-compressed-file.zip');
  });

  it('should call onClose when the modal is closed', () => {
    const { getByText } = render(
      <CompressAction
        isOpen={true}
        files={mockFiles}
        setLoading={setLoading}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        currentPath="test/path"
      />
    );

    fireEvent.click(getByText('Cancel'));
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should call onError when the compress request fails', async () => {
    mockSave.mockImplementationOnce(() => {
      mockOnError(new Error('Compression failed'));
    });

    const { getByText } = render(
      <CompressAction
        isOpen={true}
        files={mockFiles}
        setLoading={setLoading}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        currentPath="test/path"
      />
    );

    fireEvent.click(getByText('Compress'));
    await waitFor(() => expect(mockOnError).toHaveBeenCalledWith(new Error('Compression failed')));
  });
});
