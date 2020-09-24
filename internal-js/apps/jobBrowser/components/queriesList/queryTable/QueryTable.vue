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
  import { Prop } from 'vue-property-decorator';
  import HueTable from '../../../../../../desktop/core/src/desktop/js/components/HueTable.vue';
  import { Column } from '../../../../../../desktop/core/src/desktop/js/components/HueTable';
  import ColumnSelectorPanel from '../../../../../../desktop/core/src/desktop/js/components/ColumnSelectorPanel.vue';
  import { fetchSuggestedSearches } from '../apiUtils';
  import QueriesSearch from '../components/QueriesSearch.vue';
  import { DataProcessor, Query, Search, TableDefinition } from '../index';

  @Component({
    components: { HueTable, ColumnSelectorPanel, QueriesSearch }
  })
  export default class QueryTable extends Vue {
    @Prop({ required: true })
    columns!: Column[];
    @Prop({ required: true })
    queries!: Query[];

    searches: Search[] = [];
    visibleColumns: Column[] = [];
    columnSelectorIsVisible = false;

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

    updateVisibleColumns(columns: Column[]): void {
      this.visibleColumns = columns;
      this.columnSelectorIsVisible = false;
    }

    toggleColumnSelector(): void {
      this.columnSelectorIsVisible = !this.columnSelectorIsVisible;
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
