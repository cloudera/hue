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

import { SHOWN_EVENT, SHOW_EVENT } from './ko.sessionAuthModal';
import huePubSub from 'utils/huePubSub';

import 'ext/bootstrap.2.3.2.min';
import sessionManager from 'apps/editor/execution/sessionManager';
import { simulateInput } from 'jest/koTestUtils';

describe('ko.sessionAuthModal.js', () => {
  it('should render component', async () => {
    huePubSub.publish(SHOW_EVENT, {
      session: {
        properties: []
      },
      message: 'hello'
    });

    await new Promise(resolve => {
      huePubSub.subscribeOnce(SHOWN_EVENT, resolve);
    });

    expect(window.document.documentElement.outerHTML).toMatchSnapshot();
  });

  it('should submit credentials', async () => {
    huePubSub.publish(SHOW_EVENT, {
      session: {
        properties: []
      },
      message: 'hello'
    });

    const element = await new Promise(resolve => {
      huePubSub.subscribeOnce(SHOWN_EVENT, resolve);
    });

    const TEST_USER = 'someUser';
    const TEST_PASS = 'somePass';

    let spyCalled = false;
    jest.spyOn(sessionManager, 'createDetachedSession').mockImplementation(async options => {
      expect(
        options.properties.some(prop => prop.name === 'user' && prop.value === TEST_USER)
      ).toBeTruthy();
      expect(
        options.properties.some(prop => prop.name === 'password' && prop.value === TEST_PASS)
      ).toBeTruthy();
      spyCalled = true;
    });

    simulateInput(element.querySelector('[data-test="usernameInput"]'), TEST_USER);
    simulateInput(element.querySelector('[data-test="passwordInput"]'), TEST_PASS);
    element.querySelector('.btn-primary').click();

    expect(spyCalled).toBeTruthy();
  });
});
