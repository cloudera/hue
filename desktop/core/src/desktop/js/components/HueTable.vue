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

<!-- eslint-disable vue/no-v-html -->
<template>
  <div ref="tableContainer" class="hue-table-container" @scroll="onContainerScroll">
    <table
      class="hue-table"
      :class="{ 'sticky-header': stickyHeader && showHeader, 'header-less': !showHeader }"
    >
      <caption>
        <!-- Because of Web:TableWithoutCaptionCheck -->
        {{
          caption
        }}
      </caption>
      <thead v-if="showHeader">
        <tr class="header-row">
          <th
            v-for="(column, colIndex) in columns"
            :key="colIndex"
            :class="cellClass(column.headerCssClass, colIndex)"
            scope="col"
          >
            {{ typeof column.label !== 'undefined' ? column.label : column.key }}
          </th>
          <!-- To fill the blank space to the right when table width is smaller than available horizontal space -->
          <th class="column-flush" scope="col" />
        </tr>
      </thead>
      <tbody :class="{ 'clickable-rows': clickableRows }">
        <tr v-for="(row, rowIndex) in rows" :key="rowIndex" @click="onRowClick(row)">
          <td
            v-for="(column, colIndex) in columns"
            :key="colIndex"
            :class="cellClass(column.cssClass, colIndex)"
          >
            <slot v-if="hasCellSlot(column)" :name="cellSlotName(column)" v-bind="row" />
            <div v-else-if="column.htmlValue" v-html="row[column.key]" />
            <template v-else>
              {{ column.adapter ? column.adapter(column.key, row) : row[column.key] }}
            </template>
          </td>
          <td class="column-flush" />
        </tr>
      </tbody>
    </table>
  </div>
</template>
<!-- eslint-enable vue/no-v-html -->

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import './HueTable.scss';
  import { Column, Row } from './HueTable';

  export default defineComponent({
    name: 'HueTable',
    props: {
      rows: {
        type: Array as PropType<Row[]>,
        required: false,
        default: () => []
      },
      columns: {
        type: Array as PropType<Column<unknown>[]>,
        required: false,
        default: () => []
      },
      caption: {
        type: String,
        default: undefined
      },
      showHeader: {
        type: Boolean,
        required: false,
        default: true
      },
      stickyHeader: {
        type: Boolean,
        required: false,
        default: false
      },
      stickyFirstColumn: {
        type: Boolean,
        required: false,
        default: false
      },
      clickableRows: {
        type: Boolean,
        default: false
      }
    },

    emits: ['scroll-to-end', 'row-clicked'],

    methods: {
      hasCellSlot(column: Column<unknown>): boolean {
        return !!this.$slots[this.cellSlotName(column)];
      },
      cellSlotName(column: Column<unknown>): string {
        return 'cell-' + column.key;
      },
      onContainerScroll(): void {
        const containerEl = <HTMLElement>this.$refs.tableContainer;
        if (containerEl.scrollHeight === containerEl.scrollTop + containerEl.clientHeight) {
          this.$emit('scroll-to-end');
        }
      },
      cellClass(cellClass: string | undefined, index: number): string | null {
        // This prevents rendering of empty class="" for :class="[x,y]" when x and y are undefined
        // Possibly fixed in Vue 3
        if (cellClass && this.stickyFirstColumn && index === 0) {
          return `${cellClass} sticky-first-col`;
        } else if (this.stickyFirstColumn && index === 0) {
          return 'sticky-first-col';
        }
        return cellClass || null;
      },
      onRowClick(row: Row): void {
        if (this.clickableRows) {
          this.$emit('row-clicked', row);
        }
      }
    }
  });
</script>
