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

export interface FileSystem {
  file_system: string;
  user_home_directory: string;
  config?: {
    is_trash_enabled: boolean;
    is_hdfs_superuser: boolean;
    groups: string[];
    users: string[];
    superuser: string;
    supergroup: string;
  };
}

export interface FileStats {
  atime: number;
  blockSize: number;
  group: string;
  mode: number;
  mtime: number;
  path: string;
  replication: number;
  rwx: string;
  size: number;
  type: string;
  user: string;
}

export interface StorageDirectoryTableData
  extends Pick<FileStats, 'path' | 'user' | 'group' | 'type' | 'replication'> {
  name: string;
  size: string;
  permission: string;
  mtime: string;
}

export interface PageStats {
  page_number: number;
  total_pages: number;
  page_size: number;
  total_size: number;
}

export interface FilePreview {
  contents: string;
  end: number;
  length: number;
  mode: string;
  offset: number;
}

export interface ListDirectory {
  files: FileStats[];
  page: PageStats;
}

export interface ContentSummary {
  directoryCount: number;
  ecPolicy: string;
  fileCount: number;
  length: number;
  quota: number;
  spaceConsumed: number;
  spaceQuota: number;
  typeQuota: number;
  replication: number;
}

export enum SortOrder {
  ASC = 'ascending',
  DSC = 'descending',
  NONE = 'none'
}

export enum BrowserViewType {
  dir = 'dir',
  file = 'file'
}
