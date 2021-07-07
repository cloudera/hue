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
  <div v-if="statusSpec" :title="statusSpec.title">
    <i class="fa fa-fw" :class="statusSpec.faIcon" />
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType, toRefs, computed } from 'vue';

  import { ExecutionStatus } from '../execution/sqlExecutable';
  import I18n from 'utils/i18n';

  interface StatusSpec {
    title: string;
    faIcon: string;
  }

  export default defineComponent({
    name: 'ExecutionStatusIcon',
    props: {
      status: {
        type: String as PropType<ExecutionStatus | null>,
        default: null
      }
    },
    setup(props) {
      const { status } = toRefs(props);

      const statusSpec = computed<StatusSpec | null>(() => {
        switch (status.value) {
          case ExecutionStatus.expired:
            return { title: I18n('Expired'), faIcon: 'fa-unlink' };
          case ExecutionStatus.available:
            return { title: I18n('Available'), faIcon: 'fa-check' };
          case ExecutionStatus.failed:
            return { title: I18n('Failed'), faIcon: 'fa-exclamation' };
          case ExecutionStatus.streaming:
            return { title: I18n('Streaming'), faIcon: 'fa-fighter-jet' };
          case ExecutionStatus.running:
            return { title: I18n('Running'), faIcon: 'fa-fighter-jet' };
        }
        return null;
      });

      return {
        statusSpec
      };
    }
  });
</script>
