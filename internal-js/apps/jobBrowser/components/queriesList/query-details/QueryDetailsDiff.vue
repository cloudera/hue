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

    <div class="query-top">
      <QueryInfoTop :query="queries[0]" class="side-by-side" />
      <QueryInfoTop :query="queries[1]" class="side-by-side" />
    </div>

    <div>
      <tabs>
        <!-- Query Tabs -->
        <tab title="Query Info">
          <QueryInfo :query="queries[0]" class="side-by-side" />
          <QueryInfo :query="queries[1]" class="side-by-side" />
        </tab>
        <tab title="Visual Explain" lazy="true">
          <VisualExplain :query="queries[0]" class="side-by-side" />
          <VisualExplain :query="queries[1]" class="side-by-side" />
        </tab>
        <tab title="Timeline">
          <div class="dag-title">
            <div>
              <div class="dag-label">Query</div>
              <div class="dag-name">{{ queries[0].queryId }}</div>
            </div>
          </div>
          <HiveTimeline :perf="queries[0].details.perf" />
          <div class="dag-title">
            <div>
              <div class="dag-label">Query</div>
              <div class="dag-name">{{ queries[1].queryId }}</div>
            </div>
          </div>
          <HiveTimeline :perf="queries[1].details.perf" />
        </tab>
        <tab title="Query Config">
          <label class="hide-similar">
            <input v-model="hideSimilarValues" type="checkbox" /> Hide Similar Values
          </label>
          <ConfigsTable
            :hide-similar-values="hideSimilarValues"
            :configs="[
              { title: `Query ${queries[0].queryId}`, configs: queries[0].details.configuration },
              { title: `Query ${queries[1].queryId}`, configs: queries[1].details.configuration }
            ]"
          />
        </tab>

        <!-- DAG Tabs -->
        <tab title="DAG Info">
          <div v-for="(dagSet, index) in buildDagSets(queries)" :key="index" class="dag-info">
            <DagInfo :dag="dagSet.dagA" class="side-by-side" />
            <DagInfo :dag="dagSet.dagB" class="side-by-side" />
          </div>
        </tab>
        <tab title="DAG Flow">
          <div v-for="(dagSet, index) in buildDagSets(queries)" :key="index" class="dag-details">
            <div class="dag-title">
              <div>
                <div class="dag-label">Dag</div>
                <div class="dag-name">{{ dagSet.dagA.dagInfo.dagId }}</div>
              </div>
              <div class="position-right">
                <div class="dag-label">Dag</div>
                <div class="dag-name">{{ dagSet.dagB.dagInfo.dagId }}</div>
              </div>
            </div>
            <DagGraph :dag="dagSet.dagA" class="side-by-side" />
            <DagGraph :dag="dagSet.dagB" class="side-by-side" />
          </div>
        </tab>
        <tab title="DAG Swimlane">
          <div v-for="(dagSet, index) in buildDagSets(queries)" :key="index" class="dag-details">
            <div class="dag-title">
              <div>
                <div class="dag-label">Dag</div>
                <div class="dag-name">{{ dagSet.dagA.dagInfo.dagId }}</div>
              </div>
            </div>
            <DagSwimlane :dag="dagSet.dagA" />
            <div class="dag-title">
              <div>
                <div class="dag-label">Dag</div>
                <div class="dag-name">{{ dagSet.dagB.dagInfo.dagId }}</div>
              </div>
            </div>
            <DagSwimlane :dag="dagSet.dagB" />
          </div>
        </tab>
        <tab title="DAG Counters">
          <label class="hide-similar">
            <input v-model="hideSimilarValues" type="checkbox" /> Hide Similar Values
          </label>
          <div v-for="(dagSet, index) in buildDagSets(queries)" :key="index" class="dag-details">
            <CountersTable
              :hide-similar-values="hideSimilarValues"
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
          </div>
        </tab>
        <tab title="DAG Configurations">
          <label class="hide-similar">
            <input v-model="hideSimilarValues" type="checkbox" /> Hide Similar Values
          </label>
          <div v-for="(dagSet, index) in buildDagSets(queries)" :key="index" class="dag-details">
            <ConfigsTable
              :hide-similar-values="hideSimilarValues"
              :configs="[
                { title: `DAG : ${dagSet.dagA.dagInfo.dagId}`, configs: dagSet.dagA.config },
                { title: `DAG : ${dagSet.dagB.dagInfo.dagId}`, configs: dagSet.dagB.config }
              ]"
            />
          </div>
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
  import QueryInfoTop from './QueryInfoTop.vue';
  import VisualExplain from './visual-explain/VisualExplain.vue';

  import CountersTable from './counters-table/CountersTable.vue';
  import DagInfo from './DagInfo.vue';
  import DagGraph from './dag-graph/DagGraph.vue';
  import DagSwimlane from './dag-swimlane/DagSwimlane.vue';

  import { Dag, Query } from '../index';

  interface DagSet {
    dagA: Dag;
    dagB: Dag;
  }

  const DUMMY_DAG: Dag = <Dag>{
    dagInfo: { dagId: '-' },
    dagDetails: { counters: <unknown[]>[] },
    config: {}
  };
  const buildDagSets = ([queryA, queryB]: Query[]): DagSet[] => {
    const dagSets: DagSet[] = [];
    const setCount: number = Math.max(queryA.dags.length, queryB.dags.length);
    for (let i = 0; i < setCount; i++) {
      dagSets.push({
        dagA: queryA.dags[i] || DUMMY_DAG,
        dagB: queryB.dags[i] || DUMMY_DAG
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
      QueryInfoTop,

      CountersTable,
      DagInfo,
      DagGraph,
      DagSwimlane
    },
    methods: {
      buildDagSets
    }
  })
  export default class QueryDetails extends Vue {
    @Prop({ required: true }) queries!: Query[];
    @Inject() showQueries?: () => void;

    hideSimilarValues = false;
  }
</script>

<style lang="scss" scoped>
  @import '../../../../../../desktop/core/src/desktop/js/components/styles/colors';

  .query-search {
    color: #0a78a3;
  }

  .side-by-side {
    display: inline-block;
    width: calc(50% - 5px);
    vertical-align: top;
  }

  .query-top {
    .side-by-side {
      width: calc(50% - 30px);
    }
  }

  .hide-similar {
    text-align: right;
    input {
      vertical-align: top;
    }
  }

  .dag-details,
  .dag-info {
    padding: 10px;
  }

  .dag-details {
    &:first-child {
      padding-top: 0;
    }
  }

  .dag-info {
    border-top: 1px solid $fluid-gray-200;

    &:first-child {
      border: none;
    }
  }

  .dag-title {
    position: relative;

    font-size: 1.1em;
    padding: 10px 0;

    .dag-label {
      text-transform: uppercase;
      color: $fluid-gray-500;
      font-weight: normal;
      font-size: 12px;
      margin: 0;
    }

    .dag-name {
      color: $fluid-gray-700;
      font-size: 14px;
    }

    .position-right {
      position: absolute;
      text-align: right;
      top: 0;
      right: 0;
    }
  }
</style>
