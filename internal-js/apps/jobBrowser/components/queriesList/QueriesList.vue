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
  <query-table
    v-if="!selectedQuery && !queriesToDiff"
    :queries="queries"
    :columns="columns"
    @diff-queries="diffQueries"
    @query-selected="querySelected"
  />
  <query-details v-else-if="selectedQuery" :query="selectedQuery" />
  <query-diff v-else :queries="queriesToDiff" />
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Column } from '../../../../../desktop/core/src/desktop/js/components/HueTable';
  import { search } from './apiUtils';
  import QueryDiff from './queryDiff/QueryDiff.vue';
  import QueryDetails from './queryDetails/QueryDetails.vue';
  import { Query } from './index';
  import QueryTable from './queryTable/QueryTable.vue';

  @Component({
    components: { QueryDiff, QueryDetails, QueryTable }
  })
  export default class QueriesList extends Vue {
    selectedQuery?: Query;
    queriesToDiff?: Query[];

    // TODO: Move to QueryTable?
    queries: Query[] = [];
    columns: Column[] = [
      { key: 'status', label: 'Status' },
      { key: 'query', label: 'Query' },
      { key: 'queueName', label: 'Queue' },
      { key: 'requestUser', label: 'User' },
      { key: 'tablesRead', label: 'Tables Read' },
      { key: 'tablesWritten', label: 'Tables Written' },
      { key: 'startTime', label: 'Start Time' },
      { key: 'dagID', label: 'DAG ID' },
      { key: 'appID', label: 'Application ID' },
      { key: 'cpuTime', label: 'CPU Time' },
      { key: 'physicalMemory', label: 'Physical Memory' },
      { key: 'virtualMemory', label: 'Virtual Memory' },
      { key: 'dataRead', label: 'Data Read' },
      { key: 'dataWritten', label: 'Data Written' },
      { key: 'executionMode', label: 'Execution Mode' },
      { key: 'usedCBO', label: 'Cost Based Optimizer (CBO)' }
    ];

    async created(): void {
      const now = Date.now();
      const searchResponse = await search({
        endTime: now,
        limit: 25,
        offset: 0,
        sortText: 'startTime:DESC',
        startTime: now - 1000 * 60 * 60 * 24 * 7,
        type: 'basic'
      });
      this.queries = searchResponse.queries;
    }

    showTable(): void {
      this.selectedQuery = undefined;
      this.queriesToDiff = undefined;
    }

    diffQueries(queries: Query[]): void {
      this.queriesToDiff = queries;
    }

    querySelected(query: Query): void {
      this.selectedQuery = query;
    }
  }
</script>

<style lang="scss" scoped></style>
