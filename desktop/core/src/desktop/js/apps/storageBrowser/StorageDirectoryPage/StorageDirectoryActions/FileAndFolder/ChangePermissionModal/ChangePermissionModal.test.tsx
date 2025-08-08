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
import ChangePermissionModal from './ChangePermissionModal';
import { StorageDirectoryTableData } from '../../../../types';

const mockFiles: StorageDirectoryTableData[] = [
  {
    name: 'file1.txt',
    size: '0 Byte',
    type: 'file',
    permission: 'rwxrwxrwx',
    mtime: '2021-01-01 00:00:00',
    path: 'test/path/file1.txt',
    user: 'user1',
    group: 'group1',
    replication: 1
  }
];

const mockSave = jest.fn();
jest.mock('../../../../../../utils/hooks/useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: mockSave,
    loading: false
  }))
}));

const mockOnSuccess = jest.fn();
const mockOnError = jest.fn();
const mockOnClose = jest.fn();

describe('ChangePermissionModal Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the modal with initial permissions', () => {
    const { getByText } = render(
      <ChangePermissionModal
        isOpen={true}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    waitFor(() => {
      expect(getByText('Change Permissions')).toBeInTheDocument();
      expect(getByText('Submit')).toBeInTheDocument();
      expect(getByText('Cancel')).toBeInTheDocument();
      expect(getByText('read')).toBeInTheDocument();
      expect(getByText('write')).toBeInTheDocument();
      expect(getByText('execute')).toBeInTheDocument();
      expect(getByText('sticky')).toBeInTheDocument();
      expect(getByText('recursive')).toBeInTheDocument();
    });
  });

  it('should toggle permission checkboxes correctly for user, group', () => {
    const { getAllByRole } = render(
      <ChangePermissionModal
        isOpen={true}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    const checkboxes = getAllByRole('checkbox');
    const userReadCheckbox = checkboxes[0];
    const groupWriteCheckbox = checkboxes[1];

    waitFor(() => expect(userReadCheckbox).toBeChecked());
    fireEvent.click(userReadCheckbox);
    waitFor(() => expect(userReadCheckbox).not.toBeChecked());

    fireEvent.click(groupWriteCheckbox);
    waitFor(() => expect(groupWriteCheckbox).toBeChecked());
  });

  it('should submit the form when the Submit button is clicked', () => {
    const { getByText } = render(
      <ChangePermissionModal
        isOpen={true}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    fireEvent.click(getByText('Submit'));

    waitFor(() => {
      const expectedFormData = new FormData();
      expectedFormData.append(
        'permission',
        '{"user_read":true,"user_write":true,"user_execute":true,"group_read":true,"group_write":true,"group_execute":true,"other_read":true,"other_write":true,"other_execute":true}'
      );
      expectedFormData.append('path', 'test/path/file1.txt');
      expect(mockSave).toHaveBeenCalledTimes(1);
      expect(mockSave).toHaveBeenCalledWith(expectedFormData);
    });
  });

  it('should call onSuccess when the request is successful', () => {
    mockSave.mockImplementationOnce(() => {
      mockOnSuccess();
    });

    const { getByText } = render(
      <ChangePermissionModal
        isOpen={true}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    fireEvent.click(getByText('Submit'));

    waitFor(() => expect(mockOnSuccess).toHaveBeenCalledTimes(1));
  });

  it('should call onError when the request fails', () => {
    mockSave.mockImplementationOnce(() => {
      mockOnError(new Error('Something went wrong'));
    });

    const { getByText } = render(
      <ChangePermissionModal
        isOpen={true}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    fireEvent.click(getByText('Submit'));

    waitFor(() => expect(mockOnError).toHaveBeenCalledTimes(1));
  });

  it('should call onClose when the modal is closed', () => {
    const { getByText } = render(
      <ChangePermissionModal
        isOpen={true}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    fireEvent.click(getByText('Cancel'));
    waitFor(() => expect(mockOnClose).toHaveBeenCalledTimes(1));
  });

  it('should disable Submit button when the permissions have not been modified', () => {
    const { getByText, getAllByRole } = render(
      <ChangePermissionModal
        isOpen={true}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    const submitButton = getByText('Submit');
    expect(submitButton).not.toBeDisabled();

    const checkboxes = getAllByRole('checkbox');
    fireEvent.click(checkboxes[0]);
    waitFor(() => expect(submitButton).toBeDisabled());
  });
});
