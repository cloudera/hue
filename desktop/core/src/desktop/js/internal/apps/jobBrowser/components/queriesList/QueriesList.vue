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
  <div class="queries-list">
    <InlineAlert
      v-if="error"
      :type="AlertType.Error"
      :message="error.message"
      :details="error.details"
      show-close="true"
      @close="showQueries"
    />
    <query-table
      v-else-if="!selectedQuery && !queriesToDiff"
      :queries="queries"
      :total-queries="(searchMeta && searchMeta.size) || 0"
      @diff-queries="diffQueries"
      @kill-queries="killQueries"
      @query-selected="querySelected"
      @search="fetch"
    />
    <query-details v-else-if="selectedQuery" :query="selectedQuery" />
    <query-details-diff v-else :queries="queriesToDiff" />
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Provide } from 'vue-property-decorator';
  import { Page } from '../../../../../components/Paginator';
  import hueUtils from '../../../../../utils/hueUtils';
  import HumanByteSize from '../../../../../components/HumanByteSize.vue';
  import TimeAgo from '../../../../../components/TimeAgo.vue';
  import { searchQueries, SearchFacet } from './api-utils/search';
  import { fetchExtendedQuery, kill } from './api-utils/query';
  import QueryDetailsDiff from './query-details/QueryDetailsDiff.vue';
  import QueryDetails from './query-details/QueryDetails.vue';
  import { Query, SearchMeta } from './index';
  import QueryTable from './query-table/QueryTable.vue';
  import InlineAlert from '../../../../../components/InlineAlert.vue';
  import { AlertType } from '../../../../../components/InlineAlert.vue';

  const QUERY_ID_PARAM = 'queryId';

  @Component({
    components: { QueryDetailsDiff, QueryDetails, QueryTable, TimeAgo, HumanByteSize, InlineAlert }
  })
  export default class QueriesList extends Vue {
    selectedQuery: Query | null = null;
    queriesToDiff: Query[] | null = null;
    queries: Query[] = [];
    searchMeta: SearchMeta | null = null;
    error: Error | null = null;

    AlertType = AlertType;

    async fetch(options: {
      page: Page;
      text?: string;
      timeRange?: { from: number; to: number };
      facets: SearchFacet[];
    }): Promise<void> {
      // Initial fetch triggered by the paginator
      const now = Date.now();
      try {
        const searchResponse = await searchQueries({
          endTime: (options.timeRange && options.timeRange.to) || now,
          limit: options.page.limit,
          offset: options.page.offset,
          facets: options.facets,
          text: options.text,
          sortText: 'startTime:DESC',
          startTime: (options.timeRange && options.timeRange.from) || now - 1000 * 60 * 60 * 24 * 7
        });
        this.searchMeta = searchResponse.meta;
        this.queries = searchResponse.queries;
      } catch (error) {
        this.error = error;
      }
    }

    @Provide()
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
    }

    async created(): Promise<void> {
      const urlParams = new URLSearchParams(window.location.search);

      const queryIdValues = [];
      let queryIndex = 0;
      while (urlParams.get(QUERY_ID_PARAM + queryIndex)) {
        queryIdValues.push(urlParams.get(QUERY_ID_PARAM + queryIndex));
        queryIndex++;
      }

      if (queryIdValues.length === 1) {
        await this.querySelected(<Query>{ queryId: queryIdValues[0] });
      } else if (queryIdValues.length > 1) {
        await this.diffQueries(<Query[]>queryIdValues.map(queryId => ({ queryId })));
      }
    }

    async diffQueries(queriesToDiff: Query[]): Promise<void> {
      queriesToDiff.forEach((query, index) => {
        hueUtils.changeURLParameter(QUERY_ID_PARAM + index, query.queryId);
      });
      try {
        const fetchPromises = queriesToDiff.map(query => fetchExtendedQuery(query.queryId));
        this.queriesToDiff = await Promise.all(fetchPromises);
      } catch (error) {
        this.error = error;
      }
    }

    async killQueries(queriesToKill: Query[]): Promise<void> {
      await kill(queriesToKill);
      // TODO: Refresh the queries?
    }

    async querySelected(query: Query): Promise<void> {
      hueUtils.changeURLParameter(QUERY_ID_PARAM + 0, query.queryId);
      try {
        this.selectedQuery = await fetchExtendedQuery(query.queryId);
      } catch (error) {
        this.error = error;
      }
    }
  }
</script>

<style lang="scss" scoped>
  .queries-list {
    margin: 10px;
  }
</style>
