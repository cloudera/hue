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
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ImporterFilePreview from './ImporterFilePreview';
import { FileMetaData, ImporterFileSource } from '../types';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import { mocked } from 'jest-mock';

// Minimal mock data for basic rendering tests
const mockPreviewData = {
  columns: [
    { name: 'Name', type: 'string' },
    { name: 'Age', type: 'int' }
  ],
  previewData: {
    Name: ['Alice', 'Bob'],
    Age: ['30', '25']
  }
};

jest.mock('../../../utils/hooks/useLoadData/useLoadData');
// Simple mock for useSaveData hook
jest.mock('../../../utils/hooks/useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: jest.fn(),
    loading: false
  }))
}));

// Simple mock for useDataCatalog hook - only provide what's needed for basic rendering
jest.mock('../../../utils/hooks/useDataCatalog/useDataCatalog', () => ({
  useDataCatalog: jest.fn(() => ({
    loading: false,
    databases: [],
    connectors: [],
    computes: [],
    setCompute: jest.fn(),
    setConnector: jest.fn(),
    setDatabase: jest.fn()
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
    // Simplified mock for useLoadData - provide minimal data needed for basic rendering
    (mocked(useLoadData) as jest.MockedFunction<typeof useLoadData>).mockReturnValue({
      loading: false,
      data: mockPreviewData,
      reloadData: jest.fn()
    });
  });

  it('should render preview section and edit columns button', () => {
    render(<ImporterFilePreview fileMetaData={mockFileMetaData} />);

    // Check for key elements without complex interactions
    expect(screen.getByText('Preview')).toBeInTheDocument();
    expect(screen.getByText('Edit Columns')).toBeInTheDocument();
  });

  it('should render basic action buttons', () => {
    render(<ImporterFilePreview fileMetaData={mockFileMetaData} />);

    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.getByText('Finish Import')).toBeInTheDocument();
  });

  it('should render data table when preview data is available', () => {
    render(<ImporterFilePreview fileMetaData={mockFileMetaData} />);

    const table = screen.getByRole('table');
    expect(table).toBeInTheDocument();
  });

  it('should open edit columns modal when button is clicked', async () => {
    render(<ImporterFilePreview fileMetaData={mockFileMetaData} />);

    const editColumnsButton = screen.getByText('Edit Columns');
    await userEvent.click(editColumnsButton);

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });
  });
});
