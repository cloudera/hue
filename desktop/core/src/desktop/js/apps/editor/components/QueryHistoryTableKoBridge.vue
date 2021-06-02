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
  <QueryHistoryTable
    :connector="connector"
    @history-entry-clicked="$emit('history-entry-clicked', $event)"
  />
</template>

<script lang="ts">
  import { defineComponent, PropType, ref, toRefs } from 'vue';
  import KnockoutObservable from '@types/knockout';

  import QueryHistoryTable from './QueryHistoryTable.vue';
  import { wrap } from 'vue/webComponentWrap';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import { Connector } from 'config/types';

  const QueryHistoryTableKoBridge = defineComponent({
    name: 'QueryHistoryTableKoBridge',
    components: {
      QueryHistoryTable
    },
    props: {
      connectorObservable: {
        type: Object as PropType<KnockoutObservable<Connector | undefined>>,
        default: undefined
      }
    },
    emits: ['history-entry-clicked'],
    setup(props) {
      const subTracker = new SubscriptionTracker();
      const { connectorObservable } = toRefs(props);

      const connector = ref<Connector | undefined>(undefined);

      subTracker.trackObservable(connectorObservable, connector);

      return {
        connector
      };
    }
  });

  export const COMPONENT_NAME = 'query-history-table-ko-bridge';
  wrap(COMPONENT_NAME, QueryHistoryTableKoBridge);

  export default QueryHistoryTableKoBridge;
</script>
