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
  <br/>
  <br/>
  <div id="timeline" class="target detail-panel" >
    <div class="row">
      <div class="col-md-12">
        <div class="title">Timeline - A</div>
      </div>
    </div>

    <div class="row">
      <div class="col-md-12">
        <div class="body">
          <timeline-diff-bars v-if="explainPlanOne.details.perf" :perf="explainPlanOne.details.perf"></timeline-diff-bars>
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
          <timeline-diff-bars v-if="explainPlanTwo.details.perf" :perf="explainPlanTwo.details.perf"></timeline-diff-bars>
          <h4 v-else>Data not available to display Timeline!</h4>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import TimelineDiffBars
    from './TimelineDiffBars.vue';
  import TimelineBar from '../../common/TimelineBar.vue';
  import TimelineBarGroups from '../../common/TimelineBarGroups.vue';
  import TimelineBars from '../../common/TimelineBars.vue';
  import { QueryModel } from '../index';

  @Component({
    components: { TimelineDiffBars, TimelineBar, TimelineBarGroups, TimelineBars }
  })
  export default class TimelineDiff extends Vue {
    @Prop({ required: false })
    explainPlanOne?: QueryModel;
    @Prop({ required: false })
    explainPlanTwo?: QueryModel;
  }
</script>

<style lang="scss" scoped>
</style>
