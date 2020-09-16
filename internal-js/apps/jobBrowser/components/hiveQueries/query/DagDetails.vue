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
    <select v-if="queryModel.dags.length > 1" v-model="selectedDagId" @change="dagSelected($event.target.value)" class="form-control">
      <option v-for="dag in queryModel.dags" v-bind:value="dag.dagInfo.dagId">{{ dag.dagInfo.dagId }}</option>
    </select>

    <br/>

    <!-- {{#bs-tab fade=false as |tab|}} -->
    <tabs>
      <tab title="DAG INFO"><dag-swimlane></dag-swimlane></tab>
      <tab title="DAG FLOW"><dag-graphical-view></dag-graphical-view></tab>
      <tab title="DAG COUNTERS"><dag-counters></dag-counters></tab>
      <tab title="DAG CONFIGURATIONS"><dag-configs></dag-configs></tab>
    </tabs>
    <!-- {{/bs-tab}} -->
  </div>
</template>

<script lang="ts">
  import Component from 'vue-class-component';
  import QueryComponent from './QueryComponent.vue';
  import Tab from '../../common/Tab.vue';
  import Tabs from '../../common/Tabs.vue';
  import { Dag } from '../index';
  import DagConfigs from './DagConfigs.vue';
  import DagCounters from './DagCounters.vue';
  import DagGraphicalView from './DagGraphicalView.vue';
  import DagSwimlane from './DagSwimlane.vue';

  @Component({
    components: {
      Tab, Tabs, DagConfigs, DagCounters, DagGraphicalView, DagSwimlane
    }
  })

  export default class DagDetails extends QueryComponent {
    selectedDagId?: string;

    dagSelected(dag: Dag) {
      // TODO: Implement
    }
  }
</script>

<style lang="scss" scoped>
</style>
