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
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import FileChooserInput from './FileChooserInput';

jest.mock('../../../utils/hooks/useLoadData/useLoadData', () => ({
  __esModule: true,
  default: jest.fn()
}));

import useLoadData from '../../../utils/hooks/useLoadData/useLoadData';

const mockUseLoadData = useLoadData as jest.MockedFunction<typeof useLoadData>;

describe('FileChooserInput', () => {
  const mockOnChange = jest.fn();

  const mockDirectoryData = {
    files: [
      {
        path: '/test/directory/file1.txt',
        type: 'file',
        size: 1024,
        mtime: Date.now(),
        user: 'testuser',
        group: 'testgroup',
        rwx: 'rw-r--r--',
        mode: 644,
        atime: Date.now(),
        blockSize: 4096,
        replication: 3
      },
      {
        path: '/test/directory/file2.txt',
        type: 'file',
        size: 2048,
        mtime: Date.now(),
        user: 'testuser',
        group: 'testgroup',
        rwx: 'rw-r--r--',
        mode: 644,
        atime: Date.now(),
        blockSize: 4096,
        replication: 3
      },
      {
        path: '/test/directory/subfolder',
        type: 'dir',
        size: 0,
        mtime: Date.now(),
        user: 'testuser',
        group: 'testgroup',
        rwx: 'rwxr-xr-x',
        mode: 755,
        atime: Date.now(),
        blockSize: 0,
        replication: 0
      }
    ],
    page: {
      number: 1,
      numPages: 1,
      startIndex: 0,
      endIndex: 3,
      totalRecords: 3,
      pageSize: 1000,
      previousPage: 1,
      nextPage: 1
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseLoadData.mockReturnValue({
      data: mockDirectoryData,
      loading: false,
      error: undefined,
      reloadData: jest.fn()
    });
  });

  it('should render input field with value', () => {
    render(<FileChooserInput value="/test/path" onChange={mockOnChange} />);

    const input = screen.getByRole('textbox');
    expect(input).toBeInTheDocument();
    expect(input).toHaveValue('/test/path');
  });

  it('should render Choose button', () => {
    render(<FileChooserInput value="" onChange={mockOnChange} />);

    const button = screen.getByRole('button', { name: 'Choose' });
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent('Choose');
  });

  it('should render with placeholder', () => {
    render(<FileChooserInput value="" onChange={mockOnChange} placeholder="Enter file path" />);

    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('placeholder', 'Enter file path');
  });

  it('should call onChange when typing in input field', async () => {
    const user = userEvent.setup();
    render(<FileChooserInput value="" onChange={mockOnChange} />);

    const input = screen.getByRole('textbox');
    await user.type(input, '/new/path');

    expect(mockOnChange).toHaveBeenCalled();
  });

  it('should show error status when error prop is true', () => {
    render(<FileChooserInput value="" onChange={mockOnChange} error={true} />);

    const input = screen.getByRole('textbox');
    expect(input).toHaveClass('ant-input-status-error');
  });

  it('should open FileChooserModal when Choose button is clicked', async () => {
    const user = userEvent.setup();
    render(<FileChooserInput value="/initial/path" onChange={mockOnChange} />);

    const button = screen.getByRole('button', { name: 'Choose' });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText('Choose a file')).toBeInTheDocument();
    });
  });

  it('should update value and close modal when file is selected', async () => {
    const user = userEvent.setup();
    render(<FileChooserInput value="" onChange={mockOnChange} />);

    const button = screen.getByRole('button', { name: 'Choose' });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText('Choose a file')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('file1.txt')).toBeInTheDocument();
    });

    const fileRow = screen.getByText('file1.txt');
    await user.click(fileRow);

    await waitFor(() => {
      expect(mockOnChange).toHaveBeenCalledWith('/test/directory/file1.txt');
    });

    await waitFor(() => {
      expect(screen.queryByText('Choose a file')).not.toBeInTheDocument();
    });
  });

  it('should close modal when cancel is clicked', async () => {
    const user = userEvent.setup();
    render(<FileChooserInput value="" onChange={mockOnChange} />);

    const button = screen.getByRole('button', { name: 'Choose' });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText('Choose a file')).toBeInTheDocument();
    });

    const cancelButton = screen.getByRole('button', { name: 'Cancel' });
    await user.click(cancelButton);

    await waitFor(() => {
      expect(screen.queryByText('Choose a file')).not.toBeInTheDocument();
    });
  });

  it('should use root path "/" as default sourcePath when value is empty', async () => {
    const user = userEvent.setup();
    render(<FileChooserInput value="" onChange={mockOnChange} />);

    const button = screen.getByRole('button', { name: 'Choose' });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText('Choose a file')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(mockUseLoadData).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          params: expect.objectContaining({
            path: '/'
          })
        })
      );
    });
  });

  it('should use existing value as sourcePath when available', async () => {
    const user = userEvent.setup();
    render(<FileChooserInput value="/existing/path" onChange={mockOnChange} />);

    const button = screen.getByRole('button', { name: 'Choose' });
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText('Choose a file')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(mockUseLoadData).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          params: expect.objectContaining({
            path: '/existing/path'
          })
        })
      );
    });
  });
});
