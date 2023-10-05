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

import { mount } from '@vue/test-utils';

import QueryKillButton from './QueryKillButton.vue';
import { QueryStatus } from '../index.d';

const sleep = ms => new Promise(r => setTimeout(r, ms));

import * as queryApiUtils from '../api-utils/query';

describe('QueryKillButton.vue', () => {
  it('should render disabled', async () => {
    const wrapper = mount(QueryKillButton, {
      propsData: {
        queries: []
      }
    });
    expect(wrapper.text()).toContain('Kill');
    expect(wrapper.attributes('disabled')).toBeDefined();
  });

  it('should render Kill, disabled', () => {
    const wrapper = mount(QueryKillButton, {
      propsData: {
        queries: [
          {
            status: QueryStatus.SUCCESS
          }
        ]
      }
    });
    expect(wrapper.text()).toContain('Kill');
    expect(wrapper.attributes('disabled')).toBeDefined();
  });

  it('should render Kill', () => {
    const wrapper = mount(QueryKillButton, {
      propsData: {
        queries: [
          {
            status: QueryStatus.RUNNING
          }
        ]
      }
    });
    expect(wrapper.text()).toContain('Kill');
    expect(wrapper.attributes('disabled')).toBeUndefined();
  });

  it('should render Killing, disabled', async () => {
    const wrapper = mount(QueryKillButton, {
      propsData: {
        queries: [
          {
            status: QueryStatus.RUNNING
          }
        ]
      }
    });
    await wrapper.trigger('click');
    expect(wrapper.text()).toContain('Killing');
    expect(wrapper.attributes('disabled')).toBeDefined();
  });

  it('should render Error, disabled', async () => {
    jest.spyOn(queryApiUtils, 'kill').mockImplementation(async (): Promise<void> => {
      throw new Error();
    });

    const wrapper = mount(QueryKillButton, {
      propsData: {
        queries: [
          {
            status: QueryStatus.RUNNING
          }
        ]
      }
    });

    await wrapper.trigger('click');
    await sleep(100);
    expect(wrapper.text()).toContain('Error');
    expect(wrapper.attributes('disabled')).toBeDefined();
  });

  it('should render Unknown, disabled', async () => {
    jest.spyOn(queryApiUtils, 'kill').mockImplementation(async (): Promise<void> => {
      true;
    });
    jest.spyOn(queryApiUtils, 'waitIf').mockImplementation(async (): Promise<boolean> => true);

    const wrapper = mount(QueryKillButton, {
      propsData: {
        queries: [
          {
            status: QueryStatus.RUNNING
          }
        ]
      }
    });

    await wrapper.trigger('click');
    await sleep(100);
    expect(wrapper.text()).toContain('Unknown');
    expect(wrapper.attributes('disabled')).toBeDefined();
  });
});
