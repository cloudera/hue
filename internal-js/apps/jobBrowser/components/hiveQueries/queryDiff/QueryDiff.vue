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
      <div class="diff-panel"><query-info title="A" :query="queries[0]"></query-info></div>
      <div class="diff-panel"><query-info title="B" :query="queries[1]"></query-info></div>
      <div class="query-diff-highlighter" style="clear:both;">
        <query-text-diff :query-one="queries[0].query" :query-two="queries[1]"></query-text-diff>
      </div>
    </div>
    <query-visual-explain :queries="queries"></query-visual-explain>
    <query-config :queries="queries"></query-config>
    <query-timeline :queries="queries"></query-timeline>
    <div v-if="!isDagEmpty()" id="dag-panel" class="target detail-panel dag-panel">
      <div class="row">
        <div class="col-xs-6">
          <select v-if="queries[0].dags && queries[0].dags.length > 1" v-model="selectedDagId1" @change="dagSelected1($event.target.value)" class="form-control">
            <option v-for="dag in queries[0].dags" v-bind:value="dag.dagInfo.dagId">{{ dag.dagInfo.dagId }}</option>
          </select>
        </div>
        <div class="col-xs-6">
          <select v-if="queries[1].dags && queries[1].dags.length > 1" v-model="selectedDagId2" @change="dagSelected2($event.target.value)" class="form-control">
            <option v-for="dag in queries[1].dags" v-bind:value="dag.dagInfo.dagId">{{ dag.dagInfo.dagId }}</option>
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
  import Component from 'vue-class-component';
  import MultiQueryComponent from '../queryDetails/MultiQueryComponent.vue';
  import QueryVisualExplain from '../queryDetails/QueryVisualExplain.vue';
  import QueryTimeline from '../queryDetails/QueryTimeline.vue';
  import QueryConfig from '../queryDetails/QueryConfig.vue';
  import QueryTextDiff from '../../common/QueryTextDiff.vue';
  import Tab from '../../common/Tab.vue';
  import Tabs from '../../common/Tabs.vue';
  import DagConfigs from '../queryDetails/DagConfigs.vue';
  import DagCounters from '../queryDetails/DagCounters.vue';
  import DagGraphicalView from '../queryDetails/DagGraphicalView.vue';
  import DagSwimlane from '../queryDetails/DagSwimlane.vue';
  import { Dag } from '../index';
  import QueryInfo from '../queryDetails/QueryInfo.vue';

  @Component({
    components: {
      QueryVisualExplain, QueryTimeline, QueryConfig, QueryTextDiff, DagConfigs, DagCounters,
      DagGraphicalView, DagSwimlane, Tab, Tabs, QueryInfo
    }
  })
  export default class QueryDiff extends MultiQueryComponent {
    selectedDagId1?: string;
    selectedDagId2?: string;

    constructor() {
      super();
      if (this.queries.length !== 2) {
        throw new Error(`Got ${this.queries.length}, expected 2 for diff.`)
      }
    }

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
