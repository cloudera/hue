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

import { mount, shallowMount } from '@vue/test-utils';
import TimeAgo from 'components/TimeAgo.vue';
import { Column, Row } from './HueTable';
import HueTable from './HueTable.vue';

describe('HueTable.vue', () => {
  it('should render a table', () => {
    const wrapper = shallowMount(HueTable, {
      propsData: {
        columns: <Column[]>[
          { key: 'a', label: 'A' },
          { key: 'd', label: 'D' },
          { key: 'c', label: 'C' },
          { key: 'b', label: 'B' }
        ],
        rows: <Row[]>[
          { a: '1', b: 5, c: false, d: undefined },
          { a: '2', b: 6, c: true, d: null },
          { a: '3', b: 7, c: false },
          { a: '4', b: 8, c: true }
        ]
      }
    });
    expect(wrapper.element).toMatchSnapshot();
  });

  it('should render a table with a custom component for a cell', () => {
    const now = Date.now() + 30000000000; // Guarantees future ~year, i.e, TimeAgo will show "now"
    const wrapper = mount(HueTable, {
      components: { 'time-ago': TimeAgo },
      propsData: {
        columns: <Column[]>[
          { key: 'a', label: 'A' },
          {
            key: 'b',
            label: 'B',
            cellComponent: TimeAgo,
            cellProps: (key, row) => ({ value: row[key] })
          }
        ],
        rows: <Row[]>[
          { a: '1', b: now },
          { a: '4', b: now }
        ]
      }
    });
    expect(wrapper.element).toMatchSnapshot();
  });

  it('should render a table with adapter', () => {
    const wrapper = shallowMount(HueTable, {
      propsData: {
        columns: <Column[]>[
          { key: 'a', label: 'A' },
          {
            key: 'b',
            label: 'B + C',
            adapter: (key, row) => (row['b'] as number) + (row['c'] as number)
          }
        ],
        rows: <Row[]>[
          { a: '1', b: 5, c: 9 },
          { a: '2', b: 6, c: 10 },
          { a: '3', b: 7, c: 11 },
          { a: '4', b: 8, c: 12 }
        ]
      }
    });
    expect(wrapper.element).toMatchSnapshot();
  });
});
