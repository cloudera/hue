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

import * as ko from 'knockout';
import { SHOWN_EVENT, SHOW_EVENT } from './ko.shareDocModal';
import huePubSub from 'utils/huePubSub';

import 'ext/bootstrap.2.3.2.min';

describe('ko.shareDocModal.js', () => {
  it('should render component', async () => {
    huePubSub.publish(SHOW_EVENT, {
      document: ko.observable({
        isShared: () => false,
        hasErrors: () => false,
        loading: () => false,
        selectedPerm: () => undefined,
        fileEntry: {
          canModify: () => false
        },
        definition: ko.observable({
          name: 'hello',
          perms: {
            read: {
              groups: [],
              users: []
            },
            write: {
              groups: [],
              users: []
            }
          }
        })
      }),
      loadDocument: () => {}
    });

    await new Promise(resolve => {
      huePubSub.subscribeOnce(SHOWN_EVENT, resolve);
    });

    expect(window.document.documentElement.outerHTML).toMatchSnapshot();
  });
});
