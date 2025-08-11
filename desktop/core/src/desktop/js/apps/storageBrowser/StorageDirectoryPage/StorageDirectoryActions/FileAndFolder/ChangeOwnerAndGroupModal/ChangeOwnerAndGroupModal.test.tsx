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
import userEvent from '@testing-library/user-event';
import ChangeOwnerAndGroupModal from './ChangeOwnerAndGroupModal';
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

const users = ['user1', 'user2', 'user3'];
const groups = ['group1', 'group2', 'group3'];

describe('ChangeOwnerAndGroupModal Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render correctly and show the modal', () => {
    const { getByText } = render(
      <ChangeOwnerAndGroupModal
        isOpen={true}
        superUser="hadoop-superuser"
        superGroup="hdfs-supergroup"
        users={users}
        groups={groups}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    expect(getByText('Change Owner / Group')).toBeInTheDocument();
    expect(getByText('Submit')).toBeInTheDocument();
    expect(getByText('Cancel')).toBeInTheDocument();
    expect(getByText('User')).toBeInTheDocument();
    expect(getByText('Group')).toBeInTheDocument();
    expect(getByText('Recursive')).toBeInTheDocument();
    expect(
      getByText(
        'Note: Only the Hadoop superuser, "{{superuser}}" or the HDFS supergroup, "{{supergroup}}" on this file system, may change the owner of a file.'
      )
    ).toBeInTheDocument();
  });

  it('should show input fields for custom user when "Others" is selected', async () => {
    const { getAllByRole, getByText, getByPlaceholderText } = render(
      <ChangeOwnerAndGroupModal
        isOpen={true}
        superUser="hadoop-superuser"
        superGroup="hdfs-supergroup"
        users={users}
        groups={groups}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    const [userSelect] = getAllByRole('combobox');

    await userEvent.click(userSelect);
    fireEvent.click(getByText('others'));
    fireEvent.change(userSelect, { target: { value: 'others' } });

    const userInput = getByPlaceholderText('Enter user');
    expect(userInput).toBeInTheDocument();

    fireEvent.change(userInput, { target: { value: 'customUser' } });
    expect(userInput).toHaveValue('customUser');
  });

  it('should show input fields for custom group when "Others" is selected', async () => {
    const { getAllByRole, getByText, getByPlaceholderText } = render(
      <ChangeOwnerAndGroupModal
        isOpen={true}
        superUser="hadoop-superuser"
        superGroup="hdfs-supergroup"
        users={users}
        groups={groups}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    const groupSelect = getAllByRole('combobox')[1];

    await userEvent.click(groupSelect);
    fireEvent.click(getByText('others'));
    fireEvent.change(groupSelect, { target: { value: 'others' } });

    const groupInput = getByPlaceholderText('Enter group');
    expect(groupInput).toBeInTheDocument();

    fireEvent.change(groupInput, { target: { value: 'customGroup' } });
    expect(groupInput).toHaveValue('customGroup');
  });

  it('should toggle the recursive checkbox', () => {
    const { getByRole } = render(
      <ChangeOwnerAndGroupModal
        isOpen={true}
        superUser="hadoop-superuser"
        superGroup="hdfs-supergroup"
        users={users}
        groups={groups}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    const recursiveCheckbox = getByRole('checkbox');
    expect(recursiveCheckbox).not.toBeChecked();
    fireEvent.click(recursiveCheckbox);
    expect(recursiveCheckbox).toBeChecked();
    fireEvent.click(recursiveCheckbox);
    expect(recursiveCheckbox).not.toBeChecked();
  });

  it('should call handleChangeOwner when the form is submitted', async () => {
    const { getByText } = render(
      <ChangeOwnerAndGroupModal
        isOpen={true}
        superUser="hadoop-superuser"
        superGroup="hdfs-supergroup"
        users={users}
        groups={groups}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    fireEvent.click(getByText('Submit'));

    await waitFor(() => {
      const expectedFormData = new FormData();
      expectedFormData.append('user', 'user1');
      expectedFormData.append('group', 'group1');
      expectedFormData.append('path', 'test/path/file1.txt');
      expect(mockSave).toHaveBeenCalledTimes(1);
      expect(mockSave).toHaveBeenCalledWith(expectedFormData);
    });
  });

  it('should call onSuccess when the request is successful', async () => {
    mockSave.mockImplementationOnce(() => {
      mockOnSuccess();
    });

    const { getByText } = render(
      <ChangeOwnerAndGroupModal
        isOpen={true}
        superUser="hadoop-superuser"
        superGroup="hdfs-supergroup"
        users={users}
        groups={groups}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    fireEvent.click(getByText('Submit'));

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledTimes(1);
    });
  });

  it('should call onError when the request fails', async () => {
    mockSave.mockImplementationOnce(() => {
      mockOnError(new Error());
    });

    const { getByText } = render(
      <ChangeOwnerAndGroupModal
        isOpen={true}
        superUser="hadoop-superuser"
        superGroup="hdfs-supergroup"
        users={users}
        groups={groups}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    fireEvent.click(getByText('Submit'));

    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledTimes(1);
    });
  });

  it('should call onClose when the modal is closed', () => {
    const { getByText } = render(
      <ChangeOwnerAndGroupModal
        isOpen={true}
        superUser="hadoop-superuser"
        superGroup="hdfs-supergroup"
        users={users}
        groups={groups}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    fireEvent.click(getByText('Cancel'));
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('should disable submit button when other option is selected and input not provided', async () => {
    const { getAllByRole, getAllByText, getByPlaceholderText, getByRole } = render(
      <ChangeOwnerAndGroupModal
        isOpen={true}
        superUser="hadoop-superuser"
        superGroup="hdfs-supergroup"
        users={users}
        groups={groups}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
      />
    );

    const [userSelect] = getAllByRole('combobox');

    await userEvent.click(userSelect);
    fireEvent.click(getAllByText('others')[0]);
    fireEvent.change(userSelect, { target: { value: 'others' } });

    const submitButton = getByRole('button', { name: /submit/i });
    expect(submitButton).toBeDisabled();

    const userInput = getByPlaceholderText('Enter user');
    fireEvent.change(userInput, { target: { value: 'customUser' } });
    waitFor(() => expect(submitButton).toBeEnabled());
  });
});
