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
  <div class="table-component">
    <queries-search :searches="searches" :table-definition="tableDefinition"></queries-search>
    <div class="left-panel">
      <div v-if="!columnSelectorIsVisible" class="refine-header">
        Refine
        <i v-if="!dataProcessor.facets.fieldCount" class="fa fa-spinner fa-pulse fa-fw"></i>
        <i class='fa fa-plus' title="Customize" @click="showColumnSelector"></i>
      </div>
      <!-- {{em-table-facet-panel tableDefinition=definition dataProcessor=dataProcessor}} -->
      <!-- if columnSelectorIsVisible (v-else) ... -->
      <!-- {{column-selector-panel tableDefinition=definition dataProcessor=dataProcessor columnPrefDef=columnPrefDef}}-->
    </div>
    <div class="table">
      <!-- {{em-table
        title=title

        rows=rows
        rowCount=rowCount

        classNames=classNames

        headerComponentNames=headerComponentNames
        footerComponentNames=footerComponentNames

        leftPanelComponentName=""

        enableSort=enableSort
        enableSearch=enableSearch
        enableFaceting=enableFaceting

        definition=definition
        dataProcessor=dataProcessor

        columnWidthChangeAction="columnWidthChanged"
        scrollChangeAction="scrollChange"

        showScrollShadow=true

        rowAction=rowAction
      }} -->
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Emit } from 'vue-property-decorator';
  import { fetchSuggestedSearches } from '../apiUtils';
  import QueriesSearch from '../components/QueriesSearch.vue';
  import {Query, Search, TableDefinition} from '../index';

  interface DataProcessor {
    facets: {
      fieldCount?: number;
    }
  }

  @Component({
    components: { QueriesSearch }
  })
  export default class QueryTable extends Vue {
    searches: Search[] = [];
    // TODO: Properly initiate TableDefinition
    tableDefinition: TableDefinition = {
      rangeData: {
        title: 'Some title'
      }
    }
    // TODO: Properly initiate DataProcessor
    dataProcessor: DataProcessor = {
      facets: { fieldCount: 0 }
    };


    columnSelectorIsVisible = false;

    async created() {
      this.searches = await fetchSuggestedSearches({ entityType: 'query' });
    }

    showColumnSelector() {
      this.columnSelectorIsVisible = true;
    }

    @Emit('query-selected')
    querySelected(query: Query) {
    }

    @Emit('diff-queries')
    diffQueries(queries: Query[]) {

    }
  }
</script>

<style lang="scss" scoped>
</style>
