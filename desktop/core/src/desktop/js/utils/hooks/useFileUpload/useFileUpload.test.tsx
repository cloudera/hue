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
import { FileStatus, RegularFile } from './types';

const mockAddRegularFiles = jest.fn();
const mockCancelRegularFile = jest.fn();
const mockAddChunkFile = jest.fn();
const mockCancelChunkFile = jest.fn();
const mockLoading = jest.fn().mockReturnValue(false);

jest.mock('./useRegularUpload', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    addFiles: mockAddRegularFiles,
    cancelFile: mockCancelRegularFile,
    isLoading: mockLoading()
  }))
}));
jest.mock('./useChunkUpload', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    addFiles: mockAddChunkFile,
    cancelFile: mockCancelChunkFile,
    isLoading: mockLoading()
  }))
}));

describe('useFileUpload', () => {
  const mockOnComplete = jest.fn();

  const mockFiles: RegularFile[] = [
    {
      uuid: '1',
      filePath: 'path/to/file',
      file: new File(['content'], 'file.txt', { type: 'text/plain' }),
      status: FileStatus.Pending,
      error: undefined,
      progress: 0
    },
    {
      uuid: '2',
      filePath: 'path/to/file2',
      file: new File(['content'], 'file2.txt', { type: 'text/plain' }),
      status: FileStatus.Pending,
      error: undefined,
      progress: 0
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('adds files to the upload queue with regular upload', () => {
    const { result } = renderHook(() =>
      useFileUpload({ isChunkUpload: false, onComplete: mockOnComplete })
    );

    act(() => {
      result.current.addFiles(mockFiles);
    });

    expect(result.current.uploadQueue).toEqual(mockFiles);
    expect(mockAddRegularFiles).toHaveBeenCalledWith(mockFiles);
  });

  it('adds files to the upload queue with chunk upload', () => {
    const { result } = renderHook(() =>
      useFileUpload({ isChunkUpload: true, onComplete: mockOnComplete })
    );

    act(() => {
      result.current.addFiles(mockFiles);
    });

    expect(result.current.uploadQueue).toEqual(mockFiles);
    expect(mockAddChunkFile).toHaveBeenCalledWith(mockFiles);
  });

  it('cancels a pending file using regular upload', () => {
    const { result } = renderHook(() =>
      useFileUpload({ isChunkUpload: false, onComplete: mockOnComplete })
    );

    act(() => {
      result.current.addFiles(mockFiles);
    });

    act(() => {
      result.current.cancelFile(mockFiles[1]);
    });

    expect(mockCancelRegularFile).toHaveBeenCalledWith(mockFiles[1].uuid);
  });

  it('cancels a pending file using chunk upload', () => {
    const { result } = renderHook(() =>
      useFileUpload({ isChunkUpload: true, onComplete: mockOnComplete })
    );

    act(() => {
      result.current.addFiles(mockFiles);
    });

    act(() => {
      result.current.cancelFile(mockFiles[1]);
    });

    expect(mockCancelChunkFile).toHaveBeenCalledWith(mockFiles[1].uuid);
  });

  it('returns isLoading as true if regular upload method is loading', () => {
    mockLoading.mockReturnValue(true);
    const { result } = renderHook(() =>
      useFileUpload({ isChunkUpload: false, onComplete: mockOnComplete })
    );

    expect(result.current.isLoading).toBe(true);
  });

  it('returns isLoading as true if chunk upload method is loading', () => {
    mockLoading.mockReturnValue(true);
    const { result } = renderHook(() =>
      useFileUpload({ isChunkUpload: true, onComplete: mockOnComplete })
    );

    expect(result.current.isLoading).toBe(true);
  });
});
