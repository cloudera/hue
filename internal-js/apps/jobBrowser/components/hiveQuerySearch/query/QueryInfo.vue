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
  <div id="query-details" class="target detail-panel">
    <div class="row">
      <div class="col-md-12">
        <div class="query-title">Query Details <span v-if="title">- {{ title }}</span></div>
      </div>
    </div>
    <div class="row" >
      <div class="col-md-4">
        <div class="query-details-row">
          <label class="query-details-label">Query ID</label>
          <div class="query-details-value">{{ querymodel.queryId }}</div>
        </div>

        <div class="query-details-row">
          <label class="query-details-label">User</label>
          <div class="query-details-value">{{ querymodel.requestUser }}</div>
        </div>

        <div class="query-details-row">
          <label class="query-details-label">Status</label>
          <div class="query-details-value">{{ queryModel.status }}<!-- {{em-table-status-cell content=querymodel.status}} --></div>
        </div>

        <div class="query-details-row">
          <label class="query-details-label">Start Time</label>
          <div class="query-details-value">{{ queryModel.startTime }}<!-- {{date-formatter content=querymodel.startTime}} --></div>
        </div>

        <div class="query-details-row">
          <label class="query-details-label">End Time</label>
          <div class="query-details-value">{{ queryModel.endTime }}<!-- {{date-formatter content=querymodel.endTime}} --></div>
        </div>

        <div class="query-details-row">
          <label class="query-details-label">Duration</label>
          <div class="query-details-value">{{ queryModel.duration }}<!-- {{txt querymodel.duration type="duration"}} --></div>
        </div>

        <div class="query-details-row">
          <label class="query-details-label">Tables Read</label>
          <div class="query-details-value">
            <span v-if="queryModel.tablesReadWithDatabase">{{ queryModel.tablesReadWithDatabase }}</span>
            <span v-else class="txt-message">Not Available!</span>
          </div>
        </div>

        <div class="query-details-row">
          <label class="query-details-label">Tables Written</label>
          <div class="query-details-value">
            <span v-if="queryModel.tablesWrittenWithDatabase">{{ queryModel.tablesWrittenWithDatabase }}</span>
            <span v-else class="txt-message">Not Available!</span>
          </div>
        </div>

        <div class="query-details-row">
          <label class="query-details-label">Application ID</label>
          <div class="query-details-value">
            <span v-if="queryModel.appIds.length">{{ queryModel.appIds }}</span>
            <span v-else class="txt-message">Not Available!</span>
          </div>
        </div>

        <div class="query-details-row">
          <label class="query-details-label">DAG ID</label>
          <div class="query-details-value">
            <span v-if="queryModel.dagIds.length">{{ queryModel.dagIds }}</span>
            <span v-else class="txt-message">Not Available!</span>
          </div>
        </div>

        <div class="query-details-row">
          <label class="query-details-label">Session ID</label>
          <div class="query-details-value">{{ querymodel.sessionId }}</div>
        </div>

        <div v-if="queryModel.llapAppId" class="query-details-row">
          <label class="query-details-label">LLAP App ID</label>
          <div class="query-details-value">{{ querymodel.llapAppId }}</div>
        </div>

        <div class="query-details-row">
          <label class="query-details-label">Thread Id</label>
          <div class="query-details-value">{{ queryModel.threadId }}</div>
        </div>

        <div class="query-details-row">
          <label class="query-details-label">Queue</label>
          <div class="query-details-value">
            <span v-if="queryModel.queueName">{{ queryModel.queueName }}</span>
            <span v-else>None</span>
          </div>
        </div>
      </div>

      <!--
      <div class="col-md-8">
        {{caller-info title="Query Text" type="Hive" info=querymodel.query}}
      </div>
      -->
    </div>
  </div>

  <div v-if="queryModel.details.diagnostics" class="panel panel-danger">
    <div class="panel-heading">DAG Diagnostics</div>
    <div class="diagnostics">{{ queryModel.details.diagnostics }}</div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import {Prop} from 'vue-property-decorator';
  import { QueryModel } from '../index';

  @Component
  export default class QueryInfo extends Vue {
    @Prop({ required: true })
    queryModel!: QueryModel;

    @Prop({ required: false })
    title?: string;
  }
</script>

<style lang="scss" scoped>
</style>
