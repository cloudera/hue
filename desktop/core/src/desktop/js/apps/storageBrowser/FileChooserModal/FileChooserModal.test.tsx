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
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

import FileChooserModal from './FileChooserModal';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';

jest.mock('../../../utils/hooks/useLoadData/useLoadData', () => ({
  __esModule: true,
  default: jest.fn()
}));

const mockReloadData = jest.fn();

const mockData = [
  {
    name: 'test',
    path: 'user/test',
    type: 'file'
  },
  {
    name: 'testFolder',
    path: 'user/testFolder',
    type: 'dir'
  }
];

describe('FileChooserModal', () => {
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
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders the modal with basic props', async () => {
    render(
      <FileChooserModal
        showModal={true}
        onClose={() => {}}
        onSubmit={() => {}}
        title="Select File"
        sourcePath="/path/to/source"
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Select File')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
      expect(screen.getByText('Submit')).toBeInTheDocument();
    });
  });

  test('displays empty message if there are no files in the directory', async () => {
    (useLoadData as jest.Mock).mockReturnValueOnce({
      data: { files: [] }, // Empty files array
      loading: false,
      error: null,
      reloadData: mockReloadData
    });
    render(
      <FileChooserModal
        showModal={true}
        onClose={() => {}}
        onSubmit={() => {}}
        title="Select File"
        sourcePath="/path/to/source"
      />
    );
    await waitFor(() => {
      expect(screen.getByText('Folder is empty')).toBeInTheDocument();
    });
  });

  test('Submit button is disabled if destination path is same as source path', async () => {
    const mockOnSubmit = jest.fn();
    render(
      <FileChooserModal
        showModal={true}
        onClose={() => {}}
        onSubmit={mockOnSubmit}
        title="Select File"
        sourcePath="/path/to/source"
      />
    );

    const submitButton = screen.getByRole('button', { name: 'Submit' });
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    });
  });
});
