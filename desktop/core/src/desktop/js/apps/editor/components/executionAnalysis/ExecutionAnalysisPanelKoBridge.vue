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
  <ExecutionAnalysisPanel
    v-if="executable"
    :executable="executable"
    @execution-error="onExecutionError"
  />
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { wrap } from 'vue/webComponentWrap';

  import ExecutionAnalysisPanel from './ExecutionAnalysisPanel.vue';
  import SqlExecutable from 'apps/editor/execution/sqlExecutable';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';

  const ExecutionAnalysisPanelKoBridge = defineComponent({
    components: {
      ExecutionAnalysisPanel
    },

    props: {
      executableObservable: {
        type: Object as PropType<KnockoutObservable<SqlExecutable | undefined>> | null,
        default: null
      }
    },

    setup() {
      const subTracker = new SubscriptionTracker();
      return { subTracker };
    },

    data() {
      return {
        initialized: false,
        executable: null as SqlExecutable | null
      };
    },

    updated(): void {
      if (!this.initialized && this.executableObservable) {
        this.executable = this.executableObservable() || null;
        this.subTracker.subscribe(this.executableObservable, executable => {
          this.executable = executable || null;
        });
        this.initialized = true;
      }
    },

    unmounted(): void {
      this.subTracker.dispose();
    },

    methods: {
      onExecutionError(): void {
        this.$el.dispatchEvent(new CustomEvent('execution-error', { bubbles: true }));
      }
    }
  });

  export const COMPONENT_NAME = 'execution-analysis-panel-ko-bridge';
  wrap(COMPONENT_NAME, ExecutionAnalysisPanelKoBridge);

  export default ExecutionAnalysisPanelKoBridge;
</script>
