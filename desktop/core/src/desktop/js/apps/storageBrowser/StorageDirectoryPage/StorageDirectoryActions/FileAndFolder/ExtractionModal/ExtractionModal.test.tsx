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
import ExtractAction from './ExtractionModal';
import { StorageDirectoryTableData } from '../../../../types';

const mockFile: StorageDirectoryTableData = {
  name: 'archive.zip',
  size: '50 MB',
  type: 'file',
  permission: 'rwxrwxrwx',
  mtime: '2021-01-01 00:00:00',
  path: 'test/path/archive.zip',
  user: 'test',
  group: 'test',
  replication: 1
};

const mockSave = jest.fn();
let mockLoading = false;
jest.mock('../../../../../../utils/hooks/useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: mockSave,
    loading: mockLoading
  }))
}));

describe('ExtractAction Component', () => {
  const mockOnSuccess = jest.fn();
  const mockOnError = jest.fn();
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the Extract modal with the correct title and buttons', () => {
    const { getByText, getByRole } = render(
      <ExtractAction
        isOpen={true}
        file={mockFile}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        currentPath="test/path"
      />
    );

    expect(getByText('Extract Archive')).toBeInTheDocument();
    expect(getByText(`Are you sure you want to extract "{{fileName}}" file?`)).toBeInTheDocument();
    expect(getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
    expect(getByRole('button', { name: 'Extract' })).toBeInTheDocument();
  });

  it('should call handleExtract with the correct path and name when "Extract" is clicked', async () => {
    const { getByText } = render(
      <ExtractAction
        isOpen={true}
        file={mockFile}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        currentPath="test/path"
      />
    );

    fireEvent.click(getByText('Extract'));

    expect(mockSave).toHaveBeenCalledWith({
      upload_path: 'test/path',
      archive_name: mockFile.name
    });
  });

  it('should call onSuccess when the extract request is successful', async () => {
    mockSave.mockImplementationOnce(() => {
      mockOnSuccess();
    });

    const { getByText } = render(
      <ExtractAction
        isOpen={true}
        file={mockFile}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        currentPath="test/path"
      />
    );

    fireEvent.click(getByText('Extract'));
    await waitFor(() => expect(mockOnSuccess).toHaveBeenCalledTimes(1));
  });

  it('should call onError when the extract request fails', async () => {
    mockSave.mockImplementationOnce(() => {
      mockOnError(new Error('Extraction failed'));
    });

    const { getByText } = render(
      <ExtractAction
        isOpen={true}
        file={mockFile}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        currentPath="test/path"
      />
    );

    fireEvent.click(getByText('Extract'));
    await waitFor(() => expect(mockOnError).toHaveBeenCalledWith(new Error('Extraction failed')));
  });

  it('should call onClose when the modal is closed', () => {
    const { getByText } = render(
      <ExtractAction
        isOpen={true}
        file={mockFile}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        currentPath="test/path"
      />
    );

    fireEvent.click(getByText('Cancel'));
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should disable the "Extract" button while loading', () => {
    mockLoading = true;

    const { getByRole } = render(
      <ExtractAction
        isOpen={true}
        file={mockFile}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        currentPath="test/path"
      />
    );

    expect(getByRole('button', { name: 'loading Extract' })).toBeInTheDocument();
  });
});
