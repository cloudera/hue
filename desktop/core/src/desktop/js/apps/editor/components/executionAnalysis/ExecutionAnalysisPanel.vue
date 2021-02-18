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
      <LogsPanel class="execution-analysis-logs-panel" :logs="logs" />
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { ExecutionJob } from 'apps/editor/execution/api';
  import HueLink from 'components/HueLink.vue';

  import Executable, {
    EXECUTABLE_UPDATED_EVENT,
    ExecutionStatus
  } from 'apps/editor/execution/executable';
  import ExecutionLogs, {
    ExecutionError,
    LOGS_UPDATED_EVENT
  } from 'apps/editor/execution/executionLogs';
  import LogsPanel from 'components/LogsPanel.vue';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import I18n from 'utils/i18n';

  export default defineComponent({
    components: {
      HueLink,
      LogsPanel
    },

    props: {
      executable: {
        type: Object as PropType<Executable>,
        required: true
      }
    },

    emits: ['execution-error'],

    setup(): {
      subTracker: SubscriptionTracker;
    } {
      return {
        subTracker: new SubscriptionTracker()
      };
    },

    data(): {
      logs: string;
      jobs: ExecutionJob[];
      errors: ExecutionError[];
      notifiedErrors: boolean;
    } {
      return {
        logs: '',
        jobs: [],
        errors: [],
        notifiedErrors: false
      };
    },

    computed: {
      analysisAvailable(): boolean {
        return this.executable.status !== ExecutionStatus.ready || !!this.errors.length;
      },

      jobsWithUrls(): ExecutionJob[] {
        return (this.jobs && this.jobs.filter(job => job.url)) || [];
      },

      jobsAvailable(): boolean {
        return !!this.jobsWithUrls.length;
      }
    },

    watch: {
      errors(errors: ExecutionError[]): void {
        if (errors.length && !this.notifiedErrors) {
          this.$emit('execution-error');
        }
        this.notifiedErrors = !!errors.length;
      }
    },

    mounted(): void {
      this.subTracker.subscribe(EXECUTABLE_UPDATED_EVENT, (executable: Executable) => {
        if (executable.logs) {
          this.updateFromExecutionLogs(executable.logs);
        }
      });

      this.subTracker.subscribe(LOGS_UPDATED_EVENT, this.updateFromExecutionLogs.bind(this));
    },

    unmounted(): void {
      this.subTracker.dispose();
    },

    methods: {
      I18n,
      updateFromExecutionLogs(executionLogs: ExecutionLogs): void {
        if (this.executable.id === executionLogs.executable.id) {
          this.logs = executionLogs.fullLog;
          this.jobs = executionLogs.jobs;
          this.errors = executionLogs.errors;
        }
      }
    }
  });
</script>

<style lang="scss">
  @import './ExecutionAnalysisPanel.scss';
</style>
