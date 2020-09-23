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
    <div class="title">Duration</div>

    <table class="detail-list">
      <thead>
        <tr>
          <th>Pre-Execution + DAG construction</th>
          <th v-for="(perf, index) in perfs" :key="index">
            {{ numberToLetter(index) + ' - ' + perf.groupTotal.pre }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Compile</td>
          <td v-for="(perf, index) in perfs" :key="index">
            {{ perf.compile }}
          </td>
        </tr>
        <tr>
          <td>Parse</td>
          <td v-for="(perf, index) in perfs" :key="index">
            {{ perf.parse }}
          </td>
        </tr>
        <tr>
          <td>Build Dag</td>
          <td v-for="(perf, index) in perfs" :key="index">
            {{ perf.TezBuildDag }}
          </td>
        </tr>
      </tbody>
    </table>

    <table class="detail-list">
      <thead>
        <tr>
          <th>DAG Submission</th>
          <th v-for="(perf, index) in perfs" :key="index">
            {{ numberToLetter(index) + ' - ' + perf.groupTotal.submit }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Submit Dag</td>
          <td v-for="(perf, index) in perfs" :key="index">
            {{ perf.TezSubmitDag }}
          </td>
        </tr>
        <tr>
          <td>Submit To Running</td>
          <td v-for="(perf, index) in perfs" :key="index">
            {{ perf.TezSubmitToRunningDag }}
          </td>
        </tr>
      </tbody>
    </table>

    <table class="detail-list">
      <thead>
        <tr>
          <th>DAG Runtime</th>
          <th v-for="(perf, index) in perfs" :key="index">
            {{ numberToLetter(index) + ' - ' + perf.groupTotal.running }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Run Dag</td>
          <td v-for="(perf, index) in perfs" :key="index">
            {{ perf.TezRunDag }}
          </td>
        </tr>
      </tbody>
    </table>

    <table class="detail-list">
      <thead>
        <tr>
          <th>Post Execution</th>
          <th v-for="(perf, index) in perfs" :key="index">
            {{ numberToLetter(index) + ' - ' + perf.groupTotal.post }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Post Hive Hook</td>
          <td v-for="(perf, index) in perfs" :key="index">
            {{ perf.PostHiveProtoLoggingHook }}
          </td>
        </tr>
        <tr>
          <td>Remove Files</td>
          <td v-for="(perf, index) in perfs" :key="index">
            {{ perf.RemoveTempOrDuplicateFiles }}
          </td>
        </tr>
        <tr>
          <td>Rename Or Move Files</td>
          <td v-for="(perf, index) in perfs" :key="index">
            {{ perf.RenameOrMoveFiles }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
  import { numberToLetter } from './utils';
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import { NormalizedQueryPerf } from '../index';

  @Component({
    methods: { numberToLetter }
  })
  export default class QueryTimelineLegend extends Vue {
    @Prop({ required: true })
    perfs!: NormalizedQueryPerf[];
  }
</script>

<style lang="scss" scoped></style>
