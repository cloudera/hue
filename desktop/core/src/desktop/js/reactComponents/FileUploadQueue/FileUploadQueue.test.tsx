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
import FileUploadQueue from './FileUploadQueue';
import { FileStatus, RegularFile } from '../../utils/hooks/useFileUpload/types';
import { act } from 'react-dom/test-utils';
import huePubSub from '../../utils/huePubSub';
import { FILE_UPLOAD_START_EVENT } from './event';
import { CancellablePromise } from '../../api/cancellablePromise';
import useFileUpload from '../../utils/hooks/useFileUpload/useFileUpload';
import * as apiUtils from '../../api/utils';

const mockGet = jest.spyOn(apiUtils, 'get');

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

const mockCancelFile = jest.fn();
const mockAddFiles = jest.fn();
const mockRemoveAllFiles = jest.fn();

jest.mock('../../utils/hooks/useFileUpload/useFileUpload', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    uploadQueue: mockFilesQueue,
    cancelFile: mockCancelFile,
    addFiles: mockAddFiles,
    removeAllFiles: mockRemoveAllFiles,
    isLoading: false
  }))
}));

const mockUseFileUpload = jest.mocked(useFileUpload);

describe('FileUploadQueue', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockGet.mockRejectedValue({ response: { status: 404 } });

    huePubSub.removeAll(FILE_UPLOAD_START_EVENT);
    huePubSub.removeAll('set.current.app.name');
    huePubSub.removeAll('get.current.app.name');

    // Set up the get.current.app.name subscription to return storagebrowser by default
    huePubSub.subscribe('get.current.app.name', (callback: (appName: string) => void) => {
      callback('storagebrowser');
    });

    mockUseFileUpload.mockReturnValue({
      uploadQueue: mockFilesQueue,
      cancelFile: mockCancelFile,
      addFiles: mockAddFiles,
      removeAllFiles: mockRemoveAllFiles,
      isLoading: false
    });
  });

  afterEach(() => {
    huePubSub.removeAll('get.current.app.name');
  });

  it('should not render when current app is not storagebrowser', async () => {
    huePubSub.removeAll('get.current.app.name');
    huePubSub.subscribe('get.current.app.name', (callback: (appName: string) => void) => {
      callback('editor');
    });

    const { container } = render(<FileUploadQueue />);

    act(() => {
      huePubSub.publish(FILE_UPLOAD_START_EVENT, { files: mockFilesQueue });
    });

    await waitFor(() => {
      expect(container.firstChild).toBeNull();
    });
  });

  it('should render when current app is storagebrowser', async () => {
    const { container } = render(<FileUploadQueue />);
    await waitFor(() => {
      expect(container.firstChild).not.toBeNull();
    });
  });

  it('should render the component with initial files in the queue', async () => {
    const { getByText } = render(<FileUploadQueue />);

    act(() => {
      huePubSub.publish(FILE_UPLOAD_START_EVENT, { files: mockFilesQueue });
    });

    await waitFor(() => {
      expect(getByText('file1.txt')).toBeVisible();
      expect(getByText('file2.txt')).toBeVisible();
    });
  });

  it('should toggle the visibility of the queue when the header is clicked', async () => {
    const { getByText, queryByText, getByRole } = render(<FileUploadQueue />);

    act(() => {
      huePubSub.publish(FILE_UPLOAD_START_EVENT, { files: mockFilesQueue });
    });

    // Wait for items to appear
    await waitFor(() => expect(getByText('file1.txt')).toBeVisible());
    await waitFor(() => expect(getByText('file2.txt')).toBeVisible());

    const header = getByRole('button', { name: /toggle upload queue/i });

    fireEvent.click(header);

    expect(queryByText('file1.txt')).toBeNull();
    expect(queryByText('file2.txt')).toBeNull();

    fireEvent.click(header);

    await waitFor(() => expect(getByText('file1.txt')).toBeVisible());
    await waitFor(() => expect(getByText('file2.txt')).toBeVisible());
  });

  it('should show conflict modal when files already exist', async () => {
    const files: RegularFile[] = [
      {
        uuid: 'c1',
        filePath: '/dir',
        status: FileStatus.Pending,
        file: new File([], 'conflict.txt')
      },
      {
        uuid: 'n1',
        filePath: '/dir',
        status: FileStatus.Pending,
        file: new File([], 'new.txt')
      }
    ];

    mockGet.mockImplementation((_url: string, data?: unknown) => {
      const params = data as { path: string };
      return CancellablePromise.resolve({ path: params.path });
    });

    const { getByText } = render(<FileUploadQueue />);

    act(() => {
      huePubSub.publish(FILE_UPLOAD_START_EVENT, { files });
    });

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalled();
      expect(getByText('Detected Filename Conflicts')).toBeVisible();
      expect(
        getByText('2 files you are trying to upload already exist in the uploaded files.')
      ).toBeVisible();
      expect(getByText('conflict.txt')).toBeVisible();
    });
  });

  it('should allow canceling conflict resolution', async () => {
    const files: RegularFile[] = [
      {
        uuid: 'c1',
        filePath: '/dir',
        status: FileStatus.Pending,
        file: new File([], 'conflict.txt')
      }
    ];

    mockGet.mockImplementation((_url: string, data?: unknown) => {
      const params = data as { path: string };
      return CancellablePromise.resolve({ path: params.path });
    });

    const { getByText, queryByText } = render(<FileUploadQueue />);

    act(() => {
      huePubSub.publish(FILE_UPLOAD_START_EVENT, { files });
    });

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalled();
      expect(getByText('Detected Filename Conflicts')).toBeVisible();
      expect(getByText('conflict.txt')).toBeVisible();
    });

    fireEvent.click(getByText('Cancel'));

    await waitFor(() => {
      expect(queryByText('Detected Filename Conflicts')).toBeNull();
      expect(mockAddFiles).toHaveBeenCalledWith([]);
    });
  });

  it('should allow skipping upload for conflicted files', async () => {
    const files: RegularFile[] = [
      {
        uuid: 'c1',
        filePath: '/dir',
        status: FileStatus.Pending,
        file: new File([], 'conflict.txt')
      }
    ];

    mockGet.mockImplementation(() => {
      return CancellablePromise.resolve({ path: '/dir/conflict.txt' });
    });

    const { getByText, queryByText } = render(<FileUploadQueue />);

    act(() => {
      huePubSub.publish(FILE_UPLOAD_START_EVENT, { files });
    });

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalled();
      expect(getByText('Detected Filename Conflicts')).toBeVisible();
      expect(getByText('conflict.txt')).toBeVisible();
    });

    fireEvent.click(getByText('Skip Upload'));

    await waitFor(() => {
      expect(queryByText('Detected Filename Conflicts')).toBeNull();
      expect(mockAddFiles).toHaveBeenCalledWith([]);
    });
  });

  it('should allow individual file cancellation', async () => {
    const { getAllByTestId } = render(<FileUploadQueue />);

    act(() => {
      huePubSub.publish(FILE_UPLOAD_START_EVENT, { files: mockFilesQueue });
    });

    await waitFor(() => {
      const closeButtons = getAllByTestId('hue-upload-queue-row__close-icon');
      expect(closeButtons).toHaveLength(2);
      fireEvent.click(closeButtons[0]);
      expect(mockCancelFile).toHaveBeenCalledWith(mockFilesQueue[0]);
    });
  });

  it('should show cancel all button when files are in pending or uploading state', async () => {
    mockUseFileUpload.mockReturnValue({
      uploadQueue: mockFilesQueue,
      cancelFile: mockCancelFile,
      addFiles: mockAddFiles,
      removeAllFiles: mockRemoveAllFiles,
      isLoading: true
    });

    const { getByText } = render(<FileUploadQueue />);

    await waitFor(() => {
      expect(getByText('Cancel All')).toBeVisible();
    });

    fireEvent.click(getByText('Cancel All'));
    expect(mockRemoveAllFiles).toHaveBeenCalled();
  });

  it('should sort files by status priority', async () => {
    const mixedStatusFiles: RegularFile[] = [
      {
        uuid: '1',
        filePath: '/path/to/uploaded.txt',
        status: FileStatus.Uploaded,
        file: new File([], 'uploaded.txt')
      },
      {
        uuid: '2',
        filePath: '/path/to/uploading.txt',
        status: FileStatus.Uploading,
        file: new File([], 'uploading.txt')
      },
      {
        uuid: '3',
        filePath: '/path/to/failed.txt',
        status: FileStatus.Failed,
        file: new File([], 'failed.txt')
      },
      {
        uuid: '4',
        filePath: '/path/to/pending.txt',
        status: FileStatus.Pending,
        file: new File([], 'pending.txt')
      }
    ];

    mockUseFileUpload.mockReturnValue({
      uploadQueue: mixedStatusFiles,
      cancelFile: mockCancelFile,
      addFiles: mockAddFiles,
      removeAllFiles: mockRemoveAllFiles,
      isLoading: true
    });

    const { container } = render(<FileUploadQueue />);

    await waitFor(() => {
      const fileRows = container.querySelectorAll('.hue-upload-queue-row__name');
      const fileNames = Array.from(fileRows).map(row => row.textContent);

      expect(fileNames).toEqual(['uploading.txt', 'failed.txt', 'pending.txt', 'uploaded.txt']);
    });
  });

  it('should display uploading progress for files in progress', async () => {
    const uploadingFile: RegularFile = {
      uuid: '1',
      filePath: '/path/to/uploading.txt',
      status: FileStatus.Uploading,
      progress: 65,
      file: new File([], 'uploading.txt')
    };

    mockUseFileUpload.mockReturnValue({
      uploadQueue: [uploadingFile],
      cancelFile: mockCancelFile,
      addFiles: mockAddFiles,
      removeAllFiles: mockRemoveAllFiles,
      isLoading: false
    });

    const { getByTestId } = render(<FileUploadQueue />);

    await waitFor(() => {
      const progressBar = getByTestId('hue-upload-queue-row__progressbar');
      expect(progressBar).toHaveStyle('width: 65%');
    });
  });

  it('should show preparing to upload state during conflict checking', async () => {
    const files: RegularFile[] = [
      {
        uuid: 'p1',
        filePath: '/dir',
        status: FileStatus.Pending,
        file: new File([], 'pending.txt')
      }
    ];

    let resolveFn: (value: unknown) => void;
    const pending = new CancellablePromise<unknown>((resolve, _reject, onCancel) => {
      resolveFn = resolve;
      onCancel(() => {});
    });

    mockGet.mockImplementation(() => pending);

    const { getByText, queryByText } = render(<FileUploadQueue />);

    act(() => {
      huePubSub.publish(FILE_UPLOAD_START_EVENT, { files });
    });

    await waitFor(() => {
      expect(getByText('Preparing to upload...')).toBeVisible();
    });

    act(() => {
      resolveFn({ path: undefined });
    });

    await waitFor(() => {
      expect(queryByText('Preparing to upload...')).toBeNull();
    });
  });

  it('should display correct header text for different upload states', async () => {
    // Test pending files
    const { getByText, rerender } = render(<FileUploadQueue />);

    act(() => {
      huePubSub.publish(FILE_UPLOAD_START_EVENT, { files: mockFilesQueue });
    });

    await waitFor(() => {
      expect(getByText('2 files remaining')).toBeVisible();
    });

    // Test completed files
    const completedFiles: RegularFile[] = mockFilesQueue.map(file => ({
      ...file,
      status: FileStatus.Uploaded
    }));

    mockUseFileUpload.mockReturnValue({
      uploadQueue: completedFiles,
      cancelFile: mockCancelFile,
      addFiles: mockAddFiles,
      removeAllFiles: mockRemoveAllFiles,
      isLoading: false
    });

    rerender(<FileUploadQueue />);

    await waitFor(() => {
      expect(getByText('2 files uploaded')).toBeVisible();
    });
  });
});
