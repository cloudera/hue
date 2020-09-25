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
    <div class="dag-panel">
      <fixed-anchor-nav :query="query" />
      <!-- {{#bs-tab fade=false as |tab|}} -->

      <tabs>
        <tab title="QUERY INFO">
          <query-info :query="query" />
        </tab>
        <tab title="VISUAL EXPLAIN">
          <visual-explain :queries="[query]" />
        </tab>
        <tab title="QUERY CONFIG">
          <query-config :queries="[query]" />
        </tab>
        <tab title="TIMELINE">
          <query-timeline :queries="[query]" />
        </tab>
      </tabs>

      <!-- {{/bs-tab}} -->
    </div>

    <dag-details v-if="!isDagEmpty" :query="query" />
  </div>
</template>

<script lang="ts">
  import Component from 'vue-class-component';
  import SingleQueryComponent from './SingleQueryComponent.vue';
  import Tab from '../../../../../../desktop/core/src/desktop/js/components/Tab.vue';
  import Tabs from '../../../../../../desktop/core/src/desktop/js/components/Tabs.vue';
  import FixedAnchorNav from './FixedAnchorNav.vue';
  import QueryTimeline from './QueryTimeline.vue';
  import DagDetails from './DagDetails.vue';
  import QueryConfig from './QueryConfig.vue';
  import QueryInfo from './QueryInfo.vue';
  import VisualExplain from './VisualExplain.vue';

  @Component({
    components: {
      Tab,
      Tabs,
      FixedAnchorNav,
      QueryTimeline,
      DagDetails,
      QueryConfig,
      VisualExplain,
      QueryInfo
    }
  })
  export default class QueryDetails extends SingleQueryComponent {
    get isDagEmpty(): boolean {
      return false; // TODO: Implement
    }
  }
</script>

<style lang="scss" scoped>
  .query-search {
    color: #0a78a3;
  }
</style>
