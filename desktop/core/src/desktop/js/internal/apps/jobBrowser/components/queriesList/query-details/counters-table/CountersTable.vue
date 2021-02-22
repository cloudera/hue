<!--
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->

<template>
  <div>
    <HueTable v-if="rows.length" :columns="columns" :rows="rows" />
    <h2 v-else>No counters available!</h2>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { Column } from '../../../../../../../components/HueTable';
  import HueTable from '../../../../../../../components/HueTable.vue';

  import { CounterGroup, CounterDetails } from '../../index';

  import CounterSet from './CounterSet';

  //TODO: Must be imported from components/HueTable.d
  type Row = { [key: string]: unknown };

  const DEFAULT_VALUE_COLUMN_TITLE = 'Counter Value';
  const NAME_COLUMNS: Column<Row>[] = [
    {
      label: 'Group Name',
      key: 'groupName'
    },
    {
      label: 'Counter Name',
      key: 'counterName'
    }
  ];

  export default defineComponent({
    components: {
      HueTable
    },

    props: {
      counters: {
        type: Object as PropType<CounterSet[]>,
        required: true
      },
      hideSimilarValues: {
        type: Boolean,
        default: false
      }
    },

    computed: {
      columns(): Column<Row>[] {
        const valueColumns: Column<Row>[] = [];

        this.counters.forEach((counterSet: CounterSet, index: number) => {
          valueColumns.push({
            label: counterSet.title || DEFAULT_VALUE_COLUMN_TITLE,
            key: this.generateValueColumnkey(index),
            headerCssClass: counterSet.cssClass,
            cssClass: counterSet.cssClass
          });
        });

        return NAME_COLUMNS.concat(valueColumns);
      },
      rows(): Row[] {
        const rowHash: Map<string, Row> = new Map();
        let rows: Row[];

        const counters = this.counters.filter((counterSet: CounterSet) => counterSet.counters);
        counters.forEach((counterSet: CounterSet, index: number) => {
          const counterKey: string = this.generateValueColumnkey(index);
          counterSet.counters.forEach((counterGroup: CounterGroup) => {
            counterGroup.counters.forEach((counter: CounterDetails) => {
              const counterId: string = counterGroup.counterGroupName + counter.counterName;
              let row: Row | undefined = rowHash.get(counterId);
              if (!row) {
                row = {
                  groupName: counterGroup.counterGroupName,
                  counterName: counter.counterName
                };
                rowHash.set(counterId, row);
              }
              row[counterKey] = counter.counterValue;
            });
          });
        });

        rows = Array.from(rowHash.values());

        if (this.hideSimilarValues) {
          rows = rows.filter((row: Row) => this.areDifferent(row, this.counters.length));
        }

        return rows;
      }
    },

    methods: {
      generateValueColumnkey(index: number): string {
        return `counterSet_${index}`;
      },

      areDifferent(row: Row, valueCount: number): boolean {
        if (valueCount > 1) {
          const firstVal = row[this.generateValueColumnkey(0)];
          for (let i = 1; i < valueCount; i++) {
            if (row[this.generateValueColumnkey(i)] !== firstVal) {
              return true;
            }
          }
          return false;
        }
        return true;
      }
    }
  });
</script>
