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
  <div class="hue-info-box">
    <LabeledInfo label="DAG ID" class="inline-info">
      {{ dag.dagInfo.dagId }}
    </LabeledInfo>

    <LabeledInfo label="DAG Name" class="inline-info">
      {{ dag.dagInfo.dagName }}
    </LabeledInfo>

    <LabeledInfo label="Status" class="inline-info">
      {{ dag.dagInfo.status }}
    </LabeledInfo>

    <LabeledInfo label="Duration" class="inline-info">
      <duration
        v-if="dag.dagInfo.endTime"
        :value="dag.dagInfo.endTime - dag.dagInfo.startTime"
        :short="false"
      />
    </LabeledInfo>

    <LabeledInfo label="Start Time" class="inline-info">
      <time-ago :value="dag.dagInfo.startTime" />
    </LabeledInfo>

    <LabeledInfo label="End Time" class="inline-info">
      <time-ago v-if="dag.dagInfo.endTime" :value="dag.dagInfo.endTime" />
    </LabeledInfo>

    <LabeledInfo v-if="dag.dagDetails.diagnostics" label="Diagnostics">
      <pre>{{ dag.dagDetails.diagnostics }}</pre>
    </LabeledInfo>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import Duration from '../../../../../../components/Duration.vue';
  import TimeAgo from '../../../../../../components/TimeAgo.vue';
  import LabeledInfo from '../components/LabeledInfo.vue';

  import { Dag } from '..';

  export default defineComponent({
    components: {
      Duration,
      TimeAgo,
      LabeledInfo
    },
    props: {
      dag: {
        type: Object as PropType<Dag>,
        required: true
      }
    }
  });
</script>

<style lang="scss" scoped>
  @import '../../../../../../components/styles/variables';
  @import '../../../../../../components/styles/mixins';

  .hue-info-box {
    padding: 10px;
    border: 1px solid $fluidx-gray-300;
    border-radius: $hue-panel-border-radius;

    display: flex;
    flex-wrap: wrap;

    column-gap: 10px;
    row-gap: 10px;

    > * {
      flex: 1;
      flex-basis: 100%;
    }

    > .inline-info {
      flex-basis: 500px;
    }
  }
</style>
