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

import { shallowMount } from '@vue/test-utils';
import Duration from './Duration.vue';

describe('Duration.vue', () => {
  it('should render', () => {
    const wrapper = shallowMount(Duration, {
      propsData: {
        value: 1234567890
      }
    });
    expect(wrapper.element).toMatchSnapshot();
  });

  it('should render 00:00:00 duration', () => {
    const wrapper = shallowMount(Duration, {
      propsData: {
        value: 0
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('00:00:00');
  });

  it('should render 01:01:01 duration', () => {
    const wrapper = shallowMount(Duration, {
      propsData: {
        value: 1000 + 1000 * 60 + 1000 * 60 * 60
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('01:01:01');
  });

  it('should render 100:01:01 duration', () => {
    const wrapper = shallowMount(Duration, {
      propsData: {
        value: 1000 + 1000 * 60 + 1000 * 60 * 60 * 100
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('100:01:01');
  });
});
