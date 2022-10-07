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
    <HueTable v-if="rows.length" :columns="columns" :rows="rows" >
      <template #cell-variance="row">
        <VarianceCell :data="row" />
      </template>
    </HueTable>
    <h2 v-else>No configurations available!</h2>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { Column } from '../../../../../../../components/HueTable';
  import HueTable from '../../../../../../../components/HueTable.vue';

  import ConfigSet, { Row, generateValueColumnKey } from './ConfigSet';
  import VarianceCell from './VarianceCell.vue';

  const DEFAULT_VALUE_COLUMN_TITLE = 'Config Value';
  const NAME_COLUMNS: Column<Row>[] = [
    {
      label: 'Config Name',
      key: 'configName'
    }
  ];

  export default defineComponent({
    components: {
      HueTable,
      VarianceCell
    },

    props: {
      configs: {
        type: Object as PropType<ConfigSet[]>,
        required: true
      },
      hideSimilarValues: {
        type: Boolean,
        default: false
      }
    },

    computed: {
      rows(): Row[] {
        const rowHash: Map<string, Row> = new Map();
        let rows: Row[];

        const configs = this.configs.filter((configSet: ConfigSet) => configSet.configs);
        configs.forEach((configSet: ConfigSet, index: number) => {
          const configKey: string = generateValueColumnKey(index);

          for (const configName in configSet.configs) {
            let row: Row | undefined = rowHash.get(configName);
            if (!row) {
              row = { configName };
              rowHash.set(configName, row);
            }
            row[configKey] = configSet.configs[configName];
          }
        });

        rows = Array.from(rowHash.values());

        if (this.hideSimilarValues) {
          rows = rows.filter((row: Row) => this.areDifferent(row, this.configs.length));
        }

        return rows;
      },

      columns(): Column<Row>[] {
        const valueColumns: Column<Row>[] = [];

        this.configs.forEach((configSet: ConfigSet, index: number) => {
          valueColumns.push({
            label: configSet.title || DEFAULT_VALUE_COLUMN_TITLE,
            key: generateValueColumnKey(index),
            headerCssClass: configSet.cssClass,
            cssClass: configSet.cssClass
          });
        });

        if (this.configs.length > 1) {
          valueColumns.push({
            label: 'Variance',
            key: 'variance'
          });
        }

        return NAME_COLUMNS.concat(valueColumns);
      }
    },

    methods: {
      areDifferent(row: Row, valueCount: number): boolean {
        if (valueCount > 1) {
          const firstVal = row[generateValueColumnKey(0)];
          for (let i = 1; i < valueCount; i++) {
            if (row[generateValueColumnKey(i)] !== firstVal) {
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
