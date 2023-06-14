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

import { CancellablePromise } from '../../api/cancellablePromise';
import * as ApiUtils from '../../api/utils';
import { fetchFileSystems } from './api';

describe('tests the filesystems api', () => {
  it('test for valid filesystem api response', async () => {
    const mockData = [
      { file_system: 'hdfs', user_home_directory: '/user/demo' },
      { file_system: 'abfs', user_home_directory: 'abfs://jahlenc' }
    ];

    const getSpy = jest
      .spyOn(ApiUtils, 'get')
      .mockImplementation(() => CancellablePromise.resolve(mockData));

    const filesystems = await fetchFileSystems();

    expect(getSpy).toHaveBeenCalledWith('/api/v1/storage/filesystems');
    expect(filesystems).toEqual(mockData);
  });

  //TODO: tests for errors
});
