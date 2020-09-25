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
  <div class="hive-timeline">
    <div class="timeline-bars">
      <div class="groups">
        <div
          class="bar"
          :data-value="normalizedPerf.groupTotal.pre"
          title="Pre-Execution + DAG construction"
        >
          Pre-Execution + DAG construction
        </div>
        <div class="bar" :data-value="normalizedPerf.groupTotal.submit" title="DAG Submission">
          DAG Submission
        </div>
        <div class="bar" :data-value="normalizedPerf.groupTotal.running" title="DAG Runtime">
          DAG Runtime
        </div>
        <div class="bar" :data-value="normalizedPerf.groupTotal.post" title="Post Execution">
          Post Execution
        </div>
      </div>

      <div class="sub-groups">
        <div class="bar" :data-value="normalizedPerf.compile" title="Compile">
          Compile
        </div>
        <div class="bar" :data-value="normalizedPerf.parse" title="Parse">
          Parse
        </div>
        <div class="bar" :data-value="normalizedPerf.TezBuildDag" title="Build Dag">
          Build Dag
        </div>

        <div class="bar" :data-value="normalizedPerf.TezSubmitDag" title="Submit Dag">
          Submit Dag
        </div>
        <div
          class="bar"
          :data-value="normalizedPerf.TezSubmitToRunningDag"
          title="Submit To Running"
        >
          Submit To Running
        </div>

        <div class="bar" :data-value="normalizedPerf.TezRunDag" title="Run Dag">
          Run Dag
        </div>

        <div
          class="bar"
          :data-value="normalizedPerf.PostHiveProtoLoggingHook"
          title="Post Logging Hook"
        >
          Post ATS Hook
        </div>
        <div
          class="bar"
          :data-value="normalizedPerf.RemoveTempOrDuplicateFiles"
          title="Remove Files"
        >
          Remove Files
        </div>
        <div
          class="bar"
          :data-value="normalizedPerf.RenameOrMoveFiles"
          title="Rename Or Move Files"
        >
          Rename Or Move Files
        </div>
      </div>
    </div>

    <table class="detail-list" aria-describedby="Pre-Execution + DAG construction">
      <thead>
        <tr>
          <th scope="colgroup" colspan="2">
            Pre-Execution + DAG construction : {{ fmtDuration(normalizedPerf.groupTotal.pre) }}
          </th>
        </tr>
      </thead>

      <tbody>
        <tr>
          <td><i />Compile</td>
          <td>{{ fmtDuration(normalizedPerf.compile) }}</td>
        </tr>
        <tr>
          <td><i />Parse</td>
          <td>{{ fmtDuration(normalizedPerf.parse) }}</td>
        </tr>
        <tr>
          <td><i />Build Dag</td>
          <td>{{ fmtDuration(normalizedPerf.TezBuildDag) }}</td>
        </tr>
      </tbody>
    </table>

    <table class="detail-list" aria-describedby="DAG Submission">
      <thead>
        <tr>
          <th scope="colgroup" colspan="2">
            DAG Submission : {{ fmtDuration(normalizedPerf.groupTotal.submit) }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><i />Submit Dag</td>
          <td>{{ fmtDuration(normalizedPerf.TezSubmitDag) }}</td>
        </tr>
        <tr>
          <td><i />Submit To Running</td>
          <td>{{ fmtDuration(normalizedPerf.TezSubmitToRunningDag) }}</td>
        </tr>
      </tbody>
    </table>

    <table class="detail-list" aria-describedby="DAG Runtime">
      <thead>
        <tr>
          <th scope="colgroup" colspan="2">
            DAG Runtime : {{ fmtDuration(normalizedPerf.groupTotal.running) }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><i />Run Dag</td>
          <td>{{ fmtDuration(normalizedPerf.TezRunDag) }}</td>
        </tr>
      </tbody>
    </table>

    <table class="detail-list" aria-describedby="Post Execution">
      <thead>
        <tr>
          <th scope="colgroup" colspan="2">
            Post Execution : {{ fmtDuration(normalizedPerf.groupTotal.post) }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="normalizedPerf.PostHiveProtoLoggingHook">
          <td><i />Post Hive Hook</td>
          <td>{{ fmtDuration(normalizedPerf.PostHiveProtoLoggingHook) }}</td>
        </tr>
        <tr v-if="normalizedPerf.RemoveTempOrDuplicateFiles">
          <td><i />Remove Files</td>
          <td>{{ fmtDuration(normalizedPerf.RemoveTempOrDuplicateFiles) }}</td>
        </tr>
        <tr v-if="normalizedPerf.RenameOrMoveFiles">
          <td><i />Rename Or Move Files</td>
          <td>{{ fmtDuration(normalizedPerf.RenameOrMoveFiles) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
  import { Component, Prop, Vue } from 'vue-property-decorator';
  import { fmtDuration } from 'vue-meth';
  import NormalizedHivePerf from './NormalizedHivePerf';

  import './hive-timeline.scss';

  @Component({
    methods: {
      fmtDuration
    }
  })
  export default class HiveTimeline extends Vue {
    @Prop() perf: unknown;

    get normalizedPerf(): NormalizedHivePerf {
      return new NormalizedHivePerf(this.perf);
    }

    alignBars(bars: NodeListOf<HTMLElement>, perf: NormalizedHivePerf): void {
      bars.forEach((bar: HTMLElement) => {
        const perfValue = parseInt(bar.dataset.value || '0');
        const widthPercent = (perfValue / perf.total) * 100;
        bar.style.width = `${widthPercent}%`;
      });
    }

    alignTimeline(): void {
      this.alignBars(this.$el.querySelectorAll('.sub-groups .bar'), this.normalizedPerf);
      this.alignBars(this.$el.querySelectorAll('.groups .bar'), this.normalizedPerf);
    }

    mounted(): void {
      this.alignTimeline();
    }

    updated(): void {
      this.alignTimeline();
    }
  }
</script>
