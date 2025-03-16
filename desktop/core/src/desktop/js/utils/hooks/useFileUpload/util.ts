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

import { FileUploadStatus } from '../../../utils/constants/storageBrowser';
import { CHUNK_UPLOAD_URL, CHUNK_UPLOAD_COMPLETE_URL } from '../../../apps/storageBrowser/api';
import { TaskServerResponse, TaskStatus } from '../../../reactComponents/TaskBrowser/TaskBrowser';

export interface UploadItem {
  uuid: string;
  filePath: string;
  file: File;
  status: FileUploadStatus;
  progress?: number;
  error?: Error;
}

export interface UploadItemVariables
  extends Partial<Omit<UploadItem, 'uuid' | 'filePath' | 'file'>> {}

export interface UploadMetaData {
  qqtotalparts: string;
  qqtotalfilesize: string;
  qqfilename: string;
  inputName: string;
  dest: string;
  qquuid: string;
}

export interface UploadChunkItem extends Omit<UploadItem, 'file'> {
  file: Blob; // storing only part of the file to avoid big file duplication
  fileName: string;
  totalSize: number;
  totalChunks: number;
  chunkIndex: number;
  chunkStart: number;
  chunkEnd: number;
}

export interface InProgressChunk {
  chunkIndex: number;
  progress: number;
  chunkSize: number;
}

export interface AvailableServerSpaceResponse {
  uploadAvailableSpace: number;
}

interface ChunkPayload {
  url: string;
  payload: FormData;
}

export const getNewFileItems = (newQueue: UploadItem[], oldQueue: UploadItem[]): UploadItem[] => {
  return newQueue.filter(
    newItem =>
      !oldQueue.some(
        oldItem => oldItem.file.name === newItem.file.name && oldItem.filePath === newItem.filePath
      )
  );
};

export const getTotalChunk = (fileSize: number, DEFAULT_CHUNK_SIZE: number): number => {
  return Math.ceil(fileSize / DEFAULT_CHUNK_SIZE);
};

export const getMetaData = (item: UploadChunkItem): UploadMetaData => ({
  qqtotalparts: String(item.totalChunks),
  qqtotalfilesize: String(item.totalSize),
  qqfilename: item.fileName,
  inputName: 'hdfs_file',
  dest: item.filePath,
  qquuid: item.uuid
});

export const createChunks = (item: UploadItem, chunkSize: number): UploadChunkItem[] => {
  const totalChunks = getTotalChunk(item.file.size, chunkSize);

  const chunks = Array.from({ length: totalChunks }, (_, i) => {
    const chunkStart = i * chunkSize;
    const chunkEnd = Math.min(chunkStart + chunkSize, item.file.size);
    return {
      ...item,
      fileName: item.file.name,
      totalSize: item.file.size,
      file: item.file.slice(chunkStart, chunkEnd),
      totalChunks,
      chunkIndex: i,
      chunkStart,
      chunkEnd
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
      [row.task_id]: row.status
    }),
    {}
  );

export const getChunkItemPayload = (chunkItem: UploadChunkItem): ChunkPayload => {
  const metaData = getMetaData(chunkItem);
  const chunkQueryParams = new URLSearchParams({
    ...metaData,
    qqpartindex: String(chunkItem.chunkIndex),
    qqpartbyteoffset: String(chunkItem.chunkStart),
    qqchunksize: String(chunkItem.chunkEnd - chunkItem.chunkStart)
  }).toString();

  const url = `${CHUNK_UPLOAD_URL}?${chunkQueryParams}`;

  const payload = new FormData();
  payload.append('hdfs_file', chunkItem.file);
  return { url, payload };
};

export const getChunksCompletePayload = (processingItem: UploadChunkItem): ChunkPayload => {
  const fileMetaData = getMetaData(processingItem);
  const payload = new FormData();
  Object.entries(fileMetaData).forEach(([key, value]) => {
    payload.append(key, value);
  });
  return { url: CHUNK_UPLOAD_COMPLETE_URL, payload };
};

export const getChunkSinglePayload = (item: UploadChunkItem): ChunkPayload => {
  const metaData = getMetaData(item);

  const singleChunkParams = Object.fromEntries(
    Object.entries(metaData).filter(([key]) => key !== 'qqtotalparts')
  );

  const queryParams = new URLSearchParams(singleChunkParams).toString();
  const url = `${CHUNK_UPLOAD_URL}?${queryParams}`;

  const payload = new FormData();
  payload.append('hdfs_file', item.file);

  return { url, payload };
};

export const getItemProgress = (progress?: ProgressEvent): number => {
  if (!progress?.total || !progress?.loaded || progress?.total === 0) {
    return 0;
  }
  return Math.round((progress.loaded * 100) / progress.total);
};

export const getItemsTotalProgress = (
  chunkItem?: UploadChunkItem,
  chunks?: InProgressChunk[]
): number => {
  if (!chunkItem || !chunks) {
    return 0;
  }
  return chunks.reduce((acc, chunk) => {
    return acc + (chunk.progress * chunk.chunkSize) / chunkItem.totalSize;
  }, 0);
};
