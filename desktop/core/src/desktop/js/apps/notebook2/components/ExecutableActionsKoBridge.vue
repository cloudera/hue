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
  <div>
    <executable-actions
      :executable="executable"
      :before-execute="beforeExecute"
      @limit-changed="limitChanged"
    />
  </div>
</template>

<script lang="ts">
  import ExecutableActions from './ExecutableActions.vue';
  import SqlExecutable from 'apps/notebook2/execution/sqlExecutable';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import { wrap } from 'vue/webComponentWrapper';

  @Component({
    components: { ExecutableActions }
  })
  export default class ExecutableActionsKoBridge extends Vue {
    @Prop()
    executableObservable?: KnockoutObservable<SqlExecutable | undefined>;
    @Prop()
    beforeExecute?: () => Promise<void>;

    subTracker = new SubscriptionTracker();
    initialized = false;
    executable: SqlExecutable | null = null;

    updated(): void {
      if (!this.initialized && this.executableObservable) {
        this.executable = this.executableObservable() || null;
        this.subTracker.subscribe(this.executableObservable, (executable: SqlExecutable) => {
          this.executable = executable;
        });
        this.initialized = true;
      }
    }

    destroyed(): void {
      this.subTracker.dispose();
    }

    limitChanged(limit: number): void {
      if (this.executable && this.executable.executor.defaultLimit) {
        this.executable.executor.defaultLimit(limit);
      }
    }
  }

  export const COMPONENT_NAME = 'executable-actions-ko-bridge';
  wrap(COMPONENT_NAME, ExecutableActionsKoBridge);
</script>
