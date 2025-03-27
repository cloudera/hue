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
import '@testing-library/jest-dom';
import { RegularFile, FileStatus } from '../../../utils/hooks/useFileUpload/types';
import FileUploadRow from './FileUploadRow';

const mockUploadRow: RegularFile = {
  uuid: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx1',
  filePath: '/path/to/file1.txt',
  status: FileStatus.Pending,
  file: new File(['mock test file'], 'file1.txt'),
  progress: 0
};
const mockOnCancel = jest.fn();

describe('FileUploadRow', () => {
  it('should render the row with name', () => {
    const { getByText } = render(<FileUploadRow data={mockUploadRow} onCancel={mockOnCancel} />);

    expect(getByText('file1.txt')).toBeInTheDocument();
    expect(getByText('14 Bytes')).toBeInTheDocument();
  });

  it('should call onCancel when cancel button is clicked', async () => {
    const { getByTestId } = render(<FileUploadRow data={mockUploadRow} onCancel={mockOnCancel} />);

    const cancelButton = getByTestId('hue-upload-queue-row__close-icon');
    fireEvent.click(cancelButton);

    await waitFor(() => {
      expect(mockOnCancel).toHaveBeenCalled();
    });
  });

  it('should hide cancel button for files is not in Pending state', () => {
    const mockData = { ...mockUploadRow, status: FileStatus.Failed };
    const { queryByTestId } = render(<FileUploadRow data={mockData} onCancel={mockOnCancel} />);

    const cancelButtons = queryByTestId('hue-upload-queue-row__close-icon');
    expect(cancelButtons).not.toBeInTheDocument();
  });

  it('should show progress bar when file is in uploading state', () => {
    const mockData = { ...mockUploadRow, status: FileStatus.Uploading, progress: 10 };
    const { getByTestId } = render(<FileUploadRow data={mockData} onCancel={mockOnCancel} />);
    const progressBar = getByTestId('hue-upload-queue-row__progressbar');
    expect(progressBar).toBeInTheDocument();
    expect(progressBar).toHaveStyle('width: 10%');
  });
});
