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
import { render, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import FileUploadQueue from './FileUploadQueue';
import { FileStatus, RegularFile } from '../../utils/hooks/useFileUpload/types';
import { act } from 'react-dom/test-utils';
import huePubSub from '../../utils/huePubSub';
import { FILE_UPLOAD_START_EVENT } from './event';

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

jest.mock('../../utils/hooks/useFileUpload/useFileUpload', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    uploadQueue: mockFilesQueue,
    onCancel: jest.fn(),
    addFiles: jest.fn()
  }))
}));

describe('FileUploadQueue', () => {
  it('should render the component with initial files in the queue', () => {
    const { getByText } = render(<FileUploadQueue />);

    act(() => huePubSub.publish(FILE_UPLOAD_START_EVENT, { files: mockFilesQueue }));

    expect(getByText('file1.txt')).toBeInTheDocument();
    expect(getByText('file2.txt')).toBeInTheDocument();
  });

  it('should toggle the visibility of the queue when the header is clicked', () => {
    const { getByText, getByTestId, queryByText } = render(<FileUploadQueue />);

    act(() => huePubSub.publish(FILE_UPLOAD_START_EVENT, { files: mockFilesQueue }));

    const header = getByTestId('hue-upload-queue-container__expand-button');
    expect(getByText('file1.txt')).toBeVisible();
    expect(getByText('file2.txt')).toBeVisible();

    fireEvent.click(header);

    expect(queryByText('file1.txt')).toBeNull();
    expect(queryByText('file2.txt')).toBeNull();

    fireEvent.click(header);

    expect(getByText('file1.txt')).toBeVisible();
    expect(getByText('file2.txt')).toBeVisible();
  });
});
