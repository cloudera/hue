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

import { renderHook, waitFor } from '@testing-library/react';
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

let mockProcessCallback: ((item: RegularFile) => Promise<void>) | null = null;
let mockOnSuccessCallback: (() => void) | null = null;

jest.mock('../useQueueProcessor/useQueueProcessor', () => ({
  __esModule: true,
  default: jest.fn((processCallback, options) => {
    mockProcessCallback = processCallback;
    mockOnSuccessCallback = options.onSuccess;
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
    mockProcessCallback = null;
    mockOnSuccessCallback = null;
  });

  it('should enqueue files when addFiles is called', async () => {
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
    if (mockProcessCallback) {
      await mockProcessCallback(mockFile);
    }

    expect(mockSave).toHaveBeenCalledTimes(1);
    const [formDataArg, optionsArg] = mockSave.mock.calls[0];

    // FormData: only the file is sent
    expect(formDataArg).toBeInstanceOf(FormData);
    const fdFile = formDataArg.get('file') as File;
    expect(fdFile).toBeInstanceOf(File);
    expect(fdFile.name).toBe('file.txt');
    expect(formDataArg.has('destination_path')).toBe(false);
    expect(formDataArg.has('overwrite')).toBe(false);

    // Params: destination_path and overwrite=false
    expect(optionsArg).toBeDefined();
    expect(optionsArg.options).toBeDefined();
    expect(optionsArg.options.params).toEqual({
      destination_path: '/uploads/',
      overwrite: 'false'
    });
    expect(typeof optionsArg.onSuccess).toBe('function');
    expect(typeof optionsArg.onError).toBe('function');
    expect(typeof optionsArg.options.onUploadProgress).toBe('function');

    expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
      status: FileStatus.Uploading
    });
  });

  it('should include overwrite=true in params when file has overwrite flag', async () => {
    const { result } = renderHook(() =>
      useRegularUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    const fileWithOverwrite: RegularFile = { ...mockFile, overwrite: true };
    result.current.addFiles([fileWithOverwrite]);
    if (mockProcessCallback) {
      await mockProcessCallback(fileWithOverwrite);
    }

    const [formDataArg, optionsArg] = mockSave.mock.calls.at(-1)!;

    // FormData still only has the file
    expect(formDataArg).toBeInstanceOf(FormData);
    expect((formDataArg.get('file') as File).name).toBe('file.txt');
    expect(formDataArg.has('destination_path')).toBe(false);
    expect(formDataArg.has('overwrite')).toBe(false);

    // Params: destination_path and overwrite=true
    expect(optionsArg.options.params).toEqual({
      destination_path: '/uploads/',
      overwrite: 'true'
    });
  });

  it('should call updateFileVariables with correct status on success', async () => {
    const { result } = renderHook(() =>
      useRegularUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.addFiles([mockFile]);

    if (mockProcessCallback) {
      mockSave.mockImplementationOnce((_, { onSuccess }) => {
        onSuccess();
      });

      await mockProcessCallback(mockFile);
    }

    await waitFor(() => {
      expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
        status: FileStatus.Uploaded
      });
    });
  });

  it('should call updateFileVariables with correct status on error', async () => {
    const { result } = renderHook(() =>
      useRegularUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.addFiles([mockFile]);

    if (mockProcessCallback) {
      mockSave.mockImplementationOnce((_, { onError }) => {
        onError(new Error('Upload failed'));
      });

      await mockProcessCallback(mockFile);
    }

    await waitFor(() => {
      expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
        status: FileStatus.Failed,
        error: new Error('Upload failed')
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

  it('should call onComplete when all files are processed', async () => {
    const { result } = renderHook(() =>
      useRegularUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.addFiles([mockFile]);

    if (mockProcessCallback) {
      mockSave.mockImplementationOnce((_, { onSuccess }) => {
        onSuccess();
      });

      await mockProcessCallback(mockFile);

      if (mockOnSuccessCallback) {
        mockOnSuccessCallback();
      }
    }

    await waitFor(() => {
      expect(mockOnComplete).toHaveBeenCalled();
    });
  });
});
