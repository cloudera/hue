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
import { render, fireEvent, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import DestinationSettings from './DestinationSettings';
import { DestinationConfig } from '../../types';
import { useDataCatalog } from '../../../../utils/hooks/useDataCatalog/useDataCatalog';

const mockUseDataCatalog = {
  loading: false,
  databases: ['database1', 'database2'],
  database: 'database1',
  connectors: [
    { id: 'connector1', displayName: 'Connector 1' },
    { id: 'connector2', displayName: 'Connector 2' }
  ],
  connector: { id: 'connector1', displayName: 'Connector 1' },
  computes: [
    { id: 'compute1', name: 'Compute 1' },
    { id: 'compute2', name: 'Compute 2' }
  ],
  compute: { id: 'compute1', name: 'Compute 1' },
  setCompute: jest.fn(),
  setConnector: jest.fn(),
  setDatabase: jest.fn()
};

jest.mock('../../../../utils/hooks/useDataCatalog/useDataCatalog', () => ({
  useDataCatalog: jest.fn()
}));

const defaultProps = {
  defaultValues: {
    database: 'database1',
    tableName: 'test_table',
    connectorId: 'connector1',
    computeId: 'compute1'
  } as DestinationConfig,
  onChange: jest.fn()
};

describe('DestinationSettings Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useDataCatalog as jest.Mock).mockReturnValue(mockUseDataCatalog);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should render all form fields correctly', () => {
    render(<DestinationSettings {...defaultProps} />);

    expect(screen.getByLabelText('Engine')).toBeInTheDocument();
    expect(screen.getByLabelText('Compute')).toBeInTheDocument();
    expect(screen.getByLabelText('Database')).toBeInTheDocument();
    expect(screen.getByLabelText('Table Name')).toBeInTheDocument();
  });

  it('should display correct initial values', () => {
    render(<DestinationSettings {...defaultProps} />);

    expect(screen.getByDisplayValue('test_table')).toBeInTheDocument();
  });

  it('should hide compute field when only one compute is available', () => {
    const mockUseDataCatalogSingleCompute = {
      ...mockUseDataCatalog,
      computes: [{ id: 'compute1', name: 'Compute 1' }]
    };

    (useDataCatalog as jest.Mock).mockReturnValueOnce(mockUseDataCatalogSingleCompute);

    render(<DestinationSettings {...defaultProps} />);

    expect(screen.queryByLabelText('Compute')).not.toBeInTheDocument();
  });

  it('should show compute field when multiple computes are available', () => {
    render(<DestinationSettings {...defaultProps} />);

    expect(screen.getByLabelText('Compute')).toBeInTheDocument();
  });

  it('should call onChange when engine dropdown changes', async () => {
    render(<DestinationSettings {...defaultProps} />);

    const engineSelect = screen.getByLabelText('Engine');
    fireEvent.mouseDown(engineSelect);

    await waitFor(() => {
      const option = screen.getByText('Connector 2');
      fireEvent.click(option);
    });

    expect(mockUseDataCatalog.setConnector).toHaveBeenCalledWith({
      id: 'connector2',
      displayName: 'Connector 2'
    });
    expect(defaultProps.onChange).toHaveBeenCalledWith('engine', 'connector2');
  });

  it('should call onChange when database dropdown changes', async () => {
    render(<DestinationSettings {...defaultProps} />);

    const databaseSelect = screen.getByLabelText('Database');
    fireEvent.mouseDown(databaseSelect);

    await waitFor(() => {
      const options = screen.getAllByText('database2');
      const option = options.find(el => el.closest('.ant-select-item'));
      if (option) {
        fireEvent.click(option);
      }
    });

    expect(mockUseDataCatalog.setDatabase).toHaveBeenCalledWith('database2');
    expect(defaultProps.onChange).toHaveBeenCalledWith('database', 'database2');
  });

  it('should call onChange when compute dropdown changes', async () => {
    render(<DestinationSettings {...defaultProps} />);

    const computeSelect = screen.getByLabelText('Compute');
    fireEvent.mouseDown(computeSelect);

    await waitFor(() => {
      const option = screen.getByText('Compute 2');
      fireEvent.click(option);
    });

    expect(mockUseDataCatalog.setCompute).toHaveBeenCalledWith({
      id: 'compute2',
      name: 'Compute 2'
    });
    expect(defaultProps.onChange).toHaveBeenCalledWith('compute', 'compute2');
  });

  it('should update table name input and not call onChange immediately', () => {
    render(<DestinationSettings {...defaultProps} />);

    const tableNameInput = screen.getByLabelText('Table Name');
    fireEvent.change(tableNameInput, { target: { value: 'new_table_name' } });

    expect(screen.getByDisplayValue('new_table_name')).toBeInTheDocument();
    expect(defaultProps.onChange).not.toHaveBeenCalled();
  });

  it('should show loader in select dropdown when loading state is true', () => {
    const mockUseDataCatalogLoading = {
      ...mockUseDataCatalog,
      loading: true
    };

    (useDataCatalog as jest.Mock).mockReturnValueOnce(mockUseDataCatalogLoading);

    render(<DestinationSettings {...defaultProps} />);

    const selectDropdowns = document.querySelectorAll('.ant-select');
    selectDropdowns.forEach(select => {
      expect(select).toBeInTheDocument();
      expect(select).toHaveClass('ant-select-loading');
    });
  });

  it('should not show loader in select dropdown when loading state is false', () => {
    const mockUseDataCatalogLoading = {
      ...mockUseDataCatalog,
      loading: false
    };

    (useDataCatalog as jest.Mock).mockReturnValueOnce(mockUseDataCatalogLoading);

    render(<DestinationSettings {...defaultProps} />);

    const selectDropdowns = document.querySelectorAll('.ant-select');
    selectDropdowns.forEach(select => {
      expect(select).toBeInTheDocument();
      expect(select).not.toHaveClass('ant-select-loading');
    });
  });

  it('should set default values from props on component mount', () => {
    const mockSetConnector = jest.fn();
    const mockSetDatabase = jest.fn();
    const mockSetCompute = jest.fn();

    const mockUseDataCatalogWithSetters = {
      ...mockUseDataCatalog,
      setConnector: mockSetConnector,
      setDatabase: mockSetDatabase,
      setCompute: mockSetCompute
    };

    (useDataCatalog as jest.Mock).mockReturnValueOnce(mockUseDataCatalogWithSetters);

    render(<DestinationSettings {...defaultProps} />);

    expect(mockSetConnector).toHaveBeenCalledWith({
      id: 'connector1',
      displayName: 'Connector 1'
    });
    expect(mockSetDatabase).toHaveBeenCalledWith('database1');
    expect(mockSetCompute).toHaveBeenCalledWith({
      id: 'compute1',
      name: 'Compute 1'
    });
  });

  it('should not call setters when no matching items found in defaultValues', () => {
    const mockSetConnector = jest.fn();
    const mockSetDatabase = jest.fn();
    const mockSetCompute = jest.fn();

    const mockUseDataCatalogNoMatch = {
      ...mockUseDataCatalog,
      connectors: [{ id: 'different_connector', displayName: 'Different Connector' }],
      databases: ['different_database'],
      computes: [{ id: 'different_compute', name: 'Different Compute' }],
      setConnector: mockSetConnector,
      setDatabase: mockSetDatabase,
      setCompute: mockSetCompute
    };

    (useDataCatalog as jest.Mock).mockReturnValueOnce(mockUseDataCatalogNoMatch);

    render(<DestinationSettings {...defaultProps} />);

    expect(mockSetConnector).not.toHaveBeenCalled();
    expect(mockSetDatabase).not.toHaveBeenCalled();
    expect(mockSetCompute).not.toHaveBeenCalled();
  });
});
