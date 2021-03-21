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
  <form autocomplete="off" class="inline-block margin-left-10">
    <input
      v-model="limit"
      class="input-small limit-input"
      type="number"
      autocorrect="off"
      autocomplete="do-not-autocomplete"
      autocapitalize="off"
      spellcheck="false"
      :placeholder="I18n('Limit')"
      @change="$emit('limit-changed', limit)"
    />
  </form>
</template>

<script lang="ts">
  import { EXECUTABLE_UPDATED_TOPIC, ExecutableUpdatedEvent } from 'apps/editor/execution/events';
  import { defineComponent, PropType, ref, toRefs, watch } from 'vue';

  import SqlExecutable from 'apps/editor/execution/sqlExecutable';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import I18n from 'utils/i18n';

  export default defineComponent({
    name: 'ExecuteLimitInput',
    props: {
      executable: {
        type: Object as PropType<SqlExecutable>,
        default: undefined
      }
    },
    emits: ['limit-changed'],
    setup(props) {
      const { executable } = toRefs(props);
      const limit = ref<number | null>(null);
      const subTracker = new SubscriptionTracker();

      const updateFromExecutable = (updatedExecutable: SqlExecutable): void => {
        limit.value =
          (updatedExecutable.executor.defaultLimit && updatedExecutable.executor.defaultLimit()) ||
          null;
      };

      subTracker.subscribe<ExecutableUpdatedEvent>(EXECUTABLE_UPDATED_TOPIC, updatedExecutable => {
        if (executable.value && executable.value.id === updatedExecutable.id) {
          updateFromExecutable(updatedExecutable);
        }
      });

      watch(
        executable,
        newVal => {
          if (newVal) {
            updateFromExecutable(newVal as SqlExecutable);
          }
        },
        { immediate: true }
      );

      return { limit, I18n };
    }
  });
</script>

<style lang="scss" scoped>
  input.limit-input {
    -moz-appearance: textfield;
    border-radius: 2px;
    height: 13px;
    width: 50px;
    margin: 0 5px;
    padding: 5px 6px;

    &::-webkit-outer-spin-button,
    &::-webkit-inner-spin-button {
      -webkit-appearance: none;
      margin: 0;
    }
  }
</style>
