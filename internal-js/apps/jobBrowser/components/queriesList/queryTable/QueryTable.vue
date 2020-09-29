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
    <!-- <queries-search :searches="searches" :table-definition="tableDefinition" /> -->
    <search-input @search="searchQueryChanged" />
    <hue-button :disabled="selectedQueries.length !== 2" @click="diffQueries(selectedQueries)">
      {{ I18n('Compare') }}
    </hue-button>
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
      <hue-table :columns="visibleColumns" :rows="queries">
        <template #cell-select="query">
          <input v-model="selectedQueries" type="checkbox" :value="query" />
        </template>
        <template #cell-query="query">
          <hue-link @click="querySelected(query)">{{ query.query }}</hue-link>
        </template>
      </hue-table>
    </div>
    <paginator
      ref="paginator"
      :total-entries="totalQueries"
      :current-page="currentPage"
      @page-changed="pageChanged"
    />
  </div>
</template>

<script lang="ts">
  import { Page } from 'components/Paginator';
  import I18n from '../../../../../../desktop/core/src/desktop/js/utils/i18n';
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import { duration } from '../../../../../../desktop/core/src/desktop/js/components/Duration.vue';
  import { humanSize } from '../../../../../../desktop/core/src/desktop/js/components/HumanByteSize.vue';
  import HueButton from '../../../../../../desktop/core/src/desktop/js/components/HueButton.vue';
  import HueLink from '../../../../../../desktop/core/src/desktop/js/components/HueLink.vue';
  import { timeAgo } from '../../../../../../desktop/core/src/desktop/js/components/TimeAgo.vue';
  import HueTable from '../../../../../../desktop/core/src/desktop/js/components/HueTable.vue';
  import Paginator from '../../../../../../desktop/core/src/desktop/js/components/Paginator.vue';
  import SearchInput from '../../../../../../desktop/core/src/desktop/js/components/SearchInput.vue';
  import { Column } from '../../../../../../desktop/core/src/desktop/js/components/HueTable';
  import ColumnSelectorPanel from '../../../../../../desktop/core/src/desktop/js/components/ColumnSelectorPanel.vue';
  import { fetchSuggestedSearches } from '../apiUtils';
  import QueriesSearch from '../components/QueriesSearch.vue';
  import { DataProcessor, Query, Search, TableDefinition } from '../index';

  @Component({
    components: {
      SearchInput,
      HueButton,
      HueLink,
      HueTable,
      ColumnSelectorPanel,
      QueriesSearch,
      Paginator
    },
    methods: {
      I18n: I18n
    }
  })
  export default class QueryTable extends Vue {
    @Prop({ required: true })
    queries!: Query[];
    @Prop({ required: true })
    totalQueries!: number;

    searches: Search[] = [];
    visibleColumns: Column<Query>[] = [];
    columnSelectorIsVisible = false;
    selectedQueries: Query[] = [];

    currentPage?: Page;
    searchQuery = '';

    columns: Column<Query>[] = [
      { key: 'select', label: '' },
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
      {
        key: 'startTime',
        label: 'Start Time',
        adapter: (key: string, query: Query): string => timeAgo(query.startTime)
      },
      {
        key: 'duration',
        label: 'Duration',
        adapter: (key: string, query: Query): string =>
          (query.duration && duration(query.duration)) || ''
      },
      { key: 'dagID', label: 'DAG ID' },
      { key: 'appID', label: 'Application ID' },
      { key: 'cpuTime', label: 'CPU Time' },
      {
        key: 'physicalMemory',
        label: 'Physical Memory',
        adapter: (key: string, query: Query): string => humanSize(query.physicalMemory)
      },
      {
        key: 'virtualMemory',
        label: 'Virtual Memory',
        adapter: (key: string, query: Query): string => humanSize(query.virtualMemory)
      },
      {
        key: 'dataRead',
        label: 'Data Read',
        adapter: (key: string, query: Query): string => humanSize(query.dataRead)
      },
      {
        key: 'dataWritten',
        label: 'Data Written',
        adapter: (key: string, query: Query): string => humanSize(query.dataWritten)
      },
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

    notifyThrottle = -1;

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

    notifySearch(): void {
      window.clearTimeout(this.notifyThrottle);
      this.notifyThrottle = window.setTimeout(() => {
        this.$emit('search', { page: this.currentPage, text: this.searchQuery });
      }, 0);
    }

    pageChanged(page: Page): void {
      this.currentPage = page;
      this.notifySearch();
    }

    searchQueryChanged(searchQuery: string): void {
      this.searchQuery = searchQuery;
      if (this.currentPage && this.currentPage.offset !== 0) {
        // pageChanged will notify
        (<Paginator>this.$refs.paginator).gotoFirstPage();
      } else {
        this.notifySearch();
      }
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
