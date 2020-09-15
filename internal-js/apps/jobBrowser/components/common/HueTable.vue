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

<!--
  TODO: Decide whether we should have our own or replace with vue-good-table, vue-tables-2, bootstrap-vue etc.
        More at https://awesome-vue.js.org/components-and-libraries/ui-components.html
-->

<template>
  <table>
    <thead>
      <tr>
        <th v-for="(column, colIndex) in columns" :key="colIndex">
          {{ column.label }}>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(row, rowIndex) in rows" :key="rowIndex">
        <td v-for="(column, colIndex) in columns" :key="colIndex">
          {{ column[row.key] }}
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';

  export interface Column {
    label: string;
    key: string;
  }
  export type Row = { [key: string]: unknown };

  @Component
  export default class HueTable extends Vue {
    @Prop({ required: false })
    rows: Row[] = [];
    @Prop({ required: false })
    columns: Column[] = [];
  }
</script>

<style lang="scss" scoped></style>
