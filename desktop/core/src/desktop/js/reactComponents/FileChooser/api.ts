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
import { get, post } from '../../api/utils';
import { CancellablePromise } from '../../api/cancellablePromise';
import { ContentSummary } from './types';

export const FILESYSTEMS_API_URL = '/api/v1/storage/filesystems';
export const VIEWFILES_API_URl = '/api/v1/storage/view=';
export const DOWNLOAD_API_URL = '/filebrowser/download=';
export const SET_REPLICATION_API_URL = '/api/v1/storage/set_replication';
const MAKE_DIRECTORY_API_URL = '/api/v1/storage/mkdir';
const TOUCH_API_URL = '/api/v1/storage/touch';
export const CONTENT_SUMMARY_API_URL = '/api/v1/storage/content_summary=';
export const RENAME_API_URL = '/api/v1/storage/rename';

export interface ApiFileSystem {
  file_system: string;
  user_home_directory: string;
}

export const mkdir = async (folderName: string, path: string): Promise<void> => {
  await post(MAKE_DIRECTORY_API_URL, { name: folderName, path: path });
};

export const touch = async (fileName: string, path: string): Promise<void> => {
  await post(TOUCH_API_URL, { name: fileName, path: path });
};
