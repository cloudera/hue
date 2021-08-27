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
  <PresentationMode
    v-if="executor"
    :executor="executor"
    :title="title"
    :description="description"
    @before-execute="onBeforeExecute"
    @close="onClose"
    @variables-changed="onVariablesChanged"
  />
</template>

<script lang="ts">
  import { defineComponent, PropType, reactive, ref, toRefs } from 'vue';
  import KnockoutObservable from '@types/knockout';

  import { Variable } from 'apps/editor/components/variableSubstitution/types';
  import { IdentifierLocation } from 'parse/types';
  import { POST_FROM_LOCATION_WORKER_EVENT } from 'sql/workers/events';
  import { wrap } from 'vue/webComponentWrap';

  import PresentationMode from './PresentationMode.vue';
  import SqlExecutable from 'apps/editor/execution/sqlExecutable';
  import Executor from 'apps/editor/execution/executor';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';

  const PresentationModeKoBridge = defineComponent({
    name: 'PresentationModeKoBridge',
    components: {
      PresentationMode
    },
    props: {
      descriptionObservable: {
        type: Object as PropType<KnockoutObservable<string | undefined>>,
        default: undefined
      },
      executor: {
        type: Object as PropType<Executor | null>,
        default: null
      },
      initialVariables: {
        type: Object as PropType<Variable[]>,
        default: undefined
      },
      titleObservable: {
        type: Object as PropType<KnockoutObservable<string | undefined>>,
        default: undefined
      }
    },
    setup(props) {
      const subTracker = new SubscriptionTracker();
      const { descriptionObservable, titleObservable } = toRefs(props);

      const description = ref<string | null>(null);
      const locations = reactive<IdentifierLocation[]>([]);
      const title = ref<string | null>(null);

      subTracker.trackObservable(descriptionObservable, description);
      subTracker.trackObservable(titleObservable, title);

      subTracker.subscribe(
        POST_FROM_LOCATION_WORKER_EVENT,
        (e: { data?: { locations?: IdentifierLocation[] } }) => {
          if (e.data && e.data.locations) {
            locations.splice(0, locations.length, ...e.data.locations);
          }
        }
      );

      return {
        description,
        locations,
        title
      };
    },
    methods: {
      onBeforeExecute(executable: SqlExecutable): void {
        this.$el.dispatchEvent(
          new CustomEvent<SqlExecutable>('before-execute', { bubbles: true, detail: executable })
        );
      },
      onClose(): void {
        this.$el.dispatchEvent(new CustomEvent<void>('close', { bubbles: true }));
      },
      onVariablesChanged(variables: Variable[]): void {
        this.$el.dispatchEvent(
          new CustomEvent<Variable[]>('variables-changed', { bubbles: true, detail: variables })
        );
      }
    }
  });

  export const COMPONENT_NAME = 'presentation-mode-ko-bridge';
  wrap(COMPONENT_NAME, PresentationModeKoBridge);

  export default PresentationModeKoBridge;
</script>
