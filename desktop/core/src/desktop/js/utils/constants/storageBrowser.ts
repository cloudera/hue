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

export const DEFAULT_PAGE_SIZE = 50;
export const DEFAULT_CHUNK_SIZE = 5 * 1024 * 1024; // 5 MiB
export const DEFAULT_CONCURRENT_MAX_CONNECTIONS = 3;
export const DEFAULT_ENABLE_CHUNK_UPLOAD = false;

export enum SupportedFileTypes {
  IMAGE = 'image',
  TEXT = 'text',
  DOCUMENT = 'document',
  AUDIO = 'audio',
  VIDEO = 'video',
  OTHER = 'other'
}

export enum FileUploadStatus {
  Pending = 'Pending',
  Uploading = 'Uploading',
  Uploaded = 'Uploaded',
  Canceled = 'Canceled',
  Failed = 'Failed'
}

export const SUPPORTED_FILE_EXTENSIONS: Record<string, SupportedFileTypes> = {
  png: SupportedFileTypes.IMAGE,
  jpg: SupportedFileTypes.IMAGE,
  jpeg: SupportedFileTypes.IMAGE,

  txt: SupportedFileTypes.TEXT,
  log: SupportedFileTypes.TEXT,
  json: SupportedFileTypes.TEXT,
  csv: SupportedFileTypes.TEXT,
  sql: SupportedFileTypes.TEXT,
  tsv: SupportedFileTypes.TEXT,

  // TODO: add feature to edit these files
  // parquet: SupportedFileTypes.TEXT,
  // orc: SupportedFileTypes.TEXT,
  // avro: SupportedFileTypes.TEXT,

  pdf: SupportedFileTypes.DOCUMENT,

  mp3: SupportedFileTypes.AUDIO,

  mp4: SupportedFileTypes.VIDEO
};

export const EDITABLE_FILE_FORMATS = {
  [SupportedFileTypes.TEXT]: 1
};
