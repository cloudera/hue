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
import DeletionModal from './DeletionModal';
import { StorageDirectoryTableData } from '../../../../types';
import { BULK_DELETION_API_URL, DELETION_API_URL } from '../../../../api';

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
const mockLoading = jest.fn().mockReturnValue(false);
jest.mock('../../../../../../utils/hooks/useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: mockSave,
    loading: mockLoading()
  }))
}));

describe('DeletionModal Component', () => {
  const mockOnSuccess = jest.fn();
  const mockOnError = jest.fn();
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the Delete modal with the correct title and buttons', () => {
    const { getByText, getByRole } = render(
      <DeletionModal
        isOpen={true}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        isTrashEnabled={true}
      />
    );

    expect(getByText('Confirm Delete')).toBeInTheDocument();
    expect(getByText('Move to Trash')).toBeInTheDocument();
    expect(getByText('Delete Permanently')).toBeInTheDocument();
    expect(getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
  });

  it('should render the Delete modal with the correct title and buttons when trash is not enabled', () => {
    const { getByText, queryByText, getByRole } = render(
      <DeletionModal
        isOpen={true}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        isTrashEnabled={false}
      />
    );

    expect(getByText('Confirm Delete')).toBeInTheDocument();
    expect(queryByText('Move to Trash')).not.toBeVisible();
    expect(getByText('Delete Permanently')).toBeInTheDocument();
    expect(getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
  });

  it('should call handleDeletion with the correct data for single delete when "Delete Permanently" is clicked', async () => {
    const { getByText } = render(
      <DeletionModal
        isOpen={true}
        files={[mockFiles[0]]}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        isTrashEnabled={false}
      />
    );

    fireEvent.click(getByText('Delete Permanently'));

    const formData = new FormData();
    formData.append('path', mockFiles[0].path);
    formData.append('skip_trash', 'true');

    expect(mockSave).toHaveBeenCalledWith(formData, { url: DELETION_API_URL });
  });

  it('should call handleDeletion with the correct data for bulk delete when "Delete Permanently" is clicked', async () => {
    const { getByText } = render(
      <DeletionModal
        isOpen={true}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        isTrashEnabled={false}
      />
    );

    fireEvent.click(getByText('Delete Permanently'));

    const formData = new FormData();
    mockFiles.forEach(file => {
      formData.append('path', file.path);
    });
    formData.append('skip_trash', 'true');

    expect(mockSave).toHaveBeenCalledWith(formData, { url: BULK_DELETION_API_URL });
  });

  it('should call handleDeletion with the correct data for trash delete when "Move to Trash" is clicked', async () => {
    const { getByText } = render(
      <DeletionModal
        isOpen={true}
        files={[mockFiles[0]]}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        isTrashEnabled={true}
      />
    );

    fireEvent.click(getByText('Move to Trash'));

    const formData = new FormData();
    formData.append('path', mockFiles[0].path);

    expect(mockSave).toHaveBeenCalledWith(formData, { url: DELETION_API_URL });
  });

  it('should call handleDeletion with the correct data for bulk trash delete when "Move to Trash" is clicked', async () => {
    const { getByText } = render(
      <DeletionModal
        isOpen={true}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        isTrashEnabled={true}
      />
    );

    fireEvent.click(getByText('Move to Trash'));

    const formData = new FormData();
    mockFiles.forEach(file => {
      formData.append('path', file.path);
    });

    expect(mockSave).toHaveBeenCalledWith(formData, { url: BULK_DELETION_API_URL });
  });

  it('should call onError when the delete request fails', async () => {
    mockSave.mockImplementationOnce(() => {
      mockOnError(new Error());
    });
    const { getByText } = render(
      <DeletionModal
        isOpen={true}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        isTrashEnabled={true}
      />
    );

    fireEvent.click(getByText('Move to Trash'));

    expect(mockOnError).toHaveBeenCalledTimes(1);
  });

  it('should call onClose when the modal is closed', () => {
    const { getByText } = render(
      <DeletionModal
        isOpen={true}
        files={mockFiles}
        onSuccess={mockOnSuccess}
        onError={mockOnError}
        onClose={mockOnClose}
        isTrashEnabled={true}
      />
    );

    fireEvent.click(getByText('Cancel'));

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  describe('Loading and Disabled States', () => {
    describe('When trash is enabled', () => {
      it('should show normal state when not loading', () => {
        mockLoading.mockReturnValue(false);

        const { getByRole } = render(
          <DeletionModal
            isOpen={true}
            files={mockFiles}
            onSuccess={mockOnSuccess}
            onError={mockOnError}
            onClose={mockOnClose}
            isTrashEnabled={true}
          />
        );

        const moveToTrashButton = getByRole('button', { name: 'Move to Trash' });
        const deletePermButton = getByRole('button', { name: 'Delete Permanently' });
        const cancelButton = getByRole('button', { name: 'Cancel' });

        expect(moveToTrashButton).not.toBeDisabled();
        expect(deletePermButton).not.toBeDisabled();
        expect(cancelButton).not.toBeDisabled();

        expect(moveToTrashButton).not.toHaveClass('ant-btn-loading');
        expect(deletePermButton).not.toHaveClass('ant-btn-loading');
      });

      it('should disable modal close when loading', () => {
        mockLoading.mockReturnValue(true);

        const { container } = render(
          <DeletionModal
            isOpen={true}
            files={mockFiles}
            onSuccess={mockOnSuccess}
            onError={mockOnError}
            onClose={mockOnClose}
            isTrashEnabled={true}
          />
        );

        const closeButton = container.querySelector('.ant-modal-close');
        expect(closeButton).not.toBeInTheDocument();
      });

      it('should show correct button states when loading is true', () => {
        mockLoading.mockReturnValue(true);

        const { getByRole } = render(
          <DeletionModal
            isOpen={true}
            files={mockFiles}
            onSuccess={mockOnSuccess}
            onError={mockOnError}
            onClose={mockOnClose}
            isTrashEnabled={true}
          />
        );

        const moveToTrashButton = getByRole('button', { name: 'Move to Trash' });
        // Initially isMoveTrashClicked is false, so "Delete Permanently" should show loading
        const deletePermButton = getByRole('button', { name: 'loading Delete Permanently' });
        const cancelButton = getByRole('button', { name: 'Cancel' });

        expect(moveToTrashButton).toBeDisabled();
        expect(deletePermButton).toHaveClass('ant-btn-loading');
        expect(cancelButton).toBeDisabled();
      });
    });

    describe('When trash is disabled', () => {
      it('should disable modal close when loading', () => {
        mockLoading.mockReturnValue(true);

        const { container } = render(
          <DeletionModal
            isOpen={true}
            files={mockFiles}
            onSuccess={mockOnSuccess}
            onError={mockOnError}
            onClose={mockOnClose}
            isTrashEnabled={false}
          />
        );

        const closeButton = container.querySelector('.ant-modal-close');
        expect(closeButton).not.toBeInTheDocument();
      });

      it('should show normal state when not loading', () => {
        mockLoading.mockReturnValue(false);

        const { getByRole, queryByRole } = render(
          <DeletionModal
            isOpen={true}
            files={mockFiles}
            onSuccess={mockOnSuccess}
            onError={mockOnError}
            onClose={mockOnClose}
            isTrashEnabled={false}
          />
        );

        const deletePermButton = getByRole('button', { name: 'Delete Permanently' });
        const cancelButton = getByRole('button', { name: 'Cancel' });

        expect(queryByRole('button', { name: 'Move to Trash' })).not.toBeInTheDocument();
        expect(deletePermButton).not.toBeDisabled();
        expect(cancelButton).not.toBeDisabled();

        expect(deletePermButton).not.toHaveClass('ant-btn-loading');
      });

      it('should show correct button states when loading is true', () => {
        mockLoading.mockReturnValue(true);

        const { getByRole, queryByRole } = render(
          <DeletionModal
            isOpen={true}
            files={mockFiles}
            onSuccess={mockOnSuccess}
            onError={mockOnError}
            onClose={mockOnClose}
            isTrashEnabled={false}
          />
        );

        const deletePermButton = getByRole('button', { name: 'loading Delete Permanently' });
        const cancelButton = getByRole('button', { name: 'Cancel' });

        expect(queryByRole('button', { name: 'Move to Trash' })).not.toBeInTheDocument();

        expect(deletePermButton).toHaveClass('ant-btn-loading');
        expect(cancelButton).toBeDisabled();
      });
    });
  });
});
