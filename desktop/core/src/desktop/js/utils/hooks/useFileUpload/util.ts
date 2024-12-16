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

import { FileUploadStatus } from 'utils/constants/storageBrowser';
import { TaskServerResponse, TaskStatus } from '../../../reactComponents/TaskBrowser/TaskBrowser';
import { CHUNK_UPLOAD_URL, CHUNK_UPLOAD_COMPLETE_URL } from 'reactComponents/FileChooser/api';

export interface UploadItem {
  uuid: string;
  filePath: string;
  file: File;
  status: FileUploadStatus;
}

export interface UploadMetaData {
  qqtotalparts: string;
  qqtotalfilesize: string;
  qqfilename: string;
  inputName: string;
  dest: string;
  qquuid: string;
}

export interface UploadChunkItem extends UploadItem {
  chunkIndex: number;
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

export const getMetaData = (item: UploadItem, DEFAULT_CHUNK_SIZE: number): UploadMetaData => ({
  qqtotalparts: String(getTotalChunk(item.file.size, DEFAULT_CHUNK_SIZE)),
  qqtotalfilesize: String(item.file.size),
  qqfilename: item.file.name,
  inputName: 'hdfs_file',
  dest: item.filePath,
  qquuid: item.uuid
});

export const createChunks = (item: UploadItem, chunkSize: number): UploadChunkItem[] => {
  const totalChunks = getTotalChunk(item.file.size, chunkSize);

  const chunks = Array.from({ length: totalChunks }, (_, i) => ({
    ...item,
    chunkIndex: i
  }));

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

export const getChunkItemPayload = (
  chunkItem: UploadChunkItem,
  chunkSize: number
): ChunkPayload => {
  const chunkStart = (chunkItem.chunkIndex ?? 0) * chunkSize;
  const chunkEnd = Math.min(chunkStart + chunkSize, chunkItem!.file.size);

  const metaData = getMetaData(chunkItem, chunkSize);
  const chunkQueryParams = new URLSearchParams({
    ...metaData,
    qqpartindex: String(chunkItem.chunkIndex),
    qqpartbyteoffset: String(chunkStart),
    qqchunksize: String(chunkEnd - chunkStart)
  }).toString();
  const url = `${CHUNK_UPLOAD_URL}?${chunkQueryParams}`;

  const payload = new FormData();
  payload.append('hdfs_file', chunkItem!.file.slice(chunkStart, chunkEnd));
  return { url, payload };
};

export const getChunksCompletePayload = (
  processingItem: UploadItem,
  chunkSize: number
): ChunkPayload => {
  const fileMetaData = getMetaData(processingItem, chunkSize);
  const payload = new FormData();
  Object.entries(fileMetaData).forEach(([key, value]) => {
    payload.append(key, value);
  });
  return { url: CHUNK_UPLOAD_COMPLETE_URL, payload };
};

export const getChunkSinglePayload = (item: UploadItem, chunkSize: number): ChunkPayload => {
  const metaData = getMetaData(item, chunkSize);

  const singleChunkParams = Object.fromEntries(
    Object.entries(metaData).filter(([key]) => key !== 'qqtotalparts')
  );

  const queryParams = new URLSearchParams(singleChunkParams).toString();
  const url = `${CHUNK_UPLOAD_URL}?${queryParams}`;

  const payload = new FormData();
  payload.append('hdfs_file', item.file);

  return { url, payload };
};
