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
      <div class="buttons-container">
        <hue-button @click="showQueries">Queries</hue-button>

        <!-- <hue-button v-if="!query.isComplete && stoppingQuery" disabled>
          <em class="fa fa-spinner fa-pulse fa-fw" /> Stopping query
        </hue-button>
        <hue-button v-else-if="!query.isComplete" @click="stopQuery">Stop</hue-button> -->

        <a
          :href="`${HUE_BASE_URL}/jobbrowser/query-store/data-bundle/${query.queryId}`"
          target="_blank"
          download
          class="btn btn-outline-primary download-link"
        >
          Download
        </a>
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

        <template v-if="query.dags.length">
          <!-- DAG Tabs -->
          <tab title="DAG Info" class="hue-layout-column">
            <div v-for="dag in query.dags" :key="dag.dagInfo.id">
              <DagInfo :dag="dag" />
            </div>
          </tab>
          <tab title="DAG Flow" class="hue-layout-column">
            <div v-for="dag in query.dags" :key="dag.dagInfo.id">
              <LabeledInfo label="DAG">{{ dag.dagInfo.dagId }}</LabeledInfo>
              <DagGraph :dag="dag" />
            </div>
          </tab>
          <tab title="DAG Swimlane" class="hue-layout-column">
            <div v-for="dag in query.dags" :key="dag.dagInfo.id">
              <LabeledInfo label="DAG">{{ dag.dagInfo.dagId }}</LabeledInfo>
              <DagSwimlane :dag="dag" />
            </div>
          </tab>
          <tab title="DAG Counters" class="hue-layout-column">
            <div v-for="dag in query.dags" :key="dag.dagInfo.id">
              <LabeledInfo label="DAG">{{ dag.dagInfo.dagId }}</LabeledInfo>
              <CountersTable :counters="[{ counters: dag.dagDetails.counters }]" />
            </div>
          </tab>
          <tab title="DAG Configurations" class="hue-layout-column">
            <div v-for="dag in query.dags" :key="dag.dagInfo.id">
              <LabeledInfo label="DAG">{{ dag.dagInfo.dagId }}</LabeledInfo>
              <ConfigsTable :configs="[{ configs: dag.config }]" />
            </div>
          </tab>
        </template>
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

  import LabeledInfo from '../components/LabeledInfo.vue';

  import { Query } from '../index';

  // TODO: Move it to a better place
  declare global {
    interface Window {
      HUE_BASE_URL: string;
    }
  }

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
      DagSwimlane,

      LabeledInfo
    }
  })
  export default class QueryDetails extends Vue {
    @Prop({ required: true })
    query!: Query;

    @Inject()
    showQueries?: () => void;

    HUE_BASE_URL = window.HUE_BASE_URL;

    stoppingQuery = false;

    async stopQuery(): void {
      this.stoppingQuery = true;
      await kill([this.query]);
      this.stoppingQuery = false;
    }
  }
</script>

<style lang="scss" scoped>
  @import '../../../../../../components/styles/colors';
  @import '../../../../../../components/styles/mixins';

  .buttons-container {
    margin-bottom: 20px;
  }

  .download-link {
    border-radius: $hue-panel-border-radius;
  }

  .hue-layout-column {
    @include hue-flex-layout(column);
  }
</style>
