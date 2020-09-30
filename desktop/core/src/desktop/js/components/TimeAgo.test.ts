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
import TimeAgo from './TimeAgo.vue';

describe('TimeAgo.vue', () => {
  const RealDate = Date.now;

  const MOCK_NOW = 1000 * 60 * 60 * 24 * 365 * 10;

  beforeAll(() => {
    global.Date.now = jest.fn(() => MOCK_NOW);
  });

  afterAll(() => {
    global.Date.now = RealDate;
  });

  it('should render', () => {
    const wrapper = shallowMount(TimeAgo, {
      propsData: {
        value: MOCK_NOW
      }
    });
    expect(wrapper.element).toMatchSnapshot();
  });

  it('should render 1 second ago', () => {
    const wrapper = shallowMount(TimeAgo, {
      propsData: {
        value: MOCK_NOW - 1000
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('1 second ago');
  });

  it('should render 4 seconds ago', () => {
    const wrapper = shallowMount(TimeAgo, {
      propsData: {
        value: MOCK_NOW - 4 * 1000
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('4 seconds ago');
  });

  it('should render 1 minute ago', () => {
    const wrapper = shallowMount(TimeAgo, {
      propsData: {
        value: MOCK_NOW - 1000 * 60
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('1 minute ago');
  });

  it('should render 4 minutes ago', () => {
    const wrapper = shallowMount(TimeAgo, {
      propsData: {
        value: MOCK_NOW - 1000 * 60 * 4
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('4 minutes ago');
  });

  it('should render 1 hour ago', () => {
    const wrapper = shallowMount(TimeAgo, {
      propsData: {
        value: MOCK_NOW - 1000 * 60 * 60
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('1 hour ago');
  });

  it('should render 4 hours ago', () => {
    const wrapper = shallowMount(TimeAgo, {
      propsData: {
        value: MOCK_NOW - 1000 * 60 * 60 * 4
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('4 hours ago');
  });

  it('should render 1 day ago', () => {
    const wrapper = shallowMount(TimeAgo, {
      propsData: {
        value: MOCK_NOW - 1000 * 60 * 60 * 24
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('1 day ago');
  });

  it('should render 4 days ago', () => {
    const wrapper = shallowMount(TimeAgo, {
      propsData: {
        value: MOCK_NOW - 1000 * 60 * 60 * 24 * 4
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('4 days ago');
  });

  it('should render 1 month ago', () => {
    const wrapper = shallowMount(TimeAgo, {
      propsData: {
        value: MOCK_NOW - 1000 * 60 * 60 * 24 * (365 / 12)
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('1 month ago');
  });

  it('should render 4 months ago', () => {
    const wrapper = shallowMount(TimeAgo, {
      propsData: {
        value: MOCK_NOW - 1000 * 60 * 60 * 24 * (365 / 12) * 4
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('4 months ago');
  });

  it('should render 1 year ago', () => {
    const wrapper = shallowMount(TimeAgo, {
      propsData: {
        value: MOCK_NOW - 1000 * 60 * 60 * 24 * (365 / 12) * 12
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('1 year ago');
  });

  it('should render 4 years ago', () => {
    const wrapper = shallowMount(TimeAgo, {
      propsData: {
        value: MOCK_NOW - 1000 * 60 * 60 * 24 * (365 / 12) * 12 * 4
      }
    });
    expect(wrapper.element.firstChild?.textContent).toContain('4 years ago');
  });
});
