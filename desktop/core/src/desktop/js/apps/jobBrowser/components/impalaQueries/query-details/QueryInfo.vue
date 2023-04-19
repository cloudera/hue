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
          <sql-text :enable-overflow="true" :format="true" :value="query.queryText" />
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
          <duration v-if="query.duration" :value="query.duration" :short="true" />
        </LabeledInfo>

        <LabeledInfo label="Query Type">
          {{ query.queryType }}
        </LabeledInfo>

        <LabeledInfo label="User Name">
          {{ query.userName }}
        </LabeledInfo>

        <LabeledInfo label="Coordinator">
          {{ query.coordinator }}
        </LabeledInfo>

        <LabeledInfo label="CPU Time">
          <duration v-if="query.cpuTime" :value="query.cpuTime" :short="true" />
        </LabeledInfo>

        <LabeledInfo label="Rows Produced">
          <span v-if="query.rowsProduced">{{ query.rowsProduced }}</span>
          <span v-else>None</span>
        </LabeledInfo>

        <LabeledInfo label="Peak Memory">
          <HumanByteSize v-if="query.peakMemory" :value="query.peakMemory" />
        </LabeledInfo>

        <LabeledInfo label="HDFS Bytes Read">
          <HumanByteSize v-if="query.hdfsBytesRead" :value="query.hdfsBytesRead" />
        </LabeledInfo>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import Duration from '../../../../../components/Duration.vue';
  import SqlText from '../../../../../components/SqlText.vue';
  import TimeAgo from '../../../../../components/TimeAgo.vue';
  import HumanByteSize from '../../../../../components/HumanByteSize.vue';
  import LabeledInfo from './LabeledInfo.vue';

  import { ImpalaQuery } from '../index';

  export default defineComponent({
    components: {
      Duration,
      TimeAgo,
      SqlText,
      HumanByteSize,
      LabeledInfo
    },

    props: {
      query: {
        type: Object as PropType<ImpalaQuery>,
        required: true
      },
      layout: {
        type: String as PropType<'row' | 'column'>,
        default: 'row'
      }
    }
  });
</script>

<style lang="scss" scoped>
  @import '../../../../../components/styles/variables.scss';
  @import '../../../../../components/styles/mixins';

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

      overflow: hidden;
      white-space: normal;

      border: 1px solid $fluidx-gray-300;
      border-radius: $hue-panel-border-radius;
    }
  }
</style>
