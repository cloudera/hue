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

import huePubSub from 'utils/huePubSub';
import AssistFunctionsPanel from './ko.assistFunctionsPanel';

describe('ko.assistFunctionsPanel.js', () => {
  it('should handle cluster config updates', () => {
    let clusterConfigGetCalled = false;
    const configSub = huePubSub.subscribe('cluster.config.get.config', () => {
      clusterConfigGetCalled = true;
      huePubSub.publish('cluster.config.set.config', {
        app_config: {
          editor: {
            interpreters: [{ type: 'pig' }, { type: 'pig' }, { type: 'impala' }, { type: 'banana' }]
          }
        }
      });
    });
    const subject = new AssistFunctionsPanel();

    expect(clusterConfigGetCalled).toBeTruthy();
    expect(subject.availableTypes()).toEqual(['impala', 'pig']);

    huePubSub.publish('cluster.config.set.config', {
      app_config: {
        editor: {
          interpreters: [{ type: 'pig' }]
        }
      }
    });

    expect(subject.availableTypes()).toEqual(['pig']);
    expect(subject.activeType()).toEqual('pig');

    huePubSub.publish('cluster.config.set.config', {
      app_config: {
        editor: {
          interpreters: [{ type: 'banana' }]
        }
      }
    });

    expect(subject.availableTypes()).toEqual([]);
    expect(subject.activeType()).toBeFalsy();

    configSub.remove();
    subject.dispose();
  });
});
