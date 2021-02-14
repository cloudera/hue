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
  import { defineComponent, PropType } from 'vue';

  import { Variable } from 'apps/editor/components/variableSubstitution/types';
  import { IdentifierLocation } from 'parse/types';
  import { POST_FROM_LOCATION_WORKER_EVENT } from 'sql/sqlWorkerHandler';
  import { wrap } from 'vue/webComponentWrap';

  import PresentationMode from './PresentationMode.vue';
  import Executable from 'apps/editor/execution/executable';
  import Executor from 'apps/editor/execution/executor';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';

  const PresentationModeKoBridge = defineComponent({
    components: {
      PresentationMode
    },

    props: {
      executor: {
        type: Object as PropType<Executor | null>,
        default: null
      },

      titleObservable: {
        type: Object as PropType<KnockoutObservable<string | undefined>>,
        default: undefined
      },
      descriptionObservable: {
        type: Object as PropType<KnockoutObservable<string | undefined>>,
        default: undefined
      },
      initialVariables: {
        type: Object as PropType<Variable[]>,
        default: undefined
      }
    },

    setup(): {
      subTracker: SubscriptionTracker;
    } {
      return {
        subTracker: new SubscriptionTracker()
      };
    },

    data(): {
      locations: IdentifierLocation[];

      title: string | null;
      description: string | null;

      initialized: boolean;
    } {
      return {
        locations: [],

        title: null,
        description: null,

        initialized: false
      };
    },

    updated(): void {
      if (!this.initialized && this.titleObservable && this.descriptionObservable) {
        this.title = this.titleObservable() || null;
        this.subTracker.subscribe(this.titleObservable, (title?: string) => {
          this.title = title || null;
        });

        this.description = this.descriptionObservable() || null;
        this.subTracker.subscribe(this.descriptionObservable, (description?: string) => {
          this.description = description || null;
        });

        this.subTracker.subscribe(
          POST_FROM_LOCATION_WORKER_EVENT,
          (e: { data?: { locations?: IdentifierLocation[] } }) => {
            if (e.data && e.data.locations) {
              this.locations = e.data.locations;
            }
          }
        );

        this.initialized = true;
      }
    },

    unmounted(): void {
      this.subTracker.dispose();
    },

    methods: {
      onBeforeExecute(executable: Executable): void {
        this.$el.dispatchEvent(
          new CustomEvent<Executable>('before-execute', { bubbles: true, detail: executable })
        );
      },

      onClose(): void {
        this.$el.dispatchEvent(
          new CustomEvent<void>('close', { bubbles: true })
        );
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
