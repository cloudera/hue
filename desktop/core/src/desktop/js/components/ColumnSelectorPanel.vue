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
  <div>
    Columns <i class="fa fa-times" title="Close" @click="$emit('close')" />
    <ul class="column-list">
      <li>
        <input v-model="filterText" type="text" class="filter-box" placeholder="Filter" />
      </li>
      <li v-for="selectableColumn in filteredColumns" :key="selectableColumn.column.key">
        <label>
          <input v-model="selectableColumn.checked" type="checkbox" />
          {{ selectableColumn.column.label }}
        </label>
      </li>
    </ul>

    <div class="buttons">
      <button type="button" class="btn btn-default" @click="apply">
        Apply
      </button>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import { Column } from 'components/HueTable';

  interface SelectableColumn {
    column: Column;
    checked: boolean;
  }

  @Component
  export default class ColumnSelectorPanel extends Vue {
    @Prop({ required: true })
    columns!: Column[];
    @Prop({ required: true })
    visibleColumns!: Column[];

    get selectableColumns(): SelectableColumn[] {
      const visibleColsSet = new Set<Column>(this.visibleColumns);
      return this.columns.map(column => ({ column, checked: visibleColsSet.has(column) }));
    }

    filterText = '';

    get filteredColumns(): SelectableColumn[] {
      if (!this.filterText) {
        return this.selectableColumns;
      }
      const lowerFilter = this.filterText.toLowerCase();
      return this.selectableColumns.filter(
        col => col.column.label.toLowerCase().indexOf(lowerFilter) !== -1
      );
    }

    apply(): void {
      this.$emit(
        'update:visible-columns',
        this.selectableColumns
          .filter(selectable => selectable.checked)
          .map(selectable => selectable.column)
      );
    }
  }
</script>

<style lang="scss" scoped></style>
