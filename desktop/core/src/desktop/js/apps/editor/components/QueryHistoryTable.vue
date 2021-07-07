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
  <div class="query-history-table">
    <ClearQueryHistoryModal
      v-model="clearHistoryModalOpen"
      :connector="connector"
      @history-cleared="refresh"
    />
    <ImportDocumentsModal
      v-model="importHistoryModalOpen"
      :connector="connector"
      :header="I18n('Import Query History')"
      @documents-imported="refresh"
    />
    <div class="query-history-top-bar">
      <div class="query-history-filter">
        <SearchInput v-model="searchFilter" :show-magnify="false" :small="true" />
      </div>
      <div class="query-history-actions">
        <HueButton :small="true" :disabled="!history.length" @click="onClearClick">
          <i class="fa fa-fw fa-calendar-times-o" /> {{ I18n('Clear') }}
        </HueButton>
        <HueButton :small="true" :disabled="!history.length" @click="onExportClick">
          <i
            class="fa fa-fw"
            :class="{ 'fa-download': !exportingHistory, 'fa-spinner fa-spin': exportingHistory }"
          />
          {{ I18n('Export') }}
        </HueButton>
        <HueButton :small="true" @click="onImportClick">
          <i class="fa fa-fw fa-upload" /> {{ I18n('import') }}
        </HueButton>
      </div>
    </div>
    <div class="query-history-table-container">
      <Spinner :spin="loadingHistory" :center="true" :size="'xlarge'" :overlay="true" />
      <div class="query-history-table-scrollable">
        <HueTable
          :clickable-rows="true"
          :columns="columns"
          :rows="history"
          :show-header="false"
          @row-clicked="$emit('history-entry-clicked', $event)"
        >
          <template #cell-lastExecuted="historyEntry">
            <TimeAgo class="query-history-last-executed" :value="historyEntry.lastExecuted" />
          </template>
          <template #cell-status="historyEntry">
            <ExecutionStatusIcon class="query-history-status" :status="historyEntry.status" />
          </template>
          <template #cell-query="historyEntry">
            <SqlText :value="historyEntry.query" :dialect="connector?.dialect" />
          </template>
        </HueTable>
        <div v-if="!loadingHistory && !totalCount" class="no-history-entries">
          <span v-if="!searchFilter">{{ I18n('Query History is empty') }}</span>
          <span v-else>{{ I18n('No queries found for: ') }}{{ searchFilter }}</span>
        </div>
        <Paginator
          v-show="!loadingHistory && totalCount"
          :total-entries="totalCount"
          @page-changed="onPageChange"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { debounce } from 'lodash';
  import { defineComponent, PropType, ref, toRefs, watch } from 'vue';

  import ClearQueryHistoryModal from './ClearQueryHistoryModal.vue';
  import ExecutionStatusIcon from './ExecutionStatusIcon.vue';
  import './QueryHistoryTable.scss';
  import { fetchHistory, FetchHistoryResponse } from '../api';
  import { ExecutionStatus } from '../execution/sqlExecutable';
  import { CancellablePromise } from 'api/cancellablePromise';
  import {
    EXECUTABLE_TRANSITIONED_TOPIC,
    ExecutableTransitionedEvent
  } from 'apps/editor/execution/events';
  import { Connector } from 'config/types';
  import HueButton from 'components/HueButton.vue';
  import { Column } from 'components/HueTable';
  import HueTable from 'components/HueTable.vue';
  import ImportDocumentsModal from 'components/ImportDocumentsModal.vue';
  import Paginator from 'components/Paginator.vue';
  import { Page } from 'components/Paginator';
  import SearchInput from 'components/SearchInput.vue';
  import Spinner from 'components/Spinner.vue';
  import SqlText from 'components/SqlText.vue';
  import TimeAgo from 'components/TimeAgo.vue';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import { hueWindow } from 'types/types';
  import huePubSub from 'utils/huePubSub';
  import I18n from 'utils/i18n';

  interface HistoryEntry {
    absoluteUrl?: string;
    query: string;
    lastExecuted: number;
    status: ExecutionStatus;
    name: string;
    uuid: string;
  }

  const IGNORE_NEXT_UNLOAD_EVENT = 'ignore.next.unload';

  const trimEllipsis = (str: string): string =>
    `${str.substring(0, 1000)}${str.length > 1000 ? '...' : ''}`;

  export default defineComponent({
    name: 'QueryHistoryTable',
    components: {
      ExecutionStatusIcon,
      ClearQueryHistoryModal,
      HueButton,
      HueTable,
      ImportDocumentsModal,
      Paginator,
      SearchInput,
      Spinner,
      SqlText,
      TimeAgo
    },
    props: {
      connector: {
        type: Object as PropType<Connector | undefined>,
        default: undefined
      }
    },
    emits: ['history-entry-clicked'],
    setup(props) {
      const { connector } = toRefs(props);
      const subTracker = new SubscriptionTracker();
      const clearHistoryModalOpen = ref(false);
      const exportingHistory = ref(false);
      const history = ref<HistoryEntry[]>([]);
      const importHistoryModalOpen = ref(false);
      const loadingHistory = ref(true);
      const searchFilter = ref('');
      const totalCount = ref(0);

      const columns: Column<HistoryEntry>[] = [
        { key: 'lastExecuted' },
        { key: 'status' },
        { key: 'name' },
        { key: 'query' }
      ];

      let runningPromise: CancellablePromise<FetchHistoryResponse> | undefined = undefined;

      const updateHistory = async (page?: Page) => {
        if (runningPromise) {
          runningPromise.cancel();
        }
        if (connector.value && connector.value.dialect) {
          loadingHistory.value = true;
          runningPromise = fetchHistory({
            type: connector.value.dialect,
            page: page?.pageNumber,
            limit: page?.limit,
            docFilter: searchFilter.value
          });

          try {
            const response = await runningPromise;
            totalCount.value = response.count;
            history.value = response.history.map(({ name, data, uuid, absoluteUrl }) => ({
              name,
              query: trimEllipsis(data.statement),
              lastExecuted: data.lastExecuted,
              status: data.status,
              uuid,
              absoluteUrl
            }));
          } catch (err) {}
          runningPromise = undefined;
          loadingHistory.value = false;
        }
      };

      const onClearClick = (): void => {
        clearHistoryModalOpen.value = true;
      };

      const onExportClick = async (): Promise<void> => {
        const dialect = connector.value?.dialect;
        if (!dialect || exportingHistory.value) {
          return;
        }
        try {
          exportingHistory.value = true;
          const historyResponse = await fetchHistory({ type: dialect, page: 1, limit: 500 });

          huePubSub.publish(IGNORE_NEXT_UNLOAD_EVENT);

          if (historyResponse && historyResponse.history) {
            window.location.href = `${
              (window as hueWindow).HUE_BASE_URL
            }/desktop/api2/doc/export?history=true&documents=[${historyResponse.history
              .map(historyDoc => historyDoc.id)
              .join(',')}]`;
          }
        } catch (err) {}
        exportingHistory.value = false;
      };

      const onImportClick = (): void => {
        importHistoryModalOpen.value = true;
      };

      const debouncedUpdate = debounce(updateHistory, 300);
      watch(connector, () => debouncedUpdate(), { immediate: true });
      watch(searchFilter, () => debouncedUpdate());

      subTracker.subscribe<ExecutableTransitionedEvent>(
        EXECUTABLE_TRANSITIONED_TOPIC,
        ({ newStatus, executable }) => {
          if (
            (newStatus === ExecutionStatus.available ||
              newStatus === ExecutionStatus.failed ||
              newStatus === ExecutionStatus.success) &&
            executable.history &&
            executable.handle &&
            executable.executor.connector().id === connector.value?.id &&
            !history.value.some(entry => entry.uuid === executable.history!.uuid)
          ) {
            history.value = [
              {
                absoluteUrl: undefined,
                lastExecuted: executable.executeStarted,
                name: executable.executor.snippet?.name() || '',
                query: executable.handle.statement!,
                status: executable.status,
                uuid: executable.history.uuid!
              },
              ...history.value
            ];
            totalCount.value++;
          }
        }
      );

      return {
        I18n,
        clearHistoryModalOpen,
        columns,
        exportingHistory,
        history,
        importHistoryModalOpen,
        loadingHistory,
        onClearClick,
        onExportClick,
        onImportClick,
        onPageChange: updateHistory,
        refresh: debouncedUpdate,
        searchFilter,
        totalCount
      };
    }
  });
</script>
