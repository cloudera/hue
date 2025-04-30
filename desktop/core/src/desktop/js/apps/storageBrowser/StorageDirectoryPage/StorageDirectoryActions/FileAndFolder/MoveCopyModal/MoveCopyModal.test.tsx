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
import MoveCopyModal from './MoveCopyModal';
import { ActionType } from '../FileAndFolderActions.util';
import { BULK_COPY_API_URL, BULK_MOVE_API_URL } from '../../../../api';
import { StorageDirectoryTableData } from '../../../../types';

const mockFiles: StorageDirectoryTableData[] = [
  {
    name: 'folder1',
    size: '',
    type: 'dir',
    permission: 'rwxrwxrwx',
    mtime: '2021-01-01 00:00:00',
    path: 'test/path/folder1',
    user: 'test',
    group: 'test',
    replication: 1
  },
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
  }
];

const mockReloadData = jest.fn();
jest.mock('../../../../../../utils/hooks/useLoadData/useLoadData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    data: {
      files: mockFiles
    },
    loading: false,
    error: null,
    reloadData: mockReloadData
  }))
}));

const mockSave = jest.fn();
jest.mock('../../../../../../utils/hooks/useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: mockSave
  }))
}));

const currentPath = 'test/path';

describe('MoveCopy Action Component', () => {
  const mockOnSuccess = jest.fn();
  const mockOnError = jest.fn();
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Copy Actions', () => {
    it('should render correctly and open the modal', () => {
      const { getByText } = render(
        <MoveCopyModal
          isOpen={true}
          action={ActionType.Copy}
          currentPath={currentPath}
          files={mockFiles}
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          onClose={mockOnClose}
        />
      );

      expect(getByText('Copy to')).toBeInTheDocument();
      expect(getByText('Copy')).toBeInTheDocument();
    });

    it('should call handleCopyOrMove with the correct data when the form is submitted', async () => {
      const newDestPath = 'test/path/folder1';

      const { getByText } = render(
        <MoveCopyModal
          isOpen={true}
          action={ActionType.Copy}
          currentPath={currentPath}
          files={mockFiles}
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          onClose={mockOnClose}
        />
      );
      fireEvent.click(getByText('folder1'));
      const copyButton = getByText('Copy');
      await waitFor(() => expect(copyButton).not.toBeDisabled());
      fireEvent.click(copyButton);

      await waitFor(() => expect(mockSave).toHaveBeenCalledTimes(1));

      const formData = new FormData();
      mockFiles.forEach(file => {
        formData.append('source_path', file.path);
      });
      formData.append('destination_path', newDestPath);

      expect(mockSave).toHaveBeenCalledWith(formData, { url: BULK_COPY_API_URL });
    });

    it('should call onSuccess when the request succeeds', async () => {
      mockSave.mockImplementationOnce(mockOnSuccess);
      const { getByText } = render(
        <MoveCopyModal
          isOpen={true}
          action={ActionType.Copy}
          currentPath={currentPath}
          files={mockFiles}
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          onClose={mockOnClose}
        />
      );

      fireEvent.click(getByText('folder1'));
      fireEvent.click(getByText('Copy'));

      await waitFor(() => {
        expect(mockSave).toHaveBeenCalledTimes(1);
        expect(mockOnSuccess).toHaveBeenCalledTimes(1);
      });
    });

    it('should call onError when the request fails', async () => {
      mockSave.mockImplementationOnce(() => {
        mockOnError(new Error());
      });
      const { getByText } = render(
        <MoveCopyModal
          isOpen={true}
          action={ActionType.Copy}
          currentPath={currentPath}
          files={mockFiles}
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          onClose={mockOnClose}
        />
      );

      fireEvent.click(getByText('folder1'));
      fireEvent.click(getByText('Copy'));

      await waitFor(() => {
        expect(mockSave).toHaveBeenCalledTimes(1);
        expect(mockOnError).toHaveBeenCalledTimes(1);
      });
    });

    it('should call onClose when the modal is closed', async () => {
      const { getByText } = render(
        <MoveCopyModal
          isOpen={true}
          action={ActionType.Copy}
          currentPath={currentPath}
          files={mockFiles}
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          onClose={mockOnClose}
        />
      );

      fireEvent.click(getByText('Cancel'));

      await waitFor(() => expect(mockOnClose).toHaveBeenCalledTimes(1));
    });
  });

  describe('Move Actions', () => {
    it('should render correctly and open the modal', () => {
      const { getByText } = render(
        <MoveCopyModal
          isOpen={true}
          action={ActionType.Move}
          currentPath={currentPath}
          files={mockFiles}
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          onClose={mockOnClose}
        />
      );

      expect(getByText('Move to')).toBeInTheDocument();
      expect(getByText('Move')).toBeInTheDocument();
    });

    it('should call handleCopyOrMove with the correct data when the form is submitted', async () => {
      const newDestPath = 'test/path/folder1';

      const { getByText } = render(
        <MoveCopyModal
          isOpen={true}
          action={ActionType.Move}
          currentPath={currentPath}
          files={mockFiles}
          onSuccess={mockOnSuccess}
          onError={mockOnError}
          onClose={mockOnClose}
        />
      );
      fireEvent.click(getByText('folder1'));

      const moveButton = getByText('Move');
      await waitFor(() => expect(moveButton).not.toBeDisabled());
      fireEvent.click(moveButton);

      await waitFor(() => expect(mockSave).toHaveBeenCalledTimes(1));

      const formData = new FormData();
      mockFiles.forEach(file => {
        formData.append('source_path', file.path);
      });
      formData.append('destination_path', newDestPath);

      expect(mockSave).toHaveBeenCalledWith(formData, { url: BULK_MOVE_API_URL });
    });
  });
});
