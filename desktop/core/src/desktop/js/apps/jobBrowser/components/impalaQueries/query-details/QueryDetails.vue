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
        <hue-button borderless @click="() => showQueries && showQueries()">
          <em class="fa fa-chevron-left" />
          {{ I18n('Queries') }}
        </hue-button>
        <div class="buttons-right">
          <hue-button @click="$emit('reload')">
            <em class="fa fa-refresh" />
            {{ I18n('Refresh') }}
          </hue-button>
        </div>
      </div>

      <QueryInfoTop :query="query" />

      <tabs>
        <tab :title="I18n('Query Info')">
          <QueryInfo :query="query" />
        </tab>
        <tab :title="I18n('Plan')">
          <pre class="hue-box">
            {{ query.profile.summaryMap['Plan'] }}
          </pre>
        </tab>
        <tab :title="I18n('Exec Summary')">
          <pre class="hue-box">
            {{ query.profile.summaryMap['ExecSummary'] }}
          </pre>
        </tab>
        <tab :title="I18n('Metrics')">
          <CountersTable
            :counters="[
              {
                title: `${I18n('Metrics')} : ${query.queryId}`,
                counters: getCounters(query.profile),
                cssClass: ''
              }
            ]"
          />
        </tab>
      </tabs>
    </div>
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

  import { CounterDetails, CounterGroup, ImpalaQuery, ImpalaQueryProfile } from '../index';
  import { hueWindow } from 'types/types';
  import huePubSub from 'utils/huePubSub';

  import I18n from 'utils/i18n';

  declare const ENABLE_HUE_5: boolean;

  export default defineComponent({
    components: {
      Tab,
      Tabs,
      HueButton,
      QueryInfo,
      QueryInfoTop,
      CountersTable
    },

    props: {
      query: {
        type: Object as PropType<ImpalaQuery>,
        required: true
      }
    },

    emits: ['reload'],

    setup(): {
      showQueries?: () => void;
    } {
      return {
        showQueries: inject('showQueries')
      };
    },

    methods: {
      I18n,
      async reExecute() {
        huePubSub.publish('open.editor.new.query', {
          sourceType: 'impala'
        });

        huePubSub.subscribeOnce(
          ENABLE_HUE_5 ? 'ace.editor.focused' : 'set.current.app.view.model',
          () =>
            setTimeout(() => {
              huePubSub.publish('editor.insert.at.cursor', {
                text: this.query.queryText,
                cursorEndAdjust: 0
              });
            }, 100),
          ''
        );
      },
      getCounters: function (profile: ImpalaQueryProfile): CounterGroup[] {
        const kvToCounters = (kv: ImpalaQueryProfile['cpuMetrics']): CounterDetails[] =>
          Object.keys(kv).map(key => ({
            counterName: key,
            counterValue: kv[key]
          }));
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
      border-color: $fluidx-blue-700;
    }
  }

  .hue-layout-column {
    @include hue-flex-layout(column);
  }
</style>
