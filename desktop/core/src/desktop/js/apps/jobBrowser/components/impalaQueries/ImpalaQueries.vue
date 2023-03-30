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
  <div class="impala-queries">
    <Spinner v-if="loading" size="xlarge" :center="true" :overlay="true" />
    <InlineAlert
      v-if="error"
      :type="AlertType.Error"
      :message="error.message"
      :details="error.details"
      :show-close="true"
      @close="showQueries"
    />

    <query-details
      v-else-if="selectedQuery"
      :query="selectedQuery"
      @reload="selectedQuery && querySelected(selectedQuery)"
    />
    <query-details-diff v-else-if="queriesToDiff" :queries="queriesToDiff" />
    <query-table
      v-else
      :queries="queries"
      :total-queries="(searchMeta && searchMeta.size) || 0"
      :update-time="(searchMeta && searchMeta.updateTime) || 0"
      @diff-queries="diffQueries"
      @query-selected="querySelected"
      @reload="lastFetchOptions && fetch(lastFetchOptions)"
      @search="fetch"
    />
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  import hueUtils from 'utils/hueUtils';
  import { SearchFacet, SearchMeta } from '../../commons/api-utils/search';
  import QueryDetailsDiff from './query-details/QueryDetailsDiff.vue';
  import QueryDetails from './query-details/QueryDetails.vue';
  import QueryTable from './query-table/QueryTable.vue';
  import { ImpalaQuery } from './index';
  import InlineAlert, { AlertType } from 'components/InlineAlert.vue';
  import { Page } from 'components/Paginator';
  import Spinner from 'components/Spinner.vue';
  import { ApiError } from '../../commons/api-utils/api';
  import { loadQuery, searchQueries } from './api/query';

  const QUERY_ID_PARAM = 'queryId';
  const DEFAULT_TIME_WINDOW = 1000 * 60 * 60 * 24 * 7; // 7 days

  export type SortInfo = { column: string; order: 'ASC' | 'DESC' };

  interface FetchOptions {
    page: Page;
    text?: string;
    timeRange?: { from: number; to: number };
    facets: SearchFacet[];
    sort: SortInfo;
  }

  // TODO: Have one single implimentation for Hive & Impala
  export default defineComponent({
    name: 'ImpalaQueries',
    components: {
      InlineAlert,
      QueryDetails,
      QueryDetailsDiff,
      QueryTable,
      Spinner
    },
    provide() {
      return {
        showQueries: () => this.showQueries()
      };
    },
    data() {
      return {
        AlertType: AlertType,
        error: null as ApiError | null,
        lastFetchOptions: null as FetchOptions | null,
        loading: false,
        queries: [] as ImpalaQuery[],
        queriesToDiff: null as ImpalaQuery[] | null,
        searchMeta: null as SearchMeta | null,
        selectedQuery: null as ImpalaQuery | null
      };
    },
    async created(): Promise<void> {
      const urlParams = new URLSearchParams(window.location.search);

      const queryIdValues = [];
      let queryIndex = 0;
      while (urlParams.get(QUERY_ID_PARAM + queryIndex)) {
        queryIdValues.push(urlParams.get(QUERY_ID_PARAM + queryIndex));
        queryIndex++;
      }

      if (queryIdValues.length === 1) {
        await this.querySelected(<ImpalaQuery>{ queryId: queryIdValues[0] });
      } else if (queryIdValues.length > 1) {
        await this.diffQueries(<ImpalaQuery[]>queryIdValues.map(queryId => ({ queryId })));
      }
    },
    methods: {
      showQueries(): void {
        this.selectedQuery = null;
        this.queriesToDiff = null;
        this.error = null;

        const urlParams = new URLSearchParams(window.location.search);
        let index = 0;
        while (urlParams.get(QUERY_ID_PARAM + index)) {
          hueUtils.removeURLParameter(QUERY_ID_PARAM + index);
          index++;
        }
      },

      async fetch(options: FetchOptions): Promise<void> {
        // Initial fetch triggered by the paginator
        const now = Date.now();

        this.lastFetchOptions = options;
        this.loading = true;
        try {
          const searchResponse = await searchQueries<ImpalaQuery>({
            endTime: (options.timeRange && options.timeRange.to) || now,
            limit: options.page.limit,
            offset: options.page.offset,
            facets: options.facets,
            text: options.text,
            sortText: `${options.sort.column}:${options.sort.order}`,
            startTime: (options.timeRange && options.timeRange.from) || now - DEFAULT_TIME_WINDOW
          });
          this.searchMeta = searchResponse.meta;
          this.queries = searchResponse.queries;
        } catch (error) {
          this.error = new ApiError(String(error));
        }
        this.loading = false;
      },
      async diffQueries(queriesToDiff: ImpalaQuery[]): Promise<void> {
        queriesToDiff.forEach((query, index) => {
          hueUtils.changeURLParameter(QUERY_ID_PARAM + index, query.queryId);
        });
        this.loading = true;
        try {
          const fetchPromises = queriesToDiff.map(query => loadQuery(query.queryId));
          this.queriesToDiff = await Promise.all(fetchPromises);
        } catch (error) {
          this.error = new ApiError(String(error));
        }
        this.loading = false;
      },
      async querySelected(query: ImpalaQuery): Promise<void> {
        hueUtils.changeURLParameter(QUERY_ID_PARAM + 0, query.queryId);
        this.loading = true;
        try {
          this.selectedQuery = await loadQuery(query.queryId);
        } catch (error) {
          this.error = new ApiError(String(error));
        }
        this.loading = false;
      }
    }
  });
</script>

<style lang="scss" scoped>
  .impala-queries {
    margin: 11px;
  }
</style>
