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
  <div class="query-diff">
    <div style="clear:both"></div>
    <div id="query-details" class="target">
      <div class="diff-panel"><query-info title="A" :query-model="diffModel.queryOne"></query-info></div>
      <div class="diff-panel"><query-info title="B" :query-model="diffModel.queryTwo"></query-info></div>
      <div class="query-diff-highlighter" style="clear:both;">
        <query-text-diff :query-one="diffModel.queryOne.query" :query-two="diffModel.queryTwo.query"></query-text-diff>
      </div>
    </div>
    <visual-explain-diff :explain-plan-one="diffModel.queryOne" :explain-plan-two="diffModel.queryTwo"></visual-explain-diff>
    <query-config :query-models="[diffModel.queryOne, diffModel.queryTwo]"></query-config>
    <query-timeline :query-models="[diffModel.queryOne, diffModel.queryTwo]"></query-timeline>
    <div v-if="!isDagEmpty()" id="dag-panel" class="target detail-panel dag-panel">
      <div class="row">
        <div class="col-xs-6">
          <select v-if="diffModel.queryOne.dags.length > 1" v-model="selectedDagId1" @change="dagSelected1($event.target.value)" class="form-control">
            <option v-for="dag in diffModel.queryOne.dags" v-bind:value="dag.dagInfo.dagId">{{ dag.dagInfo.dagId }}</option>
          </select>
        </div>
        <div class="col-xs-6">
          <select v-if="diffModel.queryTwo.dags.length > 1" v-model="selectedDagId2" @change="dagSelected2($event.target.value)" class="form-control">
            <option v-for="dag in diffModel.queryTwo.dags" v-bind:value="dag.dagInfo.dagId">{{ dag.dagInfo.dagId }}</option>
          </select>
        </div>
      </div>

      <!-- {{#bs-tab as |tab|}} -->
      <tabs>
        <tab title="DAG SWIMLANE"><dag-swimlane></dag-swimlane></tab>
        <tab title="DAG FLOW"><dag-graphical-view></dag-graphical-view></tab>
        <tab title="DAG COUNTERS"><dag-counters></dag-counters></tab>
        <tab title="DAG CONFIGURATIONS"><dag-configs></dag-configs></tab>
      </tabs>
      <!-- {{/bs-tab}} -->
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import QueryTimeline from '../query/QueryTimeline.vue';
  import QueryConfig from '../query/QueryConfig.vue';
  import VisualExplainDiff from '../queryDiff/VisualExplainDiff.vue';
  import QueryTextDiff from '../../common/QueryTextDiff.vue';
  import Tab from '../../common/Tab.vue';
  import Tabs from '../../common/Tabs.vue';
  import DagConfigs from '../query/DagConfigs.vue';
  import DagCounters from '../query/DagCounters.vue';
  import DagGraphicalView from '../query/DagGraphicalView.vue';
  import DagSwimlane from '../query/DagSwimlane.vue';
  import { Dag, DiffQueryModel } from '../index';
  import QueryInfo from '../query/QueryInfo.vue';

  @Component({
    components: {
      QueryTimeline, QueryConfig, VisualExplainDiff, QueryTextDiff, DagConfigs, DagCounters,
      DagGraphicalView, DagSwimlane, Tab, Tabs, QueryInfo
    }
  })
  export default class QueryDiff extends Vue {
    @Prop({ required: true })
    diffModel!: DiffQueryModel; // TODO: Consider diffModel: QueryModel[]

    selectedDagId1?: string;
    selectedDagId2?: string;

    isDagEmpty(): boolean {
      return false; // TODO: Implement
    }

    dagSelected1(dag: Dag) {
      // TODO: Implement
    }

    dagSelected2(dag: Dag) {
      // TODO: Implement
    }
  }
</script>

<style lang="scss" scoped>
</style>
