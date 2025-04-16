import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import SourceConfiguration from './SourceConfiguration';
import { FileFormatResponse } from '../../types';
import { separator } from '../../constants';

describe('SourceConfiguration Component', () => {
  const mockSetFileFormat = jest.fn();
  const mockFileFormat: FileFormatResponse = {
    quoteChar: '"',
    recordSeparator: '\\n',
    type: 'csv',
    hasHeader: true,
    fieldSeparator: ',',
    status: 0
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render the component', () => {
    const { getByText, getAllByRole } = render(
      <SourceConfiguration fileFormat={mockFileFormat} setFileFormat={mockSetFileFormat} />
    );
    expect(getByText('Configure source')).toBeInTheDocument();
    expect(getAllByRole('combobox')).toHaveLength(5);
  });

  it('calls setFileFormat on option change', async () => {
    const { getByText, getAllByRole } = render(
      <SourceConfiguration fileFormat={mockFileFormat} setFileFormat={mockSetFileFormat} />
    );

    const selectElement = getAllByRole('combobox')[0];
    await userEvent.click(selectElement);
    fireEvent.click(getByText(separator[3].label));

    await waitFor(() =>
      expect(mockSetFileFormat).toHaveBeenCalledWith({
        ...mockFileFormat,
        fieldSeparator: separator[3].value
      })
    );
  });
});
