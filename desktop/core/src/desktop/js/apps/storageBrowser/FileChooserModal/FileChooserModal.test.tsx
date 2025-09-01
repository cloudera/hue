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
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

import FileChooserModal from './FileChooserModal';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import useSaveData from '../../../utils/hooks/useSaveData/useSaveData';

jest.mock('../../../utils/hooks/useLoadData/useLoadData', () => ({
  __esModule: true,
  default: jest.fn()
}));

jest.mock('../../../utils/hooks/useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn()
}));

const mockReloadData = jest.fn();

const mockData = [
  {
    name: 'testFile',
    path: '/user/testFile',
    type: 'file'
  },
  {
    name: 'testFolder',
    path: '/user/testFolder',
    type: 'dir'
  }
];

describe('FileChooserModal', () => {
  const defaultProps = {
    onClose: jest.fn(),
    onSubmit: jest.fn(() => Promise.resolve()),
    title: 'Select File',
    sourcePath: '/user',
    submitText: 'Submit',
    cancelText: 'Cancel'
  };

  beforeAll(() => {
    jest.clearAllMocks();
  });

  beforeEach(() => {
    (useLoadData as jest.Mock).mockReturnValue({
      data: { files: mockData },
      loading: false,
      error: null,
      reloadData: mockReloadData
    });

    (useSaveData as jest.Mock).mockReturnValue({
      save: jest.fn((_data, { onSuccess }) => onSuccess()),
      loading: false,
      error: null
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders the modal with basic props', async () => {
    render(<FileChooserModal {...defaultProps} showModal />);
    await waitFor(() => {
      expect(screen.getByText('Select File')).toBeInTheDocument();
      expect(screen.getByRole('row', { name: 'testFile' })).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
      expect(screen.getByText('Submit')).toBeInTheDocument();
    });
  });

  test('does not render modal when showModal is false', () => {
    render(<FileChooserModal showModal={false} {...defaultProps} />);
    expect(screen.queryByText('Select File')).not.toBeInTheDocument();
  });

  test('displays empty message if there are no files in the directory', async () => {
    (useLoadData as jest.Mock).mockReturnValueOnce({
      data: { files: [] }, // Empty files array
      loading: false,
      error: null,
      reloadData: mockReloadData
    });
    render(<FileChooserModal showModal {...defaultProps} />);
    await waitFor(() => {
      expect(screen.getByText('Folder is empty')).toBeInTheDocument();
    });
  });

  test('Submit button is disabled if destination path is same as source path', async () => {
    render(<FileChooserModal showModal {...defaultProps} />);

    const submitButton = screen.getByRole('button', { name: 'Submit' });
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    });
  });

  test('Upload button is visible instead of submit if upload is enabled', async () => {
    render(<FileChooserModal showModal {...defaultProps} isUploadEnabled={true} />);

    const submitButton = screen.getByRole('button', { name: 'Upload file' });
    await waitFor(() => {
      expect(submitButton).toBeVisible();
    });
  });

  test('Secondary button create folder is visible', async () => {
    render(<FileChooserModal showModal {...defaultProps} isUploadEnabled={true} />);

    const createFolderButton = screen.getByRole('button', { name: 'Create folder' });
    await waitFor(() => {
      expect(createFolderButton).toBeVisible();
    });
  });

  test('Clicking on create folder opens bottom panel modal', async () => {
    render(<FileChooserModal showModal {...defaultProps} isUploadEnabled={true} />);
    const createFolderButton = screen.getByRole('button', { name: 'Create folder' });
    await waitFor(() => {
      fireEvent.click(createFolderButton);
      expect(screen.getByRole('button', { name: 'Create' })).toBeVisible();
    });
  });
});
