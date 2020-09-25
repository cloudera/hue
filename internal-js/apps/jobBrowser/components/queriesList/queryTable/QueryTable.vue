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

<!-- from table-component.hbs -->

<template>
  <div class="table-component">
    <queries-search :searches="searches" :table-definition="tableDefinition" />
    <div class="left-panel">
      <template v-if="!columnSelectorIsVisible">
        <div class="refine-header">
          Refine
          <i v-if="!dataProcessor.facets.fieldCount" class="fa fa-spinner fa-pulse fa-fw" />
          <i class="fa fa-plus" title="Customize" @click="toggleColumnSelector" />
        </div>
        <!-- {{em-table-facet-panel tableDefinition=definition dataProcessor=dataProcessor}} -->
      </template>
      <column-selector-panel
        v-else
        :columns="columns"
        :visible-columns="visibleColumns"
        @update:visible-columns="updateVisibleColumns"
        @close="toggleColumnSelector"
      />
    </div>
    <div class="table">
      <hue-table :columns="visibleColumns" :rows="queries" @row-clicked="querySelected" />
      <paginator :total-entries="totalQueries" @page-changed="pageChanged" />
    </div>
  </div>
</template>

<script lang="ts">
  import { Page } from 'components/Paginator';
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import Duration from '../../../../../../desktop/core/src/desktop/js/components/Duration.vue';
  import HumanByteSize from '../../../../../../desktop/core/src/desktop/js/components/HumanByteSize.vue';
  import TimeAgo from '../../../../../../desktop/core/src/desktop/js/components/TimeAgo.vue';
  import HueTable from '../../../../../../desktop/core/src/desktop/js/components/HueTable.vue';
  import Paginator from '../../../../../../desktop/core/src/desktop/js/components/Paginator.vue';
  import { Column } from '../../../../../../desktop/core/src/desktop/js/components/HueTable';
  import ColumnSelectorPanel from '../../../../../../desktop/core/src/desktop/js/components/ColumnSelectorPanel.vue';
  import { fetchSuggestedSearches } from '../apiUtils';
  import QueriesSearch from '../components/QueriesSearch.vue';
  import { DataProcessor, Query, Search, TableDefinition } from '../index';

  @Component({
    components: { HueTable, ColumnSelectorPanel, QueriesSearch, Paginator }
  })
  export default class QueryTable extends Vue {
    @Prop({ required: true })
    queries!: Query[];
    @Prop({ required: true })
    totalQueries!: number;

    searches: Search[] = [];
    visibleColumns: Column<Query>[] = [];
    columnSelectorIsVisible = false;

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
        cellComponent: Duration
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

    // TODO: Properly initiate TableDefinition
    tableDefinition: TableDefinition = {
      rangeData: {
        title: 'Some title'
      },
      columnPreferences: [{ id: 'some id' }]
    };

    // TODO: Properly initiate DataProcessor
    dataProcessor: DataProcessor = {
      facets: { fieldCount: 0 }
    };

    mounted(): void {
      this.visibleColumns = [...this.columns];
    }

    async created(): Promise<void> {
      this.searches = await fetchSuggestedSearches({ entityType: 'query' });
    }

    updateVisibleColumns(columns: Column<Query>[]): void {
      this.visibleColumns = columns;
      this.columnSelectorIsVisible = false;
    }

    toggleColumnSelector(): void {
      this.columnSelectorIsVisible = !this.columnSelectorIsVisible;
    }

    pageChanged(page: Page): void {
      this.$emit('page-changed', page);
    }

    querySelected(query: Query): void {
      this.$emit('query-selected', query);
    }

    diffQueries(queries: Query[]): void {
      this.$emit('diff-queries', queries);
    }
  }
</script>

<style lang="scss" scoped></style>
