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
  <div id="timeline" class="target detail-panel">
    <div v-for="(perf, index) in perfs" :key="perf.title">
      <div class="row">
        <div class="col-md-12">
          <div class="title">
            {{ perf.title }}
          </div>
        </div>
      </div>

      <div class="row">
        <div class="col-md-12">
          <div class="body">
            <query-timeline-bars v-if="perf" :perf="perf" />
            <h4 v-else>
              Data not available to display Timeline!
            </h4>
            <query-timeline-legend
              v-if="perfs.length > 1 && index === perfs.length - 1"
              :perfs="perfs"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import Component from 'vue-class-component';
  import MultiQueryComponent from './MultiQueryComponent.vue';
  import QueryTimelineBars from './QueryTimelineBars.vue';
  import QueryTimelineLegend from './QueryTimelineLegend.vue';
  import { NormalizedQueryPerf, Query } from '../index';

  const normalizePerf = (query?: Query): NormalizedQueryPerf => {
    const result = Object.assign(
      {
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
      },
      query && query.details && query.details.perf
    );

    result.groupTotal.post =
      result.PostHiveProtoLoggingHook +
      result.RemoveTempOrDuplicateFiles +
      result.RenameOrMoveFiles;
    result.groupTotal.pre = result.compile + result.parse + result.TezBuildDag;
    result.groupTotal.running = result.TezRunDag;
    result.groupTotal.submit = result.TezSubmitDag + result.TezSubmitToRunningDag;

    result.total =
      result.groupTotal.pre +
      result.groupTotal.submit +
      result.groupTotal.running +
      result.groupTotal.post;

    return result;
  };

  @Component({
    components: { QueryTimelineLegend, QueryTimelineBars }
  })
  export default class QueryTimeline extends MultiQueryComponent {
    get perfs(): { title: string; perf: NormalizedQueryPerf }[] {
      return this.queries.map((query, index) => {
        let title = 'Timeline';
        if (this.queries.length > 1) {
          title += ' - ' + this.numberToLetter(index);
        }
        return { title: title, perf: normalizePerf(query) };
      });
    }
  }
</script>

<style lang="scss" scoped></style>
