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
  <HueTable :columns="columns" :rows="rows" />
</template>

<script lang="ts">
  import { Component, Prop, Vue } from 'vue-property-decorator';

  import {
    Column,
    Row
  } from '../../../../../../../desktop/core/src/desktop/js/components/HueTable';
  import HueTable from '../../../../../../../desktop/core/src/desktop/js/components/HueTable.vue';

  import { CounterGroup, CounterDetails } from '../..';

  import CounterSet from './CounterSet';

  const DEFAULT_VALUE_COLUMN_TITLE = 'Counter Value';
  const NAME_COLUMNS: Column[] = [
    {
      label: 'Group Name',
      key: 'groupName'
    },
    {
      label: 'Counter Name',
      key: 'counterName'
    }
  ];

  @Component({
    components: {
      HueTable
    }
  })
  export default class CountersTable extends Vue {
    @Prop({ required: true }) counters!: CounterSet[];

    generateCounterSetkey(index: number): string {
      return `counterSet_${index}`;
    }

    get columns(): Column[] {
      const valueColumns: Column[] = [];

      this.counters.forEach((counterSet: CounterSet, index: number) => {
        valueColumns.push({
          label: counterSet.title || DEFAULT_VALUE_COLUMN_TITLE,
          key: this.generateCounterSetkey(index)
        });
      });

      return NAME_COLUMNS.concat(valueColumns);
    }

    get rows(): Row[] {
      const rowHash: Map<string, Row> = new Map();

      this.counters.forEach((counterSet: CounterSet, index: number) => {
        const counterKey: string = this.generateCounterSetkey(index);
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

      return Array.from(rowHash.values());
    }
  }
</script>
