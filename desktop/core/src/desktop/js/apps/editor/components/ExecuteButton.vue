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
  <HueButton
    v-if="loadingSession"
    key="loading-button"
    :small="true"
    :disabled="disabled"
    :title="I18n('Creating session')"
  >
    <i class="fa fa-fw fa-spinner fa-spin" /> {{ I18n('Loading') }}
  </HueButton>
  <HueButton
    v-if="showExecute"
    key="execute-button"
    :small="true"
    :primary="true"
    :disabled="disabled"
    @click="execute"
  >
    <i class="fa fa-play fa-fw" /> {{ I18n('Execute') }}
  </HueButton>

  <HueButton
    v-if="showStop && !stopping"
    key="stop-button"
    :small="true"
    :alert="true"
    @click="stop"
  >
    <i class="fa fa-stop fa-fw" />
    <span v-if="waiting">{{ I18n('Stop batch') }}</span>
    <span v-else>{{ I18n('Stop') }}</span>
  </HueButton>

  <HueButton v-if="showStop && stopping" key="stopping-button" :small="true" :alert="true">
    <i class="fa fa-fw fa-spinner fa-spin" /> {{ I18n('Stopping') }}
  </HueButton>
</template>

<script lang="ts">
  import { defineComponent, PropType, ref, toRefs, watch } from 'vue';

  import { EXECUTE_ACTIVE_EXECUTABLE_TOPIC, ExecuteActiveExecutableEvent } from './events';
  import { Session } from 'apps/editor/execution/api';
  import {
    EXECUTABLE_TRANSITIONED_TOPIC,
    EXECUTABLE_UPDATED_TOPIC,
    ExecutableTransitionedEvent,
    ExecutableUpdatedEvent
  } from 'apps/editor/execution/events';
  import sessionManager from 'apps/editor/execution/sessionManager';
  import SqlExecutable, { ExecutionStatus } from 'apps/editor/execution/sqlExecutable';
  import HueButton from 'components/HueButton.vue';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import huePubSub from 'utils/huePubSub';
  import I18n from 'utils/i18n';

  const WHITE_SPACE_REGEX = /^\s*$/;

  export default defineComponent({
    name: 'ExecuteButton',
    components: {
      HueButton
    },
    props: {
      executable: {
        type: Object as PropType<SqlExecutable | undefined>,
        default: undefined
      },
      beforeExecute: {
        type: Function as PropType<((executable: SqlExecutable) => Promise<void>) | undefined>,
        default: undefined
      }
    },
    emits: [
      'execute-failed',
      'execute-started',
      'execute-successful',
      'executable-updated',
      'execute-stopping'
    ],
    setup(props, { emit }) {
      const { executable, beforeExecute } = toRefs(props);
      const subTracker = new SubscriptionTracker();

      let lastSession = null as Session | null;

      const stopping = ref(false);
      const loadingSession = ref(true);
      const partOfRunningExecution = ref(false);
      const status = ref<ExecutionStatus>(ExecutionStatus.ready);
      const hasStatement = ref(false);

      const execute = async (): Promise<void> => {
        huePubSub.publish('hue.ace.autocompleter.hide');
        if (!executable.value) {
          return;
        }
        if (beforeExecute.value) {
          await beforeExecute.value(executable.value as SqlExecutable);
        }
        await executable.value.reset();
        emit('execute-started', executable.value);
        executable.value.execute();
      };

      const stop = async (): Promise<void> => {
        if (stopping.value || !executable.value) {
          return;
        }
        emit('execute-stopping', executable.value);
        stopping.value = true;
        await executable.value.cancelBatchChain(true);
        stopping.value = false;
      };

      const updateFromExecutable = (executable: SqlExecutable): void => {
        const waitForSession =
          !lastSession || lastSession.type !== executable.executor.connector().type;
        status.value = executable.status;
        hasStatement.value =
          !executable.parsedStatement ||
          !WHITE_SPACE_REGEX.test(executable.parsedStatement.statement);
        partOfRunningExecution.value = executable.isPartOfRunningExecution();
        if (waitForSession) {
          loadingSession.value = true;
          lastSession = null;
          sessionManager.getSession({ type: executable.executor.connector().id }).then(session => {
            lastSession = session;
            loadingSession.value = false;
          });
        }
      };

      watch(
        executable,
        newVal => {
          if (newVal) {
            updateFromExecutable(newVal as SqlExecutable);
          }
        },
        { immediate: true }
      );

      subTracker.subscribe<ExecutableUpdatedEvent>(EXECUTABLE_UPDATED_TOPIC, updatedExecutable => {
        const active = executable.value && executable.value.id === updatedExecutable.id;
        if (active) {
          updateFromExecutable(updatedExecutable);
        }
        emit('executable-updated', { executable: updatedExecutable, active });
      });

      subTracker.subscribe<ExecutableTransitionedEvent>(EXECUTABLE_TRANSITIONED_TOPIC, event => {
        if (event.executable.id === executable.value?.id) {
          if (
            event.newStatus === ExecutionStatus.available ||
            event.newStatus === ExecutionStatus.streaming ||
            event.newStatus === ExecutionStatus.success
          ) {
            emit('execute-successful', executable.value);
          } else if (event.newStatus === ExecutionStatus.failed) {
            emit('execute-failed', executable.value);
          }
        }
      });

      subTracker.subscribe<ExecuteActiveExecutableEvent>(
        EXECUTE_ACTIVE_EXECUTABLE_TOPIC,
        async eventExecutable => {
          if (executable.value && executable.value.id === eventExecutable.id) {
            await execute();
          }
        }
      );

      return {
        execute,
        subTracker,
        stop,
        stopping,
        loadingSession,
        partOfRunningExecution,
        status,
        hasStatement,
        I18n
      };
    },
    computed: {
      waiting(): boolean {
        return !!(this.executable && this.executable.isReady() && this.partOfRunningExecution);
      },
      disabled(): boolean {
        return this.loadingSession || !this.executable || !this.hasStatement;
      },
      showExecute(): boolean {
        return (
          !!this.executable &&
          !this.waiting &&
          !this.loadingSession &&
          this.status !== ExecutionStatus.running &&
          this.status !== ExecutionStatus.streaming
        );
      },
      showStop(): boolean {
        return (
          this.status === ExecutionStatus.running ||
          this.status === ExecutionStatus.streaming ||
          this.waiting
        );
      }
    }
  });
</script>
