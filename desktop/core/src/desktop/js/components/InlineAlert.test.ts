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
import InlineAlert from './InlineAlert.vue';
import { AlertType } from './InlineAlert.vue';

describe('InlineAlert.vue', () => {
  it('AlertType check', () => {
    expect(AlertType.Success).toBeDefined();
    expect(AlertType.Error).toBeDefined();
    expect(AlertType.Warning).toBeDefined();
    expect(AlertType.Info).toBeDefined();
    expect(AlertType.Unknown).toBeDefined();
  });

  it('should render', () => {
    const wrapper = shallowMount(InlineAlert, {
      propsData: {
        type: AlertType.Success,
        message: 'Test Message'
      }
    });
    expect(wrapper.element).toMatchSnapshot();
  });

  it('should render with more-less button', () => {
    const wrapper = shallowMount(InlineAlert, {
      propsData: {
        type: AlertType.Success,
        message: 'Test Message',
        details: 'Test Details'
      }
    });
    expect(wrapper.element).toMatchSnapshot();
  });

  it('show close', () => {
    const wrapper = shallowMount(InlineAlert, {
      propsData: {
        type: AlertType.Success,
        message: 'Test Message',
        showClose: true
      }
    });
    expect(wrapper.element).toMatchSnapshot();
  });
});
