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
  <div class="query-info-box">
    <div class="query-info-row">
      <div class="query-info-label">Query ID</div>
      <div class="query-info-value">{{ query.queryId }}</div>
    </div>

    <div class="query-info-row">
      <div class="query-info-label">User</div>
      <div class="query-info-value">{{ query.requestUser }}</div>
    </div>

    <div class="query-info-row">
      <div class="query-info-label">Status</div>
      <div class="query-info-value">
        <StatusIndicator :value="query.status" />
        {{ query.status }}
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import { Component, Prop } from 'vue-property-decorator';

  import StatusIndicator from '../../../../../../desktop/core/src/desktop/js/components/StatusIndicator.vue';

  import { Query } from '..';

  @Component({
    components: { StatusIndicator }
  })
  export default class QueryInfoTab extends Vue {
    @Prop({ required: true }) query!: Query;
  }
</script>

<style lang="scss" scoped>
  @import '../../../../../../desktop/core/src/desktop/js/components/styles/colors';
  @import '../../../../../../desktop/core/src/desktop/js/components/styles/mixins';

  .query-info-row {
    display: inline-block;
    margin-right: 20px;

    .query-info-label {
      text-transform: uppercase;
      color: $fluid-gray-500;
      font-weight: normal;
      font-size: 12px;
      margin: 0;
    }

    .query-info-value {
      color: $fluid-gray-700;
    }

    .query-info-query {
      padding: 5px;
      width: 570px;
    }
  }

  .query-info-box {
    padding: 10px;
    margin: 20px 0 -10px 0;

    vertical-align: top;

    border: 1px solid $fluid-gray-300;
    border-radius: 5px;
  }
</style>
