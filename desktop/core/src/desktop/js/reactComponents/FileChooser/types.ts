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

//TODO: the interface will change based on the new api to accomodate errors
export interface FileSystem {
  label: string;
  key: number;
  icon: JSX.Element;
  user_home_dir: string;
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

export interface StorageBrowserTableData {
  name: string;
  size: string;
  user: string;
  group: string;
  permission: string;
  mtime: string;
  type: string;
  path: string;
  replication: number;
}

export interface PageStats {
  number: number;
  num_pages: number;
  previous_page_number: number;
  next_page_number: number;
  start_index: number;
  end_index: number;
  total_count: number;
}

export interface BreadcrumbData {
  label: string;
  url: string;
}

export interface FilePreview {
  contents: string;
  compression?: string;
  end: number;
  length: number;
  mode: string;
  offset: number;
}

export interface ListDirectory {
  files: FileStats[];
  page: PageStats;
  groups: string[];
  users: string[];
  supergroup: string;
  superuser: string;
  is_fs_superuser: boolean;
  is_trash_enabled: boolean;
}

export interface ContentSummary {
  summary: {
    directoryCount: number;
    ecPolicy: string;
    fileCount: number;
    length: number;
    quota: number;
    spaceConsumed: number;
    spaceQuota: number;
    typeQuota: number;
    replication: number;
  };
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
