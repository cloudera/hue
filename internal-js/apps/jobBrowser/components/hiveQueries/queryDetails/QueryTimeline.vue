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
  import { normalizePerf, numberToLetter } from './utils';
  import MultiQueryComponent from './MultiQueryComponent.vue';
  import QueryTimelineBars from './QueryTimelineBars.vue';
  import QueryTimelineLegend from './QueryTimelineLegend.vue';
  import { NormalizedQueryPerf } from '../index';

  @Component({
    components: { QueryTimelineLegend, QueryTimelineBars }
  })
  export default class QueryTimeline extends MultiQueryComponent {
    get perfs(): { title: string; perf: NormalizedQueryPerf }[] {
      return this.queries.map((query, index) => {
        let title = 'Timeline';
        if (this.queries.length > 1) {
          title += ' - ' + numberToLetter(index);
        }
        return { title: title, perf: normalizePerf(query) };
      });
    }
  }
</script>

<style lang="scss" scoped></style>
