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
  <div class="executable-progress-container">
    <div v-if="visible" class="executable-progress">
      <div
        class="executable-progress-bar"
        :class="progressClass"
        :style="{ width: progressBarWidth, height: progressBarHeight }"
      />
    </div>
  </div>
</template>

<script lang="ts">
  import { EXECUTABLE_UPDATED_TOPIC, ExecutableUpdatedEvent } from 'apps/editor/execution/events';
  import { defineComponent, PropType, ref, toRefs, watch } from 'vue';

  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import SqlExecutable, { ExecutionStatus } from '../execution/sqlExecutable';

  export default defineComponent({
    name: 'ExecutableProgressBar',
    props: {
      executable: {
        type: Object as PropType<SqlExecutable>,
        default: undefined
      }
    },
    setup(props) {
      const subTracker = new SubscriptionTracker();
      const { executable } = toRefs(props);

      const progress = ref(0);
      const status = ref<ExecutionStatus>(ExecutionStatus.ready);
      const progressBarHeight = ref('100%');

      let hideTimeout = -1;

      const updateFromExecutable = (updated?: SqlExecutable) => {
        window.clearTimeout(hideTimeout);
        progress.value = (updated && updated.progress) || 0;
        status.value = (updated && updated.status) || ExecutionStatus.ready;
        if (progress.value === 100) {
          hideTimeout = window.setTimeout(() => {
            progressBarHeight.value = '0';
          }, 2000);
        } else {
          progressBarHeight.value = '100%';
        }
      };

      watch(
        executable,
        newVal => {
          updateFromExecutable(newVal as SqlExecutable);
        },
        { immediate: true }
      );

      subTracker.subscribe<ExecutableUpdatedEvent>(EXECUTABLE_UPDATED_TOPIC, updated => {
        if (executable.value && executable.value.id === updated.id) {
          updateFromExecutable(updated);
        }
      });

      return { subTracker, progress, status, progressBarHeight };
    },
    computed: {
      visible(): boolean {
        return this.status !== ExecutionStatus.canceled;
      },
      progressBarWidth(): string {
        return this.status === ExecutionStatus.failed ? '100%' : `${Math.max(2, this.progress)}%`;
      },
      progressClass(): string {
        if (this.status === ExecutionStatus.failed) {
          return 'progress-failed';
        }
        if (
          this.progress === 0 &&
          (this.status === ExecutionStatus.running ||
            this.status === ExecutionStatus.streaming ||
            this.status === ExecutionStatus.starting)
        ) {
          return 'progress-starting';
        }
        if (0 < this.progress && this.progress < 100) {
          return 'progress-running';
        }
        if (this.progress === 100) {
          return 'progress-success';
        }
        return '';
      }
    }
  });
</script>

<style lang="scss" scoped>
  @import '../../../components/styles/colors.scss';
  @import '../../../components/styles/mixins.scss';

  .executable-progress-container {
    height: 3px;
    overflow: hidden;
    margin-bottom: 2px;
    padding: 0 5px;

    .executable-progress {
      width: 100%;
      height: 100%;
      position: relative;

      .executable-progress-bar {
        background-color: $fluid-white;

        @include ease-transition(height);

        @include keyframes(pulsate) {
          0% {
            margin-left: 0;
          }

          50% {
            margin-left: 30px;
          }

          100% {
            margin-left: 0;
          }
        }

        &.progress-starting {
          background-color: $hue-primary-color-dark;
          @include animation('pulsate 1s infinite');
        }

        &.progress-running {
          background-color: $hue-primary-color-dark;
        }

        &.progress-success {
          background-color: $fluid-green-400;
        }

        &.progress-failed {
          background-color: $fluid-red-400;
        }
      }
    }
  }
</style>
