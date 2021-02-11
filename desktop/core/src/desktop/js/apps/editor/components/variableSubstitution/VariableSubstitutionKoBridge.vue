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
  <VariableSubstitution
    v-if="initialVariables"
    :locations="locations"
    :initial-variables="initialVariables"
    @variables-changed="onVariablesChanged"
  />
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { wrap } from 'vue/webComponentWrap';

  import { Variable } from './types';
  import VariableSubstitution from './VariableSubstitution.vue';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import { IdentifierLocation } from 'parse/types';
  import { POST_FROM_LOCATION_WORKER_EVENT } from 'sql/sqlWorkerHandler';

  const VariableSubstitutionKoBridge = defineComponent({
    components: {
      VariableSubstitution
    },

    props: {
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
    } {
      return {
        locations: []
      };
    },

    mounted(): void {
      this.subTracker.subscribe(
        POST_FROM_LOCATION_WORKER_EVENT,
        (e: { data?: { locations?: IdentifierLocation[] } }) => {
          if (e.data && e.data.locations) {
            this.locations = e.data.locations;
          }
        }
      );
    },

    methods: {
      onVariablesChanged(variables: Variable[]): void {
        this.$el.dispatchEvent(
          new CustomEvent<Variable[]>('variables-changed', { bubbles: true, detail: variables })
        );
      }
    }
  });

  export const COMPONENT_NAME = 'variable-substitution-ko-bridge';
  wrap(COMPONENT_NAME, VariableSubstitutionKoBridge);

  export default VariableSubstitutionKoBridge;
</script>
