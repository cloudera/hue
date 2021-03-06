// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import $ from 'jquery';

import AssistStorageEntry from './assistStorageEntry';
import * as hueConfig from 'config/hueConfig';

describe('assistStorageEntry.js', () => {
  it('it should handle domain in ADLS/ABFS', () => {
    const spy = jest.spyOn($, 'ajax').mockImplementation(data => {
      const url = data.url;
      const deferred = $.Deferred();

      if (
        url ===
        '/filebrowser/view=ABFS%3A%2F%2F?format=json&sortby=name&descending=false&pagesize=100&pagenum=1'
      ) {
        deferred.resolve({
          status: 200,
          contentType: 'application/json',
          responseText: JSON.stringify({
            status: 0,
            files: [{ name: 'path' }],
            page: { next_page_number: 0 }
          })
        });
      } else if (
        url ===
        '/filebrowser/view=ABFS%3A%2F%2Fpath?format=json&sortby=name&descending=false&pagesize=100&pagenum=1'
      ) {
        deferred.resolve({
          status: 200,
          contentType: 'application/json',
          responseText: JSON.stringify({
            status: 0,
            files: [{ name: 'p2' }],
            page: { next_page_number: 0 }
          })
        });
      } else {
        deferred.reject();
      }

      return deferred.promise();
    });

    const findSpy = jest
      .spyOn(hueConfig, 'findBrowserConnector')
      .mockImplementation(() => ({ type: 'abfs', page: '' }));

    AssistStorageEntry.getEntry('abfs://test.com/path').always(entry => {
      expect(entry.path).toBe('/path');
    });
    AssistStorageEntry.getEntry('abfs://path').always(entry => {
      expect(entry.path).toBe('/path');
    });
    AssistStorageEntry.getEntry('abfs://path@test.com').always(entry => {
      expect(entry.path).toBe('/path');
    });
    AssistStorageEntry.getEntry('abfs://path@test.com/p2').always(entry => {
      expect(entry.path).toBe('/path/p2');
    });
    expect(spy).toHaveBeenCalled();
    expect(findSpy).toHaveBeenCalled();

    spy.mockRestore();
    spy.mockClear();
  });
});
