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
    <div class="buttons-container">
      <hue-button @click="showQueries">Queries</hue-button>
    </div>

    <div class="hue-layout-row">
      <QueryInfoTop :query="queries[0]" />
      <QueryInfoTop :query="queries[1]" class="query-b" />
    </div>

    <tabs>
      <!-- Query Tabs -->
      <tab title="Query Info" class="query-info">
        <QueryInfo :query="queries[0]" layout="column" />
        <QueryInfo :query="queries[1]" layout="column" class="query-b-deep" />
      </tab>
      <tab title="Visual Explain" :lazy="true" class="hue-layout-row">
        <VisualExplain :query="queries[0]" />
        <VisualExplain :query="queries[1]" class="query-b" />
      </tab>
      <tab title="Timeline" class="hue-layout-column">
        <div class="hue-info-box">
          <LabeledInfo label="Query">{{ queries[0].queryId }}</LabeledInfo>
          <HiveTimeline :perf="queries[0].details.perf" />
        </div>
        <div class="hue-info-box query-b">
          <LabeledInfo label="Query">{{ queries[1].queryId }}</LabeledInfo>
          <HiveTimeline :perf="queries[1].details.perf" />
        </div>
      </tab>
      <tab title="Query Config">
        <label class="hide-similar">
          <input v-model="hideSimilarValues" type="checkbox" /> Hide Equal Values
        </label>
        <ConfigsTable
          class="query-b-deep"
          :hide-similar-values="hideSimilarValues"
          :configs="[
            { title: `Query ${queries[0].queryId}`, configs: queries[0].details.configuration },
            {
              title: `Query ${queries[1].queryId}`,
              configs: queries[1].details.configuration,
              cssClass: 'query-b'
            }
          ]"
        />
      </tab>

      <template v-if="queries[0].dags.length || queries[1].dags.length">
        <!-- DAG Tabs -->
        <tab :title="'DAG Info' + (hasDiagnostics ? ' *' : '')" class="hue-layout-row">
          <div class="hue-layout-column">
            <DagInfo v-for="dag in queries[0].dags" :key="dag.dagInfo.dagId" :dag="dag" />
            <div v-if="!get(queries, '[0].dags.length')" class="hue-info-box">No DAGs!</div>
          </div>
          <div class="hue-layout-column">
            <DagInfo
              v-for="dag in queries[1].dags"
              :key="dag.dagInfo.dagId"
              :dag="dag"
              class="query-b"
            />
            <div v-if="!get(queries, '[1].dags.length')" class="hue-info-box query-b">No DAGs!</div>
          </div>
        </tab>
        <tab title="DAG Flow" class="hue-layout-row">
          <div class="hue-layout-column">
            <div v-for="dag in queries[0].dags" :key="dag.dagInfo.dagId">
              <LabeledInfo label="DAG">{{ dag.dagInfo.dagId }}</LabeledInfo>
              <DagGraph :dag="dag" />
            </div>
            <div v-if="!get(queries, '[0].dags.length')" class="hue-info-box">No DAGs!</div>
          </div>
          <div class="hue-layout-column query-b-deep">
            <div v-for="dag in queries[1].dags" :key="dag.dagInfo.dagId">
              <LabeledInfo label="DAG">{{ dag.dagInfo.dagId }}</LabeledInfo>
              <DagGraph :dag="dag" />
            </div>
            <div v-if="!get(queries, '[1].dags.length')" class="hue-info-box query-b">No DAGs!</div>
          </div>
        </tab>
        <tab title="DAG Swimlane" class="hue-layout-column">
          <div class="hue-layout-column hue-info-box">
            <div v-for="dag in queries[0].dags" :key="dag.dagInfo.dagId">
              <LabeledInfo label="DAG">{{ dag.dagInfo.dagId }}</LabeledInfo>
              <DagSwimlane :dag="dag" />
            </div>
            <div v-if="!get(queries, '[0].dags.length')">No DAGs!</div>
          </div>
          <div class="hue-layout-column hue-info-box query-b">
            <div v-for="dag in queries[1].dags" :key="dag.dagInfo.dagId">
              <LabeledInfo label="DAG">{{ dag.dagInfo.dagId }}</LabeledInfo>
              <DagSwimlane :dag="dag" />
            </div>
            <div v-if="!get(queries, '[1].dags.length')">No DAGs!</div>
          </div>
        </tab>

        <tab title="DAG Counters">
          <label class="hide-similar">
            <input v-model="hideSimilarValues" type="checkbox" /> Hide Equal Values
          </label>
          <CountersTable
            class="query-b-deep"
            :hide-similar-values="hideSimilarValues"
            :counters="
              queries
                .map((query, queryIndex) =>
                  query.dags.map(dag => ({
                    title: `DAG : ${dag.dagInfo.dagId}`,
                    counters: dag.dagDetails.counters,
                    cssClass: queryIndex ? 'query-b' : ''
                  }))
                )
                .flat()
            "
          />
        </tab>
        <tab title="DAG Configurations">
          <label class="hide-similar">
            <input v-model="hideSimilarValues" type="checkbox" /> Hide Equal Values
          </label>
          <ConfigsTable
            class="query-b-deep"
            :hide-similar-values="hideSimilarValues"
            :configs="
              queries
                .map((query, queryIndex) =>
                  query.dags.map(dag => ({
                    title: `DAG : ${dag.dagInfo.dagId}`,
                    configs: dag.config,
                    cssClass: queryIndex ? 'query-b' : ''
                  }))
                )
                .flat()
            "
          />
        </tab>
      </template>
    </tabs>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType, inject } from 'vue';

  import HueButton from '../../../../../../components/HueButton.vue';
  import Tab from '../../../../../../components/Tab.vue';
  import Tabs from '../../../../../../components/Tabs.vue';

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

  import { Query, Dag } from '../index';

  import { get } from 'lodash';

  export default defineComponent({
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
      DagSwimlane,

      LabeledInfo
    },

    props: {
      queries: {
        type: Array as PropType<Query[]>,
        required: true
      }
    },

    setup() {
      const showQueries: (() => void | undefined) | undefined = inject('showQueries');
      return {
        showQueries
      };
    },

    data() {
      return {
        hideSimilarValues: false
      };
    },

    computed: {
      hasDiagnostics(): boolean {
        return this.queries.some((query: Query) =>
          query.dags.some((dag: Dag) => dag.dagDetails.diagnostics)
        );
      }
    },

    methods: {
      get
    }
  });
</script>

<style lang="scss" scoped>
  @import '../../../../../../components/styles/colors';
  @import '../../../../../../components/styles/mixins';

  .hue-info-box {
    padding: 10px;

    border: 1px solid $fluid-gray-300;
    border-radius: $hue-panel-border-radius;
  }

  .buttons-container {
    margin-bottom: 20px;
  }

  .hue-layout-row {
    @include hue-flex-layout(row);
  }

  .hue-layout-column {
    vertical-align: top;
    @include hue-flex-layout(column);
  }

  .query-info {
    white-space: nowrap;
  }

  .query-b,
  ::v-deep(.query-b-deep .query-b),
  ::v-deep(.query-b-deep .hue-info-box),
  ::v-deep(.query-b-deep .dag-view-container) {
    background-color: $fluid-blue-050;
    border-radius: $hue-panel-border-radius;
  }

  .hide-similar {
    text-align: right;
    input {
      vertical-align: top;
    }
  }
</style>
