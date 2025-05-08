import { renderHook, act, waitFor } from '@testing-library/react';
import useChunkUpload from './useChunkUpload';
import { FileStatus, RegularFile, ChunkedFile } from './types';
import { TaskStatus } from '../../../reactComponents/TaskServer/types';

const mockFile: RegularFile = {
  uuid: 'file-1',
  filePath: '/upload/',
  file: new File(['chunked'], 'chunked.txt', { type: 'text/plain' }),
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

const mockIsSpaceAvailableInServer = jest.fn().mockReturnValue(Promise.resolve(true));
jest.mock('./utils', () => ({
  __esModule: true,
  ...jest.requireActual('./utils'),
  isAllChunksOfFileUploaded: jest.fn(() => true),
  isSpaceAvailableInServer: () => mockIsSpaceAvailableInServer
}));

describe('useChunkUpload', () => {
  const mockUpdateFileVariables = jest.fn();
  const mockOnComplete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should enqueue chunked files when addFiles is called', () => {
    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    act(() => {
      result.current.addFiles([mockFile]);
    });

    expect(mockEnqueue).toHaveBeenCalledWith([mockChunk]);
  });

  it('should call dequeue when cancelFile is called', () => {
    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    act(() => {
      result.current.cancelFile(mockFile.uuid);
    });

    expect(mockDequeue).toHaveBeenCalledWith(mockFile.uuid, 'uuid');
  });

  it('should update file variables on successful chunk upload', async () => {
    mockSave.mockImplementationOnce((_, { onSuccess }) => {
      onSuccess();
    });

    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    await act(() => {
      result.current.addFiles([mockFile]);
    });

    expect(mockUpdateFileVariables).toHaveBeenNthCalledWith(1, mockFile.uuid, {
      status: FileStatus.Uploading
    });

    await waitFor(() => {
      expect(mockUpdateFileVariables).toHaveBeenNthCalledWith(2, mockFile.uuid, {
        status: FileStatus.Uploaded
      });
    });
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

    await act(() => {
      result.current.addFiles([mockFile]);
    });

    await waitFor(() => {
      expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
        status: FileStatus.Failed,
        error: expect.any(Error)
      });
    });
  });

  it('should fail if there is not enough space on the server', async () => {
    mockIsSpaceAvailableInServer.mockImplementation(() => Promise.resolve(false));

    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    await act(async () => {
      result.current.addFiles([mockFile]);
    });

    await waitFor(() => {
      expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
        status: FileStatus.Uploading
      });
      expect(mockUpdateFileVariables).toHaveBeenCalledWith(mockFile.uuid, {
        status: FileStatus.Failed,
        error: expect.any(Error)
      });
      expect(mockSave).not.toHaveBeenCalled();
    });
  });

  it('should reflect loading state from useQueueProcessor', async () => {
    mockIsLoading.mockReturnValue(true);

    const { result } = renderHook(() =>
      useChunkUpload({
        updateFileVariables: mockUpdateFileVariables,
        onComplete: mockOnComplete
      })
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(true);
      expect(mockIsLoading).toHaveBeenCalled();
    });
  });
});
