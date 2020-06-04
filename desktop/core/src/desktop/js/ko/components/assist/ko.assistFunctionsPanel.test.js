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
import * as ko from 'knockout';

import ApiHelper from 'api/apiHelper';
import * as apiUtils from 'sql/reference/apiUtils';
import AssistFunctionsPanel from './ko.assistFunctionsPanel';
import { refreshConfig } from 'utils/hueConfig';
import { sleep } from 'utils/hueUtils';

describe('ko.assistFunctionsPanel.js', () => {
  jest.spyOn(apiUtils, 'fetchUdfs').mockImplementation(() => Promise.resolve([]));

  it('should handle cluster config updates', async () => {
    const spy = jest.spyOn(ApiHelper, 'getClusterConfig').mockImplementation(() =>
      $.Deferred()
        .resolve({
          status: 0,
          app_config: {
            editor: {
              interpreters: [
                { type: 'pig', dialect: 'pig', displayName: 'Pig' },
                { type: 'impala', dialect: 'impala', displayName: 'Impala' },
                { type: 'banana', dialect: 'banana', displayName: 'Banana' }
              ]
            }
          }
        })
        .promise()
    );
    await refreshConfig();
    const connector = ko.observable({ dialect: 'impala' });
    const subject = new AssistFunctionsPanel({ activeConnector: connector });
    await sleep(0);

    expect(spy).toHaveBeenCalled();
    expect(subject.availableConnectorUdfs().length).toEqual(2);
    expect(
      subject
        .availableConnectorUdfs()
        .every(
          connectorUdfs =>
            connectorUdfs.connector.type === 'pig' || connectorUdfs.connector.type === 'impala'
        )
    ).toBeTruthy();

    spy.mockRestore();

    const changeSpy = jest.spyOn(ApiHelper, 'getClusterConfig').mockImplementation(() =>
      $.Deferred()
        .resolve({
          status: 0,
          app_config: {
            editor: {
              interpreters: [{ type: 'pig', dialect: 'pig', displayName: 'Pig' }]
            }
          }
        })
        .promise()
    );
    await refreshConfig();
    expect(changeSpy).toHaveBeenCalled();
    changeSpy.mockRestore();

    await sleep(0);

    expect(subject.availableConnectorUdfs().length).toEqual(1);
    expect(subject.availableConnectorUdfs()[0].connector.type).toEqual('pig');
    expect(subject.activeConnectorUdfs()).toEqual(subject.availableConnectorUdfs()[0]);
  });
});
