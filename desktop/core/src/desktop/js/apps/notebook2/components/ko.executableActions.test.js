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
import { NAME } from './ko.executableActions';
import { EXECUTABLE_UPDATED_EVENT, EXECUTION_STATUS } from 'apps/notebook2/execution/executable';
import { sleep } from 'utils/hueUtils';
import sessionManager from 'apps/notebook2/execution/sessionManager';

describe('ko.executableActions.js', () => {
  const setup = koSetup();

  it('should render component', async () => {
    const spy = spyOn(sessionManager, 'getSession').and.returnValue(
      Promise.resolve({ type: 'foo' })
    );
    const mockExecutable = {
      cancel: () => {},
      cancelBatchChain: () => {},
      execute: () => {},
      isPartOfRunningExecution: () => false,
      isReady: () => true,
      reset: () => {},
      nextExecutable: {},
      executor: {
        defaultLimit: () => {},
        connector: () => ({
          id: 'foo'
        })
      },
      status: EXECUTION_STATUS.ready
    };
    const activeExecutable = () => mockExecutable;
    activeExecutable.prototype.subscribe = () => {};
    const element = await setup.renderComponent(NAME, {
      activeExecutable: activeExecutable
    });

    expect(spy).toHaveBeenCalled();
    expect(element.querySelector('[data-test="' + NAME + '"]')).toBeTruthy();
  });

  it('should handle execute and stop clicks', async () => {
    const spy = spyOn(sessionManager, 'getSession').and.returnValue(
      Promise.resolve({ type: 'foo' })
    );
    let executeCalled = false;
    let cancelCalled = false;
    const mockExecutable = {
      cancel: () => {
        cancelCalled = true;
      },
      cancelBatchChain: () => {
        cancelCalled = true;
      },
      execute: async () => {
        executeCalled = true;
      },
      isPartOfRunningExecution: () => false,
      isReady: () => true,
      reset: () => {},
      nextExecutable: {},
      executor: {
        defaultLimit: () => {},
        connector: () => ({
          id: 'foo'
        })
      },
      status: EXECUTION_STATUS.ready
    };
    const activeExecutable = () => mockExecutable;
    activeExecutable.prototype.subscribe = () => {};
    const wrapper = await setup.renderComponent(NAME, {
      activeExecutable: activeExecutable
    });

    expect(spy).toHaveBeenCalled();

    // Click play
    expect(executeCalled).toBeFalsy();
    expect(wrapper.querySelector('[data-test="execute"]')).toBeTruthy();
    expect(wrapper.querySelector('[data-test="stop"]')).toBeFalsy();
    wrapper.querySelector('[data-test="execute"]').click();

    await sleep(0);

    expect(executeCalled).toBeTruthy();
    mockExecutable.status = EXECUTION_STATUS.running;
    huePubSub.publish(EXECUTABLE_UPDATED_EVENT, mockExecutable);

    await setup.waitForKoUpdate();

    // Click stop
    expect(cancelCalled).toBeFalsy();
    expect(wrapper.querySelector('[data-test="execute"]')).toBeFalsy();
    expect(wrapper.querySelector('[data-test="stop"]')).toBeTruthy();
    wrapper.querySelector('[data-test="stop"]').click();

    expect(cancelCalled).toBeTruthy();
  });
});
