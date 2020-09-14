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
      <timeline-bar :total="extendedPerf.total" :value="extendedPerf.groupTotal.pre" title="Pre-Execution + DAG construction"></timeline-bar>
      <timeline-bar :total="extendedPerf.total" :value="extendedPerf.groupTotal.submit" title="DAG Submission"></timeline-bar>
      <timeline-bar :total="extendedPerf.total" :value="extendedPerf.groupTotal.running" title="DAG Runtime"></timeline-bar>
      <timeline-bar :total="extendedPerf.total" :value="extendedPerf.groupTotal.pre" title="Pre-Execution + DAG construction"></timeline-bar>
      <timeline-bar :total="extendedPerf.total" :value="extendedPerf.groupTotal.post" title="Post Execution"></timeline-bar>
    </timeline-bar-groups>
    <timeline-bar-sub-groups>
      <timeline-bar :total="extendedPerf.total" :value="extendedPerf.compile" title="Compile"></timeline-bar>
      <timeline-bar :total="extendedPerf.total" :value="extendedPerf.parse" title="Parse"></timeline-bar>
      <timeline-bar :total="extendedPerf.total" :value="extendedPerf.TezBuildDag" title="Build Dag"></timeline-bar>
      <timeline-bar :total="extendedPerf.total" :value="extendedPerf.TezSubmitDag" title="Submit Dag"></timeline-bar>
      <timeline-bar :total="extendedPerf.total" :value="extendedPerf.TezSubmitToRunningDag" title="Submit To Running"></timeline-bar>
      <timeline-bar :total="extendedPerf.total" :value="extendedPerf.TezRunDag" title="Run Dag"></timeline-bar>
      <timeline-bar :total="extendedPerf.total" :value="extendedPerf.PostHiveProtoLoggingHook" title="Post ATS Hook"></timeline-bar>
      <timeline-bar :total="extendedPerf.total" :value="extendedPerf.RemoveTempOrDuplicateFiles" title="Remove Files"></timeline-bar>
      <timeline-bar :total="extendedPerf.total" :value="extendedPerf.RenameOrMoveFiles" title="Rename Or Move Files"></timeline-bar>
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
  import { QueryPerf } from '../index';

  @Component({
    components: { TimelineBarSubGroups, TimelineBar, TimelineBarGroups, TimelineBars }
  })
  export default class TimelineDiff extends Vue {
    @Prop({ required: false })
    perf?: QueryPerf;

    extendedPerf = {
      compile: 0,
      groupTotal: {
        pre: 0,
        submit: 0,
        running: 0,
        post: 0
      },
      parse: 0,
      PostHiveProtoLoggingHook: 0,
      RemoveTempOrDuplicateFiles: 0,
      RenameOrMoveFiles: 0,
      TezBuildDag: 0,
      TezRunDag: 0,
      TezSubmitDag: 0,
      TezSubmitToRunningDag: 0,
      total: 0
    }

    constructor() {
      super();
      Object.assign(this.extendedPerf, this.perf);

      this.extendedPerf.groupTotal.post = this.extendedPerf.PostHiveProtoLoggingHook + this.extendedPerf.RemoveTempOrDuplicateFiles + this.extendedPerf.RenameOrMoveFiles;
      this.extendedPerf.groupTotal.pre = this.extendedPerf.compile + this.extendedPerf.parse + this.extendedPerf.TezBuildDag;
      this.extendedPerf.groupTotal.running = this.extendedPerf.TezRunDag;
      this.extendedPerf.groupTotal.submit = this.extendedPerf.TezSubmitDag + this.extendedPerf.TezSubmitToRunningDag;

      this.extendedPerf.total = this.extendedPerf.groupTotal.pre +
          this.extendedPerf.groupTotal.submit +
          this.extendedPerf.groupTotal.running +
          this.extendedPerf.groupTotal.post;
    }
  }
</script>

<style lang="scss" scoped>
</style>
