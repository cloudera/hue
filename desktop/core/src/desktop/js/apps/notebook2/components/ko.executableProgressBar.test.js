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

import huePubSub from 'utils/huePubSub';
import { koSetup } from 'jest/koTestUtils';
import { NAME } from './ko.executableProgressBar';
import { EXECUTABLE_UPDATED_EVENT, ExecutionStatus } from 'apps/notebook2/execution/executable';

describe('ko.executableProgressBar.js', () => {
  const setup = koSetup();

  it('should render component', async () => {
    const mockExecutable = {
      status: ExecutionStatus.ready,
      progress: 0
    };
    const activeExecutable = () => mockExecutable;
    activeExecutable.prototype.subscribe = () => {};
    const element = await setup.renderComponent(NAME, {
      activeExecutable: activeExecutable
    });

    expect(element.querySelector('[data-test="' + NAME + '"]')).toBeTruthy();
  });

  it('should reflect progress updates', async () => {
    const mockExecutable = {
      status: ExecutionStatus.ready,
      progress: 0
    };
    const activeExecutable = () => mockExecutable;
    activeExecutable.prototype.subscribe = () => {};

    const wrapper = await setup.renderComponent(NAME, {
      activeExecutable: activeExecutable
    });

    // Progress should be 2% initially
    expect(wrapper.querySelector('[data-test="bar"]').style['width']).toEqual('2%');

    mockExecutable.status = ExecutionStatus.running;
    mockExecutable.progress = 10;
    huePubSub.publish(EXECUTABLE_UPDATED_EVENT, mockExecutable);
    await setup.waitForKoUpdate();

    expect(wrapper.querySelector('[data-test="bar"]').style['width']).toEqual('10%');
  });

  it('should be 100% and have .progress-danger when failed', async () => {
    const mockExecutable = {
      status: ExecutionStatus.ready,
      progress: 0
    };
    const activeExecutable = () => mockExecutable;
    activeExecutable.prototype.subscribe = () => {};
    const wrapper = await setup.renderComponent(NAME, {
      activeExecutable: activeExecutable
    });

    expect(wrapper.querySelector('[data-test="bar"]').style['width']).toEqual('2%');
    expect(wrapper.querySelector('[data-test="' + NAME + '"].progress-danger')).toBeFalsy();

    mockExecutable.status = ExecutionStatus.failed;
    mockExecutable.progress = 10;
    huePubSub.publish(EXECUTABLE_UPDATED_EVENT, mockExecutable);
    await setup.waitForKoUpdate();

    expect(wrapper.querySelector('[data-test="bar"]').style['width']).toEqual('100%');
    expect(wrapper.querySelector('[data-test="' + NAME + '"].progress-danger')).toBeTruthy();
  });
});
