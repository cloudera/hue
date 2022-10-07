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
        <hue-button @click="showQueries" borderless>
          <em class="fa fa-chevron-left" />
          Queries
        </hue-button>
        <div class="buttons-right">
          <hue-button @click="reExecute">
            <em class="fa fa-play" />
            {{ I18n('Re Execute') }}
          </hue-button>
          <a
            :href="`${HUE_BASE_URL}/jobbrowser/query-store/data-bundle/${query.queryId}`"
            target="_blank"
            download
            class="btn btn-outline-primary download-link"
          >
            Download
          </a>
          <QueryKillButton :queries="[query]" @killed="$emit('reload')" />
          <hue-button @click="$emit('reload')">
            <em class="fa fa-refresh" />
            {{ I18n('Refresh') }}
          </hue-button>
        </div>
      </div>

      <QueryInfoTop :query="query" />

      <tabs>
        <!-- Query Tabs -->
        <tab title="Query Info">
          <QueryInfo :query="query" />
        </tab>
        <tab title="Visual Explain" :lazy="true">
          <VisualExplain :query="query" />
        </tab>
        <tab title="Timeline">
          <HiveTimeline :perf="query.details && query.details.perf" />
        </tab>
        <tab title="Query Config">
          <ConfigsTable :configs="[{ configs: query.details && query.details.configuration }]" />
        </tab>

        <template v-if="query.dags.length">
          <!-- DAG Tabs -->
          <tab :title="'DAG Info' + (hasDiagnostics ? ' *' : '')" class="hue-layout-column">
            <div v-for="dag in query.dags" :key="dag.dagInfo.dagId">
              <DagInfo :dag="dag" />
            </div>
          </tab>
          <tab title="DAG Flow" class="hue-layout-column">
            <div v-for="dag in query.dags" :key="dag.dagInfo.dagId">
              <LabeledInfo label="DAG">{{ dag.dagInfo.dagId }}</LabeledInfo>
              <DagGraph :dag="dag" />
            </div>
          </tab>
          <tab title="DAG Swimlane" class="hue-layout-column">
            <div v-for="dag in query.dags" :key="dag.dagInfo.dagId">
              <LabeledInfo label="DAG">{{ dag.dagInfo.dagId }}</LabeledInfo>
              <DagSwimlane :dag="dag" />
            </div>
          </tab>
          <tab title="DAG Counters" class="hue-layout-column">
            <CountersTable
              :counters="
                query.dags.map(dag => ({
                  title: `DAG : ${dag.dagInfo.dagId}`,
                  counters: dag.dagDetails.counters
                }))
              "
            />
          </tab>
          <tab title="DAG Configurations" class="hue-layout-column">
            <ConfigsTable
              :configs="
                query.dags.map(dag => ({
                  title: `DAG : ${dag.dagInfo.dagId}`,
                  configs: dag.config
                }))
              "
            />
          </tab>
        </template>
      </tabs>
    </div>
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
  import QueryKillButton from '../components/QueryKillButton.vue';

  import { Query, Dag } from '../index';
  import { hueWindow } from 'types/types';
  import huePubSub from 'utils/huePubSub';

  import I18n from 'utils/i18n';

  export default defineComponent({
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

      QueryKillButton,
      LabeledInfo
    },

    props: {
      query: {
        type: Object as PropType<Query>,
        required: true
      }
    },

    emits: ['reload'],

    setup(): {
      showQueries?: () => void;
      HUE_BASE_URL?: string;
    } {
      return {
        showQueries: inject('showQueries'),
        HUE_BASE_URL: (<hueWindow>window).HUE_BASE_URL
      };
    },

    computed: {
      hasDiagnostics(): boolean {
        return this.query.dags.some((dag: Dag) => dag.dagDetails.diagnostics);
      }
    },

    methods: {
      I18n,
      async reExecute() {
        huePubSub.publish('open.editor.new.query', {
          sourceType: 'hive'
        });

        huePubSub.subscribeOnce(
          'ace.editor.focused',
          () =>
            setTimeout(() => {
              huePubSub.publish('editor.insert.at.cursor', {
                text: this.query.query,
                cursorEndAdjust: 0
              });
            }, 100),
          ''
        );
      }
    }
  });
</script>

<style lang="scss" scoped>
  @import '../../../../../../components/styles/colors';
  @import '../../../../../../components/styles/mixins';

  .buttons-container {
    margin-bottom: 20px;
    position: relative;

    .buttons-right {
      position: absolute;
      right: 0px;
      top: 0px;

      & > * {
        margin-left: 5px;
      }
    }
  }

  .download-link {
    color: $hue-action-primary;
    border-color: $hue-border-color;
    border-radius: $hue-panel-border-radius;

    &:hover {
      border-color: $fluid-blue-700;
    }
  }

  .hue-layout-column {
    @include hue-flex-layout(column);
  }
</style>
