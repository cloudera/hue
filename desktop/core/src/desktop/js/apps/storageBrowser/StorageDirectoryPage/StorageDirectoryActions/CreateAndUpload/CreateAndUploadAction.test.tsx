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
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import CreateAndUploadAction from './CreateAndUploadAction';
import { CREATE_DIRECTORY_API_URL, CREATE_FILE_API_URL } from '../../../api';
import * as storageUtils from '../../../utils/utils';

const mockSave = jest.fn();
jest.mock('../../../../../utils/hooks/useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: mockSave,
    loading: false,
    error: undefined
  }))
}));

describe('CreateAndUploadAction', () => {
  const defaultPath = '/some/path';
  const onActionSuccess = jest.fn();
  const onActionError = jest.fn();
  const mockFilesUpload = jest.fn();

  const setup = (path = defaultPath) =>
    render(
      <CreateAndUploadAction
        currentPath={path}
        onActionSuccess={onActionSuccess}
        onFilesUpload={mockFilesUpload}
        onActionError={onActionError}
      />
    );

  const openDropdown = async user => {
    await user.click(screen.getByRole('button', { name: 'New' }));
  };

  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(storageUtils, 'isS3').mockReturnValue(false);
    jest.spyOn(storageUtils, 'isGS').mockReturnValue(false);
    jest.spyOn(storageUtils, 'isABFS').mockReturnValue(false);
    jest.spyOn(storageUtils, 'isOFS').mockReturnValue(false);
  });

  const clickMenuOption = async (label: string, user) => {
    await openDropdown(user);
    await user.click(screen.getByRole('menuitem', { name: label }));
  };

  afterEach(() => {
    cleanup();
  });

  it('renders the New button', () => {
    setup();
    const newButton = screen.getByRole('button', { name: 'New' });
    expect(newButton).toBeInTheDocument();
  });

  it('should render the dropdown with CREATE and UPLOAD group actions', async () => {
    const user = userEvent.setup();
    setup();
    await openDropdown(user);
    // Check that the "Create" and "Upload" groups are in the dropdown
    expect(screen.getByText('CREATE')).toBeInTheDocument();
    expect(screen.getByText('UPLOAD')).toBeInTheDocument();
  });

  describe('create actions', () => {
    it.each([
      { label: 'New Folder', modalTitle: 'Create Folder', api: CREATE_DIRECTORY_API_URL },
      { label: 'New File', modalTitle: 'Create File', api: CREATE_FILE_API_URL }
    ])('opens ${label} modal and calls correct API', async ({ label, modalTitle, api }) => {
      const user = userEvent.setup();
      setup();
      await clickMenuOption(label, user);

      expect(screen.getByText(modalTitle)).toBeInTheDocument();

      const input = screen.getByRole('textbox');
      fireEvent.change(input, { target: { value: `Test ${label}` } });

      fireEvent.click(screen.getByRole('button', { name: 'Create' }));

      await waitFor(() => {
        expect(mockSave).toHaveBeenCalledWith(
          { path: defaultPath, name: `Test ${label}` },
          { url: api }
        );
      });
    });
  });

  describe('upload actions', () => {
    it('should render hidden file input for upload functionality', async () => {
      setup();
      const fileInput = document.querySelector('input[type="file"]');
      expect(fileInput).toBeInTheDocument();
      expect(fileInput).toHaveAttribute('hidden');
      expect(fileInput).toHaveAttribute('multiple');
    });

    it('should handle file selection and call onFilesUpload', async () => {
      setup();
      const fileInput = document.querySelector('input[type="file"]');
      expect(fileInput).toBeInTheDocument();

      const file1 = new File(['test content 1'], 'test1.txt', { type: 'text/plain' });
      const file2 = new File(['test content 2'], 'test2.txt', { type: 'text/plain' });

      fireEvent.change(fileInput!, {
        target: { files: [file1, file2] }
      });

      expect(mockFilesUpload).toHaveBeenCalledWith([file1, file2]);
    });
  });

  describe('storage-specific actions', () => {
    it('shows New Bucket when S3 root', async () => {
      const user = userEvent.setup();
      jest.spyOn(storageUtils, 'isS3').mockReturnValue(true);
      jest.spyOn(storageUtils, 'isS3Root').mockReturnValue(true);

      setup('/');
      await openDropdown(user);
      expect(screen.getByRole('menuitem', { name: 'New Bucket' })).toBeInTheDocument();
    });

    it('shows New Bucket when OFS root', async () => {
      const user = userEvent.setup();
      jest.spyOn(storageUtils, 'isOFS').mockReturnValue(true);
      jest.spyOn(storageUtils, 'isOFSRoot').mockReturnValue(true);

      setup('/');
      await openDropdown(user);
      expect(screen.getByRole('menuitem', { name: 'New Bucket' })).toBeInTheDocument();
    });

    it('does not show New Bucket when not in S3 root', async () => {
      const user = userEvent.setup();
      jest.spyOn(storageUtils, 'isS3').mockReturnValue(true);
      jest.spyOn(storageUtils, 'isS3Root').mockReturnValue(false);

      setup('s3://user');
      await openDropdown(user);
      expect(screen.queryByRole('menuitem', { name: 'New Bucket' })).not.toBeInTheDocument();
    });

    it('shows New File System when ABFS root', async () => {
      const user = userEvent.setup();
      jest.spyOn(storageUtils, 'isABFS').mockReturnValue(true);
      jest.spyOn(storageUtils, 'isABFSRoot').mockReturnValue(true);

      setup('/');
      await openDropdown(user);
      expect(screen.getByRole('menuitem', { name: 'New File System' })).toBeInTheDocument();
    });

    it('shows New Volume when OFS service ID', async () => {
      const user = userEvent.setup();
      jest.spyOn(storageUtils, 'isOFS').mockReturnValue(true);
      jest.spyOn(storageUtils, 'isOFSServiceID').mockReturnValue(true);

      setup('/ofs-service');
      await openDropdown(user);
      expect(screen.getByRole('menuitem', { name: 'New Volume' })).toBeInTheDocument();
    });

    it('does not show New Volume when OFS service ID', async () => {
      const user = userEvent.setup();
      jest.spyOn(storageUtils, 'isOFS').mockReturnValue(true);
      jest.spyOn(storageUtils, 'isOFSServiceID').mockReturnValue(false);

      setup('/ofs-service');
      await openDropdown(user);
      expect(screen.queryByRole('menuitem', { name: 'New Volume' })).not.toBeInTheDocument();
    });
  });
});
