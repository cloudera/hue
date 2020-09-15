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
  <div id="configs" class="target detail-panel" >
    <div class="row">
      <div class="col-md-12">
        <div class="title">Configurations</div>
        <label v-if="queryModels.length > 1"><input type="checkbox" v-model="showDifferences"> Show Differences</label>
      </div>
    </div>

    <div class="row">
      <div class="col-md-12 table-component">
        <div class="body">
          <hue-table :columns="configColumns" :rows="configRows"></hue-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue';
import Component from 'vue-class-component';
import { Prop } from 'vue-property-decorator';
import HueTable, { Column, Row } from '../../common/HueTable.vue';
import { QueryModel } from '../index';

@Component({
  components: { HueTable }
})
export default class QueryConfig extends Vue {
  @Prop({ required: false })
  queryModels: QueryModel[] = [];
  @Prop({ required: false })
  queryModel?: QueryModel;

  showDifferences: boolean = true;

  constructor() {
    super();

    // TODO: Does queryModel change for this component?
    if (this.queryModel) {
      this.queryModels.push(this.queryModel);
    }
  }

  get configColumns(): Column[] {
    const columns = [{
      label: 'Configuration Name',
      key: 'configName',
    }]
    this.queryModels.forEach((model, index) => {
      let label = 'Configuration Value';
      if (this.queryModels.length > 1) {
        label += ' - ' + String.fromCharCode(65 + index); // A, B, C, ...
      }
      columns.push({
        label: label,
        key: 'configurationValue' + index
      })
    })
    return columns;
  }

  get configRows(): Row[] {
    const allConfigKeys: string[] = [];

    this.queryModels.forEach(model => {
      if (model.details && model.details.configuration) {
        allConfigKeys.push(...Object.keys(model.details.configuration))
      }
    })
    allConfigKeys.sort((a, b) => a.localeCompare(b));

    const result: Row[] = [];
    allConfigKeys.forEach(configKey => {
      const row: Row = {
        configName: configKey
      };

      let hasDifferences = false;
      let previousConfigValue: unknown = undefined;
      this.queryModels.forEach((model, index) => {
        const config = model.details && model.details.configuration || {};
        row['configurationValue' + index] = config[configKey];
        if (index > 0 && !hasDifferences) {
          hasDifferences = previousConfigValue !== config[configKey];
        }
        previousConfigValue = config[configKey];
      })

      if (this.queryModels.length === 1 || !this.showDifferences || hasDifferences) {
        result.push(row)
      }
    })
    return result;
  }
}
</script>

<style lang="scss" scoped>
</style>
