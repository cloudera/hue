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
  <div class="target detail-panel">
    <div class="row">
      <div class="col-md-12">
        <div class="title">
          {{ title }}
        </div>
        <label v-if="queries.length > 1"><input v-model="showDifferences" type="checkbox" > Show Differences</label>
      </div>
    </div>

    <div class="row">
      <div class="col-md-12 table-component">
        <div class="body">
          <hue-table :columns="configColumns" :rows="configRows" />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import {Prop} from 'vue-property-decorator';
  import { Query } from '../index';
  import { numberToLetter } from './utils';
  import MultiQueryComponent from './MultiQueryComponent.vue';
  import Component from 'vue-class-component';
  import { Column, Row } from '../../common/HueTable';
  import HueTable from '../../common/HueTable.vue';

  @Component({
    components: { HueTable }
  })
  export default class QueryConfig extends MultiQueryComponent {
    showDifferences: boolean = true;

    @Prop({ required: false, default: 'Configurations' })
    title!: string;

    // Should be abstract but Vue doesn't like abstract components for some reason
    getConfigs(query: Query): { [key: string]: unknown } {
      return query.details && query.details.configuration || {};
    }

    get configColumns(): Column[] {
      const columns = [
        {
          label: 'Configuration Name',
          key: 'configName'
        }
      ];
      this.queries.forEach((query, index) => {
        let label = 'Configuration Value';
        if (this.queries.length > 1) {
          label += ' - ' + numberToLetter(index);
        }
        columns.push({
          label: label,
          key: 'configurationValue' + index
        });
      });
      return columns;
    }

    get configRows(): Row[] {
      const allConfigKeys: string[] = [];

      this.queries.forEach(query => {
        allConfigKeys.push(...Object.keys(this.getConfigs(query)));
      });
      allConfigKeys.sort((a, b) => a.localeCompare(b));

      const result: Row[] = [];
      allConfigKeys.forEach(configKey => {
        const row: Row = {
          configName: configKey
        };

        let hasDifferences = false;
        let previousConfigValue: unknown = undefined;
        this.queries.forEach((query, index) => {
          const config = this.getConfigs(query);
          row['configurationValue' + index] = config[configKey];
          if (index > 0 && !hasDifferences) {
            hasDifferences = previousConfigValue !== config[configKey];
          }
          previousConfigValue = config[configKey];
        });

        if (this.queries.length === 1 || !this.showDifferences || hasDifferences) {
          result.push(row);
        }
      });
      return result;
    }
  }
</script>

<style lang="scss" scoped></style>
