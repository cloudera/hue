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
  <div class="dag-panel">
    <!-- {{fixed-anchor-nav anchors=queryDetailsTabsMod querymodel=querymodel}} -->
    <!-- {{#bs-tab fade=false as |tab|}} -->

    <tabs>
      <tab title="QUERY INFO">
        <query-info />
      </tab>
      <tab title="VISUAL EXPLAIN">
        <visual-explain />
      </tab>
      <tab title="QUERY CONFIG">
        <query-config />
      </tab>
      <tab title="TIMELINE">
        <timeline />
      </tab>
    </tabs>

    <!-- {{/bs-tab}} -->
  </div>

  <dag-details v-if="!isDagEmpty()" />
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import DagDetails from './DagDetails.vue';
  import QueryConfig from './QueryConfig.vue';
  import QueryInfo from './QueryInfo.vue';
  import Timeline from './Timeline.vue';
  import VisualExplain from './VisualExplain.vue';

  @Component({
    components: { DagDetails, Timeline, QueryConfig, VisualExplain, QueryInfo }
  })
  export default class Query extends Vue {
    isDagEmpty(): boolean {
      return false; // TODO: Implement
    }
  }
</script>

<style lang="scss" scoped>
  .query-search {
    color: #0a78a3;
  }
</style>
