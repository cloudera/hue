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

import { EXECUTABLE_UPDATED_TOPIC, ExecutableUpdatedEvent } from 'apps/editor/execution/events';
import { nextTick } from 'vue';
import { shallowMount, mount } from '@vue/test-utils';
import SqlExecutable, { ExecutionStatus } from 'apps/editor/execution/sqlExecutable';
import ExecutableProgressBar from './ExecutableProgressBar.vue';
import huePubSub from 'utils/huePubSub';

describe('ExecutableProgressBar.vue', () => {
  it('should render', () => {
    const wrapper = shallowMount(ExecutableProgressBar);
    expect(wrapper.element).toMatchSnapshot();
  });

  it('should be 100% and have .progress-danger when failed', async () => {
    const mockExecutable = {
      id: 'some-id',
      progress: 0,
      status: ExecutionStatus.ready
    };

    const { element } = mount(ExecutableProgressBar, {
      propsData: {
        executable: <SqlExecutable>mockExecutable
      }
    });

    const progressDiv = element.querySelector('.executable-progress-bar') as HTMLElement;
    expect(progressDiv).toBeTruthy();
    expect(progressDiv.style['width']).toEqual('2%');
    expect(element.querySelector('.executable-progress-bar.progress-failed')).toBeFalsy();

    mockExecutable.status = ExecutionStatus.failed;
    mockExecutable.progress = 10;
    huePubSub.publish<ExecutableUpdatedEvent>(
      EXECUTABLE_UPDATED_TOPIC,
      mockExecutable as SqlExecutable
    );
    await nextTick();

    expect(progressDiv.style['width']).toEqual('100%');
    expect(element.querySelector('.executable-progress-bar.progress-failed')).toBeTruthy();
  });

  it('should reflect progress updates', async () => {
    const mockExecutable = {
      status: ExecutionStatus.ready,
      progress: 0
    };

    const { element } = mount(ExecutableProgressBar, {
      propsData: {
        executable: <SqlExecutable>mockExecutable
      }
    });

    // Progress should be 2% initially
    const progressDiv = element.querySelector('.executable-progress-bar') as HTMLElement;
    expect(progressDiv).toBeTruthy();
    expect(progressDiv.style['width']).toEqual('2%');

    mockExecutable.status = ExecutionStatus.running;
    mockExecutable.progress = 10;
    huePubSub.publish<ExecutableUpdatedEvent>(
      EXECUTABLE_UPDATED_TOPIC,
      mockExecutable as SqlExecutable
    );
    await nextTick();

    expect(progressDiv.style['width']).toEqual('10%');
  });
});
