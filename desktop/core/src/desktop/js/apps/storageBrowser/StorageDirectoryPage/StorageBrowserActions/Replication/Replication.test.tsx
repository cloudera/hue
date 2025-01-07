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
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ReplicationAction from './Replication';
import { StorageDirectoryTableData } from '../../../../../reactComponents/FileChooser/types';
import { SET_REPLICATION_API_URL } from '../../../../../reactComponents/FileChooser/api';

const mockSave = jest.fn();
jest.mock('../../../../../utils/hooks/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: mockSave,
    loading: false
  }))
}));

describe('ReplicationAction Component', () => {
  const mockOnSuccess = jest.fn();
  const mockOnError = jest.fn();
  const mockOnClose = jest.fn();

  const file: StorageDirectoryTableData = {
    name: 'file1.txt',
    size: '0 Byte',
    type: 'file',
    permission: 'rwxrwxrwx',
    mtime: '2021-01-01 00:00:00',
    path: '/path/to/file1.txt',
    user: 'test',
    group: 'test',
    replication: 1
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the Replication modal with the correct title and initial input', () => {
    const { getByText, getByRole } = render(
      <ReplicationAction
        isOpen={true}
        file={file}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    expect(getByText('Setting Replication factor for: /path/to/file1.txt')).toBeInTheDocument();

    const input = getByRole('spinbutton');
    expect(input).toBeInTheDocument();
    expect(input).toHaveValue(1);
  });

  it('should call handleReplication with the correct data when the form is submitted', async () => {
    const { getByRole } = render(
      <ReplicationAction
        isOpen={true}
        file={file}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    const input = getByRole('spinbutton');
    fireEvent.change(input, { target: { value: 2 } });

    const replicationButton = getByRole('button', { name: 'Submit' });
    fireEvent.click(replicationButton);

    expect(mockSave).toHaveBeenCalledTimes(1);

    expect(mockSave).toHaveBeenCalledWith(
      { path: '/path/to/file1.txt', replication_factor: '2' },
      { url: SET_REPLICATION_API_URL }
    );
  });

  it('should call onSuccess when the rename request succeeds', async () => {
    mockSave.mockImplementationOnce(mockOnSuccess);
    const { getByRole } = render(
      <ReplicationAction
        isOpen={true}
        file={file}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    const input = getByRole('spinbutton');
    fireEvent.change(input, { target: { value: 2 } });

    const replicationButton = getByRole('button', { name: 'Submit' });
    fireEvent.click(replicationButton);

    expect(mockOnSuccess).toHaveBeenCalledTimes(1);
  });

  it('should call onError when the rename request fails', async () => {
    mockSave.mockImplementationOnce(() => {
      mockOnError(new Error());
    });
    const { getByRole } = render(
      <ReplicationAction
        isOpen={true}
        file={file}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    const input = getByRole('spinbutton');
    fireEvent.change(input, { target: { value: 2 } });

    const replicationButton = getByRole('button', { name: 'Submit' });
    fireEvent.click(replicationButton);

    expect(mockOnError).toHaveBeenCalledTimes(1);
  });

  it('should call onClose when the modal is closed', () => {
    const { getByRole } = render(
      <ReplicationAction
        isOpen={true}
        file={file}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    fireEvent.click(getByRole('button', { name: 'Cancel' }));

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });
});
