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

import EditorViewModel from './EditorViewModel';
import changeURLParameter from 'utils/url/changeURLParameter';

describe('EditorViewModel.js', () => {
  it('should load the document if opened with an ID in the "editor" url parameter', async () => {
    changeURLParameter('editor', '123');
    const vm = new EditorViewModel({});
    const spy = jest.spyOn(vm, 'openNotebook').mockImplementation(() => Promise.resolve());

    await vm.init();

    expect(spy).toHaveBeenCalledWith('123');
  });
});
