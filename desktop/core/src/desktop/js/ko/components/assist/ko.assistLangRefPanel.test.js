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

import * as ko from 'knockout';

import * as apiUtils from 'api/utils';
import AssistLangRefPanel from './ko.assistLangRefPanel';
import { refreshConfig } from 'config/hueConfig';
import sleep from 'utils/timing/sleep';

describe('ko.assistLangRefPanel.js', () => {
  beforeAll(() => {
    window.IMPALA_DOC_TOP_LEVEL = [];
    window.HIVE_DOC_TOP_LEVEL = [];
  });

  it('should handle cluster config updates', async () => {
    const spy = jest.spyOn(apiUtils, 'post').mockImplementation(async () =>
      Promise.resolve({
        status: 0,
        app_config: {
          editor: {
            interpreters: [{ dialect: 'hive' }, { dialect: 'impala' }, { dialect: 'banana' }]
          }
        }
      })
    );
    await refreshConfig();
    const connector = ko.observable({ dialect: 'impala' });
    const subject = new AssistLangRefPanel({ connector: connector });
    await sleep(0);

    expect(spy).toHaveBeenCalled();
    expect(subject.availableDialects()).toEqual(['hive', 'impala']);

    spy.mockRestore();

    const changeSpy = jest.spyOn(apiUtils, 'post').mockImplementation(async () =>
      Promise.resolve({
        status: 0,
        app_config: {
          editor: {
            interpreters: [{ dialect: 'impala' }]
          }
        }
      })
    );

    await refreshConfig();
    expect(changeSpy).toHaveBeenCalled();
    changeSpy.mockRestore();

    await sleep(0);

    expect(subject.availableDialects()).toEqual(['impala']);
    expect(subject.activeDialect()).toEqual('impala');
  });
});
