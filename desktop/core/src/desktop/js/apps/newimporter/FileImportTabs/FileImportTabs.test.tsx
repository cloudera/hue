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
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

import FileImportTabs from './FileImportTabs';
import { FileMetaData, ImporterFileSource } from '../types';
import useSaveData from '../../../utils/hooks/useSaveData/useSaveData';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';

jest.mock('../../../utils/hooks/useSaveData/useSaveData');
const mockedUseSaveData = jest.mocked(useSaveData);

jest.mock('../../../utils/hooks/useLoadData/useLoadData');
const mockedUseLoadData = jest.mocked(useLoadData);

jest.mock('../../../utils/hooks/useDataCatalog/useDataCatalog', () => ({
  useDataCatalog: jest.fn(() => ({
    loading: false,
    databases: ['default'],
    database: 'default',
    connectors: [{ id: 'hive', displayName: 'Hive' }],
    connector: { id: 'hive', displayName: 'Hive' },
    computes: [{ id: 'compute1', name: 'Compute 1' }],
    compute: { id: 'compute1', name: 'Compute 1' },
    setCompute: jest.fn(),
    setConnector: jest.fn(),
    setDatabase: jest.fn()
  }))
}));

describe('FileImportTabs', () => {
  const mockFileMetaData: FileMetaData = {
    path: '/test/path/file.csv',
    fileName: 'file.csv',
    source: ImporterFileSource.LOCAL
  };

  const defaultProps = {
    fileMetaData: mockFileMetaData
  };

  beforeEach(() => {
    jest.clearAllMocks();

    mockedUseSaveData.mockReturnValue({
      save: jest.fn(),
      loading: false
    });

    mockedUseLoadData.mockReturnValue({
      data: undefined,
      loading: false,
      error: undefined,
      reloadData: jest.fn()
    });
  });

  it('renders the component with header and tabs', async () => {
    render(<FileImportTabs {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText('file.csv')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
      expect(screen.getByText('Finish Import')).toBeInTheDocument();
      expect(screen.getByText('Preview')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
      expect(screen.getByText('Partitions')).toBeInTheDocument();
    });
  });

  it('renders FilePreviewTab in the Preview tab by default', async () => {
    render(<FileImportTabs {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText('Preview')).toBeInTheDocument();
      expect(screen.getByLabelText('Engine')).toBeInTheDocument();
    });
  });

  it('starts with custom default active tab', async () => {
    render(<FileImportTabs {...defaultProps} />);

    await waitFor(() => {
      expect(screen.getByText('Settings')).toBeInTheDocument();
    });
  });

  it('has finish import button that calls save function', async () => {
    const mockSave = jest.fn();
    mockedUseSaveData.mockReturnValue({
      save: mockSave,
      loading: false
    });

    render(<FileImportTabs {...defaultProps} />);

    const finishButton = screen.getByText('Finish Import');
    fireEvent.click(finishButton);

    const expectedFormData = new FormData();
    expectedFormData.append(
      'source',
      JSON.stringify({
        inputFormat: 'local',
        path: '/test/path/file.csv',
        sourceType: 'hive'
      })
    );
    expectedFormData.append(
      'destination',
      JSON.stringify({
        outputFormat: 'table',
        nonDefaultLocation: '/test/path/file.csv',
        name: 'default.file',
        sourceType: 'hive'
      })
    );
    await waitFor(() => {
      expect(mockSave).toHaveBeenCalledWith(expectedFormData);
    });
  });

  it('shows loading state on finish import button', async () => {
    mockedUseSaveData.mockReturnValue({
      save: jest.fn(),
      loading: true
    });

    render(<FileImportTabs {...defaultProps} />);

    const finishButton = screen.getByText('Finish Import');
    await waitFor(() => {
      expect(finishButton.closest('button')).toHaveClass('ant-btn-loading');
    });
  });
});
