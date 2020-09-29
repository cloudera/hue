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
    <div class="dag-panel">
      <fixed-anchor-nav :query="query" />

      <tabs>
        <tab title="Visual Explain">
          <VisualExplain :query="query" />
        </tab>
        <tab title="Query Info">
          <query-info :query="query" />
        </tab>
        <tab title="Query Config">
          <query-config :queries="[query]" />
        </tab>
        <tab title="Timeline">
          <HiveTimeline :perf="query.details.perf" />
        </tab>
      </tabs>
    </div>

    <div
      v-for="(dag, index) in query.dags"
      :key="dag.dagInfo.id"
      class="target detail-panel dag-panel"
    >
      <div>Dag {{ index + 1 }} : {{ dag && dag.dagInfo.dagId }}</div>
      <tabs>
        <tab title="DAG Counters">
          <CountersTable :counters="[{ counters: dag.dagDetails.counters }]" />
        </tab>
        <tab title="DAG Flow"><DagGraph :dag="dag" /></tab>
        <tab title="DAG Swimlane"><DagSwimlane :dag="dag" /></tab>
        <tab title="DAG Configurations"><dag-configs :dag="dag" /></tab>
      </tabs>
    </div>
  </div>
</template>

<script lang="ts">
  import { Component, Prop, Vue } from 'vue-property-decorator';

  import Tab from '../../../../../../desktop/core/src/desktop/js/components/Tab.vue';
  import Tabs from '../../../../../../desktop/core/src/desktop/js/components/Tabs.vue';
  import FixedAnchorNav from './FixedAnchorNav.vue';
  import HiveTimeline from './hive-timeline/HiveTimeline.vue';
  import QueryConfig from './QueryConfig.vue';
  import QueryInfo from './QueryInfo.vue';
  import VisualExplain from './visual-explain/VisualExplain.vue';

  import DagConfigs from './DagConfigs.vue';
  import CountersTable from './counters-table/CountersTable.vue';
  import DagGraph from './dag-graph/DagGraph.vue';
  import DagSwimlane from './dag-swimlane/DagSwimlane.vue';

  import { Query } from '..';

  @Component({
    components: {
      Tab,
      Tabs,
      FixedAnchorNav,
      HiveTimeline,
      QueryConfig,
      VisualExplain,
      QueryInfo,

      DagConfigs,
      CountersTable,
      DagGraph,
      DagSwimlane
    }
  })
  export default class QueryDetails extends Vue {
    @Prop({ required: true }) query!: Query;
  }
</script>

<style lang="scss" scoped>
  .query-search {
    color: #0a78a3;
  }
</style>
