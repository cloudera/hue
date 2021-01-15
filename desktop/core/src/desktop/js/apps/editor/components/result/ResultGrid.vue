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
  <div class="result-grid" :class="{ 'grayed-out': grayedOut }">
    <HueTable
      :columns="tableColumns"
      :rows="tableRows"
      :sticky-header="true"
      @scroll-to-end="onScrollToEnd"
    />
  </div>
</template>

<script lang="ts">
  import { ResultMeta } from 'apps/editor/execution/api';
  import { ResultRow } from 'apps/editor/execution/executionResult';
  import { Column, Row } from 'components/HueTable';
  import HueTable from 'components/HueTable.vue';
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop, Watch } from 'vue-property-decorator';

  @Component({
    components: { HueTable }
  })
  export default class ResultGrid extends Vue {
    @Prop()
    rows!: ResultRow[];
    @Prop()
    meta!: ResultMeta[];
    @Prop()
    hasMore!: boolean;

    grayedOut = false;

    get tableColumns(): Column<ResultRow>[] {
      return this.meta.map(({ name }, index) => ({
        label: name,
        key: index,
        htmlValue: true
      }));
    }

    get tableRows(): Row[] {
      return this.rows;
    }

    @Watch('rows')
    @Watch('hasMore')
    resultChanged(): void {
      this.grayedOut = false;
    }

    onScrollToEnd(): void {
      if (this.hasMore) {
        this.grayedOut = true;
        this.$emit('fetch-more');
      }
    }
  }
</script>

<style lang="scss" scoped>
  .result-grid {
    position: relative;
    height: 100%;
    width: 100%;

    &.grayed-out {
      opacity: 0.5;

      /deep/ .hue-table-container {
        overflow: hidden !important;
      }
    }
  }
</style>
