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
    <div>
      <div>
        <hue-button @click="showQueries">Queries</hue-button>

        <hue-button v-if="!query.isComplete && stoppingQuery" disabled>
          <em class="fa fa-spinner fa-pulse fa-fw" /> Stopping query
        </hue-button>
        <hue-button v-else-if="!query.isComplete" @click="stopQuery">Stop</hue-button>

        <hue-button @click="downloadLogs">Download</hue-button>
      </div>

      <QueryInfoTop :query="query" />

      <tabs>
        <!-- Query Tabs -->
        <tab title="Query Info">
          <QueryInfo :query="query" />
        </tab>
        <tab title="Visual Explain" lazy="true">
          <VisualExplain :query="query" />
        </tab>
        <tab title="Timeline">
          <HiveTimeline :perf="query.details.perf" />
        </tab>
        <tab title="Query Config">
          <ConfigsTable :configs="[{ configs: query.details.configuration }]" />
        </tab>

        <!-- DAG Tabs -->
        <tab title="DAG Info">
          <div v-for="dag in query.dags" :key="dag.dagInfo.id" class="dag-info">
            <DagInfo :dag="dag" />
          </div>
        </tab>
        <tab title="DAG Flow">
          <div v-for="dag in query.dags" :key="dag.dagInfo.id" class="dag-details">
            <div class="dag-title">
              <div class="dag-label">Dag</div>
              <div class="dag-name">{{ dag && dag.dagInfo.dagId }}</div>
            </div>
            <DagGraph :dag="dag" />
          </div>
        </tab>
        <tab title="DAG Swimlane">
          <div v-for="dag in query.dags" :key="dag.dagInfo.id" class="dag-details">
            <div class="dag-title">
              <div class="dag-label">Dag</div>
              <div class="dag-name">{{ dag && dag.dagInfo.dagId }}</div>
            </div>
            <DagSwimlane :dag="dag" />
          </div>
        </tab>
        <tab title="DAG Counters">
          <div v-for="dag in query.dags" :key="dag.dagInfo.id" class="dag-details">
            <div class="dag-title">
              <div class="dag-label">Dag</div>
              <div class="dag-name">{{ dag && dag.dagInfo.dagId }}</div>
            </div>
            <CountersTable :counters="[{ counters: dag.dagDetails.counters }]" />
          </div>
        </tab>
        <tab title="DAG Configurations">
          <div v-for="dag in query.dags" :key="dag.dagInfo.id" class="dag-details">
            <div class="dag-title">
              <div class="dag-label">Dag</div>
              <div class="dag-name">{{ dag && dag.dagInfo.dagId }}</div>
            </div>
            <ConfigsTable :configs="[{ configs: dag.config }]" />
          </div>
        </tab>
      </tabs>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import { Component, Inject, Prop } from 'vue-property-decorator';

  import HueButton from '../../../../../../components/HueButton.vue';
  import Tab from '../../../../../../components/Tab.vue';
  import Tabs from '../../../../../../components/Tabs.vue';
  import { kill } from '../api-utils/query';
  import HiveTimeline from './hive-timeline/HiveTimeline.vue';
  import ConfigsTable from './configs-table/ConfigsTable.vue';
  import QueryInfo from './QueryInfo.vue';
  import QueryInfoTop from './QueryInfoTop.vue';
  import VisualExplain from './visual-explain/VisualExplain.vue';

  import CountersTable from './counters-table/CountersTable.vue';
  import DagInfo from './DagInfo.vue';
  import DagGraph from './dag-graph/DagGraph.vue';
  import DagSwimlane from './dag-swimlane/DagSwimlane.vue';

  import { Query } from '../index';

  @Component({
    components: {
      Tab,
      Tabs,
      HiveTimeline,
      HueButton,
      ConfigsTable,
      VisualExplain,
      QueryInfo,
      QueryInfoTop,

      CountersTable,
      DagInfo,
      DagGraph,
      DagSwimlane
    }
  })
  export default class QueryDetails extends Vue {
    @Prop({ required: true })
    query!: Query;

    @Inject()
    showQueries?: () => void;

    stoppingQuery = false;

    async stopQuery(): void {
      this.stoppingQuery = true;
      await kill([this.query]);
      this.stoppingQuery = false;
    }

    downloadLogs(): void {
      // TODO: Implement
    }
  }
</script>

<style lang="scss" scoped>
  @import '../../../../../../components/styles/colors';

  .query-search {
    color: #0a78a3;
  }

  .dag-details,
  .dag-info {
    padding: 10px;
  }

  .dag-info {
    border-top: 1px solid $fluid-gray-200;

    &:first-child {
      border: none;
    }
  }

  .dag-title {
    font-size: 1.1em;
    margin-bottom: 10px;

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
  }
</style>
