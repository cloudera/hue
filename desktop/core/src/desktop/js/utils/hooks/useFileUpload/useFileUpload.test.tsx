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

import { renderHook, act } from '@testing-library/react';
import useFileUpload from './useFileUpload';
import { FileStatus, FileVariables, RegularFile } from './types';
import useRegularUpload from './useRegularUpload';
import useChunkUpload from './useChunkUpload';

const mockAddRegularFiles = jest.fn();
const mockCancelRegularFile = jest.fn();
const mockAddChunkFile = jest.fn();
const mockCancelChunkFile = jest.fn();

jest.mock('./useRegularUpload', () => ({
  __esModule: true,
  default: jest.fn()
}));

jest.mock('./useChunkUpload', () => ({
  __esModule: true,
  default: jest.fn()
}));

jest.mock('../../../config/hueConfig', () => ({
  getLastKnownConfig: () => ({
    storage_browser: {
      concurrent_max_connection: 5
    }
  })
}));

describe('useFileUpload', () => {
  const mockOnComplete = jest.fn();

  const mockFiles: RegularFile[] = [
    {
      uuid: 'file-1',
      filePath: '/path/to/test1.txt',
      file: new File(['test content'], 'test1.txt', { type: 'text/plain' }),
      status: FileStatus.Pending,
      progress: 0
    },
    {
      uuid: 'file-2',
      filePath: '/path/to/test2.txt',
      file: new File(['test content 2'], 'test2.txt', { type: 'text/plain' }),
      status: FileStatus.Pending,
      progress: 0
    }
  ];

  const mockUseRegularUpload = jest.mocked(useRegularUpload);
  const mockUseChunkUpload = jest.mocked(useChunkUpload);

  beforeEach(() => {
    jest.clearAllMocks();

    mockUseRegularUpload.mockReturnValue({
      addFiles: mockAddRegularFiles,
      cancelFile: mockCancelRegularFile,
      isLoading: false
    });

    mockUseChunkUpload.mockReturnValue({
      addFiles: mockAddChunkFile,
      cancelFile: mockCancelChunkFile,
      isLoading: false
    });
  });

  it('should add files to the upload queue with regular upload', () => {
    const { result } = renderHook(() =>
      useFileUpload({ isChunkUpload: false, onComplete: mockOnComplete })
    );

    act(() => {
      result.current.addFiles(mockFiles);
    });

    expect(result.current.uploadQueue).toEqual(mockFiles);
    expect(mockAddRegularFiles).toHaveBeenCalledWith(mockFiles);
    expect(mockAddChunkFile).not.toHaveBeenCalled();
  });

  it('should add files to the upload queue with chunk upload', () => {
    const { result } = renderHook(() =>
      useFileUpload({ isChunkUpload: true, onComplete: mockOnComplete })
    );

    act(() => {
      result.current.addFiles(mockFiles);
    });

    expect(result.current.uploadQueue).toEqual(mockFiles);
    expect(mockAddChunkFile).toHaveBeenCalledWith(mockFiles);
    expect(mockAddRegularFiles).not.toHaveBeenCalled();
  });

  it('should cancel a pending file using regular upload', () => {
    const { result } = renderHook(() =>
      useFileUpload({ isChunkUpload: false, onComplete: mockOnComplete })
    );

    act(() => {
      result.current.addFiles(mockFiles);
    });

    act(() => {
      result.current.cancelFile(mockFiles[0]);
    });

    expect(mockCancelRegularFile).toHaveBeenCalledWith('file-1');
    expect(result.current.uploadQueue[0].status).toBe(FileStatus.Cancelled);
  });

  it('should cancel a pending file using chunk upload', () => {
    const { result } = renderHook(() =>
      useFileUpload({ isChunkUpload: true, onComplete: mockOnComplete })
    );

    act(() => {
      result.current.addFiles(mockFiles);
    });

    act(() => {
      result.current.cancelFile(mockFiles[0]);
    });

    expect(mockCancelChunkFile).toHaveBeenCalledWith('file-1');
    expect(result.current.uploadQueue[0].status).toBe(FileStatus.Cancelled);
  });

  it('should return isLoading as true if regular upload method is loading', () => {
    mockUseRegularUpload.mockReturnValue({
      addFiles: mockAddRegularFiles,
      cancelFile: mockCancelRegularFile,
      isLoading: true
    });

    const { result } = renderHook(() =>
      useFileUpload({ isChunkUpload: false, onComplete: mockOnComplete })
    );

    expect(result.current.isLoading).toBe(true);
  });

  it('should return isLoading as true if chunk upload method is loading', () => {
    mockUseChunkUpload.mockReturnValue({
      addFiles: mockAddChunkFile,
      cancelFile: mockCancelChunkFile,
      isLoading: true
    });

    const { result } = renderHook(() =>
      useFileUpload({ isChunkUpload: true, onComplete: mockOnComplete })
    );

    expect(result.current.isLoading).toBe(true);
  });

  it('should update queue with correct status sent from the queues', () => {
    let capturedUpdateFileVariables: (uuid: string, variables: FileVariables) => void;

    mockUseRegularUpload.mockImplementation(options => {
      capturedUpdateFileVariables = options.updateFileVariables;
      return {
        addFiles: mockAddRegularFiles,
        cancelFile: mockCancelRegularFile,
        isLoading: false
      };
    });

    const { result } = renderHook(() =>
      useFileUpload({ isChunkUpload: false, onComplete: mockOnComplete })
    );

    act(() => {
      result.current.addFiles(mockFiles);
    });

    expect(result.current.uploadQueue[0].status).toBe(FileStatus.Pending);
    expect(result.current.uploadQueue[0].progress).toBe(0);

    act(() => {
      capturedUpdateFileVariables('file-1', {
        status: FileStatus.Uploading,
        progress: 50
      });
    });

    expect(result.current.uploadQueue[0].status).toBe(FileStatus.Uploading);
    expect(result.current.uploadQueue[0].progress).toBe(50);

    act(() => {
      capturedUpdateFileVariables('file-1', {
        status: FileStatus.Uploaded,
        progress: 100
      });
    });

    expect(result.current.uploadQueue[0].status).toBe(FileStatus.Uploaded);
    expect(result.current.uploadQueue[0].progress).toBe(100);

    expect(result.current.uploadQueue[1].status).toBe(FileStatus.Pending);
    expect(result.current.uploadQueue[1].progress).toBe(0);

    const testError = new Error('Upload failed');
    act(() => {
      capturedUpdateFileVariables('file-2', {
        status: FileStatus.Failed,
        error: testError
      });
    });

    expect(result.current.uploadQueue[1].status).toBe(FileStatus.Failed);
    expect(result.current.uploadQueue[1].error).toBe(testError);
  });
});
