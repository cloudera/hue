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
  <div id="visual-explain" class="target detail-panel query-details-visualExplain">
    <div class="row">
      <div class="col-md-12">
        <div class="title">Visual Explain - A</div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-12">
        <div class="body">
          <div v-if="!explainPlanOne" class="explain--error">
            <div>No Visual Explain available.</div>
          </div>
          <visual-explain v-else ></visual-explain>
          <!-- {{visual-explain planId=planId1
            expandQueryResultPanel='expandQueryResultPanel'
            visualExplainJson=explainPlanOne
            isQueryRunning=isQueryRunning
          }} -->
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-12">
        <div class="title">Visual Explain - B</div>
      </div>
    </div>
    <div class="row">
      <div class="col-md-12">
        <div class="body">
          <div v-if="!explainPlanTwo" class="explain--error">
            <div>No Visual Explain available.</div>
          </div>
          <visual-explain v-else></visual-explain>
          <!-- {{visual-explain planId=planId2
            expandQueryResultPanel='expandQueryResultPanel'
            visualExplainJson=explainPlanTwo
            isQueryRunning=isQueryRunning
          }} -->
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import { QueryModel } from '../index';
  import VisualExplain from '../query/VisualExplain.vue';

  @Component({
    components: { VisualExplain }
  })
  export default class VisualExplainDiff extends Vue {
    @Prop({ required: false })
    explainPlanOne?: QueryModel;
    @Prop({ required: false })
    explainPlanTwo?: QueryModel;
  }
</script>

<style lang="scss" scoped>
</style>
