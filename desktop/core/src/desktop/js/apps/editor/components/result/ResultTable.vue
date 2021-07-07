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
      :columns="columns"
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
    <div v-else-if="isFailed">
      <h1 class="empty">{{ I18n('Execution failed!') }}</h1>
    </div>
    <div v-else-if="hasEmptyResult">
      <h1 class="empty">{{ I18n('Empty result.') }}</h1>
    </div>
    <div v-else-if="isWaitingForStream">
      <h1 class="empty">{{ I18n('Waiting for streaming data...') }}</h1>
    </div>
    <div v-else-if="!rows.length && (!executable || !executable.result)">
      <h1 class="empty">{{ I18n('Select and execute a query to see the result.') }}</h1>
    </div>
  </div>
</template>

<script lang="ts">
  import { computed, defineComponent, PropType, ref, toRefs, watch } from 'vue';

  import './ResultTable.scss';
  import {
    EXECUTABLE_RESULT_UPDATED_TOPIC,
    EXECUTABLE_UPDATED_TOPIC,
    ExecutableResultUpdatedEvent,
    ExecutableUpdatedEvent
  } from 'apps/editor/execution/events';
  import SqlExecutable, { ExecutionStatus } from 'apps/editor/execution/sqlExecutable';
  import ExecutionResult, { ResultRow, ResultType } from 'apps/editor/execution/executionResult';
  import { Column } from 'components/HueTable';
  import HueTable from 'components/HueTable.vue';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import defer from 'utils/timing/defer';
  import I18n from 'utils/i18n';

  export default defineComponent({
    name: 'ResultTable',
    components: {
      HueTable
    },
    props: {
      executable: {
        type: Object as PropType<SqlExecutable | undefined>,
        default: undefined
      }
    },
    setup(props) {
      const { executable } = toRefs(props);
      const subTracker = new SubscriptionTracker();
      const grayedOut = ref(false);
      const fetchedOnce = ref(false);
      const hasResultSet = ref(false);
      const streaming = ref(false);
      const hasMore = ref(false);

      const rows = ref<ResultRow[]>([]);
      const columns = ref<Column<ResultRow>[]>([]);

      const lastRenderedResult = ref<ExecutionResult | null>(null);
      const status = ref<ExecutionStatus | null>(null);
      const type = ref(ResultType.Table);

      const hasEmptyResult = computed<boolean>(
        () =>
          !rows.value.length &&
          hasResultSet.value &&
          status.value === ExecutionStatus.available &&
          fetchedOnce.value
      );

      const hasEmptySuccessResult = computed<boolean>(
        () =>
          !rows.value.length &&
          !hasResultSet.value &&
          status.value === ExecutionStatus.available &&
          fetchedOnce.value
      );

      const isExecuting = computed<boolean>(() => status.value === ExecutionStatus.running);

      const isExpired = computed<boolean>(
        () => !rows.value.length && status.value === ExecutionStatus.expired
      );

      const isFailed = computed<boolean>(
        () => !rows.value.length && status.value === ExecutionStatus.failed
      );

      const isWaitingForStream = computed<boolean>(
        () => !rows.value.length && streaming.value && status.value !== ExecutionStatus.running
      );

      const resetResultData = (): void => {
        type.value = ResultType.Table;

        fetchedOnce.value = false;
        streaming.value = false;
        hasMore.value = false;

        rows.value = [];
        columns.value = [];
      };

      const updateFromExecutable = (executable: SqlExecutable): void => {
        status.value = executable.status;
        hasResultSet.value = !!(executable.handle && executable.handle.has_result_set);
        if (!hasResultSet.value) {
          resetResultData();
        }
      };

      const updateFromExecutionResult = (
        executionResult: ExecutionResult,
        refresh?: boolean
      ): void => {
        if (refresh) {
          resetResultData();
        }

        if (executionResult) {
          fetchedOnce.value = executionResult.fetchedOnce;
          hasMore.value = executionResult.hasMore;
          type.value = executionResult.type || ResultType.Table;
          streaming.value = executionResult.streaming;

          if (!columns.value.length && executionResult.meta.length) {
            columns.value = executionResult.meta.map(({ name }, index) => ({
              label: name,
              key: index,
              htmlValue: true
            }));
          }

          const addRows = (existingRows: ResultRow[], newRows: ResultRow[]) => {
            newRows.forEach(row => {
              if (streaming.value) {
                existingRows.unshift(row);
              } else {
                existingRows.push(row);
              }
            });
          };

          if (refresh) {
            const existingRows: ResultRow[] = [];
            addRows(existingRows, executionResult.rows);
            rows.value = existingRows;
          } else if (
            executionResult.lastRows.length &&
            rows.value.length !== executionResult.rows.length
          ) {
            addRows(rows.value, executionResult.lastRows);
          }
        }
      };

      const handleResultChange = (): void => {
        const result = executable.value?.result;
        if (result) {
          const refresh = lastRenderedResult.value !== executable.value.result;
          updateFromExecutionResult(result as ExecutionResult, refresh);
          lastRenderedResult.value = result;
        } else {
          resetResultData();
        }
      };

      const onScrollToEnd = async (): Promise<void> => {
        if (streaming.value) {
          return;
        }
        if (hasMore.value && !grayedOut.value && executable.value?.result) {
          grayedOut.value = true;
          try {
            await executable.value.result.fetchRows({ rows: 100 });
          } catch (e) {}
          defer(() => {
            // Allow executable events to finish before enabling the result scroll again
            grayedOut.value = false;
          });
        }
      };

      watch(executable, handleResultChange);

      subTracker.subscribe<ExecutableUpdatedEvent>(EXECUTABLE_UPDATED_TOPIC, updatedExecutable => {
        if (executable.value?.id === updatedExecutable.id) {
          updateFromExecutable(updatedExecutable);
        }
      });

      subTracker.subscribe<ExecutableResultUpdatedEvent>(
        EXECUTABLE_RESULT_UPDATED_TOPIC,
        (executionResult: ExecutionResult) => {
          if (executable.value?.id === executionResult.executable.id) {
            handleResultChange();
          }
        }
      );

      return {
        I18n,
        columns,
        grayedOut,
        hasEmptyResult,
        hasEmptySuccessResult,
        isExecuting,
        isExpired,
        isFailed,
        isWaitingForStream,
        onScrollToEnd,
        rows,
        subTracker
      };
    }
  });
</script>
