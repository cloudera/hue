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
  <timeline-bars>
    <timeline-bar-groups>
      <timeline-bar :total="perf.total" :value="perf.groupTotal.pre" title="Pre-Execution + DAG construction"></timeline-bar>
      <timeline-bar :total="perf.total" :value="perf.groupTotal.submit" title="DAG Submission"></timeline-bar>
      <timeline-bar :total="perf.total" :value="perf.groupTotal.running" title="DAG Runtime"></timeline-bar>
      <timeline-bar :total="perf.total" :value="perf.groupTotal.pre" title="Pre-Execution + DAG construction"></timeline-bar>
      <timeline-bar :total="perf.total" :value="perf.groupTotal.post" title="Post Execution"></timeline-bar>
    </timeline-bar-groups>
    <timeline-bar-sub-groups>
      <timeline-bar :total="perf.total" :value="perf.compile" title="Compile"></timeline-bar>
      <timeline-bar :total="perf.total" :value="perf.parse" title="Parse"></timeline-bar>
      <timeline-bar :total="perf.total" :value="perf.TezBuildDag" title="Build Dag"></timeline-bar>
      <timeline-bar :total="perf.total" :value="perf.TezSubmitDag" title="Submit Dag"></timeline-bar>
      <timeline-bar :total="perf.total" :value="perf.TezSubmitToRunningDag" title="Submit To Running"></timeline-bar>
      <timeline-bar :total="perf.total" :value="perf.TezRunDag" title="Run Dag"></timeline-bar>
      <timeline-bar :total="perf.total" :value="perf.PostHiveProtoLoggingHook" title="Post ATS Hook"></timeline-bar>
      <timeline-bar :total="perf.total" :value="perf.RemoveTempOrDuplicateFiles" title="Remove Files"></timeline-bar>
      <timeline-bar :total="perf.total" :value="perf.RenameOrMoveFiles" title="Rename Or Move Files"></timeline-bar>
    </timeline-bar-sub-groups>
  </timeline-bars>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import TimelineBar from '../../common/TimelineBar.vue';
  import TimelineBarGroups from '../../common/TimelineBarGroups.vue';
  import TimelineBars from '../../common/TimelineBars.vue';
  import TimelineBarSubGroups from '../../common/TimelineBarSubGroups.vue';
  import { NormalizedQueryPerf } from '../index';

  @Component({
    components: { TimelineBarSubGroups, TimelineBar, TimelineBarGroups, TimelineBars }
  })
  export default class TimelineDiffBars extends Vue {
    @Prop({ required: true })
    perf!: NormalizedQueryPerf;
  }
</script>

<style lang="scss" scoped>
</style>
