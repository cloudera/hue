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

export enum FileStatus {
  Pending = 'pending',
  Uploading = 'uploading',
  Uploaded = 'uploaded',
  Cancelled = 'cancelled',
  Failed = 'failed'
}

// Interface for file upload as a whole file in one single request.
export interface RegularFile {
  uuid: string;
  filePath: string;
  file: File;
  status: FileStatus;
  progress?: number;
  error?: Error;
  overwrite?: boolean;
}

// Interface for file upload in chunks.
// One RegularFile can be broken down into multiple ChunkedFile.
// And each ChunkedFile can be uploaded independently and combined at backed server
export interface ChunkedFile extends Omit<RegularFile, 'file'> {
  file: Blob; // storing only part of the file to avoid big file duplication
  fileName: string;
  totalSize: number;
  chunkNumber: number;
  chunkStartOffset: number;
  chunkEndOffset: number;
  totalChunks: number;
}

export interface FileVariables extends Partial<Omit<RegularFile, 'uuid' | 'filePath' | 'file'>> {}

export interface FileChunkMetaData {
  qqtotalparts: string;
  qqtotalfilesize: string;
  qqfilename: string;
  inputName: string;
  dest: string;
  qquuid: string;
}

export interface ChunkedFilesInProgress {
  [uuid: string]: {
    chunkNumber: number;
    progress: number;
    chunkSize: number;
  }[];
}

export interface FileUploadApiPayload {
  url: string;
  payload: FormData;
}
