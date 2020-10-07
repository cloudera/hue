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
    <div class="info-inline">
      <div class="info-label">DAG ID</div>
      <div class="info-value">{{ dag.dagInfo.dagId }}</div>
    </div>

    <div class="info-inline">
      <div class="info-label">DAG Name</div>
      <div class="info-value">{{ dag.dagInfo.dagName }}</div>
    </div>

    <div class="info-inline">
      <div class="info-label">Status</div>
      <div class="info-value">{{ dag.dagInfo.status }}</div>
    </div>

    <div class="info-inline">
      <div class="info-label">Start Time</div>
      <div class="info-value">
        <time-ago :value="dag.dagInfo.startTime" />
      </div>
    </div>

    <div class="info-inline">
      <div class="info-label">End Time</div>
      <div class="info-value">
        <time-ago :value="dag.dagInfo.endTime" />
      </div>
    </div>

    <div class="info-inline">
      <div class="info-label">Duration</div>
      <div class="info-value">
        <duration v-if="dag.dagInfo.endTime" :value="dag.dagInfo.endTime - dag.dagInfo.startTime" />
        <span v-else>-</span>
      </div>
    </div>

    <div v-if="dag.dagDetails.diagnostics" class="info-row">
      <div class="info-label">Diagnostics</div>
      <pre class="info-value">{{ dag.dagDetails.diagnostics }}</pre>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import { Component, Prop } from 'vue-property-decorator';

  import Duration from '../../../../../../desktop/core/src/desktop/js/components/Duration.vue';
  import TimeAgo from '../../../../../../desktop/core/src/desktop/js/components/TimeAgo.vue';

  import { Dag } from '..';

  @Component({
    components: { Duration, TimeAgo }
  })
  export default class DagInfo extends Vue {
    @Prop({ required: true }) dag!: Dag;
  }
</script>

<style lang="scss" scoped>
  @import '../../../../../../desktop/core/src/desktop/js/components/styles/colors';
  @import '../../../../../../desktop/core/src/desktop/js/components/styles/mixins';

  .info-inline,
  .info-row {
    margin-bottom: 15px;
    margin-left: 10px;

    .info-label {
      text-transform: uppercase;
      color: $fluid-gray-500;
      font-weight: normal;
      font-size: 12px;
      margin: 0;
    }

    .info-value {
      color: $fluid-gray-700;
    }
  }

  .info-inline {
    display: inline-block;
    min-width: 600px;
  }
</style>
