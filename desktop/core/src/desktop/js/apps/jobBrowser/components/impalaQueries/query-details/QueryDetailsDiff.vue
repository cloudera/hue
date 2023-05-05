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
      <hue-button borderless @click="() => showQueries && showQueries()">
        <em class="fa fa-chevron-left" />
        {{ I18n('Queries') }}
      </hue-button>
    </div>

    <div class="hue-layout-row">
      <QueryInfoTop :query="queries[0]" />
      <QueryInfoTop :query="queries[1]" class="query-b" />
    </div>

    <tabs>
      <!-- Query Tabs -->
      <tab :title="I18n('Query Info')" class="query-info">
        <QueryInfo :query="queries[0]" layout="column" />
        <QueryInfo :query="queries[1]" layout="column" class="query-b" />
      </tab>
      <tab :title="I18n('Plan')">
        <pre class="hue-box">
          {{ queries[0].profile.summaryMap['Plan'] }}
        </pre>
        <pre class="hue-box query-b">
          {{ queries[1].profile.summaryMap['Plan'] }}
        </pre>
      </tab>
      <tab :title="I18n('Exec Summary')">
        <pre class="hue-box">
          {{ queries[0].profile.summaryMap['ExecSummary'] }}
        </pre>
        <pre class="hue-box query-b">
          {{ queries[1].profile.summaryMap['ExecSummary'] }}
        </pre>
      </tab>
      <tab :title="I18n('Metrics')">
        <CountersTable
          :counters="[
            {
              title: `${I18n('Metrics')} : ${queries[0].queryId}`,
              counters: getCounters(queries[0].profile),
              cssClass: ''
            },
            {
              title: `${I18n('Metrics')} : ${queries[1].queryId}`,
              counters: getCounters(queries[1].profile),
              cssClass: ''
            }
          ]"
        />
      </tab>
    </tabs>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType, inject } from 'vue';

  import HueButton from '../../../../../components/HueButton.vue';
  import Tab from '../../../../../components/Tab.vue';
  import Tabs from '../../../../../components/Tabs.vue';
  import QueryInfoTop from './QueryInfoTop.vue';
  import QueryInfo from './QueryInfo.vue';
  import CountersTable from './counters-table/CountersTable.vue';

  import I18n from 'utils/i18n';

  import { CounterDetails, CounterGroup, ImpalaQuery } from '../index';

  import { get } from 'lodash';

  export default defineComponent({
    components: {
      HueButton,
      Tab,
      Tabs,
      QueryInfoTop,
      QueryInfo,
      CountersTable
    },

    props: {
      queries: {
        type: Array as PropType<ImpalaQuery[]>,
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
        hideSimilarValues: false,
        useSameTimeScale: true
      };
    },

    methods: {
      get,
      I18n,
      getCounters: function (profile: any): CounterGroup[] {
        const kvToCounters = (kv: any): CounterDetails[] => {
          return Object.keys(kv).map(key => ({
            counterName: key,
            counterValue: kv[key]
          }));
        };
        return [
          {
            counterGroupName: I18n('CPU Metrics'),
            counters: kvToCounters(profile.cpuMetrics)
          },
          {
            counterGroupName: I18n('HDFS Metrics'),
            counters: kvToCounters(profile.hdfsMetrics)
          },
          {
            counterGroupName: I18n('Memory Metrics'),
            counters: kvToCounters(profile.memoryMetrics)
          },
          {
            counterGroupName: I18n('Thread Time Metrics'),
            counters: kvToCounters(profile.threadTimeMetrics)
          }
        ];
      }
    }
  });
</script>

<style lang="scss" scoped>
  @import '../../../../../components/styles/variables.scss';
  @import '../../../../../components/styles/mixins';

  .hue-info-box {
    padding: 10px;

    border: 1px solid $fluidx-gray-300;
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
    background-color: $fluidx-blue-050;
    border-radius: $hue-panel-border-radius;
  }

  .hide-similar {
    text-align: right;
    input {
      vertical-align: top;
    }
  }

  .scale-controls {
    label {
      display: inline-block;
      input {
        vertical-align: top;
      }
    }
  }
</style>
