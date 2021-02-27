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
  <div class="execution-analysis-panel">
    <div v-if="!analysisAvailable">
      <h1 class="empty">{{ I18n('Select and execute a query to see the analysis.') }}</h1>
    </div>

    <div v-if="analysisAvailable && errors.length" class="execution-analysis-errors">
      <h4>{{ I18n('Errors') }}</h4>
      <ul>
        <li v-for="error of errors" :key="error.message">{{ error.message }}</li>
      </ul>
    </div>

    <div v-if="analysisAvailable && jobsAvailable" class="execution-analysis-jobs">
      <h4>{{ I18n('Jobs') }}</h4>
      <div class="execution-analysis-jobs-panel">
        <hue-link v-for="job of jobsWithUrls" :key="job.url" :url="job.url" target="_blank">
          {{ job.name }}
        </hue-link>
      </div>
    </div>

    <div v-if="analysisAvailable" class="execution-analysis-logs">
      <h4>{{ I18n('Logs') }}</h4>
      <LogsPanel class="execution-analysis-logs-panel" :logs="executionLogs" />
    </div>
  </div>
</template>

<script lang="ts">
  import { debounce } from 'lodash';
  import { defineComponent, computed, onBeforeUnmount, ref, reactive } from 'vue';

  import { ExecutionJob } from 'apps/editor/execution/api';
  import Executable, {
    EXECUTABLE_UPDATED_EVENT,
    ExecutionStatus
  } from 'apps/editor/execution/executable';
  import SqlExecutable from 'apps/editor/execution/sqlExecutable';
  import ExecutionLogs, {
    ExecutionError,
    LOGS_UPDATED_EVENT
  } from 'apps/editor/execution/executionLogs';
  import HueLink from 'components/HueLink.vue';
  import LogsPanel from 'components/LogsPanel.vue';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import I18n from 'utils/i18n';

  export default defineComponent({
    name: 'ExecutionAnalysisPanel',
    components: {
      HueLink,
      LogsPanel
    },
    props: {
      executable: {
        type: SqlExecutable,
        required: true
      }
    },
    emits: ['execution-error'],
    setup(props, { emit }) {
      const subTracker = new SubscriptionTracker();
      onBeforeUnmount(subTracker.dispose.bind(subTracker));

      const analysisAvailable = ref(false);
      const executionLogs = ref('');
      const jobs = reactive<ExecutionJob[]>([]);
      const errors = reactive<ExecutionError[]>([]);

      const jobsAvailable = computed(() => !!jobs.length);
      const jobsWithUrls = computed(() => jobs.filter(job => job.url));

      let notifiedErrors = false;

      const debouncedUpdate = debounce((executable: Executable): void => {
        const { status, logs } = executable;
        executionLogs.value = logs.fullLog;
        jobs.splice(0, jobs.length, ...logs.jobs);
        errors.splice(0, errors.length, ...logs.errors);

        analysisAvailable.value = status !== ExecutionStatus.ready || !!errors.length;

        if (errors.length && !notifiedErrors) {
          emit('execution-error');
        }
        notifiedErrors = !!errors.length;
      }, 5);

      const updateFromExecutable = (executable: Executable): void => {
        if (props.executable.id !== executable.id) {
          return;
        }
        debouncedUpdate.cancel();
        debouncedUpdate(executable);
      };

      updateFromExecutable(props.executable);

      subTracker.subscribe(EXECUTABLE_UPDATED_EVENT, updateFromExecutable);

      subTracker.subscribe(LOGS_UPDATED_EVENT, (executionLogs: ExecutionLogs) => {
        updateFromExecutable(executionLogs.executable);
      });

      return {
        analysisAvailable,
        executionLogs,
        jobs,
        jobsAvailable,
        jobsWithUrls,
        errors,
        notifiedErrors,
        I18n
      };
    }
  });
</script>

<style lang="scss">
  @import './ExecutionAnalysisPanel.scss';
</style>
