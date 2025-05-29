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

import { renderHook, act, waitFor } from '@testing-library/react';
import useRegularUpload from './useRegularUpload';
import { FileStatus, RegularFile } from './types';

const mockFile: RegularFile = {
  uuid: 'abc-123',
  filePath: '/uploads/',
  file: new File(['hello'], 'file.txt', { type: 'text/plain' }),
  status: FileStatus.Pending,
  error: undefined,
  progress: 0
};

const mockEnqueue = jest.fn();
const mockDequeue = jest.fn();
const mockIsLoading = jest.fn().mockReturnValue(false);
jest.mock('../useQueueProcessor/useQueueProcessor', () => ({
  __esModule: true,
  default: jest.fn(callback => {
    callback(mockFile);
    return {
      enqueue: mockEnqueue,
      dequeue: mockDequeue,
      isLoading: mockIsLoading()
    };
  })
}));

const mockSave = jest.fn();
jest.mock('../useSaveData/useSaveData', () => ({
  __esModule: true,
  default: jest.fn(() => ({
    save: mockSave
  }))
}));

describe('useRegularUpload', () => {
  const mockUpdateFileVariables = jest.fn();
  const mockOnComplete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should enqueue files when addFiles is called', () => {
    const { result } = renderHook(() =>
      useRegularUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.addFiles([mockFile]);

    expect(mockEnqueue).toHaveBeenCalledWith([mockFile]);
  });

  it('should call dequeue with correct uuid when cancelFile is called', () => {
    const { result } = renderHook(() =>
      useRegularUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.cancelFile(mockFile.uuid);

    expect(mockDequeue).toHaveBeenCalledWith(mockFile.uuid, 'uuid');
  });

  it('should call save with correct payload and update file variables on success', async () => {
    const { result } = renderHook(() =>
      useRegularUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.addFiles([mockFile]);

    expect(mockSave).toHaveBeenCalledWith(expect.any(FormData), expect.any(Object));
    expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
      status: FileStatus.Uploading
    });
  });

  it('should call updateFileVariables with correct status on success', async () => {
    mockSave.mockImplementationOnce((_, { onSuccess }) => {
      onSuccess();
    });

    const { result } = renderHook(() =>
      useRegularUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.addFiles([mockFile]);

    await waitFor(() => {
      expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
        status: FileStatus.Uploaded
      });
    });
  });

  it('should call updateFileVariables with correct status on error', async () => {
    mockSave.mockImplementationOnce((_, { onError }) => {
      onError(new Error('Upload failed'));
    });

    const { result } = renderHook(() =>
      useRegularUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.addFiles([mockFile]);

    await waitFor(() => {
      expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
        status: FileStatus.Failed,
        error: expect.any(Error)
      });
    });
  });

  it('should reflect loading state from useQueueProcessor', () => {
    mockIsLoading.mockReturnValue(true);

    const { result } = renderHook(() =>
      useRegularUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    expect(result.current.isLoading).toBe(true);
  });
});
