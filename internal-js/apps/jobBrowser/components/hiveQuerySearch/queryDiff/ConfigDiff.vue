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
        <label><input type="checkbox" v-model="showDifferences"> Show Differences</label>
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
  export default class ConfigDiff extends Vue {
    @Prop({ required: false })
    explainPlanOne?: QueryModel;

    @Prop({ required: false })
    explainPlanTwo?: QueryModel;

    showDifferences: boolean = true;
    configColumns: Column[] = [{
      label: 'Configuration Name',
      key: 'configName',
    }, {
      label: 'Configuration Value - A',
      key: 'configValueOne',
    }, {
      label: 'Configuration Value - B',
      key: 'configValueTwo',
    }];

    get configRows(): Row[] {
      const configOne = this.explainPlanOne && this.explainPlanOne.details && this.explainPlanOne.details.configuration || {};
      const configTwo = this.explainPlanTwo && this.explainPlanTwo.details && this.explainPlanTwo.details.configuration || {};

      const allConfigKeys = Object.keys(configOne).concat(Object.keys(configTwo));
      allConfigKeys.sort((a, b) => a.localeCompare(b));

      const result: Row[] = [];
      allConfigKeys.forEach(configKey => {
        const configValueOne = configOne[configKey];
        const configValueTwo = configTwo[configKey];
        if (!this.showDifferences || configValueOne !== configValueTwo) {
          result.push({
            configName: configKey,
            configValueOne: configValueOne,
            configValueTwo: configValueTwo
          })
        }
      })
      return result;
    }
  }
</script>

<style lang="scss" scoped>
</style>
