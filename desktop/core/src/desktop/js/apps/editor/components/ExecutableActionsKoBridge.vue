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
  <executable-actions
    :executable="executable"
    :before-execute="beforeExecute"
    @limit-changed="limitChanged"
    @execute-failed="$emit('execute-failed', $event)"
    @execute-successful="$emit('execute-successful', $event)"
  />
</template>

<script lang="ts">
  import { defineComponent, PropType, ref, toRefs } from 'vue';
  import KnockoutObservable from '@types/knockout';

  import ExecutableActions from './ExecutableActions.vue';
  import SqlExecutable from 'apps/editor/execution/sqlExecutable';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';

  import { wrap } from 'vue/webComponentWrap';

  const ExecutableActionsKoBridge = defineComponent({
    name: 'ExecutableActionsKoBridge',
    components: {
      ExecutableActions
    },
    props: {
      executableObservable: {
        type: Object as PropType<KnockoutObservable<SqlExecutable | undefined>>,
        default: undefined
      },
      beforeExecute: {
        type: Object as PropType<() => Promise<void>>,
        default: undefined
      }
    },
    emits: ['execute-failed', 'execute-successful'],
    setup(props) {
      const subTracker = new SubscriptionTracker();
      const { executableObservable } = toRefs(props);

      const executable = ref<SqlExecutable | null>(null);

      subTracker.trackObservable(executableObservable, executable);

      return {
        executable
      };
    },
    methods: {
      limitChanged(limit: number): void {
        if (this.executable && this.executable.executor.defaultLimit) {
          this.executable.executor.defaultLimit(limit);
        }
      }
    }
  });

  export const COMPONENT_NAME = 'executable-actions-ko-bridge';
  wrap(COMPONENT_NAME, ExecutableActionsKoBridge);

  export default ExecutableActionsKoBridge;
</script>
