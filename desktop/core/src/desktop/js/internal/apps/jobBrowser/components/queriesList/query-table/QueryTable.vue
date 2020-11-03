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
  <div class="query-table">
    <!-- <queries-search :searches="searches" :table-definition="tableDefinition" /> -->
    <div class="query-table-actions">
      <search-input v-model="searchQuery" @search="searchQueryEnter" />

      <div class="query-table-filters">
        <hue-icon type="hi-filter" /> Filter by:
        <facet-selector
          ref="statusFacetSelector"
          :facet="statusFacet"
          :value-labels="statusValueLabels"
          field-label="Status"
          @facet-removed="facetRemoved"
          @facet-changed="facetChanged"
        />
        <facet-selector
          ref="userFacetSelector"
          :facet="userFacet"
          field-label="User"
          :disabled="userFacet.values.length === 0"
          @facet-removed="facetRemoved"
          @facet-changed="facetChanged"
        />
        <date-range-picker ref="rangePicker" @date-range-changed="timeRangeChanged" />
        <hue-link class="clear-link" @click="clearSearch">{{ I18n('Clear All') }}</hue-link>
        <hue-link class="columns-link" @click="toggleColumnSelector">
          {{ I18n('Columns') }}
        </hue-link>
      </div>

      <div class="query-table-actions-right">
        <hue-button :disabled="selectedQueries.length !== 2" @click="diffQueries(selectedQueries)">
          {{ I18n('Compare') }}
        </hue-button>

        <hue-button :disabled="selectedQueries.length === 0" @click="killQueries(selectedQueries)">
          {{ I18n('Kill') }}
        </hue-button>
      </div>
    </div>
    <div class="query-table-container">
      <div v-if="columnSelectorIsVisible" class="query-table-left-panel">
        <column-selector-panel
          :columns="columns"
          :visible-columns="visibleColumns"
          @update:visible-columns="updateVisibleColumns"
          @close="toggleColumnSelector"
        />
      </div>
      <div class="query-table-right-panel">
        <hue-table :columns="visibleColumns" :rows="queries">
          <template #cell-status="query">
            <status-indicator class="status-indicator" :value="query.status" />
          </template>
          <template #cell-select="query">
            <input v-model="selectedQueries" type="checkbox" :value="query" />
          </template>
          <template #cell-query="query">
            <hue-link @click="querySelected(query)">{{ query.query }}</hue-link>
          </template>
          <template #cell-tablesRead="query">
            <TablesList :tables="query.tablesRead" />
          </template>
          <template #cell-tablesWritten="query">
            <TablesList :tables="query.tablesWritten" />
          </template>
        </hue-table>
      </div>
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
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import { Range } from '../../../../../../components/DateRangePicker';
  import { Page } from '../../../../../../components/Paginator';
  import I18n from '../../../../../../utils/i18n';
  import DateRangePicker from '../../../../../../components/DateRangePicker.vue';
  import { duration } from '../../../../../../components/Duration.vue';
  import { humanSize } from '../../../../../../components/HumanByteSize.vue';
  import HueButton from '../../../../../../components/HueButton.vue';
  import HueIcon from '../../../../../../components/HueIcon.vue';
  import HueLink from '../../../../../../components/HueLink.vue';
  import { timeAgo } from '../../../../../../components/TimeAgo.vue';
  import HueTable from '../../../../../../components/HueTable.vue';
  import Paginator from '../../../../../../components/Paginator.vue';
  import SearchInput from '../../../../../../components/SearchInput.vue';
  import StatusIndicator from '../../../../../../components/StatusIndicator.vue';
  import { Column } from '../../../../../../components/HueTable';
  import ColumnSelectorPanel from '../../../../../../components/ColumnSelectorPanel.vue';
  import FacetSelector from '../../../../../../components/FacetSelector.vue';
  import TablesList from '../components/TablesList.vue';
  import {
    Facet,
    FacetValue,
    FacetValueLabels,
    SearchFacet
  } from '../../../../../../components/FacetSelector';
  import { fetchFacets } from '../api-utils/search';
  import QueriesSearch from '../components/QueriesSearch.vue';
  import { DataProcessor, Query, Search, TableDefinition } from '../index';

  const DEFAULT_STATUS_FACET_VALUES: FacetValue[][] = [
    ['STARTED', { key: 'STARTED', value: 0 }],
    ['RUNNING', { key: 'RUNNING', value: 0 }],
    ['SUCCESS', { key: 'SUCCESS', value: 0 }],
    ['ERROR', { key: 'ERROR', value: 0 }]
  ];

  @Component({
    components: {
      FacetSelector,
      HueIcon,
      DateRangePicker,
      StatusIndicator,
      SearchInput,
      HueButton,
      HueLink,
      HueTable,
      TablesList,
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
    timeRange?: Range;
    facets: { [field: string]: SearchFacet } = {};

    statusFacet: Facet = {
      facetField: 'status',
      values: []
    };

    statusValueLabels: FacetValueLabels = {
      STARTED: I18n('Started'),
      RUNNING: I18n('Running'),
      SUCCESS: I18n('Success'),
      ERROR: I18n('Error')
    };

    userFacet: Facet = {
      facetField: 'userId',
      values: []
    };

    columns: Column<Query>[] = [
      { key: 'select', label: '' },
      { key: 'status', label: 'Status' },
      { key: 'query', label: 'Query' },
      { key: 'queueName', label: 'Queue' },
      { key: 'userId', label: 'User' },
      {
        key: 'tablesRead',
        label: 'Tables Read'
      },
      {
        key: 'tablesWritten',
        label: 'Tables Written'
      },
      {
        key: 'startTime',
        label: 'Start Time',
        adapter: (key: string, query: Query): string => timeAgo(query.startTime)
      },
      {
        key: 'elapsedTime',
        label: 'Duration',
        adapter: (key: string, query: Query): string =>
          (query.elapsedTime && duration(query.elapsedTime)) || ''
      },
      {
        key: 'dagIDs',
        label: 'DAG IDs',
        adapter: (key: string, query: Query): string =>
          query.dags.map(dag => dag.dagInfo.dagId).join(',')
      },
      {
        key: 'appID',
        label: 'Application ID',
        adapter: (key: string, query: Query): string =>
          query.dags[0] && query.dags[0].dagInfo.applicationId
      },
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

    async mounted(): void {
      this.visibleColumns = [...this.columns];
      this.setStatusFacetValues([]);
    }

    async created(): Promise<void> {
      // this.searches = await fetchSuggestedSearches({ entityType: 'query' });
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
      this.notifyThrottle = window.setTimeout(async () => {
        this.$emit('search', {
          page: this.currentPage,
          text: this.searchQuery,
          timeRange: this.timeRange,
          facets: Object.values(this.facets)
        });

        const now = Date.now();
        try {
          const facetResponse = await fetchFacets({
            startTime: this.timeRange?.from || now - 1000 * 60 * 60 * 24 * 7,
            endTime: this.timeRange?.to || now,
            facetFields: ['status', 'userId']
          });
          facetResponse.facets.forEach(facet => {
            if (facet.facetField === 'userId') {
              this.$set(this.userFacet, 'values', facet.values);
            } else if (facet.facetField === 'status') {
              this.setStatusFacetValues(facet.values);
            }
          });
        } catch (err) {
          this.setStatusFacetValues([]);
        }
      }, 0);
    }

    setStatusFacetValues(values: FacetValue[]): void {
      const valueMap = new Map<string, FacetValue>(DEFAULT_STATUS_FACET_VALUES);

      values.forEach(val => {
        valueMap.get(val.key).value = val.value;
      });

      this.$set(this.statusFacet, 'values', [...valueMap.values()]);
    }

    clearSearch(): void {
      this.searchQuery = '';
      (<DateRangePicker>this.$refs.rangePicker).clear();
      (<FacetSelector>this.$refs.statusFacetSelector).clear();
      (<FacetSelector>this.$refs.userFacetSelector).clear();
    }

    pageChanged(page: Page): void {
      this.currentPage = page;
      this.notifySearch();
    }

    timeRangeChanged(timeRange: Range): void {
      this.timeRange = timeRange;
      this.notifySearch();
    }

    facetRemoved(field: string): void {
      if (this.facets[field]) {
        delete this.facets[field];
        this.notifySearch();
      }
    }

    facetChanged(searchFacet: SearchFacet): void {
      this.facets[searchFacet.field] = searchFacet;
      this.notifySearch();
    }

    searchQueryEnter(searchQuery: string): void {
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

    killQueries(queries: Query[]): void {
      this.$emit('kill-queries', queries);
    }
  }
</script>

<style lang="scss" scoped>
  @import '../../../../../../components/styles/colors';

  .query-table {
    .query-table-actions {
      margin-bottom: 20px;
      width: 100%;

      /deep/ button {
        margin-left: 10px;
      }

      .query-table-filters {
        display: inline-block;
        margin-left: 30px;

        .columns-link,
        .clear-link {
          margin-left: 30px;
        }
      }

      .query-table-actions-right {
        float: right;
        display: inline-block;
      }
    }

    .query-table-container {
      display: flex;
      flex-direction: row;

      .query-table-left-panel {
        flex: 0 0 100px;
      }

      .query-table-right-panel {
        flex: 1 1 100%;
        max-width: 100%;
      }
    }

    .status-indicator {
      font-size: 24px;
      margin: 4px;

      /deep/ i {
        font-size: 20px;
        padding: 2px;
        color: $fluid-gray-500;
      }
    }
  }
</style>
