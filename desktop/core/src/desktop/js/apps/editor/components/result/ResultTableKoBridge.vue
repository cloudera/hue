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
  <ResultTable v-if="executable" :executable="executable" />
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { wrap } from 'vue/webComponentWrap';

  import ResultTable from './ResultTable.vue';
  import SqlExecutable from 'apps/editor/execution/sqlExecutable';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';

  const ResultTableKoBridge = defineComponent({
    components: {
      ResultTable
    },

    props: {
      executableObservable: {
        type: Object as PropType<KnockoutObservable<SqlExecutable | null>> | null,
        default: null
      }
    },

    setup() {
      const subTracker = new SubscriptionTracker();
      return { subTracker };
    },

    data(): {
      initialized: boolean;
      executable: SqlExecutable | null;
    } {
      return {
        initialized: false,
        executable: null
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
    }
  });

  export const COMPONENT_NAME = 'result-table-ko-bridge';
  wrap(COMPONENT_NAME, ResultTableKoBridge);

  export default ResultTableKoBridge;
</script>
