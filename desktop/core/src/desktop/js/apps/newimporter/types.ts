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

export enum ImporterFileTypes {
  CSV = 'csv',
  JSON = 'json',
  EXCEL = 'excel'
}

export enum ImporterFileSource {
  LOCAL = 'local',
  REMOTE = 'remote'
}

export enum TableFormat {
  TEXT = 'text',
  PARQUET = 'parquet',
  AVRO = 'avro',
  ORC = 'orc',
  JSON = 'json',
  KUDU = 'kudu',
  CSV = 'csv'
}

export enum StoreLocation {
  MANAGED = 'managed',
  EXTERNAL = 'external'
}

export interface LocalFileUploadResponse {
  filePath: string;
}

export interface FileFormatResponse {
  type?: ImporterFileTypes;
  fieldSeparator?: string;
  quoteChar?: string;
  recordSeparator?: string;
  sheetNames?: string[];
}

export interface GuessHeaderResponse {
  hasHeader?: boolean;
}

export interface CombinedFileFormat extends FileFormatResponse, GuessHeaderResponse {
  selectedSheetName?: string;
}

export interface FileMetaData {
  path: string;
  fileName?: string;
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
  previewData: FilePreviewTableData;
}

export interface ImporterTableData {
  importerDataKey: string;
  [key: string]: string | number;
}

export interface DestinationConfig {
  database?: string;
  tableName?: string;
  connectorId?: string;
  computeId?: string;
}

// TODO: Verify the fields once Backend is ready
export interface ImporterSettings {
  storeLocation: StoreLocation;
  isTransactional: boolean;
  isInsertOnly: boolean;
  externalLocation: string;
  importData: boolean;
  isIcebergTable: boolean;
  isCopyFile: boolean;
  description: string;
  tableFormat: string;
  primaryKeys: string[];
  createEmptyTable: boolean;
  useExternalLocation: boolean;
  customCharDelimiters: boolean;
  fieldDelimiter: string;
  arrayMapDelimiter: string;
  structDelimiter: string;
}

export interface Partition {
  id: string;
  name: string;
  type: string;
  value: string;
}

export interface PartitionConfig {
  partitions: Partition[];
}

export interface SettingsContext extends ImporterSettings {
  isRemoteTable: boolean;
  isIcebergEnabled: boolean;
}
