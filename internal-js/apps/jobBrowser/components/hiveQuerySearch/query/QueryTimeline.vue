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
    <template v-for='(perf, index) in perfs' :key='perf.title'>
      <div class="row">
        <div class="col-md-12">
          <div class="title">{{ perf.title }}</div>
        </div>
      </div>

      <div class="row">
        <div class="col-md-12">
          <div class="body">
            <query-timeline-bars v-if="perf" :perf="perf"></query-timeline-bars>
            <h4 v-else>Data not available to display Timeline!</h4>
            <query-timeline-legend v-if="perfs.length > 1 && index === perfs.length - 1" :perfs="perfs"></query-timeline-legend>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import QueryTimelineBars from '../query/QueryTimelineBars.vue';
  import QueryTimelineLegend from '../query/QueryTimelineLegend.vue';
  import { NormalizedQueryPerf, QueryModel } from '../index';

  const normalizePerf = (queryModel?: QueryModel): NormalizedQueryPerf => {
    const result = Object.assign({
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
    }, queryModel && queryModel.details && queryModel.details.perf);

    result.groupTotal.post = result.PostHiveProtoLoggingHook + result.RemoveTempOrDuplicateFiles + result.RenameOrMoveFiles;
    result.groupTotal.pre = result.compile + result.parse + result.TezBuildDag;
    result.groupTotal.running = result.TezRunDag;
    result.groupTotal.submit = result.TezSubmitDag + result.TezSubmitToRunningDag;

    result.total = result.groupTotal.pre +
        result.groupTotal.submit +
        result.groupTotal.running +
        result.groupTotal.post;

    return result;
  }

  @Component({
    components: { QueryTimelineLegend, QueryTimelineBars }
  })
  export default class QueryTimeline extends Vue {
    @Prop({ required: false })
    queryModels: QueryModel[] = [];
    @Prop({ required: false })
    queryModel?: QueryModel;

    constructor() {
      super();

      // TODO: Does queryModel change for this component?
      if (this.queryModel) {
        this.queryModels.push(this.queryModel);
      }
    }

    get perfs(): { title: string, perf: NormalizedQueryPerf }[] {
      return this.queryModels.map((model, index) => {
        let title = 'Timeline';
        if (this.queryModels.length > 1) {
          title += ' - ' + String.fromCharCode(65 + index);
        }
        return { title: title, perf: normalizePerf(model) }
      });
    }
  }
</script>

<style lang="scss" scoped></style>
