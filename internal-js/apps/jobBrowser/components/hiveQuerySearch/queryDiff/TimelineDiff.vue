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
  <div id="timeline" class="target detail-panel" >
    <div class="row">
      <div class="col-md-12">
        <div class="title">Timeline - A</div>
      </div>
    </div>

    <div class="row">
      <div class="col-md-12">
        <div class="body">
          <timeline-diff-bars
              v-if="explainPlanOne && explainPlanOne.details && explainPlanOne.details.perf"
              :perf="perfOne"
          ></timeline-diff-bars>
          <h4 v-else>Data not available to display Timeline!</h4>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-12">
        <div class="title">Timeline - B</div>
      </div>
    </div>

    <div class="row">
      <div class="col-md-12">
        <div class="body">
          <timeline-diff-bars
              v-if="explainPlanTwo && explainPlanTwo.details && explainPlanTwo.details.perf"
              :perf="perfTwo"
          ></timeline-diff-bars>
          <h4 v-else>Data not available to display Timeline!</h4>
          <timeline-diff-legend :perf-one="perfOne" :perf-two="perfTwo"></timeline-diff-legend>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import TimelineDiffLegend from './TimelineDiffLegend.vue';
  import TimelineDiffBars from './TimelineDiffBars.vue';
  import TimelineBar from '../../common/TimelineBar.vue';
  import TimelineBarGroups from '../../common/TimelineBarGroups.vue';
  import TimelineBars from '../../common/TimelineBars.vue';
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
    components: { TimelineDiffLegend, TimelineDiffBars, TimelineBar, TimelineBarGroups, TimelineBars }
  })
  export default class TimelineDiff extends Vue {
    @Prop({ required: false })
    explainPlanOne?: QueryModel;

    @Prop({ required: false })
    explainPlanTwo?: QueryModel;

    constructor() {
      super();
    }

    get perfOne(): NormalizedQueryPerf {
      return normalizePerf(this.explainPlanOne);
    }

    get perfTwo(): NormalizedQueryPerf {
      return normalizePerf(this.explainPlanTwo);
    }
  }
</script>

<style lang="scss" scoped>
</style>
