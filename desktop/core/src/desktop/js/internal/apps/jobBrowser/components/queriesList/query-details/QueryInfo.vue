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
  <div :class="`query-info layout-${layout}`">
    <div>
      <div class="hue-info-box">
        <LabeledInfo label="Query">
          <sql-text :enable-overflow="true" :format="true" :value="query.query" />
        </LabeledInfo>
      </div>
    </div>
    <div>
      <div class="hue-info-box">
        <LabeledInfo label="Start Time">
          <time-ago v-if="query.startTime" :value="query.startTime" />
        </LabeledInfo>

        <LabeledInfo label="End Time">
          <time-ago v-if="query.endTime" :value="query.endTime" />
        </LabeledInfo>

        <LabeledInfo label="Duration">
          <duration v-if="query.elapsedTime" :value="query.elapsedTime" />
        </LabeledInfo>

        <LabeledInfo label="Tables Read">
          <TablesList :tables="query.tablesRead" />
        </LabeledInfo>

        <LabeledInfo label="Tables Written">
          <TablesList :tables="query.tablesWritten" />
        </LabeledInfo>

        <LabeledInfo label="Application ID">
          {{ query.dags[0] && query.dags[0].dagInfo.applicationId }}
        </LabeledInfo>

        <LabeledInfo label="DAG ID">
          {{ query.dags && query.dags.map(dag => dag.dagInfo.dagId).join(',') }}
        </LabeledInfo>

        <LabeledInfo label="Session ID">
          {{ query.sessionId }}
        </LabeledInfo>

        <LabeledInfo label="LLAP App ID">
          {{ query.llapAppId }}
        </LabeledInfo>

        <LabeledInfo label="Thread Id">
          {{ query.threadId }}
        </LabeledInfo>

        <LabeledInfo label="Queue">
          <span v-if="query.queueName">{{ query.queueName }}</span>
          <span v-else>None</span>
        </LabeledInfo>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import { Component, Prop } from 'vue-property-decorator';

  import Duration from '../../../../../../components/Duration.vue';
  import SqlText from '../../../../../../components/SqlText.vue';
  import TimeAgo from '../../../../../../components/TimeAgo.vue';
  import TablesList from '../components/TablesList.vue';
  import LabeledInfo from '../components/LabeledInfo.vue';

  import { Query } from '..';

  @Component({
    components: { Duration, TimeAgo, SqlText, TablesList, LabeledInfo }
  })
  export default class QueryInfoTab extends Vue {
    @Prop({ required: true })
    query!: Query;

    @Prop({ default: 'row' })
    layout!: string;
  }
</script>

<style lang="scss" scoped>
  @import '../../../../../../components/styles/colors';
  @import '../../../../../../components/styles/mixins';

  .query-info {
    &.layout-row {
      white-space: nowrap;

      > div {
        width: 50%;
        display: inline-block;
        vertical-align: top;

        &:first-child {
          width: calc(50% - 14px);
          margin-right: 10px;
        }
      }
    }
    &.layout-column {
      display: inline-block;
      width: calc(50% - 7px);
      vertical-align: top;
      margin-right: 10px;

      > div {
        width: 100%;

        &:first-child {
          margin-bottom: 10px;
        }
      }
    }

    .hue-info-box {
      @include hue-flex-layout(column);

      padding: 10px;

      border: 1px solid $fluid-gray-300;
      border-radius: $hue-panel-border-radius;
    }
  }
</style>
