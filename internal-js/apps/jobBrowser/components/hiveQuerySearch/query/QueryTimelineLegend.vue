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
  <div class="title">
    Duration
  </div>

  <table class="detail-list">
    <thead>
      <tr>
        <th>Pre-Execution + DAG construction</th>
        <template v-for="(perf, index) in perfs" :key="index">
          <th>{{ String.fromCharCode(65 + index) + ' - ' + perf.groupTotal.pre }}</th>
        </template>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Compile</td>
        <template v-for="(perf, index) in perfs" :key="index">
          <td>{{ perf.compile }}</td>
        </template>
      </tr>
      <tr>
        <td>Parse</td>
        <template v-for="(perf, index) in perfs" :key="index">
          <td>{{ perf.parse }}</td>
        </template>
      </tr>
      <tr>
        <td>Build Dag</td>
        <template v-for="(perf, index) in perfs" :key="index">
          <td>{{ perf.TezBuildDag }}</td>
        </template>
      </tr>
    </tbody>
  </table>

  <table class="detail-list">
    <thead>
      <tr>
        <th>DAG Submission</th>
        <template v-for="(perf, index) in perfs" :key="index">
          <th>{{ String.fromCharCode(65 + index) + ' - ' + perf.groupTotal.submit }}</th>
        </template>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Submit Dag</td>
        <template v-for="(perf, index) in perfs" :key="index">
          <td>{{ perf.TezSubmitDag }}</td>
        </template>
      </tr>
      <tr>
        <td>Submit To Running</td>
        <template v-for="(perf, index) in perfs" :key="index">
          <td>{{ perf.TezSubmitToRunningDag }}</td>
        </template>
      </tr>
    </tbody>
  </table>

  <table class="detail-list">
    <thead>
      <tr>
        <th>DAG Runtime</th>
        <template v-for="(perf, index) in perfs" :key="index">
          <th>{{ String.fromCharCode(65 + index) + ' - ' + perf.groupTotal.running }}</th>
        </template>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Run Dag</td>
        <template v-for="(perf, index) in perfs" :key="index">
          <td>{{ perf.TezRunDag }}</td>
        </template>
      </tr>
    </tbody>
  </table>

  <table class="detail-list">
    <thead>
      <tr>
        <th>Post Execution</th>
        <template v-for="(perf, index) in perfs" :key="index">
          <th>{{ String.fromCharCode(65 + index) + ' - ' + perf.groupTotal.post }}</th>
        </template>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Post Hive Hook</td>
        <template v-for="(perf, index) in perfs" :key="index">
          <td>{{ perf.PostHiveProtoLoggingHook }}</td>
        </template>
      </tr>
      <tr>
        <td>Remove Files</td>
        <template v-for="(perf, index) in perfs" :key="index">
          <td>{{ perf.RemoveTempOrDuplicateFiles }}</td>
        </template>
      </tr>
      <tr>
        <td>Rename Or Move Files</td>
        <template v-for="(perf, index) in perfs" :key="index">
          <td>{{ perf.RenameOrMoveFiles }}</td>
        </template>
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
  export default class QueryTimelineLegend extends Vue {
    @Prop({ required: false })
    perfs: NormalizedQueryPerf[] = [];
  }
</script>

<style lang="scss" scoped></style>
