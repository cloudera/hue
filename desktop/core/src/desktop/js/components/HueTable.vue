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
  <div class="hue-table-container">
    <table class="hue-table">
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
            :class="column.headerCssClass"
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
          <td v-for="(column, colIndex) in columns" :key="colIndex" :class="column.cssClass">
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
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import { Column, Row } from './HueTable';

  @Component
  export default class HueTable<T> extends Vue {
    @Prop({ required: false, default: () => [] })
    rows?: Row[];
    @Prop({ required: false, default: () => [] })
    columns?: Column<T>[];
    @Prop()
    caption?: string;

    hasCellSlot(column: Column<T>): boolean {
      return !!this.$scopedSlots[this.cellSlotName(column)];
    }

    cellSlotName(column: Column<T>): string {
      return 'cell-' + column.key;
    }
  }
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

      thead,
      tbody {
        tr {
          height: 40px;

          th,
          td {
            @include nowrap-ellipsis;

            padding: 12px;
            border: none;
            text-align: left;
            height: 16px;
            max-width: 300px;

            &.column-flush {
              width: 100%;
            }
          }
        }
      }

      thead {
        tr {
          border-bottom: 1px solid $fluid-gray-300;

          th {
            color: $fluid-gray-700;
            font-size: 13px;
            font-weight: 500;
            white-space: nowrap;

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
          border-bottom: 1px solid $fluid-gray-200;

          td {
            color: $fluid-gray-900;
            font-size: 14px;

            &:last-of-type {
              padding-right: 8px;
            }
          }
        }
      }
    }
  }
</style>
