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
import { Column, Row } from './HueTable';
import HueTable from './HueTable.vue';

describe('HueTable.vue', () => {
  it('should render a table', () => {
    const wrapper = shallowMount(HueTable, {
      propsData: {
        columns: <Column<unknown>[]>[
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

  it('should render a table with array rows', () => {
    const wrapper = shallowMount(HueTable, {
      propsData: {
        columns: <Column<unknown>[]>[
          { key: 1, label: 'A' },
          { key: 2, label: 'D' },
          { key: 3, label: 'C' },
          { key: 4, label: 'B' }
        ],
        rows: <Row[]>[
          ['1', 5, false, undefined],
          ['2', 6, true, null],
          ['3', 7, false],
          ['4', 8, true]
        ]
      }
    });
    expect(wrapper.element).toMatchSnapshot();
  });

  it('should render a table with a custom component for a cell', () => {
    const wrapper = mount(HueTable, {
      scopedSlots: {
        'cell-a': '<div>{{ props.a + props.b }}</div>'
      },
      propsData: {
        columns: <Column<unknown>[]>[
          { key: 'a', label: 'A' },
          { key: 'b', label: 'B' }
        ],
        rows: <Row[]>[
          { a: 1, b: 2 },
          { a: 4, b: 5 }
        ]
      }
    });
    expect(wrapper.element).toMatchSnapshot();
  });

  it('should render a table with adapter', () => {
    const wrapper = shallowMount(HueTable, {
      propsData: {
        columns: <Column<{ [key: string]: unknown }>[]>[
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
