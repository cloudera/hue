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
    Columns <i class='fa fa-times' title="Close" @click="$emit('close')"></i>
    <ul class='column-list'>
      <li>
        <input type="text" class="filter-box" v-model="filterText" placeholder="Filter">
      </li>
      <template v-for="column in filteredColumns">
        <li :key="column.key">
          <label><input type="checkbox" :value="column" v-model="checkedColumns">{{ column.label }}</label>
        </li>
      </template>
    </ul>

    <div class="buttons">
      <button type="button" class="btn btn-default" @click="$emit('set-checked-columns', checkedColumns)">Apply</button>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import { Column } from 'components/HueTable';

  @Component
  export default class ColumnSelectorPanel extends Vue {
    @Prop({ required: true })
    columns!: Column[];

    checkedColumns: Column[] = [];
    filterText = '';

    mounted() {
      this.checkedColumns.push(...this.columns);
    }

    get filteredColumns(): Column[] {
      if (!this.filterText) {
        return this.columns;
      }
      const lowerFilter = this.filterText.toLowerCase();
      return this.columns.filter(col => col.label.toLowerCase().indexOf(lowerFilter) !== -1)
    }
  }
</script>

<style lang="scss" scoped>
</style>
