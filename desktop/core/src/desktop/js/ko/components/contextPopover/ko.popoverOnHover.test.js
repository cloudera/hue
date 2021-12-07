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

import $ from 'jquery';

import { koSetup } from 'jest/koTestUtils';

import { NAME } from './ko.popoverOnHover';
import huePubSub from 'utils/huePubSub';
import { HIDE_CONTEXT_POPOVER_EVENT } from './ko.contextPopover';

describe('ko.popoverOnHover.js', () => {
  const setup = koSetup();

  it('should render binding', async () => {
    const wrapper = await setup.renderKo(`<div id="foo" data-bind="${NAME}: () => {}"></div>`, {});

    expect(wrapper.innerHTML).toMatchSnapshot();
  });

  it('should call callback on hover and publish on leave', async () => {
    jest.useFakeTimers('legacy');
    let callbackCalled = false;
    const viewModel = {
      callback: () => {
        callbackCalled = true;
      }
    };
    const wrapper = await setup.renderKo(
      `<div id="foo" data-bind="${NAME}: callback"></div>`,
      viewModel
    );

    // Mouse enters
    $(wrapper.firstChild).trigger('mouseenter');
    jest.runAllTimers();
    expect(callbackCalled).toBeTruthy();

    // Mouse leaves
    let publishCalled = false;
    huePubSub.subscribeOnce(HIDE_CONTEXT_POPOVER_EVENT, () => {
      publishCalled = true;
    });
    $(wrapper.firstChild).trigger('mouseleave');
    jest.runAllTimers();
    expect(publishCalled).toBeTruthy();

    // Mouse clicks
    callbackCalled = false;
    $(wrapper.firstChild).trigger('click');
    expect(callbackCalled).toBeTruthy();
  });
});
