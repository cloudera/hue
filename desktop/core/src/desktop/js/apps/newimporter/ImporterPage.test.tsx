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
import { fireEvent, render, screen, act, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

import ImporterPage from './ImporterPage';
import useSaveData from '../../utils/hooks/useSaveData/useSaveData';
import useLoadData from '../../utils/hooks/useLoadData/useLoadData';

jest.mock('../../utils/hooks/useSaveData/useSaveData');
const mockedUseSaveData = jest.mocked(useSaveData);

jest.mock('../../utils/hooks/useLoadData/useLoadData');
const mockedUseLoadData = jest.mocked(useLoadData);

jest.mock('../../utils/hooks/useDataCatalog/useDataCatalog', () => ({
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

describe('ImporterPage', () => {
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

    (window as Window & { ENABLE_DIRECT_UPLOAD?: boolean }).ENABLE_DIRECT_UPLOAD = true;
  });

  afterEach(() => {
    delete (window as Window & { ENABLE_DIRECT_UPLOAD?: boolean }).ENABLE_DIRECT_UPLOAD;
  });

  it('renders the page with header', () => {
    render(<ImporterPage />);

    expect(screen.getByText('Importer')).toBeInTheDocument();
  });

  it('shows ImporterSourceSelector when no file is selected', () => {
    render(<ImporterPage />);

    expect(screen.getByText('Select a source to import from')).toBeInTheDocument();
    expect(screen.getByText('Upload from File')).toBeInTheDocument();
  });

  it('shows FileImportTabs when file is selected', async () => {
    const mockSave = jest.fn();
    mockedUseSaveData.mockReturnValue({
      save: mockSave,
      loading: false
    });

    render(<ImporterPage />);

    const file = new File(['test content'], 'test.csv', { type: 'text/csv' });

    const fileInput = screen
      .getByRole('button')
      .parentElement?.querySelector('input[type="file"]') as HTMLInputElement;

    expect(fileInput).toBeInTheDocument();

    act(() => {
      Object.defineProperty(fileInput, 'files', {
        value: [file],
        writable: false
      });

      fireEvent.change(fileInput);

      const saveCall = mockSave.mock.calls[0];
      if (saveCall && saveCall[1] && saveCall[1].onSuccess) {
        saveCall[1].onSuccess({
          filePath: '/tmp/test.csv'
        });
      }
    });

    await waitFor(() => {
      expect(screen.getByText('test.csv')).toBeInTheDocument();
      expect(screen.getByText('Preview')).toBeInTheDocument();
    });
  });
});
