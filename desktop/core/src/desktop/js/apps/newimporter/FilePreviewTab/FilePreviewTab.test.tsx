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
import FilePreviewTab from './FilePreviewTab';
import { FileMetaData, ImporterFileSource } from '../types';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import { mocked } from 'jest-mock';

const mockPreviewData = {
  columns: [
    { name: 'Name', type: 'string' },
    { name: 'Age', type: 'int' }
  ],
  previewData: {
    name: ['Alice', 'Bob'],
    age: ['30', '25']
  }
};

jest.mock('../../../utils/hooks/useLoadData/useLoadData');
jest.mock('../../../utils/hooks/useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: jest.fn(),
    loading: false
  }))
}));

jest.mock('../../../utils/hooks/useDataCatalog/useDataCatalog', () => ({
  useDataCatalog: jest.fn(() => ({
    loading: false,
    databases: [{ name: 'default' }],
    connectors: [{ id: 'hive', displayName: 'Hive' }],
    computes: [{ id: 'compute1', name: 'Compute 1' }],
    setCompute: jest.fn(),
    setConnector: jest.fn(),
    setDatabase: jest.fn()
  }))
}));

describe('FilePreviewTab', () => {
  const mockFileMetaData: FileMetaData = {
    source: ImporterFileSource.LOCAL,
    path: '/path/to/file.csv',
    fileName: 'file.csv'
  };

  const mockDestinationConfig = {
    tableName: 'test_table',
    connectorId: 'hive',
    database: 'default',
    computeId: 'compute1'
  };

  const mockOnDestinationConfigChange = jest.fn();

  const renderComponent = () =>
    render(
      <FilePreviewTab
        fileMetaData={mockFileMetaData}
        destinationConfig={mockDestinationConfig}
        onDestinationConfigChange={mockOnDestinationConfigChange}
      />
    );

  beforeEach(() => {
    jest.clearAllMocks();
    (mocked(useLoadData) as jest.MockedFunction<typeof useLoadData>).mockReturnValue({
      loading: false,
      data: mockPreviewData,
      reloadData: jest.fn()
    });
  });

  it('should render correctly', async () => {
    const user = userEvent.setup();
    renderComponent();

    await waitFor(() => {
      const editColumnsButton = screen.getByRole('button', { name: 'Edit Columns' });
      expect(editColumnsButton).toBeInTheDocument();
      expect(editColumnsButton).toBeVisible();
    });

    const editColumnsButton = screen.getByRole('button', { name: 'Edit Columns' });

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();

    await user.click(editColumnsButton);

    await waitFor(() => {
      const modal = screen.getByRole('dialog');
      expect(modal).toBeVisible();
      expect(modal).toHaveTextContent('Edit Columns');
    });
  });

  it('should display data in the table after previewData is available', async () => {
    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Alice')).toBeVisible();
      expect(screen.getByText('30')).toBeVisible();
      expect(screen.getByText('Bob')).toBeVisible();
      expect(screen.getByText('25')).toBeVisible();
    });
  });

  it('should close edit columns modal when Cancel button is clicked', async () => {
    const user = userEvent.setup();
    renderComponent();

    const editColumnsButton = screen.getByRole('button', { name: 'Edit Columns' });
    await user.click(editColumnsButton);

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeVisible();
    });

    const cancelButton = screen.getByRole('button', { name: 'Cancel' });
    await user.click(cancelButton);

    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });
});
