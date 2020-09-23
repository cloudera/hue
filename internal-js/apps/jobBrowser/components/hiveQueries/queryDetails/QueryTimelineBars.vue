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
      <query-timeline-bar
        :total="perf.total"
        :value="perf.groupTotal.pre"
        title="Pre-Execution + DAG construction"
      />
      <query-timeline-bar
        :total="perf.total"
        :value="perf.groupTotal.submit"
        title="DAG Submission"
      />
      <query-timeline-bar
        :total="perf.total"
        :value="perf.groupTotal.running"
        title="DAG Runtime"
      />
      <query-timeline-bar
        :total="perf.total"
        :value="perf.groupTotal.pre"
        title="Pre-Execution + DAG construction"
      />
      <query-timeline-bar
        :total="perf.total"
        :value="perf.groupTotal.post"
        title="Post Execution"
      />
    </div>
    <div class="sub-groups">
      <query-timeline-bar :total="perf.total" :value="perf.compile" title="Compile" />
      <query-timeline-bar :total="perf.total" :value="perf.parse" title="Parse" />
      <query-timeline-bar :total="perf.total" :value="perf.TezBuildDag" title="Build Dag" />
      <query-timeline-bar :total="perf.total" :value="perf.TezSubmitDag" title="Submit Dag" />
      <query-timeline-bar
        :total="perf.total"
        :value="perf.TezSubmitToRunningDag"
        title="Submit To Running"
      />
      <query-timeline-bar :total="perf.total" :value="perf.TezRunDag" title="Run Dag" />
      <query-timeline-bar
        :total="perf.total"
        :value="perf.PostHiveProtoLoggingHook"
        title="Post ATS Hook"
      />
      <query-timeline-bar
        :total="perf.total"
        :value="perf.RemoveTempOrDuplicateFiles"
        title="Remove Files"
      />
      <query-timeline-bar
        :total="perf.total"
        :value="perf.RenameOrMoveFiles"
        title="Rename Or Move Files"
      />
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import QueryTimelineBar from './QueryTimelineBar.vue';
  import { NormalizedQueryPerf } from '../index';

  @Component({
    components: { QueryTimelineBar }
  })
  export default class QueryTimelineBars extends Vue {
    @Prop({ required: true })
    perf!: NormalizedQueryPerf;
  }
</script>

<style lang="scss" scoped></style>
