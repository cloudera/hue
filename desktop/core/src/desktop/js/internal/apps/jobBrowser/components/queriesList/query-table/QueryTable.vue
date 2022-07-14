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
      <search-input
        v-model="searchText"
        :placeholder="I18n('Query text or Query/DAG/App ID')"
        :show-magnify="false"
        @search="searchQueries"
      />
      <hue-button @click="searchQueries">
        <em class="fa fa-search" />
      </hue-button>

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
        <QueryKillButton :queries="selectedQueries" @killed="reload()" />
        <hue-button @click="searchQueries">
          {{ I18n('Refresh') }}
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
            <status-indicator
              :title="query.status"
              class="status-indicator"
              :value="query.status"
            />
          </template>
          <template #cell-select="query">
            <input v-model="selectedQueries" type="checkbox" :value="query" />
          </template>
          <template #cell-query="query">
            <hue-link class="query-link" @click="querySelected(query)">
              {{ query.query }}
              <div class="query-popup">{{ query.query }}</div>
            </hue-link>
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
  import { defineComponent, PropType } from 'vue';

  import { fetchFacets } from '../api-utils/search';
  import { DataProcessor, Query, Search, TableDefinition } from '../index';
  import QueryKillButton from '../components/QueryKillButton.vue';
  import TablesList from '../components/TablesList.vue';
  import ColumnSelectorPanel from 'components/ColumnSelectorPanel.vue';
  import { Range } from 'components/DateRangePicker';
  import DateRangePicker from 'components/DateRangePicker.vue';
  import { duration } from 'components/Duration.vue';
  import { Facet, FacetValue, FacetValueLabels, SearchFacet } from 'components/FacetSelector';
  import FacetSelector from 'components/FacetSelector.vue';
  import HueButton from 'components/HueButton.vue';
  import HueIcon from 'components/HueIcon.vue';
  import HueLink from 'components/HueLink.vue';
  import HueTable from 'components/HueTable.vue';
  import { Column } from 'components/HueTable';
  import { humanSize } from 'components/HumanByteSize.vue';
  import Paginator, { Page } from 'components/Paginator';
  import SearchInput from 'components/SearchInput.vue';
  import StatusIndicator from 'components/StatusIndicator.vue';
  import { timeAgo } from 'components/TimeAgo.vue';
  import I18n from 'utils/i18n';

  const DEFAULT_STATUS_FACET_VALUES: Map<string, FacetValue> = new Map<string, FacetValue>([
    ['STARTED', { key: 'STARTED', value: 0 }],
    ['RUNNING', { key: 'RUNNING', value: 0 }],
    ['SUCCESS', { key: 'SUCCESS', value: 0 }],
    ['ERROR', { key: 'ERROR', value: 0 }]
  ]);

  export default defineComponent({
    name: 'QueryTable',
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
      QueryKillButton,
      Paginator
    },
    props: {
      queries: {
        type: Array as PropType<Query[]>,
        required: true
      },
      totalQueries: {
        type: Number,
        required: true
      }
    },
    emits: ['diff-queries', 'kill-queries', 'query-selected', 'reload', 'search'],
    setup() {
      const statusValueLabels: FacetValueLabels = {
        STARTED: I18n('Started'),
        RUNNING: I18n('Running'),
        SUCCESS: I18n('Success'),
        ERROR: I18n('Error')
      };

      const columns: Column<Query>[] = [
        { key: 'select', label: '' },
        { key: 'status', label: 'Status' },
        { key: 'query', label: 'Query' },
        { key: 'queueName', label: 'Queue' },
        { key: 'requestUser', label: 'User' },
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
          adapter: (ke, query) => timeAgo(query.startTime)
        },
        {
          key: 'elapsedTime',
          label: 'Duration',
          adapter: (key, query) => (query.elapsedTime && duration(query.elapsedTime)) || ''
        },
        {
          key: 'dagIDs',
          label: 'DAG IDs',
          adapter: (key, query) => query.dags.map(dag => dag.dagInfo.dagId).join(',')
        },
        {
          key: 'appID',
          label: 'Application ID',
          adapter: (key, query) => query.dags[0] && query.dags[0].dagInfo.applicationId
        },
        { key: 'cpuTime', label: 'CPU Time' },
        {
          key: 'physicalMemory',
          label: 'Physical Memory',
          adapter: (key, query) => humanSize(query.physicalMemory)
        },
        {
          key: 'virtualMemory',
          label: 'Virtual Memory',
          adapter: (key, query) => humanSize(query.virtualMemory)
        },
        {
          key: 'dataRead',
          label: 'Data Read',
          adapter: (key, query) => humanSize(query.dataRead)
        },
        {
          key: 'dataWritten',
          label: 'Data Written',
          adapter: (key, query) => humanSize(query.dataWritten)
        },
        { key: 'executionMode', label: 'Execution Mode' },
        { key: 'usedCBO', label: 'Cost Based Optimizer (CBO)' }
      ];

      const notifyThrottle = -1;

      return { columns, statusValueLabels, notifyThrottle };
    },
    data() {
      return {
        searches: [] as Search[],
        columnSelectorIsVisible: false,
        visibleColumns: [] as Column<Query>[],
        selectedQueries: [] as Query[],
        currentPage: null as Page | null,
        searchText: '',
        timeRange: null as Range | null,
        facets: {} as { [field: string]: SearchFacet },
        statusFacet: {
          facetField: 'status',
          values: []
        } as Facet,
        userFacet: {
          facetField: 'userId',
          values: []
        } as Facet,
        // TODO: Properly initiate TableDefinition
        tableDefinition: {
          rangeData: {
            title: 'Some title'
          },
          columnPreferences: [{ id: 'some id' }]
        } as TableDefinition,
        // TODO: Properly initiate DataProcessor
        dataProcessor: {
          facets: { fieldCount: 0 }
        } as DataProcessor
      };
    },
    async created(): Promise<void> {
      // this.searches = await fetchSuggestedSearches({ entityType: 'query' });
    },
    mounted(): void {
      this.visibleColumns = [...this.columns];
      this.setStatusFacetValues([]);
    },
    methods: {
      clearSearch(): void {
        this.searchText = '';
        (this.$refs.rangePicker as typeof DateRangePicker).clear();
        (this.$refs.statusFacetSelector as typeof FacetSelector).clear();
      },
      diffQueries(queries: Query[]): void {
        this.$emit('diff-queries', queries);
      },
      facetChanged(searchFacet: SearchFacet): void {
        this.facets[searchFacet.field] = searchFacet;
        this.notifySearch();
      },
      facetRemoved(field: string): void {
        if (this.facets[field]) {
          delete this.facets[field];
          this.notifySearch();
        }
      },
      killQueries(queries: Query[]): void {
        this.$emit('kill-queries', queries);
      },
      notifySearch(): void {
        window.clearTimeout(this.notifyThrottle);
        this.notifyThrottle = window.setTimeout(async () => {
          this.$emit('search', {
            page: this.currentPage,
            text: this.searchText,
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
                this.userFacet.values.splice(0, this.userFacet.values.length, ...facet.values);
              } else if (facet.facetField === 'status') {
                this.setStatusFacetValues(facet.values);
              }
            });
          } catch (err) {
            this.setStatusFacetValues([]);
          }
        }, 0);
      },
      pageChanged(page: Page): void {
        this.currentPage = page;
        this.notifySearch();
      },
      querySelected(query: Query): void {
        this.$emit('query-selected', query);
      },
      reload(): void {
        this.selectedQueries = [];
        this.$emit('reload');
      },
      searchQueries(searchText: string): void {
        if (searchText !== undefined) {
          this.searchText = searchText;
        }

        if (this.currentPage && this.currentPage.offset !== 0) {
          // pageChanged will notify
          const limit = this.currentPage.limit;
          this.currentPage = { offset: 0, limit };
        } else {
          this.notifySearch();
        }
      },
      setStatusFacetValues(values: FacetValue[]): void {
        values.forEach(val => {
          const facet = DEFAULT_STATUS_FACET_VALUES.get(val.key);
          if (facet) {
            facet.value = val.value;
          }
        });

        // For some reason [...valueMap.values()] throws exception
        const facetValues: FacetValue[] = [];
        DEFAULT_STATUS_FACET_VALUES.forEach(val => {
          facetValues.push(val);
        });
        this.statusFacet.values.splice(0, this.statusFacet.values.length, ...facetValues);
      },
      timeRangeChanged(timeRange: Range): void {
        this.timeRange = timeRange;
        this.notifySearch();
      },
      toggleColumnSelector(): void {
        this.columnSelectorIsVisible = !this.columnSelectorIsVisible;
      },
      updateVisibleColumns(columns: Column<Query>[]): void {
        this.visibleColumns = columns;
        this.columnSelectorIsVisible = false;
      },
      I18n
    }
  });
</script>

<style lang="scss" scoped>
  @import '../../../../../../components/styles/colors';
  @import '../../../../../../components/styles/mixins';

  .query-table {
    .query-table-actions {
      margin-bottom: 20px;
      width: 100%;

      ::v-deep(.hue-dropdown-panel button) {
        margin-left: 10px;
      }

      .hue-btn {
        margin-left: 5px;
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

      ::v-deep(i) {
        font-size: 20px;
        padding: 2px;
        color: $fluid-gray-500;
      }
    }

    .query-link {
      .query-popup {
        position: absolute;

        margin-top: 5px;

        white-space: pre-wrap;
        word-break: normal;
        overflow-wrap: break-word;

        pointer-events: none;

        max-width: 1000px;
        background-color: #fff;
        border: 1px solid $hue-border-color;
        border-radius: $hue-panel-border-radius;

        padding: 10px;

        visibility: hidden;
      }

      &:hover {
        .query-popup {
          visibility: visible;
        }
      }
    }
  }
</style>
