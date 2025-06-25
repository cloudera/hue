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
import '@testing-library/jest-dom';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ImporterFilePreview from './ImporterFilePreview';
import { FileMetaData, ImporterFileSource, ImporterFileTypes } from '../types';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import { mocked } from 'jest-mock';

const mockPreviewData = jest.fn().mockReturnValue({
  columns: [{ name: 'Name' }, { name: 'Age' }],
  previewData: {
    name: ['Alice', 'Bob'],
    age: ['30', '25']
  }
});

jest.mock('../../../utils/hooks/useLoadData/useLoadData');
jest.mock('../../../utils/hooks/useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: jest.fn(),
    loading: false
  }))
}));

describe('ImporterFilePreview', () => {
  const mockFileMetaData: FileMetaData = {
    source: ImporterFileSource.LOCAL,
    path: '/path/to/file.csv',
    fileName: 'file.csv'
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mocked(useLoadData).mockImplementation(() => ({
      loading: false,
      data: mockPreviewData(),
      reloadData: jest.fn()
    }));
  });

  it('should render correctly', async () => {
    await act(async () => {
      render(<ImporterFilePreview fileMetaData={mockFileMetaData} />);
    });

    await waitFor(() => {
      expect(screen.getByText('Preview')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
      expect(screen.getByText('Finish Import')).toBeInTheDocument();
    });
  });

  it('should display data in the table after previewData is available', async () => {
    await act(async () => {
      render(<ImporterFilePreview fileMetaData={mockFileMetaData} />);
    });

    await waitFor(() => {
      expect(screen.getByText('Alice')).toBeInTheDocument();
      expect(screen.getByText('30')).toBeInTheDocument();
      expect(screen.getByText('Bob')).toBeInTheDocument();
      expect(screen.getByText('25')).toBeInTheDocument();
    });
  });

  it('should open edit columns modal when button is clicked', async () => {
    await act(async () => {
      render(<ImporterFilePreview fileMetaData={mockFileMetaData} />);
    });

    const editColumnsButton = screen.getByText('Edit Columns');

    await act(async () => {
      await userEvent.click(editColumnsButton);
    });

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });
  });

  it('should display source configuration', async () => {
    await act(async () => {
      render(<ImporterFilePreview fileMetaData={mockFileMetaData} />);
    });

    expect(screen.getByText('Configure source')).toBeInTheDocument();
  });

  it('should display cancel button', async () => {
    await act(async () => {
      render(<ImporterFilePreview fileMetaData={mockFileMetaData} />);
    });

    const cancelButton = screen.getByTestId('hue-importer-preview-page__header__actions__cancel');
    expect(cancelButton).toBeInTheDocument();
    expect(cancelButton).toHaveTextContent('Cancel');
  });

  it('should handle complete file format workflow', async () => {
    mocked(useLoadData).mockImplementation(() => ({
      loading: false,
      data: mockPreviewData(),
      reloadData: jest.fn()
    }));

    await act(async () => {
      render(<ImporterFilePreview fileMetaData={mockFileMetaData} />);
    });

    await waitFor(() => {
      expect(screen.getByText('Preview')).toBeInTheDocument();
      expect(screen.getByText('Alice')).toBeInTheDocument();
      expect(screen.getByText('Bob')).toBeInTheDocument();
    });
  });
});
