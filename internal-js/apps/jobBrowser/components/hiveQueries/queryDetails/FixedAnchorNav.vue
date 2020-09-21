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
    <a href="javascript: void(0);" class="btn btn-success btn-sm">Queries (implement)</a>

    <div class="buttons">
      <template v-if="!query.isComplete">
        <button v-if="stoppingQuery" type="button" class="btn btn-default btn-sm disabled">
          <i class="fa fa-spinner fa-pulse fa-fw"></i> Stopping query
        </button>
        <button v-else type="button" class="btn btn-warning btn-sm" v-on:click="stopQuery">Stop</button>
      </template>

      <button type="button" class="btn btn-success btn-sm" v-on:click="downloadLogs">DOWNLOAD</button>
    </div>
  </div>
</template>

<script lang="ts">
  import Component from 'vue-class-component';
  import SingleQueryComponent from './SingleQueryComponent.vue';

  @Component
  export default class FixedAnchorNav extends SingleQueryComponent {
    stoppingQuery: boolean = false;

    stopQuery() {
      this.stoppingQuery = true;
      // TODO: Implement (see fixed-anchor-nav.js)
    }

    downloadLogs() {
      // TODO: Implement (see fixed-anchor-nav.js)
    }
  }
</script>

<style lang="scss" scoped>
</style>
