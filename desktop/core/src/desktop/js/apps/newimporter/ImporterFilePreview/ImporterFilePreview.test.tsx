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
import { FileMetaData, ImporterFileSource } from '../types';
import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';
import { mocked } from 'jest-mock';

const mockFileFormatData = {
  type: 'csv',
  fieldSeparator: ',',
  quoteChar: '"',
  recordSeparator: '\n',
  hasHeader: true,
  sheetNames: ['Sheet1'],
  selectedSheetName: 'Sheet1'
};

const mockHeaderData = {
  hasHeader: true
};

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
    databases: ['database1', 'database2'],
    database: 'database1',
    connectors: [
      { id: 'hive', displayName: 'Hive' },
      { id: 'spark', displayName: 'Spark' }
    ],
    connector: { id: 'hive', displayName: 'Hive' },
    computes: [
      { id: 'compute1', name: 'Compute 1' },
      { id: 'compute2', name: 'Compute 2' }
    ],
    compute: { id: 'compute1', name: 'Compute 1' },
    setCompute: jest.fn(),
    setConnector: jest.fn(),
    setDatabase: jest.fn()
  }))
}));

jest.mock('./DestinationSettings/DestinationSettings', () => {
  return function MockDestinationSettings({
    onChange
  }: {
    defaultValues?: Record<string, unknown>;
    onChange: (name: string, value: string) => void;
  }) {
    const React = require('react');

    React.useEffect(() => {
      onChange('connectorId', 'hive');
      onChange('database', 'database1');
      onChange('computeId', 'compute1');
    }, []); // Empty dependency array to only run once

    return React.createElement(
      'div',
      { className: 'importer-destination-settings' },
      React.createElement('div', null, 'Destination Settings Mock')
    );
  };
});

describe('ImporterFilePreview', () => {
  const mockFileMetaData: FileMetaData = {
    source: ImporterFileSource.LOCAL,
    path: '/path/to/file.csv',
    fileName: 'file.csv'
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mocked(useLoadData).mockImplementation((url?: string) => {
      if (url === '/api/v1/importer/file/guess_metadata') {
        return {
          loading: false,
          data: mockFileFormatData,
          reloadData: jest.fn()
        };
      }
      if (url === '/api/v1/importer/file/guess_header') {
        return {
          loading: false,
          data: mockHeaderData,
          reloadData: jest.fn()
        };
      }
      if (url === '/api/v1/importer/file/preview') {
        return {
          loading: false,
          data: mockPreviewData,
          reloadData: jest.fn()
        };
      }
      return {
        loading: false,
        data: ['STRING', 'INT', 'FLOAT'],
        reloadData: jest.fn()
      };
    });
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
    render(<ImporterFilePreview fileMetaData={mockFileMetaData} />);

    expect(screen.getByText('Preview')).toBeInTheDocument();
    expect(screen.getByText('Edit Columns')).toBeInTheDocument();

    const table = screen.getByRole('table');
    expect(table).toBeInTheDocument();
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

    const cancelButton = screen.getByRole('button', { name: 'Cancel' });
    expect(cancelButton).toBeInTheDocument();
  });

  it('should handle complete file format workflow', async () => {
    await act(async () => {
      render(<ImporterFilePreview fileMetaData={mockFileMetaData} />);
    });

    await waitFor(() => {
      expect(screen.getByText('Preview')).toBeInTheDocument();
      expect(screen.getByRole('table')).toBeInTheDocument();
    });
  });
});
