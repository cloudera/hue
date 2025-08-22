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
import { render, screen, fireEvent, waitFor, act, cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';
import CreateAndUploadAction from './CreateAndUploadAction';
import { CREATE_DIRECTORY_API_URL, CREATE_FILE_API_URL } from '../../../api';
import * as storageUtils from '../../../../../utils/storageBrowserUtils';

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

  const openDropdown = async () => {
    await act(async () => fireEvent.click(screen.getByRole('button', { name: 'New' })));
  };

  const clickMenuOption = async (label: string) => {
    await openDropdown();
    await act(async () => fireEvent.click(screen.getByText(label)));
  };

  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(storageUtils, 'isS3').mockReturnValue(false);
    jest.spyOn(storageUtils, 'isGS').mockReturnValue(false);
    jest.spyOn(storageUtils, 'isABFS').mockReturnValue(false);
    jest.spyOn(storageUtils, 'isOFS').mockReturnValue(false);
  });

  afterEach(() => {
    cleanup();
  });

  it('renders the New button', () => {
    setup();
    const newButton = screen.getByRole('button', { name: 'New' });
    expect(newButton).toBeInTheDocument();
  });

  it('should render the dropdown with CREATE and UPLOAD group actions', async () => {
    setup();
    await openDropdown();
    // Check that the "Create" and "Upload" groups are in the dropdown
    expect(screen.getByText('CREATE')).toBeInTheDocument();
    expect(screen.getByText('UPLOAD')).toBeInTheDocument();
  });

  describe('create actions', () => {
    it.each([
      { label: 'New Folder', modalTitle: 'Create Folder', api: CREATE_DIRECTORY_API_URL },
      { label: 'New File', modalTitle: 'Create File', api: CREATE_FILE_API_URL }
    ])('opens ${label} modal and calls correct API', async ({ label, modalTitle, api }) => {
      setup();
      await clickMenuOption(label);

      expect(screen.getByText(modalTitle)).toBeInTheDocument();

      const input = screen.getByRole('textbox');
      fireEvent.change(input, { target: { value: `Test ${label}` } });

      fireEvent.click(screen.getByText('Create'));

      await waitFor(() => {
        expect(mockSave).toHaveBeenCalledWith(
          { path: defaultPath, name: `Test ${label}` },
          { url: api }
        );
      });
    });
  });

  describe('upload actions', () => {
    it('opens upload modal when "Upload File" is clicked', async () => {
      setup();
      await clickMenuOption('Upload File');
      expect(screen.getByText('Upload a File')).toBeInTheDocument();
    });
  });

  describe('storage-specific actions', () => {
    it('shows Create Bucket when S3 root', async () => {
      jest.spyOn(storageUtils, 'isS3').mockReturnValue(true);
      jest.spyOn(storageUtils, 'isS3Root').mockReturnValue(true);

      setup('/');
      await openDropdown();
      expect(screen.getByText('New Bucket')).toBeInTheDocument();
    });

    it('shows Create File System when ABFS root', async () => {
      jest.spyOn(storageUtils, 'isABFS').mockReturnValue(true);
      jest.spyOn(storageUtils, 'isABFSRoot').mockReturnValue(true);

      setup('/');
      await openDropdown();
      expect(screen.getByText('New File System')).toBeInTheDocument();
    });

    it('shows Create Volume when OFS service ID', async () => {
      jest.spyOn(storageUtils, 'isOFS').mockReturnValue(true);
      jest.spyOn(storageUtils, 'isOFSServiceID').mockReturnValue(true);

      setup('/ofs-service');
      await openDropdown();
      expect(screen.getByText('New Volume')).toBeInTheDocument();
    });
  });
});
