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
  ></query-table>
  <query-details v-else-if="selectedQuery" :query="selectedQuery"></query-details>
  <query-diff v-else :queries="queriesToDiff"></query-diff>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Column } from '../../../../../desktop/core/src/desktop/js/components/HueTable';
  import QueryDiff from './queryDiff/QueryDiff.vue';
  import QueryDetails from './queryDetails/QueryDetails.vue';
  import { Query } from './index';
  import QueryTable from './queryTable/QueryTable.vue';

  @Component({
    components: { QueryDiff, QueryDetails, QueryTable }
  })
  export default class HiveQuerySearch extends Vue {
    selectedQuery?: Query;
    queriesToDiff?: Query[];

    queries: Query[] = [];
    columns: Column[] = []; // TODO: Move to QueryTable?

    showTable() {
      this.selectedQuery = undefined;
      this.queriesToDiff = undefined;
    }

    diffQueries(queries: Query[]) {
      this.queriesToDiff = queries;
    }

    querySelected(query: Query) {
      this.selectedQuery = query;
    }
  }
</script>

<style lang="scss" scoped>
</style>
