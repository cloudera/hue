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
  <ResultGrid :rows="rows" :meta="meta" :has-more="hasMore" @fetch-more="fetchMore" />
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop, Watch } from 'vue-property-decorator';

  import ResultGrid from './ResultGrid.vue';
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
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';

  @Component({
    components: { ResultGrid }
  })
  export default class ExecutionResults extends Vue {
    @Prop()
    executable?: Executable;

    subTracker = new SubscriptionTracker();

    status: ExecutionStatus | null = null;
    type = ResultType.Table;

    fetchedOnce = false;
    hasResultSet = false;
    streaming = false;
    hasMore = false;

    lastRenderedResult?: ExecutionResult;

    images = [];
    lastFetchedRows: ResultRow[] = [];
    rows: ResultRow[] = [];
    meta: ResultMeta[] = [];

    fetchResultThrottle = -1;

    mounted(): void {
      this.subTracker.subscribe(EXECUTABLE_UPDATED_EVENT, (executable: Executable) => {
        if (this.executable === executable) {
          this.updateFromExecutable(executable);
        }
      });

      this.subTracker.subscribe(RESULT_UPDATED_EVENT, (executionResult: ExecutionResult) => {
        if (this.executable === executionResult.executable) {
          this.handleResultChange();
        }
      });
    }

    fetchMore(): void {
      window.clearTimeout(this.fetchResultThrottle);
      this.fetchResultThrottle = window.setTimeout(() => {
        if (this.hasMore && this.executable && this.executable.result) {
          this.executable.result.fetchRows({ rows: 100 });
        }
      }, 100);
    }

    @Watch('executable')
    handleResultChange(): void {
      if (this.executable && this.executable.result) {
        const refresh = this.lastRenderedResult !== this.executable.result;
        this.updateFromExecutionResult(this.executable.result, refresh);
        this.lastRenderedResult = this.executable.result;
      } else {
        this.resetResultData();
      }
    }

    resetResultData(): void {
      this.type = ResultType.Table;

      this.fetchedOnce = false;
      this.streaming = false;
      this.hasMore = false;

      this.images = [];
      this.lastFetchedRows = [];
      this.rows = [];
      this.meta = [];
    }

    updateFromExecutable(executable: Executable): void {
      this.status = executable.status;
      this.hasResultSet = !!(executable.handle && executable.handle.has_result_set);
      if (!this.hasResultSet) {
        this.resetResultData();
      }
    }

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
</script>
