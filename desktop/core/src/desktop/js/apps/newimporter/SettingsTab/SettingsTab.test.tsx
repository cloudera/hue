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

  describe('Component Rendering', () => {
    it('should render the settings tab with all sections', () => {
      render(<SettingsTab {...defaultProps} />);

      expect(document.querySelector('.hue-importer-settings-tab')).toBeInTheDocument();
      expect(document.querySelector('.hue-importer-settings-tab__form')).toBeInTheDocument();

      expect(screen.getByText('Properties')).toBeInTheDocument();
      expect(screen.getByText('Character Delimiters')).toBeInTheDocument();
    });

    it('should render description field', () => {
      render(<SettingsTab {...defaultProps} />);

      const descriptionInput = screen.getByLabelText('Description');
      expect(descriptionInput).toBeInTheDocument();
      expect(descriptionInput).toHaveAttribute('placeholder', 'Description goes here');
    });

    it('should render format select field', () => {
      render(<SettingsTab {...defaultProps} />);

      const formatSelect = screen.getByText('Format');
      expect(formatSelect).toBeInTheDocument();
    });

    it('should render visible checkbox fields', () => {
      render(<SettingsTab {...defaultProps} />);

      expect(screen.getByText('Create empty table')).toBeInTheDocument();
      expect(screen.getByText('Use external location instead of default')).toBeInTheDocument();
      expect(screen.getByText('Custom char delimiters')).toBeInTheDocument();
    });
  });

  describe('Form Interactions', () => {
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
  });

  describe('Conditional Field Visibility', () => {
    it('should hide transactional table checkbox for Kudu tables', () => {
      const settingsWithKudu = {
        ...defaultSettings,
        tableFormat: TableFormat.KUDU
      };

      render(<SettingsTab {...defaultProps} settings={settingsWithKudu} />);

      expect(screen.queryByText('Transactional table')).not.toBeInTheDocument();
    });

    it('should hide transactional table checkbox for remote files', () => {
      render(<SettingsTab {...defaultProps} />);

      expect(screen.queryByText('Transactional table')).not.toBeInTheDocument();
    });

    it('should show transactional table checkbox for local files', () => {
      const localFileMetaData = {
        ...defaultFileMetaData,
        source: ImporterFileSource.LOCAL
      };

      render(<SettingsTab {...defaultProps} fileMetaData={localFileMetaData} />);

      expect(screen.getByText('Transactional table')).toBeInTheDocument();
    });

    it('should show insert only checkbox when transactional is enabled', () => {
      const transactionalSettings = {
        ...defaultSettings,
        isTransactional: true
      };

      render(<SettingsTab {...defaultProps} settings={transactionalSettings} />);

      expect(screen.getByText('Insert only')).toBeInTheDocument();
    });

    it('should hide insert only checkbox when transactional is disabled', () => {
      render(<SettingsTab {...defaultProps} />);

      expect(screen.queryByText('Insert only')).not.toBeInTheDocument();
    });

    it('should show iceberg table checkbox for remote tables when iceberg is enabled', () => {
      render(<SettingsTab {...defaultProps} />);

      expect(screen.getByText('Iceberg table')).toBeInTheDocument();
    });

    it('should hide iceberg table checkbox for local files', () => {
      const localFileMetaData = {
        ...defaultFileMetaData,
        source: ImporterFileSource.LOCAL
      };

      render(<SettingsTab {...defaultProps} fileMetaData={localFileMetaData} />);

      expect(screen.queryByText('Iceberg table')).not.toBeInTheDocument();
    });

    it('should show copy file checkbox for external remote tables', () => {
      const externalSettings = {
        ...defaultSettings,
        storeLocation: StoreLocation.EXTERNAL
      };

      render(<SettingsTab {...defaultProps} settings={externalSettings} />);

      expect(screen.getByText('Copy file')).toBeInTheDocument();
    });

    it('should hide copy file checkbox for managed tables', () => {
      render(<SettingsTab {...defaultProps} />);

      expect(screen.queryByText('Copy file')).not.toBeInTheDocument();
    });

    it('should hide copy file checkbox when transactional is enabled', () => {
      const transactionalSettings = {
        ...defaultSettings,
        isTransactional: true
      };

      render(<SettingsTab {...defaultProps} settings={transactionalSettings} />);

      expect(screen.queryByText('Copy file')).not.toBeInTheDocument();
    });

    it('should hide copy file checkbox when importData is false', () => {
      const noImportSettings = {
        ...defaultSettings,
        importData: false
      };

      render(<SettingsTab {...defaultProps} settings={noImportSettings} />);

      expect(screen.queryByText('Copy file')).not.toBeInTheDocument();
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

      expect(screen.getByText('Field')).toBeInTheDocument();
      expect(screen.getByText('Array Map')).toBeInTheDocument();
      expect(screen.getByText('Struct')).toBeInTheDocument();
    });

    it('should hide delimiter fields when customCharDelimiters is disabled', () => {
      render(<SettingsTab {...defaultProps} />);

      expect(screen.queryByText('Field')).not.toBeInTheDocument();
      expect(screen.queryByText('Array Map')).not.toBeInTheDocument();
      expect(screen.queryByText('Struct')).not.toBeInTheDocument();
    });
  });

  describe('Context Creation', () => {
    it('should create correct context for managed table', () => {
      const managedSettings = {
        ...defaultSettings,
        storeLocation: StoreLocation.MANAGED
      };

      render(<SettingsTab {...defaultProps} settings={managedSettings} />);

      // For managed tables, copy file should be hidden (which matches our default settings)
      expect(screen.queryByText('Copy file')).not.toBeInTheDocument();
    });

    it('should create correct context for external table', () => {
      const externalSettings = {
        ...defaultSettings,
        storeLocation: StoreLocation.EXTERNAL
      };

      render(<SettingsTab {...defaultProps} settings={externalSettings} />);

      // Copy file should be visible for external tables
      expect(screen.getByText('Copy file')).toBeInTheDocument();
    });

    it('should create correct context for different table formats with local files', () => {
      const localFileMetaData = {
        ...defaultFileMetaData,
        source: ImporterFileSource.LOCAL
      };
      const parquetSettings = {
        ...defaultSettings,
        tableFormat: TableFormat.PARQUET
      };

      render(
        <SettingsTab
          {...defaultProps}
          fileMetaData={localFileMetaData}
          settings={parquetSettings}
        />
      );

      // Transactional table should be visible for non-Kudu formats with local files
      expect(screen.getByText('Transactional table')).toBeInTheDocument();
    });
  });
});
