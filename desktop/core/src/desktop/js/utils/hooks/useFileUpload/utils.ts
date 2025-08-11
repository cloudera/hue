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
import {
  CHUNK_UPLOAD_URL,
  CHUNK_UPLOAD_COMPLETE_URL,
  UPLOAD_AVAILABLE_SPACE_URL
} from '../../../apps/storageBrowser/api';
import { TaskServerResponse, TaskStatus } from '../../../reactComponents/TaskServer/types';
import {
  ChunkedFile,
  ChunkedFilesInProgress,
  FileChunkMetaData,
  FileUploadApiPayload,
  RegularFile
} from './types';

export const getTotalChunk = (fileSize: number, DEFAULT_CHUNK_SIZE: number): number => {
  return Math.ceil(fileSize / DEFAULT_CHUNK_SIZE);
};

export const getMetaData = (item: ChunkedFile): FileChunkMetaData => ({
  qqtotalparts: String(item.totalChunks),
  qqtotalfilesize: String(item.totalSize),
  qqfilename: item.fileName,
  inputName: 'hdfs_file',
  dest: item.filePath,
  qquuid: item.uuid
});

export const createChunks = (item: RegularFile, chunkSize: number): ChunkedFile[] => {
  const totalChunks = Math.max(1, getTotalChunk(item.file.size, chunkSize));
  const chunks = Array.from({ length: totalChunks }, (_, i) => {
    const chunkStartOffset = i * chunkSize;
    const chunkEndOffset = Math.min(chunkStartOffset + chunkSize, item.file.size);
    return {
      ...item,
      fileName: item.file.name,
      totalSize: item.file.size,
      file: item.file.slice(chunkStartOffset, chunkEndOffset),
      totalChunks,
      chunkNumber: i,
      chunkStartOffset,
      chunkEndOffset,
      overwrite: item.overwrite
    };
  });

  return chunks;
};

export const getStatusHashMap = (
  serverResponse: TaskServerResponse[]
): Record<string, TaskStatus> =>
  serverResponse.reduce(
    (acc, row: TaskServerResponse) => ({
      ...acc,
      [row.taskId]: row.status
    }),
    {}
  );

export const getChunkItemPayload = (chunkItem: ChunkedFile): FileUploadApiPayload => {
  const metaData = getMetaData(chunkItem);
  const chunkQueryParams = new URLSearchParams({
    ...metaData,
    qqpartindex: String(chunkItem.chunkNumber),
    qqpartbyteoffset: String(chunkItem.chunkStartOffset),
    qqchunksize: String(chunkItem.chunkEndOffset - chunkItem.chunkStartOffset)
  }).toString();

  const url = `${CHUNK_UPLOAD_URL}?${chunkQueryParams}`;

  const payload = new FormData();
  payload.append('hdfs_file', chunkItem.file);
  payload.append('overwrite', chunkItem.overwrite ? 'true' : 'false');
  return { url, payload };
};

export const getChunksCompletePayload = (processingItem: ChunkedFile): FileUploadApiPayload => {
  const fileMetaData = getMetaData(processingItem);
  const payload = new FormData();
  Object.entries(fileMetaData).forEach(([key, value]) => {
    payload.append(key, value);
  });
  return { url: CHUNK_UPLOAD_COMPLETE_URL, payload };
};

export const getItemProgress = (progress?: ProgressEvent): number => {
  if (!progress?.total || !progress?.loaded || progress?.total === 0) {
    return 0;
  }
  return Math.round((progress.loaded * 100) / progress.total);
};

export const getItemsTotalProgress = (
  chunkItem?: ChunkedFile,
  chunks?: ChunkedFilesInProgress['uuid']
): number => {
  if (!chunkItem || !chunks) {
    return 0;
  }
  return chunks.reduce((acc, chunk) => {
    return acc + (chunk.progress * chunk.chunkSize) / chunkItem.totalSize;
  }, 0);
};

export const addChunkToInProcess = (
  currentInProcess: ChunkedFilesInProgress,
  chunkItem: ChunkedFile
): ChunkedFilesInProgress => {
  const inProcessChunkObj = {
    chunkNumber: chunkItem.chunkNumber,
    progress: 0,
    chunkSize: chunkItem.file.size
  };
  if (currentInProcess[chunkItem.uuid] === undefined) {
    currentInProcess[chunkItem.uuid] = [inProcessChunkObj];
  } else {
    currentInProcess[chunkItem.uuid].push(inProcessChunkObj);
  }
  return currentInProcess;
};

export const isSpaceAvailableInServer = async (fileSize: number): Promise<boolean> => {
  const response = await get<{
    upload_available_space: number;
  }>(UPLOAD_AVAILABLE_SPACE_URL);
  return !!response?.upload_available_space && response.upload_available_space >= fileSize;
};

export const isAllChunksOfFileUploaded = (
  filesInProgress: ChunkedFilesInProgress,
  chunk: ChunkedFile
): boolean => {
  const fileAllChunks = filesInProgress[chunk.uuid];
  const isTotalChunkCountMatched = fileAllChunks.length === chunk.totalChunks;
  const isAllChunksUploaded = filesInProgress[chunk.uuid]?.every(chunk => chunk.progress === 100);

  return isTotalChunkCountMatched && isAllChunksUploaded;
};
