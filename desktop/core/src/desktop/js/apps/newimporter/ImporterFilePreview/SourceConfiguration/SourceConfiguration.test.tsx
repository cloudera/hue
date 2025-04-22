import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import SourceConfiguration from './SourceConfiguration';
import { FileFormatResponse, SupportedFileTypes } from '../../types';

describe('SourceConfiguration Component', () => {
  const mockSetFileFormat = jest.fn();
  const mockFileFormat: FileFormatResponse = {
    quoteChar: '"',
    recordSeparator: '\\n',
    type: SupportedFileTypes.EXCEL,
    hasHeader: true,
    fieldSeparator: ',',
    status: 0
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
        type: SupportedFileTypes.CSV
      })
    );
  });

  it('should show fieldSepator and other downdown when fileType is CSV', () => {
    const { getAllByRole, getByText } = render(
      <SourceConfiguration
        fileFormat={{ ...mockFileFormat, type: SupportedFileTypes.CSV }}
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

  it('should not show fieldSepator and other downdown when fileType is not CSV', () => {
    const { getAllByRole, getByText, queryByText } = render(
      <SourceConfiguration fileFormat={mockFileFormat} setFileFormat={mockSetFileFormat} />
    );

    const selectElement = getAllByRole('combobox');

    expect(selectElement).toHaveLength(2);
    expect(getByText('File Type')).toBeInTheDocument();
    expect(getByText('Has Header')).toBeInTheDocument();
    expect(queryByText('Field Separator')).not.toBeInTheDocument();
    expect(queryByText('Record Separator')).not.toBeInTheDocument();
    expect(queryByText('Quote Character')).not.toBeInTheDocument();
  });
});
