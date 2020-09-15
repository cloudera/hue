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
    <template v-for="(queryModel, index) in queryModels" :key="index">
      <div class="row">
        <div class="col-md-12">
          <div v-if="queryModels.length > 1" class="title">
            Visual Explain - {{ numberToLetter(index) }}
          </div>
          <div v-else class="title">
            Visual Explain
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-md-12">
          <div class="body">
            <div v-if="!queryModel" class="explain--error">
              <div>No Visual Explain available.</div>
            </div>
            <visual-explain v-else :query-model="queryModel" />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script lang="ts">
  import Component from 'vue-class-component';
  import VisualExplain from './VisualExplain.vue';
  import QueryComponent from './QueryComponent.vue';
  @Component({
    components: { VisualExplain }
  })
  export default class QueryVisualExplain extends QueryComponent {}
</script>

<style lang="scss" scoped></style>
