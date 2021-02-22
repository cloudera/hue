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
import { Search, TableDefinition } from '../index';
import QueriesSearch from './QueriesSearch.vue';
import DropdownMenu from 'components/dropdown/DropdownMenu.vue';

describe('QueriesSearch.vue', () => {
  it('should render', () => {
    const wrapper = shallowMount(QueriesSearch, {
      global: {
        stubs: {
          DropdownMenu
        }
      },
      propsData: {
        tableDefinition: <TableDefinition>{
          rangeData: {
            title: 'Some title'
          }
        },
        searches: <Search[]>[
          { category: 'SUGGEST', name: 'Suggested search' },
          { category: 'SAVED', name: 'Saved search' }
        ]
      }
    });
    expect(wrapper.element).toMatchSnapshot();
  });
});
