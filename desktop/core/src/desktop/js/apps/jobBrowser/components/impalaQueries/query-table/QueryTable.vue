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
  <div class="impala-query-table">
    <div class="query-table-actions">
      <search-input
        v-model="searchText"
        :placeholder="I18n('Query text or Query ID')"
        :show-magnify="false"
        @search="searchQueries"
      />
      <hue-button @click="searchQueries">
        <i class="fa fa-search" />
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
      </div>

      <div class="query-table-sort">
        <hue-icon type="hi-sort" /> {{ I18n('Sort by') }}:
        <sort-selector :sort="sort" :columns="columns" @sort-changed="sortChanged" />
        <hue-button class="clear-link" borderless @click="clearSearch">
          {{ I18n('Clear All') }}
        </hue-button>
      </div>

      <div class="query-table-actions-right">
        <hue-button :disabled="selectedQueries.length !== 2" @click="diffQueries(selectedQueries)">
          {{ I18n('Compare') }}
        </hue-button>
        <hue-button @click="searchQueries">
          <em class="fa fa-refresh" />
          {{ I18n('Refresh') }}
          <span class="update-time">
            {{ getUpdateTimeText(updateTime) }}
          </span>
        </hue-button>
      </div>
    </div>
    <div class="query-table-container">
      <div class="query-table-right-panel">
        <hue-table :columns="columns" :rows="queries">
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
              {{ query.queryText }}
              <div class="query-popup">{{ query.queryText }}</div>
            </hue-link>
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

  import { DataProcessor, ImpalaQuery, TableDefinition } from '../index';
  import { Range } from 'components/DateRangePicker';
  import DateRangePicker from 'components/DateRangePicker.vue';
  import { duration } from 'components/Duration.vue';
  import { Facet, FacetValue, FacetValueLabels, SearchFacet } from 'components/FacetSelector';
  import FacetSelector from 'components/FacetSelector.vue';
  import SortSelector from './SortSelector.vue';
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
  import { SortInfo } from '../ImpalaQueries.vue';

  const STATUS_FACET_VALUES: FacetValue[] = [
    { key: 'FINISHED', value: 0 },
    { key: 'EXCEPTION', value: 0 }
  ];
  const STATUS_LABELS: FacetValueLabels = {
    FINISHED: I18n('Finished'),
    EXCEPTION: I18n('Exception'),
    COMPILED: I18n('Compiled')
  };

  const DEFAULT_SORT: SortInfo = {
    column: 'startTime',
    order: 'DESC'
  };

  export default defineComponent({
    name: 'QueryTable',
    components: {
      FacetSelector,
      SortSelector,
      HueIcon,
      DateRangePicker,
      StatusIndicator,
      SearchInput,
      HueButton,
      HueLink,
      HueTable,
      Paginator
    },
    props: {
      queries: {
        type: Array as PropType<ImpalaQuery[]>,
        required: true
      },
      totalQueries: {
        type: Number,
        required: true
      },
      updateTime: {
        type: Number,
        required: true
      }
    },
    emits: ['diff-queries', 'kill-queries', 'query-selected', 'reload', 'search'],
    setup() {
      const columns: Column<ImpalaQuery>[] = [
        { key: 'select', label: '' },
        { key: 'status', label: 'Status' },
        { key: 'query', label: 'Query' },
        { key: 'queryType', label: 'Query Type' },
        {
          key: 'startTime',
          label: 'Start Time',
          adapter: (_, query) => timeAgo(query.startTime)
        },
        {
          key: 'endTime',
          label: 'End Time',
          adapter: (_, query) => timeAgo(query.endTime)
        },
        {
          key: 'duration',
          label: 'Duration',
          adapter: (_, query) => duration(query.duration)
        },

        { key: 'userName', label: 'User' },
        { key: 'defaultDb', label: 'Default DB' },
        { key: 'requestPool', label: 'Request Pool' },

        {
          key: 'cpuTime',
          label: 'CPU Time',
          adapter: (_, query) => duration(query.cpuTime)
        },
        { key: 'rowsProduced', label: 'Rows Produced' },
        {
          key: 'peakMemory',
          label: 'Peak Memory',
          adapter: (_, query) => humanSize(query.peakMemory)
        },
        {
          key: 'hdfsBytesRead',
          label: 'HDFS Bytes Read',
          adapter: (_, query) => humanSize(query.hdfsBytesRead)
        },
        { key: 'coordinator', label: 'Coordinator' }
      ];

      return { columns, statusValueLabels: STATUS_LABELS, notifyThrottle: -1 };
    },
    data() {
      return {
        selectedQueries: [] as ImpalaQuery[],
        currentPage: null as Page | null,
        searchText: '',
        sort: DEFAULT_SORT,
        timeRange: null as Range | null,
        facets: {} as { [field: string]: SearchFacet },
        statusFacet: {
          facetField: 'status',
          values: STATUS_FACET_VALUES
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
    methods: {
      getUpdateTimeText(time: number): string {
        return time ? `${I18n('Data updated')} ${timeAgo(time)}` : '';
      },
      clearSearch(): void {
        this.searchText = '';
        this.sort = DEFAULT_SORT;

        (this.$refs.rangePicker as typeof DateRangePicker).clear();
        (this.$refs.statusFacetSelector as typeof FacetSelector).clear();
      },
      diffQueries(queries: ImpalaQuery[]): void {
        this.$emit('diff-queries', queries);
      },
      sortChanged(sort: SortInfo): void {
        this.sort = sort;
        this.notifySearch();
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
      killQueries(queries: ImpalaQuery[]): void {
        this.$emit('kill-queries', queries);
      },
      notifySearch(): void {
        window.clearTimeout(this.notifyThrottle);
        this.notifyThrottle = window.setTimeout(async () => {
          this.$emit('search', {
            page: this.currentPage,
            text: this.searchText,
            timeRange: this.timeRange,
            facets: Object.values(this.facets),
            sort: this.sort
          });
        }, 0);
      },
      pageChanged(page: Page): void {
        this.currentPage = page;
        this.notifySearch();
      },
      querySelected(query: ImpalaQuery): void {
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
          this.currentPage = { offset: 0, pageNumber: 0, limit };
        } else {
          this.notifySearch();
        }
      },
      timeRangeChanged(timeRange: Range): void {
        this.timeRange = timeRange;
        this.notifySearch();
      },
      I18n
    }
  });
</script>

<style lang="scss" scoped>
  @import '../../../../../components/styles/variables.scss';
  @import '../../../../../components/styles/mixins';

  .impala-query-table {
    .query-table-actions {
      margin-bottom: 20px;
      width: 100%;

      ::v-deep(.hue-dropdown-panel button) {
        margin-left: 10px;
      }

      .hue-btn {
        margin-left: 5px;
      }

      .query-table-sort,
      .query-table-filters {
        display: inline-block;
        margin-left: 30px;

        .columns-link,
        .clear-link {
          margin-left: 10px;
        }
      }

      .query-table-actions-right {
        display: inline-block;
        position: absolute;
        right: 44px;

        .update-time {
          display: inline-block;
          position: absolute;
          white-space: nowrap;

          pointer-events: none;

          font-size: 0.7em;
          color: #5a656d;

          top: 30px;
          right: 0px;
        }
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
        color: $fluidx-gray-500;
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
