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
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FileUploadQueue from './FileUploadQueue';
import { FileUploadStatus } from '../../utils/constants/storageBrowser';
import { UploadItem } from '../../utils/hooks/useFileUpload/util';

const mockFilesQueue: UploadItem[] = [
  {
    uuid: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx1',
    filePath: '/path/to/file1.txt',
    status: FileUploadStatus.Pending,
    file: new File([], 'file1.txt')
  },
  {
    uuid: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx2',
    filePath: '/path/to/file2.txt',
    status: FileUploadStatus.Pending,
    file: new File([], 'file2.txt')
  }
];

const mockOnCancel = jest.fn();
jest.mock('../../utils/hooks/useFileUpload/useFileUpload', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    uploadQueue: mockFilesQueue,
    onCancel: mockOnCancel
  }))
}));

describe('FileUploadQueue', () => {
  it('should render the component with initial files in the queue', () => {
    const { getByText } = render(
      <FileUploadQueue filesQueue={mockFilesQueue} onClose={() => {}} onComplete={() => {}} />
    );

    expect(getByText('file1.txt')).toBeInTheDocument();
    expect(getByText('file2.txt')).toBeInTheDocument();
  });

  it('should call onCancel when cancel button is clicked', async () => {
    const { getAllByTestId } = render(
      <FileUploadQueue filesQueue={mockFilesQueue} onClose={() => {}} onComplete={() => {}} />
    );

    const cancelButton = getAllByTestId('upload-queue__list__row__close-icon')[0];
    fireEvent.click(cancelButton);

    await waitFor(() => {
      expect(mockOnCancel).toHaveBeenCalled();
    });
  });

  it('should toggle the visibility of the queue when the header is clicked', () => {
    const { getByTestId } = render(
      <FileUploadQueue filesQueue={mockFilesQueue} onClose={() => {}} onComplete={() => {}} />
    );

    const header = getByTestId('upload-queue__header');
    expect(screen.getByText('file1.txt')).toBeInTheDocument();
    expect(screen.getByText('file2.txt')).toBeInTheDocument();

    fireEvent.click(header!);
    expect(screen.queryByText('file1.txt')).not.toBeInTheDocument();
    expect(screen.queryByText('file2.txt')).not.toBeInTheDocument();

    fireEvent.click(header!);
    expect(screen.getByText('file1.txt')).toBeInTheDocument();
    expect(screen.getByText('file2.txt')).toBeInTheDocument();
  });

  it('should render cancel button for files in Pending state', () => {
    const { getAllByTestId } = render(
      <FileUploadQueue filesQueue={mockFilesQueue} onClose={() => {}} onComplete={() => {}} />
    );

    const cancelButtons = getAllByTestId('upload-queue__list__row__close-icon');
    expect(cancelButtons).toHaveLength(mockFilesQueue.length);

    expect(cancelButtons[0]).toBeInTheDocument();
    expect(cancelButtons[1]).toBeInTheDocument();
  });
});
