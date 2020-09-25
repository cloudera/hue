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
    <div v-if="perfs.length">
      <HiveTimeline v-for="(perf, index) in perfs" :key="index" :perf="perf" />
    </div>
    <h4 v-else>Data not available to display Timeline!</h4>
  </div>
</template>

<script lang="ts">
  import { Component } from 'vue-property-decorator';
  import HiveTimeline from './hive-timeline/HiveTimeline';
  import MultiQueryComponent from './MultiQueryComponent.vue';

  @Component({
    components: { HiveTimeline }
  })
  export default class QueryTimeline extends MultiQueryComponent {
    get perfs(): unknown {
      if (this.queries) {
        return this.queries
          .map(query => query && query.details && query.details.perf)
          .filter(perf => perf);
      }
    }
  }
</script>

<style lang="scss" scoped></style>
