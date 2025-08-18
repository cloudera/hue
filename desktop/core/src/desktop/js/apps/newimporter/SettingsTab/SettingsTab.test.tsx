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
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

import SettingsTab from './SettingsTab';
import {
  FileMetaData,
  ImporterFileSource,
  ImporterSettings,
  StoreLocation,
  TableFormat
} from '../types';

describe('SettingsTab', () => {
  const mockOnSettingsChange = jest.fn();

  const defaultFileMetaData: FileMetaData = {
    path: '/test/path/file.csv',
    fileName: 'file.csv',
    source: ImporterFileSource.REMOTE
  };

  const defaultSettings: ImporterSettings = {
    storeLocation: StoreLocation.MANAGED,
    isTransactional: false,
    isInsertOnly: false,
    externalLocation: '',
    importData: true,
    isIcebergTable: false,
    isCopyFile: false,
    description: '',
    tableFormat: TableFormat.TEXT,
    primaryKeys: [],
    createEmptyTable: false,
    useExternalLocation: false,
    customCharDelimiters: false,
    fieldDelimiter: 'new_line',
    arrayMapDelimiter: 'comma',
    structDelimiter: 'tab'
  };

  const defaultProps = {
    fileMetaData: defaultFileMetaData,
    settings: defaultSettings,
    onSettingsChange: mockOnSettingsChange
  };

  beforeEach(() => {
    mockOnSettingsChange.mockClear();
  });

  it('should render the settings tab with all sections', () => {
    render(<SettingsTab {...defaultProps} />);

    expect(document.querySelector('.hue-importer-settings-tab')).toBeInTheDocument();
    expect(document.querySelector('.hue-importer-settings-tab__form')).toBeInTheDocument();

    expect(screen.getByText('Properties')).toBeInTheDocument();
    expect(screen.getByText('Character Delimiters')).toBeInTheDocument();
  });

  it('should call onSettingsChange when description changes', async () => {
    const user = userEvent.setup();
    render(<SettingsTab {...defaultProps} />);

    const descriptionInput = screen.getByLabelText('Description');
    await user.type(descriptionInput, 'Test description');

    expect(mockOnSettingsChange).toHaveBeenCalledWith({
      ...defaultSettings,
      description: 'Test description'
    });
  });

  it('should call onSettingsChange when checkbox is toggled', async () => {
    const user = userEvent.setup();
    render(<SettingsTab {...defaultProps} />);

    const createEmptyTableCheckbox = screen.getByRole('checkbox', {
      name: /create empty table/i
    });
    await user.click(createEmptyTableCheckbox);

    expect(mockOnSettingsChange).toHaveBeenCalledWith({
      ...defaultSettings,
      createEmptyTable: true
    });
  });

  it('should call onSettingsChange when external location checkbox is toggled', async () => {
    const user = userEvent.setup();
    render(<SettingsTab {...defaultProps} />);

    const useExternalLocationCheckbox = screen.getByRole('checkbox', {
      name: /use external location instead of default/i
    });
    await user.click(useExternalLocationCheckbox);

    expect(mockOnSettingsChange).toHaveBeenCalledWith({
      ...defaultSettings,
      useExternalLocation: true
    });
  });

  it('should call onSettingsChange when custom char delimiters checkbox is toggled', async () => {
    const user = userEvent.setup();
    render(<SettingsTab {...defaultProps} />);

    const customCharDelimitersCheckbox = screen.getByRole('checkbox', {
      name: /custom char delimiters/i
    });
    await user.click(customCharDelimitersCheckbox);

    expect(mockOnSettingsChange).toHaveBeenCalledWith({
      ...defaultSettings,
      customCharDelimiters: true
    });
  });

  it('should hide transactional table checkbox for Kudu tables', () => {
    const settingsWithKudu = {
      ...defaultSettings,
      tableFormat: TableFormat.KUDU
    };

    render(<SettingsTab {...defaultProps} settings={settingsWithKudu} />);

    expect(screen.queryByRole('checkbox', { name: /transactional table/i })).toBeNull();
  });

  it('should hide transactional table checkbox for remote files', () => {
    render(<SettingsTab {...defaultProps} />);

    expect(screen.queryByRole('checkbox', { name: /transactional table/i })).toBeNull();
  });

  it('should show transactional table checkbox for local files', () => {
    const localFileMetaData = {
      ...defaultFileMetaData,
      source: ImporterFileSource.LOCAL
    };

    render(<SettingsTab {...defaultProps} fileMetaData={localFileMetaData} />);

    expect(screen.getByRole('checkbox', { name: /transactional table/i })).toBeInTheDocument();
  });

  it('should show insert only checkbox when transactional is enabled', () => {
    const transactionalSettings = {
      ...defaultSettings,
      isTransactional: true
    };

    render(<SettingsTab {...defaultProps} settings={transactionalSettings} />);

    expect(screen.getByRole('checkbox', { name: /insert only/i })).toBeInTheDocument();
  });

  it('should hide insert only checkbox when transactional is disabled', () => {
    render(<SettingsTab {...defaultProps} />);

    expect(screen.queryByRole('checkbox', { name: /insert only/i })).toBeNull();
  });

  it('should show iceberg table checkbox for remote tables when iceberg is enabled', () => {
    render(<SettingsTab {...defaultProps} />);

    expect(screen.getByRole('checkbox', { name: /iceberg table/i })).toBeInTheDocument();
  });

  it('should hide iceberg table checkbox for local files', () => {
    const localFileMetaData = {
      ...defaultFileMetaData,
      source: ImporterFileSource.LOCAL
    };

    render(<SettingsTab {...defaultProps} fileMetaData={localFileMetaData} />);

    expect(screen.queryByRole('checkbox', { name: /iceberg table/i })).toBeNull();
  });

  it('should show copy file checkbox for external remote tables', () => {
    const externalSettings = {
      ...defaultSettings,
      storeLocation: StoreLocation.EXTERNAL
    };

    render(<SettingsTab {...defaultProps} settings={externalSettings} />);

    expect(screen.getByRole('checkbox', { name: /copy file/i })).toBeInTheDocument();
  });

  it('should hide copy file checkbox for managed tables', () => {
    render(<SettingsTab {...defaultProps} />);

    expect(screen.queryByRole('checkbox', { name: /copy file/i })).toBeNull();
  });

  it('should hide copy file checkbox when transactional is enabled', () => {
    const transactionalSettings = {
      ...defaultSettings,
      isTransactional: true
    };

    render(<SettingsTab {...defaultProps} settings={transactionalSettings} />);

    expect(screen.queryByRole('checkbox', { name: /copy file/i })).toBeNull();
  });

  it('should hide copy file checkbox when importData is false', () => {
    const noImportSettings = {
      ...defaultSettings,
      importData: false
    };

    render(<SettingsTab {...defaultProps} settings={noImportSettings} />);

    expect(screen.queryByRole('checkbox', { name: /copy file/i })).toBeNull();
  });

  it('should show external location input when useExternalLocation is enabled', () => {
    const externalLocationSettings = {
      ...defaultSettings,
      useExternalLocation: true
    };

    render(<SettingsTab {...defaultProps} settings={externalLocationSettings} />);

    const externalLocationInput = screen.getByPlaceholderText('External location');
    expect(externalLocationInput).toBeInTheDocument();
  });

  it('should hide external location input when useExternalLocation is disabled', () => {
    render(<SettingsTab {...defaultProps} />);

    expect(screen.queryByPlaceholderText('External location')).not.toBeInTheDocument();
  });

  it('should show delimiter fields when customCharDelimiters is enabled', () => {
    const customDelimiterSettings = {
      ...defaultSettings,
      customCharDelimiters: true
    };

    render(<SettingsTab {...defaultProps} settings={customDelimiterSettings} />);

    expect(screen.getByRole('combobox', { name: /field/i })).toBeInTheDocument();
    expect(screen.getByRole('combobox', { name: /array map/i })).toBeInTheDocument();
    expect(screen.getByRole('combobox', { name: /struct/i })).toBeInTheDocument();
  });

  it('should hide delimiter fields when customCharDelimiters is disabled', () => {
    render(<SettingsTab {...defaultProps} />);

    expect(screen.queryByRole('combobox', { name: /field/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('combobox', { name: /array map/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('combobox', { name: /struct/i })).not.toBeInTheDocument();
  });
});
