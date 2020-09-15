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
  <div class="timeline-bars">
    <div class="groups">
      <bar :total="perf.total" :value="perf.groupTotal.pre" title="Pre-Execution + DAG construction"></bar>
      <bar :total="perf.total" :value="perf.groupTotal.submit" title="DAG Submission"></bar>
      <bar :total="perf.total" :value="perf.groupTotal.running" title="DAG Runtime"></bar>
      <bar :total="perf.total" :value="perf.groupTotal.pre" title="Pre-Execution + DAG construction"></bar>
      <bar :total="perf.total" :value="perf.groupTotal.post" title="Post Execution"></bar>
    </div>
    <div class="sub-groups">
      <bar :total="perf.total" :value="perf.compile" title="Compile"></bar>
      <bar :total="perf.total" :value="perf.parse" title="Parse"></bar>
      <bar :total="perf.total" :value="perf.TezBuildDag" title="Build Dag"></bar>
      <bar :total="perf.total" :value="perf.TezSubmitDag" title="Submit Dag"></bar>
      <bar :total="perf.total" :value="perf.TezSubmitToRunningDag" title="Submit To Running"></bar>
      <bar :total="perf.total" :value="perf.TezRunDag" title="Run Dag"></bar>
      <bar :total="perf.total" :value="perf.PostHiveProtoLoggingHook" title="Post ATS Hook"></bar>
      <bar :total="perf.total" :value="perf.RemoveTempOrDuplicateFiles" title="Remove Files"></bar>
      <bar :total="perf.total" :value="perf.RenameOrMoveFiles" title="Rename Or Move Files"></bar>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import Bar from '../../common/Bar.vue';
  import { NormalizedQueryPerf } from '../index';

  @Component({
    components: { Bar }
  })
  export default class QueryTimelineBars extends Vue {
    @Prop({ required: true })
    perf!: NormalizedQueryPerf;
  }
</script>

<style lang="scss" scoped>
</style>
