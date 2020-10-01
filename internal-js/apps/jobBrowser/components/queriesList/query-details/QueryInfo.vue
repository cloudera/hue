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
    <div>
      <div class="query-details-row">
        <div class="query-details-label">Query ID</div>
        <div class="query-details-value">{{ query.queryId }}</div>
      </div>

      <div class="query-details-row">
        <div class="query-details-label">User</div>
        <div class="query-details-value">{{ query.requestUser }}</div>
      </div>

      <div class="query-details-row">
        <div class="query-details-label">Status</div>
        <div class="query-details-value">{{ query.status }}</div>
      </div>

      <div class="query-details-row">
        <div class="query-details-label">Start Time</div>
        <div class="query-details-value">
          <time-ago :value="query.startTime" />
        </div>
      </div>

      <div class="query-details-row">
        <div class="query-details-label">End Time</div>
        <div class="query-details-value">
          <time-ago :value="query.endTime" />
        </div>
      </div>

      <div class="query-details-row">
        <div class="query-details-label">Duration</div>
        <div class="query-details-value">
          <duration v-if="query.duration" :value="query.duration" />
          <span v-else>-</span>
        </div>
      </div>

      <div class="query-details-row">
        <div class="query-details-label">Tables Read</div>
        <div class="query-details-value">
          <span v-if="query.tablesReadWithDatabase">{{ query.tablesReadWithDatabase }}</span>
          <span v-else>-</span>
        </div>
      </div>

      <div class="query-details-row">
        <div class="query-details-label">Tables Written</div>
        <div class="query-details-value">
          <span v-if="query.tablesWrittenWithDatabase">{{ query.tablesWrittenWithDatabase }}</span>
          <span v-else>-</span>
        </div>
      </div>

      <div class="query-details-row">
        <div class="query-details-label">Application ID</div>
        <div class="query-details-value">
          <span v-if="query.appIds && query.appIds.length">{{ query.appIds }}</span>
          <span v-else>-</span>
        </div>
      </div>

      <div class="query-details-row">
        <div class="query-details-label">DAG ID</div>
        <div class="query-details-value">
          <span v-if="query.dagIds && query.dagIds.length">{{ query.dagIds }}</span>
          <span v-else>-</span>
        </div>
      </div>

      <div class="query-details-row">
        <div class="query-details-label">Session ID</div>
        <div class="query-details-value">{{ query.sessionId }}</div>
      </div>

      <div v-if="query.llapAppId" class="query-details-row">
        <div class="query-details-label">LLAP App ID</div>
        <div class="query-details-value">{{ query.llapAppId }}</div>
      </div>

      <div class="query-details-row">
        <div class="query-details-label">Thread Id</div>
        <div class="query-details-value">{{ query.threadId }}</div>
      </div>

      <div class="query-details-row">
        <div class="query-details-label">Queue</div>
        <div class="query-details-value">
          <span v-if="query.queueName">{{ query.queueName }}</span>
          <span v-else>None</span>
        </div>
      </div>

      <sql-text :value="query.query" />
    </div>

    <div v-if="query.details.diagnostics" class="panel panel-danger">
      <div class="panel-heading">DAG Diagnostics</div>
      <div class="diagnostics">{{ query.details.diagnostics }}</div>
    </div>
  </div>
</template>

<script lang="ts">
  import Component from 'vue-class-component';
  import Duration from '../../../../../../desktop/core/src/desktop/js/components/Duration.vue';
  import SqlText from '../../../../../../desktop/core/src/desktop/js/components/SqlText.vue';
  import TimeAgo from '../../../../../../desktop/core/src/desktop/js/components/TimeAgo.vue';
  import SingleQueryComponent from './SingleQueryComponent.vue';

  @Component({
    components: { Duration, TimeAgo, SqlText }
  })
  export default class QueryInfo extends SingleQueryComponent {}
</script>

<style lang="scss" scoped>
  @import '../../../../../../desktop/core/src/desktop/js/components/styles/colors';

  .query-title {
    padding: 0 10px 10px 10px;
    color: $fluid-gray-800;
    font-size: 20px;
    font-weight: 500;
  }

  .query-details-row {
    margin-bottom: 15px;
    margin-left: 10px;

    .query-details-label {
      text-transform: uppercase;
      color: $fluid-gray-500;
      font-weight: normal;
      font-size: 12px;
      margin: 0;
    }

    .query-details-value {
      color: $fluid-gray-700;
    }
  }
</style>
