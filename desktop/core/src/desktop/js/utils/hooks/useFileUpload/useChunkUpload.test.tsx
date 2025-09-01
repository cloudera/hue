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

import { renderHook, waitFor, act } from '@testing-library/react';
import useChunkUpload from './useChunkUpload';
import { FileStatus, RegularFile, ChunkedFile, ChunkedFilesInProgress } from './types';
import { TaskServerResponse, TaskStatus } from '../../../reactComponents/TaskServer/types';
import { GET_TASKS_URL } from '../../../reactComponents/TaskServer/constants';
import { DEFAULT_CONCURRENT_MAX_CONNECTIONS } from '../../constants/storageBrowser';
import useQueueProcessor from '../useQueueProcessor/useQueueProcessor';

const mockFile: RegularFile = {
  uuid: 'file-1',
  filePath: '/upload/',
  file: new File(['chunked'], 'chunked.txt', { type: 'text/plain' }),
  status: FileStatus.Pending,
  error: undefined,
  progress: 0
};

const mockFile2: RegularFile = {
  uuid: 'file-2',
  filePath: '/upload/',
  file: new File(['chunked2'], 'chunked2.txt', { type: 'text/plain' }),
  status: FileStatus.Pending,
  error: undefined,
  progress: 0
};

const mockLargeFile: RegularFile = {
  uuid: 'large-file-1',
  filePath: '/upload/',
  file: new File([new ArrayBuffer(1024 * 1024 * 10)], 'large.txt', { type: 'text/plain' }),
  status: FileStatus.Pending,
  error: undefined,
  progress: 0
};

const mockEmptyFile: RegularFile = {
  uuid: 'empty-file-1',
  filePath: '/upload/',
  file: new File([''], 'empty.txt', { type: 'text/plain' }),
  status: FileStatus.Pending,
  error: undefined,
  progress: 0
};

const mockChunk: ChunkedFile = {
  ...mockFile,
  chunkNumber: 0,
  totalChunks: 1,
  totalSize: mockFile.file.size,
  chunkStartOffset: 0,
  chunkEndOffset: mockFile.file.size,
  filePath: '/upload/',
  fileName: 'chunked.txt',
  file: new Blob(['chunked']),
  progress: 0
};

const mockEnqueue = jest.fn();
const mockDequeue = jest.fn();
let mockQueueCallback: (file: ChunkedFile) => void = jest.fn();

