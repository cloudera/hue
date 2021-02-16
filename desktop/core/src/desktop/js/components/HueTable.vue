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
    <table class="hue-table" :class="{ 'sticky-header': stickyHeader }">
      <caption>
        <!-- Because of Web:TableWithoutCaptionCheck -->
        {{
          caption
        }}
      </caption>
      <thead>
        <tr class="header-row">
          <th
            v-for="(column, colIndex) in columns"
            :key="colIndex"
            :class="cellClass(column.headerCssClass, colIndex)"
            scope="col"
          >
            {{ column.label }}
          </th>
          <!-- To fill the blank space to the right when table width is smaller than available horizontal space -->
          <th class="column-flush" scope="col" />
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, rowIndex) in rows" :key="rowIndex" @click="$emit('row-clicked', row)">
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

  import { Column, Row } from './HueTable';

  export default defineComponent({
    props: {
      rows: {
        type: Object as PropType<Row[]>,
        required: false,
        default: () => []
      },
      columns: {
        type: Object as PropType<Column<unknown>[]>,
        required: false,
        default: () => []
      },
      caption: {
        type: String,
        default: undefined
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
      }
    }
  });
</script>

<style lang="scss" scoped>
  @import './styles/colors';
  @import './styles/mixins';

  .hue-table-container {
    overflow-x: auto;
    width: 100%;
    margin: 0 0 15px 0;

    .hue-table {
      line-height: 14px;
      table-layout: auto;
      border-collapse: separate;

      thead,
      tbody {
        tr {
          height: 40px;

          th,
          td {
            @include nowrap-ellipsis;

            height: 16px;
            max-width: 300px;
            padding: 12px;
            border-bottom: 1px solid $fluid-gray-300;
            text-align: left;

            &.column-flush {
              width: 100%;
            }
          }
        }
      }

      thead {
        tr {
          th {
            background-color: $fluid-white;
            color: $fluid-gray-700;
            font-size: 13px;
            font-weight: 500;
            white-space: nowrap;

            &.sticky-first-col {
              background-color: $fluid-white;
              position: sticky;
              position: -webkit-sticky;
              left: 0;
              z-index: 102;
            }

            .sort-header {
              display: flex;
              cursor: pointer;
              align-items: center;
              letter-spacing: normal;
              outline: 0;
            }
          }
        }
      }

      tbody {
        tr {
          td {
            color: $fluid-gray-900;
            font-size: 14px;

            &.sticky-first-col {
              @include position-sticky;

              background-color: $fluid-white;
              left: 0;
              z-index: 100;
            }

            &:last-of-type {
              padding-right: 8px;
            }
          }
        }
      }

      &.sticky-header {
        thead th {
          @include position-sticky;

          top: 0;
          z-index: 101;

          &.sticky-first-col {
            @include position-sticky;

            top: 0;
          }
        }
      }
    }
  }
</style>
