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
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import FileUploadQueue from './FileUploadQueue';
import { FileStatus, RegularFile } from '../../utils/hooks/useFileUpload/types';

const mockFilesQueue: RegularFile[] = [
  {
    uuid: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx1',
    filePath: '/path/to/file1.txt',
    status: FileStatus.Pending,
    file: new File([], 'file1.txt')
  },
  {
    uuid: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx2',
    filePath: '/path/to/file2.txt',
    status: FileStatus.Pending,
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
});
