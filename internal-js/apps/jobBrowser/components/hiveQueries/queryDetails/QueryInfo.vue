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
    <div id="query-details" class="target detail-panel">
      <div class="row">
        <div class="col-md-12">
          <div class="query-title">
            Query Details <span v-if="title">- {{ title }}</span>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-md-4">
          <div class="query-details-row">
            <label class="query-details-label">Query ID</label>
            <div class="query-details-value">
              {{ query.queryId }}
            </div>
          </div>

          <div class="query-details-row">
            <label class="query-details-label">User</label>
            <div class="query-details-value">
              {{ query.requestUser }}
            </div>
          </div>

          <div class="query-details-row">
            <label class="query-details-label">Status</label>
            <div class="query-details-value">
              {{ query.status
              }}<!-- {{em-table-status-cell content=query.status}} -->
            </div>
          </div>

          <div class="query-details-row">
            <label class="query-details-label">Start Time</label>
            <div class="query-details-value">
              {{ query.startTime
              }}<!-- {{date-formatter content=query.startTime}} -->
            </div>
          </div>

          <div class="query-details-row">
            <label class="query-details-label">End Time</label>
            <div class="query-details-value">
              {{ query.endTime
              }}<!-- {{date-formatter content=query.endTime}} -->
            </div>
          </div>

          <div class="query-details-row">
            <label class="query-details-label">Duration</label>
            <div class="query-details-value">
              {{ query.duration
              }}<!-- {{txt query.duration type="duration"}} -->
            </div>
          </div>

          <div class="query-details-row">
            <label class="query-details-label">Tables Read</label>
            <div class="query-details-value">
              <span v-if="query.tablesReadWithDatabase">{{ query.tablesReadWithDatabase }}</span>
              <span v-else class="txt-message">Not Available!</span>
            </div>
          </div>

          <div class="query-details-row">
            <label class="query-details-label">Tables Written</label>
            <div class="query-details-value">
              <span v-if="query.tablesWrittenWithDatabase">{{
                query.tablesWrittenWithDatabase
              }}</span>
              <span v-else class="txt-message">Not Available!</span>
            </div>
          </div>

          <div class="query-details-row">
            <label class="query-details-label">Application ID</label>
            <div class="query-details-value">
              <span v-if="query.appIds && query.appIds.length">{{ query.appIds }}</span>
              <span v-else class="txt-message">Not Available!</span>
            </div>
          </div>

          <div class="query-details-row">
            <label class="query-details-label">DAG ID</label>
            <div class="query-details-value">
              <span v-if="query.dagIds && query.dagIds.length">{{ query.dagIds }}</span>
              <span v-else class="txt-message">Not Available!</span>
            </div>
          </div>

          <div class="query-details-row">
            <label class="query-details-label">Session ID</label>
            <div class="query-details-value">
              {{ query.sessionId }}
            </div>
          </div>

          <div v-if="query.llapAppId" class="query-details-row">
            <label class="query-details-label">LLAP App ID</label>
            <div class="query-details-value">
              {{ query.llapAppId }}
            </div>
          </div>

          <div class="query-details-row">
            <label class="query-details-label">Thread Id</label>
            <div class="query-details-value">
              {{ query.threadId }}
            </div>
          </div>

          <div class="query-details-row">
            <label class="query-details-label">Queue</label>
            <div class="query-details-value">
              <span v-if="query.queueName">{{ query.queueName }}</span>
              <span v-else>None</span>
            </div>
          </div>
        </div>

        <div class="col-md-8">
          <sql-text :value="query.query" />
        </div>
      </div>
    </div>

    <div v-if="query.details.diagnostics" class="panel panel-danger">
      <div class="panel-heading">DAG Diagnostics</div>
      <div class="diagnostics">
        {{ query.details.diagnostics }}
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import SqlText from '../../../../../../desktop/core/src/desktop/js/components/SqlText.vue';
  import SingleQueryComponent from './SingleQueryComponent.vue';

  @Component({
    components: { SqlText }
  })
  export default class QueryInfo extends SingleQueryComponent {
    @Prop({ required: false })
    title?: string;
  }
</script>

<style lang="scss" scoped></style>
