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
    <div style="margin-bottom: 20px;">
      <hue-button @click="showQueries">Queries</hue-button>
    </div>
    <div class="dag-panel">
      <tabs>
        <tab title="Visual Explain">
          <!-- Can be converted to a loop if we have to compare more than 2 queries. But thats verry unlikely to happen. -->
          <VisualExplain :query="queries[0]" class="side-by-side" />
          <VisualExplain :query="queries[1]" class="side-by-side" />
        </tab>
        <tab title="Query Info">
          <query-info :query="queries[0]" class="side-by-side" />
          <query-info :query="queries[1]" class="side-by-side" />
        </tab>
        <tab title="Query Config">
          <ConfigsTable
            :configs="[
              { title: 'Query A', configs: queries[0].details.configuration },
              { title: 'Query B', configs: queries[1].details.configuration }
            ]"
          />
        </tab>
        <tab title="Timeline">
          <HiveTimeline :perf="queries[0].details.perf" />
          <HiveTimeline :perf="queries[1].details.perf" />
        </tab>
      </tabs>
    </div>

    <div
      v-for="(dagSet, index) in constructDagSets(queries[0], queries[1])"
      :key="index"
      class="target detail-panel dag-panel"
    >
      <div>
        Dag {{ index + 1 }} : {{ dagSet.dagA && dagSet.dagA.dagInfo.dagId }} |
        {{ dagSet.dagB && dagSet.dagB.dagInfo.dagId }}
      </div>
      <tabs>
        <tab title="DAG Counters">
          <CountersTable
            :counters="[
              {
                title: `DAG : ${dagSet.dagA.dagInfo.dagId}`,
                counters: dagSet.dagA.dagDetails.counters
              },
              {
                title: `DAG : ${dagSet.dagB.dagInfo.dagId}`,
                counters: dagSet.dagB.dagDetails.counters
              }
            ]"
          />
        </tab>
        <tab title="DAG Flow">
          <DagGraph :dag="dagSet.dagA" class="side-by-side" />
          <DagGraph :dag="dagSet.dagB" class="side-by-side" />
        </tab>
        <tab title="DAG Swimlane">
          <DagSwimlane :dag="dagSet.dagA" />
          <DagSwimlane :dag="dagSet.dagB" />
        </tab>
        <tab title="DAG Configurations">
          <ConfigsTable
            :configs="[
              { title: `DAG : ${dagSet.dagA.dagInfo.dagId}`, configs: dagSet.dagA.config },
              { title: `DAG : ${dagSet.dagB.dagInfo.dagId}`, configs: dagSet.dagA.config }
            ]"
          />
        </tab>
      </tabs>
    </div>
  </div>
</template>

<script lang="ts">
  import { Component, Inject, Prop, Vue } from 'vue-property-decorator';

  import HueButton from '../../../../../../desktop/core/src/desktop/js/components/HueButton.vue';
  import Tab from '../../../../../../desktop/core/src/desktop/js/components/Tab.vue';
  import Tabs from '../../../../../../desktop/core/src/desktop/js/components/Tabs.vue';

  import HiveTimeline from './hive-timeline/HiveTimeline.vue';
  import ConfigsTable from './configs-table/ConfigsTable.vue';
  import QueryInfo from './QueryInfo.vue';
  import VisualExplain from './visual-explain/VisualExplain.vue';

  import CountersTable from './counters-table/CountersTable.vue';
  import DagGraph from './dag-graph/DagGraph.vue';
  import DagSwimlane from './dag-swimlane/DagSwimlane.vue';

  import { Dag, Query } from '..';

  interface DagSet {
    dagA: Dag;
    dagB: Dag;
  }

  const constructDagSets = (queryA: Query, queryB: Query): DagSet[] => {
    const dagSets: DagSet[] = [];
    const setCount: number = Math.max(queryA.dags.length, queryB.dags.length);
    for (let i = 0; i < setCount; i++) {
      dagSets.push({
        dagA: queryA.dags[i],
        dagB: queryB.dags[i]
      });
    }
    return dagSets;
  };

  @Component({
    components: {
      HueButton,
      Tab,
      Tabs,
      HiveTimeline,
      ConfigsTable,
      VisualExplain,
      QueryInfo,

      CountersTable,
      DagGraph,
      DagSwimlane
    },
    methods: {
      constructDagSets
    }
  })
  export default class QueryDetails extends Vue {
    @Prop({ required: true })
    queries!: Query[];
    @Inject()
    showQueries?: () => void;
  }
</script>

<style lang="scss" scoped>
  .query-search {
    color: #0a78a3;
  }
  .side-by-side {
    display: inline-block;
    width: calc(50% - 5px);
    vertical-align: top;
  }
</style>
