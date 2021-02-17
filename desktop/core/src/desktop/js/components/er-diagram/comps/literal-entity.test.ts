/**
 * Licensed to Cloudera, Inc. under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Cloudera, Inc. licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import LiteralEntity from './literal-entity.vue';
import { shallowMount } from '@vue/test-utils';
import { Literal } from '../lib/entities';

describe('LiteralEntity UTs', () => {
  test('Empty instance created', () => {
    const wrapper = shallowMount(LiteralEntity, {
      propsData: {
        entity: new Literal('abc')
      }
    });

    expect(wrapper.exists()).toBeTruthy();

    expect(wrapper.props('entity')).toBeTruthy();

    expect(wrapper.find('.literal-entity').exists()).toBeTruthy();
    expect(wrapper.find('.literal-value').exists()).toBeTruthy();

    expect(wrapper.find('.left-point').exists()).toBeTruthy();
    expect(wrapper.find('.right-point').exists()).toBeTruthy();
  });

  test('Value check', () => {
    const testValue = 'TEST_VALUE';
    const wrapper = shallowMount(LiteralEntity, {
      propsData: {
        entity: new Literal(testValue)
      }
    });

    expect(wrapper.text()).toBe(testValue);
  });
});
