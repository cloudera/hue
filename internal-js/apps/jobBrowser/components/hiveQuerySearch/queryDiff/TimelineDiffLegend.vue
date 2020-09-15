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
  <div class="title">Duration</div>
  <table class='detail-list'>
    <thead>
    <tr>
      <th colspan=2>Pre-Execution + DAG construction</th>
      <th>A - {{ perfTwo.groupTotal.pre }}</th>
      <th>B - {{ perfOne.groupTotal.pre }}</th>
    </tr>
    </thead>
    <tbody>
    <tr>
      <td colspan=2><i></i>Compile</td>
      <td>{{ perfTwo.compile }}</td>
      <td>{{ perfOne.compile }}</td>
    </tr>
    <tr>
      <td colspan=2><i></i>Parse</td>
      <td>{{ perfTwo.parse }}</td>
      <td>{{ perfOne.parse }}</td>
    </tr>
    <tr>
      <td colspan=2><i></i>Build Dag</td>
      <td>{{ perfTwo.TezBuildDag }}</td>
      <td>{{ perfOne.TezBuildDag }}</td>
    </tr>
    </tbody>
  </table>

  <table class='detail-list'>
    <thead>
    <tr>
      <th colspan=2>DAG Submission</th>
      <th>A - {{ perfTwo.groupTotal.submit }}</th>
      <th>B - {{ perfOne.groupTotal.submit }}</th>
    </tr>
    </thead>
    <tbody>
    <tr>
      <td colspan=2><i></i>Submit Dag</td>
      <td>{{ perfTwo.TezSubmitDag }}</td>
      <td>{{ perfOne.TezSubmitDag }}</td>
    </tr>
    <tr>
      <td colspan=2><i></i>Submit To Running</td>
      <td>{{ perfTwo.TezSubmitToRunningDag }}</td>
      <td>{{ perfOne.TezSubmitToRunningDag }}</td>
    </tr>
    </tbody>
  </table>
  <table class='detail-list'>
    <thead>
    <tr>
      <th colspan=2>DAG Runtime</th>
      <th>A - {{ perfTwo.groupTotal.running }}</th>
      <th>B - {{ perfOne.groupTotal.running }}</th>
    </tr>
    </thead>
    <tbody>
    <tr>
      <td colspan=2><i></i>Run Dag</td>
      <td>{{ perfTwo.TezRunDag }}</td>
      <td>{{ perfOne.TezRunDag }}</td>
    </tr>
    </tbody>
  </table>
  <table class='detail-list'>
    <thead>
    <tr>
      <th colspan=2>Post Execution</th>
      <th>A - {{ perfTwo.groupTotal.post }}</th>
      <th>B - {{ perfOne.groupTotal.post }}</th>
    </tr>
    </thead>
    <tbody>
    <tr>
      <td colspan=2><i></i>Post Hive Hook</td>
      <td>{{ perfTwo.PostHiveProtoLoggingHook }}</td>
      <td>{{ perfOne.PostHiveProtoLoggingHook }}</td>
    </tr>
    <tr>
      <td colspan=2><i></i>Remove Files</td>
      <td>{{ perfTwo.RemoveTempOrDuplicateFiles }}</td>
      <td>{{ perfOne.RemoveTempOrDuplicateFiles }}</td>
    </tr>
    <tr>
      <td colspan=2><i></i>Rename Or Move Files</td>
      <td>{{ perfTwo.RenameOrMoveFiles }}</td>
      <td>{{ perfOne.RenameOrMoveFiles }}</td>
    </tr>
    </tbody>
  </table>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import { NormalizedQueryPerf } from '../index';

  @Component
  export default class TimelineDiffLegend extends Vue {
    @Prop({ required: true })
    perfOne!: NormalizedQueryPerf;
    @Prop({ required: true })
    perfTwo!: NormalizedQueryPerf;
  }
</script>

<style lang="scss" scoped>
</style>