jest.mock('../useQueueProcessor/useQueueProcessor', () => ({
  __esModule: true,
  default: jest.fn(callback => {
    mockQueueCallback = callback;
    return {
      enqueue: mockEnqueue,
      dequeue: mockDequeue
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

const mockLoadData = jest.fn();
jest.mock('../useLoadData/useLoadData', () => ({
  __esModule: true,
  default: jest.fn((url, options) => {
    mockLoadData(url, options);
    return {};
  })
}));

const mockIsSpaceAvailableInServer = jest.fn().mockImplementation(() => Promise.resolve(true));
const mockIsAllChunksOfFileUploaded = jest.fn().mockImplementation(() => true);

jest.mock('./utils', () => {
  const actualUtils = jest.requireActual('./utils');
  return {
    __esModule: true,
    ...actualUtils,
    isSpaceAvailableInServer: () => mockIsSpaceAvailableInServer(),
    isAllChunksOfFileUploaded: (filesInProgress: ChunkedFilesInProgress, chunk: ChunkedFile) => {
      const result = mockIsAllChunksOfFileUploaded(filesInProgress, chunk);
      return result;
    }
  };
});

describe('useChunkUpload', () => {
  const mockUpdateFileVariables = jest.fn();
  const mockOnComplete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockIsSpaceAvailableInServer.mockResolvedValue(true);
    mockIsAllChunksOfFileUploaded.mockReturnValue(true);
  });

  it('should call enqueue files when addFiles is called', () => {
    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.addFiles([mockFile]);

    expect(mockEnqueue).toHaveBeenCalledWith([
      {
        uuid: mockFile.uuid,
        fileName: mockFile.file.name,
        totalSize: mockFile.file.size,
        chunkNumber: 0,
        totalChunks: 1,
        chunkStartOffset: 0,
        chunkEndOffset: mockFile.file.size,
        filePath: mockFile.filePath,
        file: new Blob([mockFile.file]),
        status: FileStatus.Pending,
        progress: 0,
        error: undefined
      }
    ]);
  });

  it('should call dequeue when cancelFile is called', () => {
    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.cancelFile(mockFile.uuid);

    expect(mockDequeue).toHaveBeenCalledWith(mockFile.uuid, 'uuid');
  });

  it('should handle multiple files upload', () => {
    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.addFiles([mockFile, mockFile2]);

    expect(mockEnqueue).toHaveBeenCalledTimes(2);
  });

  it('should handle empty files', () => {
    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.addFiles([mockEmptyFile]);

    expect(mockEnqueue).toHaveBeenCalledWith([
      {
        uuid: mockEmptyFile.uuid,
        fileName: mockEmptyFile.file.name,
        totalSize: mockEmptyFile.file.size,
        chunkNumber: 0,
        totalChunks: 1,
        chunkStartOffset: 0,
        chunkEndOffset: 0,
        filePath: mockEmptyFile.filePath,
        file: new Blob(['']),
        status: FileStatus.Pending,
        progress: 0,
        error: undefined
      }
    ]);
  });

  it('should create multiple chunks for large file', () => {
    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.addFiles([mockLargeFile]);

    expect(mockEnqueue).toHaveBeenCalledWith([
      {
        uuid: mockLargeFile.uuid,
        filePath: '/upload/',
        fileName: mockLargeFile.file.name,
        totalSize: mockLargeFile.file.size,
        totalChunks: 2,
        chunkNumber: 0,
        chunkStartOffset: 0,
        chunkEndOffset: 5242880,
        file: new Blob([new ArrayBuffer(5242880)]),
        status: FileStatus.Pending,
        progress: 0,
        error: undefined
      },
      {
        uuid: mockLargeFile.uuid,
        filePath: '/upload/',
        fileName: mockLargeFile.file.name,
        totalSize: mockLargeFile.file.size,
        totalChunks: 2,
        chunkNumber: 1,
        chunkStartOffset: 5242880,
        chunkEndOffset: 10485760,
        file: new Blob([new ArrayBuffer(5242880)]),
        status: FileStatus.Pending,
        progress: 0,
        error: undefined
      }
    ]);
  });

  it('should update file variables on chunk upload error', async () => {
    mockSave.mockImplementationOnce((_, { onError }) => {
      onError(new Error('chunk upload failed'));
    });

    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.addFiles([mockFile]);

    mockQueueCallback(mockChunk);

    await waitFor(() => {
      expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
        status: FileStatus.Failed,
        error: new Error('chunk upload failed')
      });
    });
  });

  it('should fail if there is not enough space on the server', async () => {
    mockIsSpaceAvailableInServer.mockResolvedValue(false);

    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.addFiles([mockFile]);

    mockQueueCallback(mockChunk);

    await waitFor(() => {
      expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
        status: FileStatus.Uploading
      });
      expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
        status: FileStatus.Failed,
        error: new Error('Upload server ran out of space. Try again later.')
      });
    });
    expect(mockSave).not.toHaveBeenCalled();
  });

  it('should handle successful chunk upload and progress', async () => {
    mockSave
      .mockImplementationOnce((_, { onSuccess, options }) => {
        if (options?.onUploadProgress) {
          options.onUploadProgress({ loaded: 50, total: 100 });
          options.onUploadProgress({ loaded: 100, total: 100 });
        }
        onSuccess();
      })
      .mockImplementationOnce((_, { onSuccess }) => onSuccess()); // Completion

    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.addFiles([mockFile]);

    await act(async () => {
      mockQueueCallback(mockChunk);
    });

    await waitFor(() => {
      expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
        status: FileStatus.Uploading
      });
      expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
        progress: 50
      });
      expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
        progress: 100
      });
      expect(mockSave).toHaveBeenCalledTimes(2); // Once for chunk, once for completion
    });
  });

  it('should handle chunk completion error', async () => {
    mockIsAllChunksOfFileUploaded.mockReturnValue(true);
    mockSave
      .mockImplementationOnce((_, { onSuccess }) => onSuccess()) // Chunk upload
      .mockImplementationOnce((_, { onError }) => onError(new Error('completion failed'))); // Completion

    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.addFiles([mockFile]);

    mockQueueCallback(mockChunk);

    await waitFor(() => {
      expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
        status: FileStatus.Failed,
        error: new Error('completion failed')
      });
    });
  });

  it('should poll task server for final status updates', async () => {
    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    expect(mockLoadData).toHaveBeenCalledWith(GET_TASKS_URL, {
      pollInterval: 5000,
      skip: true,
      onSuccess: expect.any(Function)
    });

    mockIsAllChunksOfFileUploaded.mockReturnValue(true);
    mockSave
      .mockImplementationOnce((_, { onSuccess }) => onSuccess()) // Chunk upload
      .mockImplementationOnce((_, { onSuccess }) => onSuccess()); // Completion

    await act(async () => {
      result.current.addFiles([mockFile]);
      mockQueueCallback(mockChunk);
    });

    await waitFor(() => {
      expect(mockLoadData).toHaveBeenCalledWith(GET_TASKS_URL, {
        pollInterval: 5000,
        skip: false,
        onSuccess: expect.any(Function)
      });
    });
  });

  it('should handle task server success response', async () => {
    let taskServerCallback: ((response: TaskServerResponse[]) => void) | undefined;
    mockLoadData.mockImplementation((url, options) => {
      taskServerCallback = options.onSuccess;
    });

    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    mockIsAllChunksOfFileUploaded.mockReturnValue(true);
    mockSave
      .mockImplementationOnce((_, { onSuccess }) => onSuccess()) // Chunk upload
      .mockImplementationOnce((_, { onSuccess }) => onSuccess()); // Completion

    await act(async () => {
      result.current.addFiles([mockFile]);
      mockQueueCallback(mockChunk);
    });

    const mockResponse = [
      { taskId: mockFile.uuid, status: TaskStatus.Success, dateDone: new Date().toISOString() }
    ];

    await act(async () => {
      if (taskServerCallback) {
        taskServerCallback(mockResponse);
      }
    });

    expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
      status: FileStatus.Uploaded
    });
    expect(mockOnComplete).toHaveBeenCalled();
  });

  it('should handle task server failure response', async () => {
    let taskServerCallback: ((response: TaskServerResponse[]) => void) | undefined;
    mockLoadData.mockImplementation((url, options) => {
      taskServerCallback = options.onSuccess;
    });

    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    mockIsAllChunksOfFileUploaded.mockReturnValue(true);
    mockSave
      .mockImplementationOnce((_, { onSuccess }) => onSuccess()) // Chunk upload
      .mockImplementationOnce((_, { onSuccess }) => onSuccess()); // Completion

    await act(async () => {
      result.current.addFiles([mockFile]);
      mockQueueCallback(mockChunk);
    });

    const mockResponse = [
      { taskId: mockFile.uuid, status: TaskStatus.Failure, dateDone: new Date().toISOString() }
    ];

    await act(async () => {
      if (taskServerCallback) {
        taskServerCallback(mockResponse);
      }
    });

    expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
      status: FileStatus.Failed
    });
    expect(mockOnComplete).toHaveBeenCalled();
  });

  it('should handle task server pending response', async () => {
    let taskServerCallback: ((response: TaskServerResponse[]) => void) | undefined;
    mockLoadData.mockImplementation((url, options) => {
      taskServerCallback = options.onSuccess;
    });

    const mockOnCompleteForPending = jest.fn();

    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnCompleteForPending
      })
    );

    mockIsAllChunksOfFileUploaded.mockReturnValue(true);
    mockSave
      .mockImplementationOnce((_, { onSuccess }) => onSuccess()) // Chunk upload
      .mockImplementationOnce((_, { onSuccess }) => onSuccess()); // Completion

    await act(async () => {
      result.current.addFiles([mockFile]);
      mockQueueCallback(mockChunk);
    });

    const mockResponse = [
      { taskId: mockFile.uuid, status: TaskStatus.Running, dateDone: new Date().toISOString() }
    ];

    await act(async () => {
      if (taskServerCallback) {
        taskServerCallback(mockResponse);
      }
    });

    expect(mockOnCompleteForPending).not.toHaveBeenCalled();
  });

  it('should return correct isLoading state', async () => {
    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    expect(result.current.isLoading).toBe(false);

    result.current.addFiles([mockFile]);

    expect(result.current.isLoading).toBe(false);
  });

  it('should handle concurrent uploads with custom concurrentProcess', () => {
    renderHook(() =>
      useChunkUpload({
        concurrentProcess: 3,
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    expect(useQueueProcessor).toHaveBeenCalledWith(expect.any(Function), { concurrentProcess: 3 });
  });

  it('should use default concurrent process when not specified', () => {
    renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    expect(useQueueProcessor).toHaveBeenCalledWith(mockQueueCallback, {
      concurrentProcess: DEFAULT_CONCURRENT_MAX_CONNECTIONS
    });
  });

  it('should handle progress updates correctly', async () => {
    const mockProgressEvent = { loaded: 75, total: 100 };

    mockSave.mockImplementationOnce((_, { onSuccess, options }) => {
      if (options?.onUploadProgress) {
        options.onUploadProgress(mockProgressEvent);
      }
      onSuccess();
    });

    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    result.current.addFiles([mockFile]);

    await act(async () => {
      mockQueueCallback(mockChunk);
    });

    await waitFor(() => {
      expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
        status: FileStatus.Uploading
      });
      expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
        progress: 75
      });
    });
  });

  it('should handle multiple task server responses', async () => {
    let taskServerCallback: ((response: TaskServerResponse[]) => void) | undefined;
    mockLoadData.mockImplementation((url, options) => {
      taskServerCallback = options.onSuccess;
    });

    renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    const mockResponse = [
      { taskId: 'file-1', status: TaskStatus.Success, dateDone: new Date().toISOString() },
      { taskId: 'file-2', status: TaskStatus.Running, dateDone: new Date().toISOString() },
      { taskId: 'file-3', status: TaskStatus.Failure, dateDone: new Date().toISOString() }
    ];

    await act(async () => {
      if (taskServerCallback) {
        taskServerCallback(mockResponse);
      }
    });

    expect(mockUpdateFileVariables).not.toHaveBeenCalledWith('file-1', expect.anything());
    expect(mockUpdateFileVariables).not.toHaveBeenCalledWith('file-3', expect.anything());
    expect(mockUpdateFileVariables).not.toHaveBeenCalledWith('file-2', expect.anything());
  });

  it('should call onComplete when all files finish uploading', async () => {
    let taskServerCallback: ((response: TaskServerResponse[]) => void) | undefined;
    mockLoadData.mockImplementation((url, options) => {
      taskServerCallback = options.onSuccess;
    });

    const mockOnCompleteForTest = jest.fn();

    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnCompleteForTest
      })
    );

    mockIsAllChunksOfFileUploaded.mockReturnValue(true);
    mockSave
      .mockImplementationOnce((_, { onSuccess }) => onSuccess()) // Chunk upload
      .mockImplementationOnce((_, { onSuccess }) => onSuccess()); // Completion

    await act(async () => {
      result.current.addFiles([mockFile]);
      mockQueueCallback(mockChunk);
    });

    expect(mockOnCompleteForTest).not.toHaveBeenCalled();

    const mockResponse = [
      { taskId: mockFile.uuid, status: TaskStatus.Success, dateDone: new Date().toISOString() }
    ];

    await act(async () => {
      if (taskServerCallback) {
        taskServerCallback(mockResponse);
      }
    });

    expect(mockOnCompleteForTest).toHaveBeenCalledTimes(1);
    expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
      status: FileStatus.Uploaded
    });
  });

  it('should call onComplete only after all multiple files finish uploading', async () => {
    let taskServerCallback: ((response: TaskServerResponse[]) => void) | undefined;
    mockLoadData.mockImplementation((url, options) => {
      taskServerCallback = options.onSuccess;
    });

    const mockOnCompleteForMultipleFiles = jest.fn();

    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnCompleteForMultipleFiles
      })
    );

    mockIsAllChunksOfFileUploaded.mockReturnValue(true);
    mockSave.mockImplementation((_, { onSuccess }) => onSuccess());

    const mockChunk2: ChunkedFile = {
      ...mockFile2,
      chunkNumber: 0,
      totalChunks: 1,
      totalSize: mockFile2.file.size,
      chunkStartOffset: 0,
      chunkEndOffset: mockFile2.file.size,
      filePath: '/upload/',
      fileName: 'chunked2.txt',
      file: new Blob(['chunked2']),
      progress: 0
    };

    await act(async () => {
      result.current.addFiles([mockFile, mockFile2]);
      mockQueueCallback(mockChunk);
      mockQueueCallback(mockChunk2);
    });

    expect(mockOnCompleteForMultipleFiles).not.toHaveBeenCalled();

    const mockResponseFirstFile = [
      { taskId: mockFile.uuid, status: TaskStatus.Success, dateDone: new Date().toISOString() }
    ];

    await act(async () => {
      if (taskServerCallback) {
        taskServerCallback(mockResponseFirstFile);
      }
    });

    expect(mockOnCompleteForMultipleFiles).not.toHaveBeenCalled();

    const mockResponseSecondFile = [
      { taskId: mockFile2.uuid, status: TaskStatus.Success, dateDone: new Date().toISOString() }
    ];

    await act(async () => {
      if (taskServerCallback) {
        taskServerCallback(mockResponseSecondFile);
      }
    });

    expect(mockOnCompleteForMultipleFiles).toHaveBeenCalledTimes(1);
  });
});
