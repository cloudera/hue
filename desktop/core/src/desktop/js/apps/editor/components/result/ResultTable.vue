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
      v-if="rows.length"
      :columns="tableColumns"
      :rows="rows"
      :sticky-header="true"
      :sticky-first-column="true"
      @scroll-to-end="onScrollToEnd"
    />
    <div v-else-if="isExecuting">
      <h1 class="empty"><i class="fa fa-spinner fa-spin" /> {{ I18n('Executing...') }}</h1>
    </div>
    <div v-else-if="hasEmptySuccessResult">
      <h1 class="empty">{{ I18n('Success.') }}</h1>
    </div>
    <div v-else-if="isExpired">
      <h1 class="empty">{{ I18n('Results have expired, rerun the query if needed.') }}</h1>
    </div>
    <div v-else-if="hasEmptyResult">
      <h1 class="empty">{{ I18n('Empty result.') }}</h1>
    </div>
    <div v-else-if="isStreaming">
      <h1 class="empty">{{ I18n('Waiting for streaming data...') }}</h1>
    </div>
    <div v-else-if="!rows.length && (!executable || !executable.result)">
      <h1 class="empty">{{ I18n('Select and execute a query to see the result.') }}</h1>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { ResultMeta } from 'apps/editor/execution/api';
  import Executable, {
    EXECUTABLE_UPDATED_EVENT,
    ExecutionStatus
  } from 'apps/editor/execution/executable';
  import ExecutionResult, {
    RESULT_UPDATED_EVENT,
    ResultRow,
    ResultType
  } from 'apps/editor/execution/executionResult';
  import { Column } from 'components/HueTable';
  import HueTable from 'components/HueTable.vue';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import { defer } from 'utils/hueUtils';
  import I18n from 'utils/i18n';

  export default defineComponent({
    components: {
      HueTable
    },

    props: {
      executable: {
        type: Object as PropType<Executable>,
        required: true
      }
    },

    setup() {
      const subTracker = new SubscriptionTracker();
      return { subTracker };
    },

    data() {
      return {
        grayedOut: false,
        fetchedOnce: false,
        hasResultSet: false,
        streaming: false,
        hasMore: false,
        rows: [] as ResultRow[],
        meta: [] as ResultMeta[],

        status: null as ExecutionStatus | null,
        type: ResultType.Table,
        images: [] as string[],
        lastFetchedRows: [] as ResultRow[],
        lastRenderedResult: null as ExecutionResult | null
      };
    },

    computed: {
      hasEmptyResult(): boolean {
        return (
          !this.rows.length &&
          this.hasResultSet &&
          this.status === ExecutionStatus.available &&
          this.fetchedOnce
        );
      },

      hasEmptySuccessResult(): boolean {
        return (
          !this.rows.length &&
          !this.hasResultSet &&
          this.status === ExecutionStatus.available &&
          this.fetchedOnce
        );
      },

      isExecuting(): boolean {
        return this.status === ExecutionStatus.running;
      },

      isExpired(): boolean {
        return this.status === ExecutionStatus.expired && !this.rows.length;
      },

      isStreaming(): boolean {
        return this.streaming && !this.rows.length && this.status !== ExecutionStatus.running;
      },

      tableColumns(): Column<ResultRow>[] {
        return this.meta.map(({ name }, index) => ({
          label: name,
          key: index,
          htmlValue: true
        }));
      }
    },

    watch: {
      executable(): void {
        this.handleResultChange();
      }
    },

    mounted(): void {
      this.subTracker.subscribe(EXECUTABLE_UPDATED_EVENT, (executable: Executable) => {
        if (this.executable.id === executable.id) {
          this.updateFromExecutable(executable);
        }
      });

      this.subTracker.subscribe(RESULT_UPDATED_EVENT, (executionResult: ExecutionResult) => {
        if (this.executable.id === executionResult.executable.id) {
          this.handleResultChange();
        }
      });
    },

    unmounted(): void {
      this.subTracker.dispose();
    },

    methods: {
      I18n,
      handleResultChange(): void {
        if (this.executable && this.executable.result) {
          const refresh = this.lastRenderedResult !== this.executable.result;
          this.updateFromExecutionResult(this.executable.result, refresh);
          this.lastRenderedResult = this.executable.result;
        } else {
          this.resetResultData();
        }
      },

      async onScrollToEnd(): Promise<void> {
        if (this.hasMore && !this.grayedOut && this.executable && this.executable.result) {
          this.grayedOut = true;
          try {
            await this.executable.result.fetchRows({ rows: 100 });
          } catch (e) {}
          defer(() => {
            // Allow executable events to finish before enabling the result scroll again
            this.grayedOut = false;
          });
        }
      },

      resetResultData(): void {
        this.type = ResultType.Table;

        this.fetchedOnce = false;
        this.streaming = false;
        this.hasMore = false;

        this.images = [];
        this.lastFetchedRows = [];
        this.rows = [];
        this.meta = [];
      },

      updateFromExecutable(executable: Executable): void {
        this.status = executable.status;
        this.hasResultSet = !!(executable.handle && executable.handle.has_result_set);
        if (!this.hasResultSet) {
          this.resetResultData();
        }
      },

      updateFromExecutionResult(executionResult: ExecutionResult, refresh?: boolean): void {
        if (refresh) {
          this.resetResultData();
        }

        if (executionResult) {
          this.fetchedOnce = executionResult.fetchedOnce;
          this.hasMore = executionResult.hasMore;
          this.type = executionResult.type || ResultType.Table;
          this.streaming = executionResult.streaming;

          if (!this.meta.length && executionResult.meta.length) {
            this.meta = executionResult.meta;
          }

          if (refresh) {
            this.rows = [...executionResult.rows];
          } else if (
            executionResult.lastRows.length &&
            this.rows.length !== executionResult.rows.length
          ) {
            this.rows.push(...executionResult.lastRows);
          }
          this.lastFetchedRows = executionResult.lastRows;
        }
      }
    }
  });
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
