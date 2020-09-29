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
    <div style="clear: both;" />
    <div id="query-details" class="target">
      <div class="diff-panel">
        <query-info title="A" :query="queries[0]" />
      </div>
      <div class="diff-panel">
        <query-info title="B" :query="queries[1]" />
      </div>
      <div class="query-diff-highlighter" style="clear: both;">
        <query-text-diff :query-one="queries[0].query" :query-two="queries[1]" />
      </div>
    </div>
    <query-visual-explain :queries="queries" />
    <query-config :queries="queries" />
    <query-timeline :queries="queries" />
    <div v-if="!isDagEmpty()" id="dag-panel" class="target detail-panel dag-panel">
      <div class="row">
        <div class="col-xs-6">
          <select
            v-if="queries[0].dags && queries[0].dags.length > 1"
            v-model="selectedDagId1"
            class="form-control"
            @change="dagSelected1($event.target.value)"
          >
            <option
              v-for="dag in queries[0].dags"
              :key="dag.dagInfo.dagId"
              :value="dag.dagInfo.dagId"
            >
              {{ dag.dagInfo.dagId }}
            </option>
          </select>
        </div>
        <div class="col-xs-6">
          <select
            v-if="queries[1].dags && queries[1].dags.length > 1"
            v-model="selectedDagId2"
            class="form-control"
            @change="dagSelected2($event.target.value)"
          >
            <option
              v-for="dag in queries[1].dags"
              :key="dag.dagInfo.dagId"
              :value="dag.dagInfo.dagId"
            >
              {{ dag.dagInfo.dagId }}
            </option>
          </select>
        </div>
      </div>

      <!-- {{#bs-tab as |tab|}} -->
      <tabs>
        <tab title="DAG SWIMLANE"><DagSwimlane :dag="queries[0].dags[0]" /></tab>
        <tab title="DAG FLOW"><DagGraph :dag="queries[0].dags[0]" /></tab>
        <tab title="DAG COUNTERS"><CountersTable :counters="[]" /></tab>
        <tab title="DAG CONFIGURATIONS"><dag-configs :queries="queries" /></tab>
      </tabs>
      <!-- {{/bs-tab}} -->
    </div>
  </div>
</template>

<script lang="ts">
  import Component from 'vue-class-component';
  import MultiQueryComponent from './MultiQueryComponent.vue';
  import QueryVisualExplain from './QueryVisualExplain.vue';
  import QueryTimeline from './QueryTimeline.vue';
  import QueryConfig from './QueryConfig.vue';
  import QueryTextDiff from '../../common/QueryTextDiff.vue';
  import Tab from '../../../../../../desktop/core/src/desktop/js/components/Tab.vue';
  import Tabs from '../../../../../../desktop/core/src/desktop/js/components/Tabs.vue';
  import DagConfigs from './DagConfigs.vue';
  import CountersTable from './counters-table/CountersTable.vue';
  import DagGraph from './dag-graph/DagGraph.vue';
  import DagSwimlane from './dag-swimlane/DagSwimlane.vue';
  import { Dag } from '../index';
  import QueryInfo from './QueryInfo.vue';

  @Component({
    components: {
      QueryVisualExplain,
      QueryTimeline,
      QueryConfig,
      QueryTextDiff,
      DagConfigs,
      CountersTable,
      DagGraph,
      DagSwimlane,
      Tab,
      Tabs,
      QueryInfo
    }
  })
  export default class QueryDetailsDiff extends MultiQueryComponent {
    selectedDagId1?: string;
    selectedDagId2?: string;

    constructor() {
      super();
      if (this.queries.length !== 2) {
        throw new Error(`Got ${this.queries.length}, expected 2 for diff.`);
      }
    }

    isDagEmpty(): boolean {
      return false; // TODO: Implement
    }

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    dagSelected1(dag: Dag): void {
      // TODO: Implement
    }

    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    dagSelected2(dag: Dag): void {
      // TODO: Implement
    }
  }
</script>

<style lang="scss" scoped></style>
