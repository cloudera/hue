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
  import { Variable } from 'apps/editor/components/variableSubstitution/types';
  import { IdentifierLocation } from 'parse/types';
  import { POST_FROM_LOCATION_WORKER_EVENT } from 'sql/sqlWorkerHandler';
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import { wrap } from 'vue/webComponentWrapper';

  import PresentationMode from './PresentationMode.vue';
  import Executable from 'apps/editor/execution/executable';
  import Executor from 'apps/editor/execution/executor';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';

  @Component({
    components: { PresentationMode }
  })
  export default class PresentationModeKoBridge extends Vue {
    @Prop()
    executor: Executor | null = null;
    @Prop()
    titleObservable!: KnockoutObservable<string | undefined>;
    @Prop()
    descriptionObservable!: KnockoutObservable<string | undefined>;
    @Prop()
    initialVariables?: Variable[];

    locations: IdentifierLocation[] = [];

    title: string | null = null;
    description: string | null = null;

    initialized = false;

    subTracker = new SubscriptionTracker();

    updated(): void {
      if (!this.initialized) {
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
    }

    destroyed(): void {
      this.subTracker.dispose();
    }

    onBeforeExecute(executable: Executable): void {
      this.$el.dispatchEvent(
        new CustomEvent<Executable>('before-execute', { bubbles: true, detail: executable })
      );
    }

    onClose(): void {
      this.$el.dispatchEvent(
        new CustomEvent<void>('close', { bubbles: true })
      );
    }

    onVariablesChanged(variables: Variable[]): void {
      this.$el.dispatchEvent(
        new CustomEvent<Variable[]>('variables-changed', { bubbles: true, detail: variables })
      );
    }
  }

  export const COMPONENT_NAME = 'presentation-mode-ko-bridge';
  wrap(COMPONENT_NAME, PresentationModeKoBridge);
</script>
