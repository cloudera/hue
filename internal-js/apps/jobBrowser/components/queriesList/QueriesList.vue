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
    <query-table
      v-if="!selectedQuery && !queriesToDiff"
      :queries="queries"
      :columns="columns"
      @diff-queries="diffQueries"
      @query-selected="querySelected"
    />
    <query-details v-else-if="selectedQuery" :query="selectedQuery" />
    <query-diff v-else :queries="queriesToDiff" />
  </div>
</template>

<script lang="ts">
  import { Duration } from 'luxon';
  import HumanByteSize from '../../../../../desktop/core/src/desktop/js/components/HumanByteSize.vue';
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Column } from '../../../../../desktop/core/src/desktop/js/components/HueTable';
  import TimeAgo from '../../../../../desktop/core/src/desktop/js/components/TimeAgo.vue';
  import { fetchExtendedQuery, search } from './apiUtils';
  import QueryDiff from './queryDiff/QueryDiff.vue';
  import QueryDetails from './query-details/QueryDetails.vue';
  import { Query } from './index';
  import QueryTable from './queryTable/QueryTable.vue';

  @Component({
    components: { QueryDiff, QueryDetails, QueryTable, TimeAgo, HumanByteSize }
  })
  export default class QueriesList extends Vue {
    selectedQuery: Query | null = null;
    queriesToDiff: Query[] | null = null;
    queries: Query[] = [];

    // TODO: Move to QueryTable?
    columns: Column<Query>[] = [
      { key: 'status', label: 'Status' },
      { key: 'query', label: 'Query' },
      { key: 'queueName', label: 'Queue' },
      { key: 'requestUser', label: 'User' },
      {
        key: 'tablesRead',
        label: 'Tables Read',
        adapter: (key: string, query: Query): string =>
          (query.tablesRead || []).map(data => `${data.table} (${data.database})`).join(', ')
      },
      {
        key: 'tablesWritten',
        label: 'Tables Written',
        adapter: (key: string, query: Query): string =>
          (query.tablesWritten || []).map(data => `${data.table} (${data.database})`).join(', ')
      },
      { key: 'startTime', label: 'Start Time', cellComponent: TimeAgo },
      {
        key: 'duration',
        label: 'Duration',
        adapter: (key: string, query: Query): string =>
          (query.duration && Duration.fromMillis(query.duration).toFormat('hh:mm:ss')) || ''
      },
      { key: 'dagID', label: 'DAG ID' },
      { key: 'appID', label: 'Application ID' },
      { key: 'cpuTime', label: 'CPU Time' },
      { key: 'physicalMemory', label: 'Physical Memory', cellComponent: HumanByteSize },
      { key: 'virtualMemory', label: 'Virtual Memory', cellComponent: HumanByteSize },
      { key: 'dataRead', label: 'Data Read', cellComponent: HumanByteSize },
      { key: 'dataWritten', label: 'Data Written', cellComponent: HumanByteSize },
      { key: 'executionMode', label: 'Execution Mode' },
      { key: 'usedCBO', label: 'Cost Based Optimizer (CBO)' }
    ];

    async created(): Promise<void> {
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
      this.selectedQuery = null;
      this.queriesToDiff = null;
    }

    diffQueries(queries: Query[]): void {
      this.queriesToDiff = queries;
    }

    async querySelected(query: Query): Promise<void> {
      this.selectedQuery = await fetchExtendedQuery({ queryId: query.queryId });
    }
  }
</script>

<style lang="scss" scoped></style>
