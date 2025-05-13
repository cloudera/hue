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

export const enum ImporterFileTypes {
  CSV = 'csv',
  JSON = 'json',
  EXCEL = 'excel'
}

export enum ImporterFileSource {
  LOCAL = 'local',
  REMOTE = 'remote'
}

export interface LocalFileUploadResponse {
  file_path: string;
}

export interface FileFormatResponse {
  type: ImporterFileTypes;
  hasHeader?: boolean;
  fieldSeparator?: string;
  quoteChar?: string;
  recordSeparator?: string;
}

export interface FileMetaData {
  path: string;
  type?: ImporterFileTypes;
  source: ImporterFileSource;
}

export type FilePreviewTableColumn = {
  importerDataKey?: string; // key for identifying unique data row
  name: string;
  type?: string;
};

export interface FilePreviewTableData {
  [key: string]: (string | number)[];
}

export interface FilePreviewResponse {
  columns: FilePreviewTableColumn[];
  hasHeader: boolean;
  previewData: FilePreviewTableData;
}

export interface ImporterTableData {
  importerDataKey: string;
  [key: string]: string | number;
}
