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

import Vue from 'vue';
import { mount, shallowMount } from '@vue/test-utils';
import Tabs from './Tabs.vue';
import Tab from './Tab.vue';

describe('Tabs.vue', () => {
  it('should render empty tabs', () => {
    const wrapper = shallowMount(Tabs);
    expect(wrapper.element).toMatchSnapshot();
  });

  it('should render tabs', async () => {
    const wrapper = mount(Tabs, {
      slots: {
        default: '<tab title="foo">foo</tab><tab title="bar">bar</tab>'
      },
      stubs: {
        tab: Tab
      }
    });
    await Vue.nextTick();
    expect(wrapper.element).toMatchSnapshot();
  });
});
