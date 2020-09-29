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
  <div class="table">
    <HueTable :columns="columns" :rows="rows" />
  </div>
</template>

<script lang="ts">
  import { Component, Prop, Vue } from 'vue-property-decorator';

  import {
    Column,
    Row
  } from '../../../../../../../desktop/core/src/desktop/js/components/HueTable';
  import HueTable from '../../../../../../../desktop/core/src/desktop/js/components/HueTable.vue';

  import ConfigSet from './ConfigSet';

  const DEFAULT_VALUE_COLUMN_TITLE = 'Config Value';
  const NAME_COLUMNS: Column[] = [
    {
      label: 'Config Name',
      key: 'configName'
    }
  ];

  @Component({
    components: {
      HueTable
    }
  })
  export default class ConfigsTable extends Vue {
    @Prop({ required: true }) configs!: ConfigSet[];

    generateConfigSetkey(index: number): string {
      return `configSet_${index}`;
    }

    get columns(): Column[] {
      const valueColumns: Column[] = [];

      this.configs.forEach((configSet: ConfigSet, index: number) => {
        valueColumns.push({
          label: configSet.title || DEFAULT_VALUE_COLUMN_TITLE,
          key: this.generateConfigSetkey(index)
        });
      });

      return NAME_COLUMNS.concat(valueColumns);
    }

    get rows(): Row[] {
      const rowHash: Map<string, Row> = new Map();

      this.configs.forEach((configSet: ConfigSet, index: number) => {
        const configKey: string = this.generateConfigSetkey(index);

        for (const configName in configSet.configs) {
          let row: Row | undefined = rowHash.get(configName);
          if (!row) {
            row = { configName };
            rowHash.set(configName, row);
          }
          row[configKey] = configSet.configs[configName];
        }
      });

      return Array.from(rowHash.values());
    }
  }
</script>
