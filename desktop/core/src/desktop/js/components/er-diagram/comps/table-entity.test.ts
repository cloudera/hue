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

import TableEntity from './table-entity.vue';
import { shallowMount } from '@vue/test-utils';
import { Table, Column } from '../lib/entities';
import { sleep } from '../test/utils';

const dbName = 'DB_NAME';
const tableName = 'TABLE_NAME';
const tableId = Table.buildId(dbName, tableName);
const columnNames = ['id', 'name'];
const defaultMaxColumns = 10;

describe('TableEntity UTs', () => {
  test('Empty instance created', () => {
    const wrapper = shallowMount(TableEntity, {
      propsData: {
        entity: {
          columns: []
        }
      }
    });

    expect(wrapper.exists()).toBeTruthy();

    expect(wrapper.props('entity')).toBeTruthy();
    expect(wrapper.props('maxColumns')).toBe(defaultMaxColumns);

    expect(wrapper.find('.table-entity').exists()).toBeTruthy();
    expect(wrapper.find('.db-name').exists()).toBeTruthy();
    expect(wrapper.find('.table-name').exists()).toBeTruthy();

    expect(wrapper.find('.columns-container').exists()).toBeTruthy();

    expect(wrapper.find('.column-entity').exists()).toBeFalsy();
    expect(wrapper.find('.grouped-columns').exists()).toBeFalsy();
  });

  test('Simple table with 2 columns', () => {
    const wrapper = shallowMount(TableEntity, {
      propsData: {
        entity: new Table(dbName, tableName, [
          new Column(tableId, columnNames[0]),
          new Column(tableId, columnNames[1])
        ])
      }
    });

    expect(wrapper.exists()).toBeTruthy();

    expect(wrapper.props('entity')).toBeTruthy();
    expect(wrapper.props('maxColumns')).toBe(defaultMaxColumns);

    expect(wrapper.find('.db-name').text()).toBe(dbName);
    expect(wrapper.find('.table-name').text()).toBe(tableName);

    expect(wrapper.findAll('.columns-container .column-entity')).toHaveLength(2);
    expect(wrapper.findAll('.columns-container .column-entity .left-point')).toHaveLength(2);
    expect(wrapper.findAll('.columns-container .column-entity .right-point')).toHaveLength(2);

    expect(wrapper.findAll('.columns-container .column-entity').at(0).text()).toBe(columnNames[0]);
    expect(
      wrapper.findAll('.columns-container .column-entity').at(0).attributes('data-entity-id')
    ).toBe(`${tableId}.${columnNames[0]}`);

    expect(wrapper.findAll('.columns-container .column-entity').at(1).text()).toBe(columnNames[1]);
    expect(
      wrapper.findAll('.columns-container .column-entity').at(1).attributes('data-entity-id')
    ).toBe(`${tableId}.${columnNames[1]}`);

    expect(wrapper.find('.grouped-columns').exists()).toBeFalsy();
  });

  test('With number of columns more than maxColumns', () => {
    const columns: Column[] = [];
    const columnCount = 20;

    for (let i = 0; i < columnCount; i++) {
      columns.push(new Column(tableId, `column_${i}`));
    }

    const wrapper = shallowMount(TableEntity, {
      propsData: {
        entity: new Table(dbName, tableName, columns)
      }
    });

    expect(wrapper.exists()).toBeTruthy();
    expect(wrapper.props('entity')).toBeTruthy();
    expect(wrapper.props('maxColumns')).toBe(defaultMaxColumns);

    expect(wrapper.find('.db-name').text()).toBe(dbName);
    expect(wrapper.find('.table-name').text()).toBe(tableName);

    const container = wrapper.find('.columns-container');
    expect(container.findAll('.column-entity')).toHaveLength(defaultMaxColumns);
    expect(container.findAll('.column-entity .left-point')).toHaveLength(defaultMaxColumns);
    expect(container.findAll('.column-entity .right-point')).toHaveLength(defaultMaxColumns);

    const groupedEntitiesIds: string = <string>(
      wrapper.find('.grouped-columns').attributes('data-entity-id')
    );

    const columnElements = wrapper.findAll('.columns-container .column-entity');
    columns.forEach((column: Column, index: number) => {
      if (index < defaultMaxColumns) {
        expect(columnElements.at(index).text()).toBe(column.name);
        expect(columnElements.at(index).attributes('data-entity-id')).toBe(column.id);
      } else {
        expect(groupedEntitiesIds.includes(column.id)).toBeTruthy();
      }
    });

    expect(wrapper.find('.grouped-columns').exists()).toBeTruthy();
    expect(groupedEntitiesIds.split(' ')).toHaveLength(columnCount - defaultMaxColumns);
    expect(wrapper.find('.grouped-columns').text()).toBe(
      `+${columnCount - defaultMaxColumns} columns`
    );
  });

  test('With custom maxColumns', () => {
    const columns: Column[] = [];
    const columnCount = 10;
    const maxColumns = 5;

    for (let i = 0; i < columnCount; i++) {
      columns.push(new Column(tableId, `column_${i}`));
    }

    const wrapper = shallowMount(TableEntity, {
      propsData: {
        entity: new Table(dbName, tableName, columns),
        maxColumns
      }
    });

    expect(wrapper.exists()).toBeTruthy();
    expect(wrapper.props('maxColumns')).toBe(maxColumns);

    const container = wrapper.find('.columns-container');
    expect(container.findAll('.column-entity')).toHaveLength(maxColumns);

    expect(wrapper.find('.grouped-columns').exists()).toBeTruthy();
    expect(wrapper.find('.grouped-columns').text()).toBe(`+${columnCount - maxColumns} columns`);
  });

  test('Column expansion test', async () => {
    const columns: Column[] = [];
    const columnCount = 10;
    const maxColumns = 5;

    for (let i = 0; i < columnCount; i++) {
      columns.push(new Column(tableId, `column_${i}`));
    }

    const wrapper = shallowMount(TableEntity, {
      propsData: {
        entity: new Table(dbName, tableName, columns),
        maxColumns
      }
    });

    expect(wrapper.exists()).toBeTruthy();
    expect(wrapper.props('maxColumns')).toBe(maxColumns);

    expect(wrapper.findAll('.columns-container .column-entity')).toHaveLength(maxColumns);

    expect(wrapper.find('.grouped-columns').exists()).toBeTruthy();
    expect(wrapper.find('.grouped-columns').text()).toBe(`+${columnCount - maxColumns} columns`);

    wrapper.find('.grouped-columns').trigger('click');

    await sleep(500);

    expect(wrapper.findAll('.columns-container .column-entity')).toHaveLength(columnCount);
    expect(wrapper.find('.grouped-columns').exists()).toBeFalsy();
  });
});
