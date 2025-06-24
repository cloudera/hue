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

import { get } from '../../../api/utils';
import { TaskStatus } from '../../../reactComponents/TaskServer/types';
import {
  getTotalChunk,
  getMetaData,
  createChunks,
  getStatusHashMap,
  getChunkItemPayload,
  getChunksCompletePayload,
  getItemProgress,
  getItemsTotalProgress,
  addChunkToInProcess,
  isSpaceAvailableInServer,
  isAllChunksOfFileUploaded
} from './utils';
import { FileStatus, RegularFile, ChunkedFile, ChunkedFilesInProgress } from './types';

jest.mock('../../../api/utils');
const mockGet = jest.mocked(get);

describe('utils', () => {
  describe('getTotalChunk function', () => {
    it('should calculate correct number of chunks for exact division', () => {
      expect(getTotalChunk(1000, 100)).toBe(10);
    });

    it('should calculate correct number of chunks with remainder', () => {
      expect(getTotalChunk(1050, 100)).toBe(11);
    });

    it('should return 1 for file smaller than chunk size', () => {
      expect(getTotalChunk(50, 100)).toBe(1);
    });

    it('should handle zero file size', () => {
      expect(getTotalChunk(0, 100)).toBe(0);
    });

    it('should handle single byte file', () => {
      expect(getTotalChunk(1, 100)).toBe(1);
    });
  });

  describe('getMetaData function', () => {
    const mockChunkedFile: ChunkedFile = {
      uuid: 'test-uuid',
      filePath: '/test/path/file.txt',
      file: new Blob(['test content']),
      fileName: 'file.txt',
      totalSize: 1000,
      chunkNumber: 0,
      chunkStartOffset: 0,
      chunkEndOffset: 100,
      totalChunks: 10,
      status: FileStatus.Pending,
      progress: 0
    };

    it('should return correct metadata object', () => {
      const result = getMetaData(mockChunkedFile);

      expect(result).toEqual({
        qqtotalparts: '10',
        qqtotalfilesize: '1000',
        qqfilename: 'file.txt',
        inputName: 'hdfs_file',
        dest: '/test/path/file.txt',
        qquuid: 'test-uuid'
      });
    });

    it('should convert numbers to strings', () => {
      const result = getMetaData(mockChunkedFile);

      expect(typeof result.qqtotalparts).toBe('string');
      expect(typeof result.qqtotalfilesize).toBe('string');
    });
  });

  describe('createChunks function', () => {
    const mockFile = new File(['a'.repeat(250)], 'test.txt', { type: 'text/plain' });
    const mockRegularFile: RegularFile = {
      uuid: 'test-uuid',
      filePath: '/test/path/test.txt',
      file: mockFile,
      status: FileStatus.Pending,
      progress: 0
    };

    it('should create correct number of chunks', () => {
      const chunks = createChunks(mockRegularFile, 100);
      expect(chunks).toHaveLength(3);
      expect(chunks[0].chunkEndOffset).toBe(100);
      expect(chunks[1].chunkEndOffset).toBe(200);
      expect(chunks[2].chunkEndOffset).toBe(250);
    });

    it('should set correct chunk properties', () => {
      const chunks = createChunks(mockRegularFile, 100);

      expect(chunks[0]).toMatchObject({
        uuid: 'test-uuid',
        filePath: '/test/path/test.txt',
        fileName: 'test.txt',
        totalSize: 250,
        totalChunks: 3,
        chunkNumber: 0,
        chunkStartOffset: 0,
        chunkEndOffset: 100
      });

      expect(chunks[2]).toMatchObject({
        chunkNumber: 2,
        chunkStartOffset: 200,
        chunkEndOffset: 250
      });
    });

    it('should create blob chunks with correct sizes', () => {
      const chunks = createChunks(mockRegularFile, 100);

      expect(chunks[0].file.size).toBe(100);
      expect(chunks[1].file.size).toBe(100);
    });

    it('should handle single chunk for small files', () => {
      const smallFile = new File(['small'], 'small.txt');
      const smallRegularFile: RegularFile = {
        ...mockRegularFile,
        file: smallFile
      };

      const chunks = createChunks(smallRegularFile, 100);
      expect(chunks).toHaveLength(1);
      expect(chunks[0].chunkStartOffset).toBe(0);
      expect(chunks[0].chunkEndOffset).toBe(5);
    });
  });

  describe('getStatusHashMap function', () => {
    it('should create correct status hash map', () => {
      const serverResponse = [
        { taskId: 'task1', status: TaskStatus.Success, dateDone: '2023-01-01' },
        { taskId: 'task2', status: TaskStatus.Failure, dateDone: '2023-01-02' },
        { taskId: 'task3', status: TaskStatus.Running, dateDone: '2023-01-03' }
      ];

      const result = getStatusHashMap(serverResponse);

      expect(result).toEqual({
        task1: TaskStatus.Success,
        task2: TaskStatus.Failure,
        task3: TaskStatus.Running
      });
    });

    it('should handle empty array', () => {
      const result = getStatusHashMap([]);
      expect(result).toEqual({});
    });

    it('should handle duplicate task IDs by keeping the last one', () => {
      const serverResponse = [
        { taskId: 'task1', status: TaskStatus.Success, dateDone: '2023-01-01' },
        { taskId: 'task1', status: TaskStatus.Failure, dateDone: '2023-01-02' }
      ];

      const result = getStatusHashMap(serverResponse);
      expect(result.task1).toBe(TaskStatus.Failure);
    });
  });

  describe('getChunkItemPayload function', () => {
    const mockChunkedFile: ChunkedFile = {
      uuid: 'test-uuid',
      filePath: '/test/path/file.txt',
      file: new Blob(['test content']),
      fileName: 'file.txt',
      totalSize: 1000,
      chunkNumber: 2,
      chunkStartOffset: 200,
      chunkEndOffset: 300,
      totalChunks: 10,
      status: FileStatus.Pending,
      progress: 0
    };

    it('should return correct payload structure', () => {
      const result = getChunkItemPayload(mockChunkedFile);

      expect(result).toHaveProperty('url');
      expect(result).toHaveProperty('payload');
      expect(result.payload).toBeInstanceOf(FormData);
    });

    it('should include correct query parameters in URL', () => {
      const result = getChunkItemPayload(mockChunkedFile);

      expect(result.url).toContain('qqtotalparts=10');
      expect(result.url).toContain('qqtotalfilesize=1000');
      expect(result.url).toContain('qqfilename=file.txt');
      expect(result.url).toContain('qqpartindex=2');
      expect(result.url).toContain('qqpartbyteoffset=200');
      expect(result.url).toContain('qqchunksize=100');
    });

    it('should append file to FormData payload', () => {
      const result = getChunkItemPayload(mockChunkedFile);

      expect(result.payload.has('hdfs_file')).toBe(true);
    });
  });

  describe('getChunksCompletePayload function', () => {
    const mockChunkedFile: ChunkedFile = {
      uuid: 'test-uuid',
      filePath: '/test/path/file.txt',
      file: new Blob(['test content']),
      fileName: 'file.txt',
      totalSize: 1000,
      chunkNumber: 0,
      chunkStartOffset: 0,
      chunkEndOffset: 100,
      totalChunks: 10,
      status: FileStatus.Pending,
      progress: 0
    };

    it('should return correct payload structure', () => {
      const result = getChunksCompletePayload(mockChunkedFile);

      expect(result).toHaveProperty('url');
      expect(result).toHaveProperty('payload');
      expect(result.payload).toBeInstanceOf(FormData);
    });

    it('should include all metadata in FormData', () => {
      const result = getChunksCompletePayload(mockChunkedFile);

      expect(result.payload.has('qqtotalparts')).toBe(true);
      expect(result.payload.has('qqtotalfilesize')).toBe(true);
      expect(result.payload.has('qqfilename')).toBe(true);
      expect(result.payload.has('inputName')).toBe(true);
      expect(result.payload.has('dest')).toBe(true);
      expect(result.payload.has('qquuid')).toBe(true);
    });
  });

  describe('getItemProgress function', () => {
    it('should calculate correct progress percentage', () => {
      const progressEvent = {
        loaded: 50,
        total: 100
      } as ProgressEvent;

      expect(getItemProgress(progressEvent)).toBe(50);
    });

    it('should return 0 for undefined progress', () => {
      expect(getItemProgress(undefined)).toBe(0);
    });

    it('should return 0 when total is 0', () => {
      const progressEvent = {
        loaded: 50,
        total: 0
      } as ProgressEvent;

      expect(getItemProgress(progressEvent)).toBe(0);
    });

    it('should return 0 when loaded or total is missing', () => {
      const progressEvent = {
        loaded: 0
      } as ProgressEvent;

      expect(getItemProgress(progressEvent)).toBe(0);
    });

    it('should round to nearest integer', () => {
      const progressEvent = {
        loaded: 33,
        total: 100
      } as ProgressEvent;

      expect(getItemProgress(progressEvent)).toBe(33);
    });
  });

  describe('getItemsTotalProgress function', () => {
    const mockChunkItem: ChunkedFile = {
      uuid: 'test-uuid',
      filePath: '/test/path/file.txt',
      file: new Blob(),
      fileName: 'file.txt',
      totalSize: 1000,
      chunkNumber: 0,
      chunkStartOffset: 0,
      chunkEndOffset: 100,
      totalChunks: 10,
      status: FileStatus.Pending,
      progress: 0
    };

    const mockChunks = [
      { chunkNumber: 0, progress: 100, chunkSize: 100 },
      { chunkNumber: 1, progress: 50, chunkSize: 100 },
      { chunkNumber: 2, progress: 0, chunkSize: 100 }
    ];

    it('should calculate correct total progress', () => {
      const result = getItemsTotalProgress(mockChunkItem, mockChunks);
      expect(result).toBe(15);
    });

    it('should return 0 when chunkItem is undefined', () => {
      expect(getItemsTotalProgress(undefined, mockChunks)).toBe(0);
    });

    it('should return 0 when chunks is undefined', () => {
      expect(getItemsTotalProgress(mockChunkItem, undefined)).toBe(0);
    });

    it('should handle empty chunks array', () => {
      expect(getItemsTotalProgress(mockChunkItem, [])).toBe(0);
    });
  });

  describe('addChunkToInProcess function', () => {
    const mockChunkItem: ChunkedFile = {
      uuid: 'test-uuid',
      filePath: '/test/path/file.txt',
      file: new Blob(['content']),
      fileName: 'file.txt',
      totalSize: 1000,
      chunkNumber: 0,
      chunkStartOffset: 0,
      chunkEndOffset: 100,
      totalChunks: 10,
      status: FileStatus.Pending,
      progress: 0
    };

    it('should add new chunk to empty in-process object', () => {
      const inProcess: ChunkedFilesInProgress = {};
      const result = addChunkToInProcess(inProcess, mockChunkItem);

      expect(result['test-uuid']).toHaveLength(1);
      expect(result['test-uuid'][0]).toEqual({
        chunkNumber: 0,
        progress: 0,
        chunkSize: 7
      });
    });

    it('should add chunk to existing file chunks', () => {
      const inProcess: ChunkedFilesInProgress = {
        'test-uuid': [{ chunkNumber: 0, progress: 100, chunkSize: 100 }]
      };

      const newChunk = { ...mockChunkItem, chunkNumber: 1 };
      const result = addChunkToInProcess(inProcess, newChunk);

      expect(result['test-uuid']).toHaveLength(2);
      expect(result['test-uuid'][1].chunkNumber).toBe(1);
    });

    it('should not affect other files in progress', () => {
      const inProcess: ChunkedFilesInProgress = {
        'other-uuid': [{ chunkNumber: 0, progress: 50, chunkSize: 100 }]
      };

      const result = addChunkToInProcess(inProcess, mockChunkItem);

      expect(result['other-uuid']).toHaveLength(1);
      expect(result['test-uuid']).toHaveLength(1);
    });
  });

  describe('isSpaceAvailableInServer function', () => {
    beforeEach(() => {
      jest.clearAllMocks();
    });

    it('should return true when sufficient space is available', async () => {
      mockGet.mockResolvedValue({
        upload_available_space: 1000
      });

      const result = await isSpaceAvailableInServer(500);
      expect(result).toBe(true);
    });

    it('should return false when insufficient space is available', async () => {
      mockGet.mockResolvedValue({
        upload_available_space: 100
      });

      const result = await isSpaceAvailableInServer(500);
      expect(result).toBe(false);
    });

    it('should return false when upload_available_space is 0', async () => {
      mockGet.mockResolvedValue({
        upload_available_space: 0
      });

      const result = await isSpaceAvailableInServer(500);
      expect(result).toBe(false);
    });

    it('should return false when upload_available_space is missing', async () => {
      mockGet.mockResolvedValue({});

      const result = await isSpaceAvailableInServer(500);
      expect(result).toBe(false);
    });

    it('should return false when API call fails', async () => {
      mockGet.mockResolvedValue(null);

      const result = await isSpaceAvailableInServer(500);
      expect(result).toBe(false);
    });
  });

  describe('isAllChunksOfFileUploaded function', () => {
    const mockChunk: ChunkedFile = {
      uuid: 'test-uuid',
      filePath: '/test/path/file.txt',
      file: new Blob(),
      fileName: 'file.txt',
      totalSize: 1000,
      chunkNumber: 0,
      chunkStartOffset: 0,
      chunkEndOffset: 100,
      totalChunks: 3,
      status: FileStatus.Pending,
      progress: 0
    };

    it('should return true when all chunks are uploaded', () => {
      const filesInProgress: ChunkedFilesInProgress = {
        'test-uuid': [
          { chunkNumber: 0, progress: 100, chunkSize: 100 },
          { chunkNumber: 1, progress: 100, chunkSize: 100 },
          { chunkNumber: 2, progress: 100, chunkSize: 100 }
        ]
      };

      const result = isAllChunksOfFileUploaded(filesInProgress, mockChunk);
      expect(result).toBe(true);
    });

    it('should return false when chunk count does not match', () => {
      const filesInProgress: ChunkedFilesInProgress = {
        'test-uuid': [
          { chunkNumber: 0, progress: 100, chunkSize: 100 },
          { chunkNumber: 1, progress: 100, chunkSize: 100 }
        ]
      };

      const result = isAllChunksOfFileUploaded(filesInProgress, mockChunk);
      expect(result).toBe(false);
    });

    it('should return false when some chunks are not fully uploaded', () => {
      const filesInProgress: ChunkedFilesInProgress = {
        'test-uuid': [
          { chunkNumber: 0, progress: 100, chunkSize: 100 },
          { chunkNumber: 2, progress: 100, chunkSize: 100 }
        ]
      };

      const result = isAllChunksOfFileUploaded(filesInProgress, mockChunk);
      expect(result).toBe(false);
    });

    it('should throw error when file is not in progress (current implementation behavior)', () => {
      const filesInProgress: ChunkedFilesInProgress = {};

      expect(() => {
        isAllChunksOfFileUploaded(filesInProgress, mockChunk);
      }).toThrow("Cannot read properties of undefined (reading 'length')");
    });

    it('should handle empty chunks array', () => {
      const filesInProgress: ChunkedFilesInProgress = {
        'test-uuid': []
      };

      const mockChunkWithZeroTotal = { ...mockChunk, totalChunks: 0 };
      const result = isAllChunksOfFileUploaded(filesInProgress, mockChunkWithZeroTotal);
      expect(result).toBe(true);
    });
  });
});
