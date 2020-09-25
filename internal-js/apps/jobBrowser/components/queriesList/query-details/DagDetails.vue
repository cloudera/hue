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
  <div id="dag-panel" class="target detail-panel dag-panel">
    <div>{{ dag.dagInfo.dagId }}</div>
    <tabs>
      <tab title="DAG SWIMLANE"><dag-swimlane :dag="dag" /></tab>
      <tab title="DAG FLOW"><dag-graphical-view /></tab>
      <tab title="DAG COUNTERS"><dag-counters /></tab>
      <tab title="DAG CONFIGURATIONS"><dag-configs :dag="dag" /></tab>
    </tabs>
  </div>
</template>

<script lang="ts">
  import { Component, Prop, Vue } from 'vue-property-decorator';
  import Tab from '../../../../../../desktop/core/src/desktop/js/components/Tab.vue';
  import Tabs from '../../../../../../desktop/core/src/desktop/js/components/Tabs.vue';
  import { Dag } from '../index';
  import DagConfigs from './DagConfigs.vue';
  import DagCounters from './DagCounters.vue';
  import DagGraphicalView from './DagGraphicalView.vue';
  import DagSwimlane from './dag-swimlane/DagSwimlane.vue';

  @Component({
    components: {
      Tab,
      Tabs,
      DagConfigs,
      DagCounters,
      DagGraphicalView,
      DagSwimlane
    }
  })
  export default class DagDetails extends Vue {
    @Prop({ required: true }) dag!: Dag;
  }
</script>

<style lang="scss" scoped></style>
