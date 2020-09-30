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
  <table class="hue-table">
    <thead>
      <tr class="header-row">
        <th v-for="(column, colIndex) in columns" :key="colIndex">
          <div class="cell-content">{{ column.label }}</div>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(row, rowIndex) in rows" :key="rowIndex" @click="$emit('row-clicked', row)">
        <td v-for="(column, colIndex) in columns" :key="colIndex">
          <div class="cell-content" :class="{ small: column.small, nowrap: column.noWrap }">
            <slot v-if="hasCellSlot(column)" :name="cellSlotName(column)" v-bind="row" />
            <template v-else>
              {{ column.adapter ? column.adapter(column.key, row) : row[column.key] }}
            </template>
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</template>

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

  .hue-table {
    background: none;
    margin: 0 0 15px 0;
    border-radius: $hue-panel-border-radius;
    border-spacing: 0;
    width: 100%;
    line-height: 14px;
    vertical-align: baseline;

    * {
      box-sizing: border-box;
    }

    thead,
    tbody {
      tr {
        height: auto;
        background: none;

        th,
        td {
          padding: 0;
          border: none;
          text-align: left;
          vertical-align: middle;

          .cell-content {
            min-height: 41px;
            display: flex;
            flex-direction: row;
            align-items: center;
            padding: 5px;
            text-align: left;

            &.nowrap {
              white-space: nowrap;
            }

            &.small {
              font-size: 12px;
            }
          }
        }
      }
    }

    thead {
      tr {
        border-bottom: 1px solid $fluid-gray-300;

        th {
          color: $fluid-gray-700;
          font-size: 12px;
          font-weight: 400;
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
</style>
