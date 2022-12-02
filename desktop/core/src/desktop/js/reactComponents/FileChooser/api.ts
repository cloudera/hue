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

import { get } from '../../api/utils';
import { CancellablePromise } from '../../api/cancellablePromise';

const FILESYSTEMS_API_URL = '/api/storage/filesystems';

export interface ApiFileSystem {
  file_system: string;
  user_home_directory: string;
}

export const fetchFileSystems = (): CancellablePromise<ApiFileSystem[]> => get(FILESYSTEMS_API_URL);
