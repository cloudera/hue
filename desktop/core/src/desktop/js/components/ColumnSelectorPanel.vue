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
  <div class="column-selector-panel">
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

    <div class="column-selector-actions">
      <hue-button type="button" @click="apply">
        Apply
      </hue-button>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import HueButton from './HueButton.vue';
  import { Column } from 'components/HueTable';

  interface SelectableColumn {
    column: Column<unknown>;
    checked: boolean;
  }

  export default defineComponent({
    components: { HueButton },

    props: {
      columns: {
        type: Object as PropType<Column<unknown>[]>,
        required: true
      },
      visibleColumns: {
        type: Object as PropType<Column<unknown>[]>,
        required: true
      }
    },

    emits: ['update:visible-columns'],

    data(): {
      filterText: string;
    } {
      return {
        filterText: ''
      };
    },

    computed: {
      selectableColumns(): SelectableColumn[] {
        const visibleColsSet = new Set<Column<unknown>>(this.visibleColumns);
        return this.columns.map(column => ({ column, checked: visibleColsSet.has(column) }));
      },

      columnsWithLabels(): SelectableColumn[] {
        return this.selectableColumns.filter(column => column.column.label);
      },

      filteredColumns(): SelectableColumn[] {
        if (!this.filterText) {
          return this.columnsWithLabels;
        }
        const lowerFilter = this.filterText.toLowerCase();
        return this.columnsWithLabels.filter(
          col => col.column.label.toLowerCase().indexOf(lowerFilter) !== -1
        );
      }
    },

    methods: {
      apply(): void {
        this.$emit(
          'update:visible-columns',
          this.selectableColumns
            .filter(selectable => selectable.checked)
            .map(selectable => selectable.column)
        );
      }
    }
  });
</script>

<style lang="scss" scoped>
  .column-selector-panel {
    padding: 15px;

    ul {
      list-style: none;
      margin: 0;
    }

    .column-selector-actions {
      margin-top: 10px;
      text-align: right;
    }
  }
</style>
