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
import HumanByteSize from './HumanByteSize.vue';

describe('HumanByteSize.vue', () => {
  it('should render', () => {
    const wrapper = shallowMount(HumanByteSize, {
      propsData: {
        value: 10
      }
    });
    expect(wrapper.element).toMatchSnapshot();
  });

  it('should render 1 B', () => {
    const wrapper = shallowMount(HumanByteSize, {
      propsData: {
        value: 1
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('1 B');
  });

  it('should render 1023 B', () => {
    const wrapper = shallowMount(HumanByteSize, {
      propsData: {
        value: 1023
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('1023 B');
  });

  it('should render 1 KB', () => {
    const wrapper = shallowMount(HumanByteSize, {
      propsData: {
        value: 1024
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('1 KB');
  });

  it('should render 1023 KB', () => {
    const wrapper = shallowMount(HumanByteSize, {
      propsData: {
        value: 1024 * 1023
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('1023 KB');
  });

  it('should render 1 GB', () => {
    const wrapper = shallowMount(HumanByteSize, {
      propsData: {
        value: 1024 * 1024 * 1024
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('1 GB');
  });

  it('should render 1.5 GB', () => {
    const wrapper = shallowMount(HumanByteSize, {
      propsData: {
        value: 1024 * 1024 * 1024 * 1.5
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('1.5 GB');
  });
});
