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
  <div class="snippet-execute-actions">
    <ExecuteButton
      :executable="executable"
      :before-execute="beforeExecute"
      @execute-successful="$emit('execute-successful', $event)"
      @execute-failed="$emit('execute-failed', $event)"
    />
    <ExecuteLimitInput :executable="executable" @limit-changed="$emit('limit-changed', $event)" />
  </div>
</template>

<script lang="ts">
  import ExecuteButton from 'apps/editor/components/ExecuteButton.vue';
  import ExecuteLimitInput from 'apps/editor/components/ExecuteLimitInput.vue';
  import { defineComponent, PropType } from 'vue';

  import './ExecuableActions.scss';
  import SqlExecutable from 'apps/editor/execution/sqlExecutable';

  export default defineComponent({
    name: 'ExecutableActions',
    components: {
      ExecuteLimitInput,
      ExecuteButton
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
    emits: ['execute-failed', 'execute-successful', 'limit-changed']
  });
</script>
