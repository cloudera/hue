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

import ERDiagram from './index.vue';
import { mount, shallowMount } from '@vue/test-utils';
import { Table } from './lib/entities';
import { createTables } from './test/utils';

import ERDData from './test/data.json';

describe('ERDiagram UTs', () => {
  test('Empty instance created', () => {
    const wrapper = shallowMount(ERDiagram, {
      propsData: {
        entities: [],
        relations: []
      }
    });

    expect(wrapper.props('entities')).toHaveLength(0);
    expect(wrapper.props('relations')).toHaveLength(0);

    expect(wrapper.exists()).toBeTruthy();
    expect(wrapper.find('[title="Toggle Fullscreen"]').exists()).toBeTruthy();
    expect(wrapper.find('.erd-scroll-panel').exists()).toBeTruthy();
    expect(wrapper.find('svg.erd-relations').exists()).toBeTruthy();

    expect(wrapper.classes('er-diagram')).toBeTruthy();

    expect(wrapper.findAll('.entity-container')).toHaveLength(0);
    expect(wrapper.findAll('.relation-path')).toHaveLength(0);
  });

  test('Single entity', () => {
    const wrapper = shallowMount(ERDiagram, {
      propsData: {
        entities: [new Table('db-name', 'table-name', [])],
        relations: []
      }
    });

    expect(wrapper.props('entities')).toHaveLength(1);
    expect(wrapper.props('relations')).toHaveLength(0);

    expect(wrapper.findAll('.entity-container')).toHaveLength(1);
    expect(wrapper.findAll('.relation-path')).toHaveLength(0);
  });

  test('Multiple unrelated entities (t0, t1, t2, t3, t4)', () => {
    const tableCount = 5;

    const wrapper = shallowMount(ERDiagram, {
      propsData: {
        entities: createTables(tableCount, 0),
        relations: []
      }
    });

    expect(wrapper.props('entities')).toHaveLength(tableCount);
    expect(wrapper.props('relations')).toHaveLength(0);

    expect(wrapper.findAll('.entity-container')).toHaveLength(tableCount);
    expect(wrapper.findAll('.relation-path')).toHaveLength(0);
  });

  test('Related entities - 3 levels (t0-t1, t0-t2, t0-t3, t3-t4, t3-t5)', () => {
    const tableCount = 6;

    const tables = createTables(tableCount, 4);
    const wrapper = shallowMount(ERDiagram, {
      propsData: {
        entities: tables,
        relations: [
          {
            desc: '',
            left: tables[0].columns[1],
            right: tables[1].columns[0]
          },
          {
            desc: '',
            left: tables[0].columns[2],
            right: tables[2].columns[0]
          },
          {
            desc: '',
            left: tables[0].columns[3],
            right: tables[3].columns[0]
          },
          {
            desc: '',
            left: tables[3].columns[3],
            right: tables[4].columns[0]
          },
          {
            desc: '',
            left: tables[3].columns[3],
            right: tables[5].columns[0]
          }
        ]
      }
    });

    expect(wrapper.props('entities')).toHaveLength(tableCount);
    expect(wrapper.props('relations')).toHaveLength(5);

    expect(wrapper.findAll('.entity-container')).toHaveLength(tableCount);
    expect(wrapper.findAll('.relation-path')).toHaveLength(5);

    expect(wrapper.findAll('.entity-group')).toHaveLength(3);
  });
});

describe('ERDiagram integration tests', () => {
  test('Check plotting of relation paths (t0-t1, t0-t2)', () => {
    const tableCount = 3;

    const tables = createTables(tableCount, 3);
    const wrapper = mount(ERDiagram, {
      propsData: {
        entities: tables,
        relations: [
          {
            desc: '',
            left: tables[0].columns[1],
            right: tables[1].columns[0]
          },
          {
            desc: '',
            left: tables[0].columns[2],
            right: tables[2].columns[0]
          }
        ]
      }
    });

    expect(wrapper.props('entities')).toHaveLength(tableCount);
    expect(wrapper.props('relations')).toHaveLength(2);

    expect(wrapper.findAll('.entity-container')).toHaveLength(tableCount);
    expect(wrapper.findAll('.relation-path')).toHaveLength(2);

    expect(wrapper.findAll('.relation-path').at(0).attributes('d')).toBe('M 0,1 C 40,1 -40,1 0,1');
    expect(wrapper.findAll('.relation-path').at(1).attributes('d')).toBe('M 0,1 C 40,1 -40,1 0,1');
  });

  test('Real data test', () => {
    const wrapper = mount(ERDiagram, {
      propsData: ERDData
    });

    expect(wrapper.props('entities')).toHaveLength(3);
    expect(wrapper.props('relations')).toHaveLength(3);

    expect(wrapper.findAll('.entity-container')).toHaveLength(3);
    expect(wrapper.findAll('.relation-path')).toHaveLength(3);

    expect(wrapper.findAll('.entity-group')).toHaveLength(2);

    expect(wrapper.findAll('.relation-path').at(0).attributes('d')).toBe('M 0,1 C 40,1 -40,1 0,1');
    expect(wrapper.findAll('.relation-path').at(1).attributes('d')).toBe('M 0,1 C 40,1 -40,1 0,1');
    expect(wrapper.findAll('.relation-path').at(2).attributes('d')).toBe('M 0,1 C 40,1 -40,1 0,1');
  });
});
