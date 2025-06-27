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
import { render, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import SourceConfiguration from './SourceConfiguration';
import { CombinedFileFormat, ImporterFileTypes } from '../../types';

describe('SourceConfiguration Component', () => {
  const mockSetFileFormat = jest.fn();
  const mockFileFormat: CombinedFileFormat = {
    quoteChar: '"',
    recordSeparator: '\\n',
    type: ImporterFileTypes.EXCEL,
    hasHeader: true,
    fieldSeparator: ','
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the component', () => {
    const { getByText } = render(
      <SourceConfiguration fileFormat={mockFileFormat} setFileFormat={mockSetFileFormat} />
    );
    expect(getByText('Configure source')).toBeInTheDocument();
  });

  it('should render as collapsible details element', () => {
    const { container, getByText } = render(
      <SourceConfiguration fileFormat={mockFileFormat} setFileFormat={mockSetFileFormat} />
    );

    const detailsElement = container.querySelector('details');
    expect(detailsElement).toBeInTheDocument();
    expect(detailsElement).toHaveClass('hue-importer-configuration');
    expect(getByText('File Type')).not.toBeVisible();
  });

  it('should call setFileFormat on option change', async () => {
    const { getByText, getAllByRole } = render(
      <SourceConfiguration fileFormat={mockFileFormat} setFileFormat={mockSetFileFormat} />
    );

    const selectElement = getAllByRole('combobox')[0];
    await userEvent.click(selectElement);
    fireEvent.click(getByText('CSV'));

    await waitFor(() =>
      expect(mockSetFileFormat).toHaveBeenCalledWith({
        ...mockFileFormat,
        type: ImporterFileTypes.CSV
      })
    );
  });

  it('should show fieldSeparator and other dropdown when fileType is CSV', () => {
    const { getAllByRole, getByText } = render(
      <SourceConfiguration
        fileFormat={{ ...mockFileFormat, type: ImporterFileTypes.CSV }}
        setFileFormat={mockSetFileFormat}
      />
    );

    const selectElement = getAllByRole('combobox');

    expect(selectElement).toHaveLength(5);
    expect(getByText('File Type')).toBeInTheDocument();
    expect(getByText('Has Header')).toBeInTheDocument();
    expect(getByText('Field Separator')).toBeInTheDocument();
    expect(getByText('Record Separator')).toBeInTheDocument();
    expect(getByText('Quote Character')).toBeInTheDocument();
  });

  it('should not show fieldSeparator and other dropdown when fileType is not CSV', () => {
    const { getAllByRole, getByText, queryByText } = render(
      <SourceConfiguration fileFormat={mockFileFormat} setFileFormat={mockSetFileFormat} />
    );

    const selectElement = getAllByRole('combobox');

    expect(selectElement).toHaveLength(3);
    expect(getByText('File Type')).toBeInTheDocument();
    expect(getByText('Has Header')).toBeInTheDocument();
    expect(queryByText('Field Separator')).not.toBeInTheDocument();
    expect(queryByText('Record Separator')).not.toBeInTheDocument();
    expect(queryByText('Quote Character')).not.toBeInTheDocument();
  });

  it('should show select sheet dropdown when fileType is EXCEL', () => {
    const { getAllByRole, getByText } = render(
      <SourceConfiguration
        fileFormat={{ ...mockFileFormat, type: ImporterFileTypes.EXCEL }}
        setFileFormat={mockSetFileFormat}
      />
    );

    const selectElement = getAllByRole('combobox');

    expect(selectElement).toHaveLength(3);
    expect(getByText('Sheet Name')).toBeInTheDocument();
  });

  it('should not show select sheet dropdown when fileType is not EXCEL', () => {
    const { getAllByRole, queryByText } = render(
      <SourceConfiguration
        fileFormat={{ ...mockFileFormat, type: ImporterFileTypes.CSV }}
        setFileFormat={mockSetFileFormat}
      />
    );

    const selectElement = getAllByRole('combobox');

    expect(selectElement).toHaveLength(5);
    expect(queryByText('Sheet Name')).not.toBeInTheDocument();
  });

  it('should not call setFileFormat when fileFormat is undefined', async () => {
    const { getAllByRole } = render(
      <SourceConfiguration fileFormat={undefined} setFileFormat={mockSetFileFormat} />
    );

    const selectElement = getAllByRole('combobox')[0];
    await userEvent.click(selectElement);

    const csvOption = getAllByRole('option').find(option => option.textContent === 'CSV');
    if (csvOption) {
      await userEvent.click(csvOption);
    }

    expect(mockSetFileFormat).not.toHaveBeenCalled();
  });

  it('should call setFileFormat with correct parameters for hasHeader change', async () => {
    const { getByText, getAllByRole } = render(
      <SourceConfiguration fileFormat={mockFileFormat} setFileFormat={mockSetFileFormat} />
    );

    const hasHeaderSelect = getAllByRole('combobox')[1];
    await userEvent.click(hasHeaderSelect);

    const noOption = getByText('No');
    await userEvent.click(noOption);

    await waitFor(() =>
      expect(mockSetFileFormat).toHaveBeenCalledWith({
        ...mockFileFormat,
        hasHeader: false
      })
    );
  });

  it('should call setFileFormat with correct parameters for fieldSeparator change', async () => {
    const csvFormat = { ...mockFileFormat, type: ImporterFileTypes.CSV };
    const { getByText, getAllByRole } = render(
      <SourceConfiguration fileFormat={csvFormat} setFileFormat={mockSetFileFormat} />
    );

    const fieldSeparatorSelect = getAllByRole('combobox')[2];
    await userEvent.click(fieldSeparatorSelect);

    const tabOption = getByText('^Tab (\\t)');
    await userEvent.click(tabOption);

    await waitFor(() =>
      expect(mockSetFileFormat).toHaveBeenCalledWith({
        ...csvFormat,
        fieldSeparator: '\\t'
      })
    );
  });

  it('should call setFileFormat with correct parameters for quoteChar change', async () => {
    const csvFormat = { ...mockFileFormat, type: ImporterFileTypes.CSV };
    const { getByText, getAllByRole } = render(
      <SourceConfiguration fileFormat={csvFormat} setFileFormat={mockSetFileFormat} />
    );

    const quoteCharSelect = getAllByRole('combobox')[4];
    await userEvent.click(quoteCharSelect);

    const singleQuoteOption = getByText("Single Quote (')");
    await userEvent.click(singleQuoteOption);

    await waitFor(() =>
      expect(mockSetFileFormat).toHaveBeenCalledWith({
        ...csvFormat,
        quoteChar: "'"
      })
    );
  });

  it('should show JSON type dropdown when fileType is JSON', () => {
    const jsonFormat = { ...mockFileFormat, type: ImporterFileTypes.JSON };
    const { getAllByRole, getByText, queryByText } = render(
      <SourceConfiguration fileFormat={jsonFormat} setFileFormat={mockSetFileFormat} />
    );

    const selectElement = getAllByRole('combobox');

    expect(selectElement).toHaveLength(2);
    expect(getByText('File Type')).toBeInTheDocument();
    expect(getByText('Has Header')).toBeInTheDocument();
    expect(queryByText('Field Separator')).not.toBeInTheDocument();
    expect(queryByText('Record Separator')).not.toBeInTheDocument();
    expect(queryByText('Quote Character')).not.toBeInTheDocument();
    expect(queryByText('Sheet Name')).not.toBeInTheDocument();
  });
});
