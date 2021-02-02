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
    <hue-button
      v-if="loadingSession"
      key="loading-button"
      small="true"
      :disabled="disabled"
      :title="I18n('Creating session')"
    >
      <i class="fa fa-fw fa-spinner fa-spin" /> {{ I18n('Loading') }}
    </hue-button>

    <hue-button
      v-if="showExecute"
      key="execute-button"
      small="true"
      primary="true"
      :disabled="disabled"
      @click="execute"
    >
      <i class="fa fa-play fa-fw" /> {{ I18n('Execute') }}
    </hue-button>

    <hue-button
      v-if="showStop && !stopping"
      key="stop-button"
      small="true"
      alert="true"
      @click="stop"
    >
      <i class="fa fa-stop fa-fw" />
      <span v-if="waiting">{{ I18n('Stop batch') }}</span>
      <span v-else>{{ I18n('Stop') }}</span>
    </hue-button>

    <hue-button v-if="showStop && stopping" key="stopping-button" small="true" alert="true">
      <i class="fa fa-fw fa-spinner fa-spin" /> {{ I18n('Stopping') }}
    </hue-button>

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
  </div>
</template>

<script lang="ts">
  import SqlExecutable from 'apps/editor/execution/sqlExecutable';
  import HueButton from 'components/HueButton.vue';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import huePubSub from 'utils/huePubSub';
  import I18n from 'utils/i18n';
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop, Watch } from 'vue-property-decorator';

  import { Session } from 'apps/editor/execution/api';
  import { EXECUTABLE_UPDATED_EVENT, ExecutionStatus } from 'apps/editor/execution/executable';
  import sessionManager from 'apps/editor/execution/sessionManager';

  export const EXECUTE_ACTIVE_EXECUTABLE_EVENT = 'executable.active.executable';
  const WHITE_SPACE_REGEX = /^\s*$/;

  @Component({
    components: { HueButton },
    methods: { I18n }
  })
  export default class ExecutableActions extends Vue {
    @Prop()
    executable?: SqlExecutable;
    @Prop()
    beforeExecute?: (executable: Executable) => Promise<void>;

    subTracker = new SubscriptionTracker();

    loadingSession = true;
    lastSession: Session | null = null;
    partOfRunningExecution = false;
    limit: number | null = null;
    stopping = false;
    status: ExecutionStatus = ExecutionStatus.ready;
    hasStatement = false;

    mounted(): void {
      this.subTracker.subscribe(EXECUTABLE_UPDATED_EVENT, executable => {
        if (this.executable === executable) {
          this.updateFromExecutable(executable);
        }
      });

      this.subTracker.subscribe(EXECUTE_ACTIVE_EXECUTABLE_EVENT, executable => {
        if (this.executable === executable) {
          this.execute();
        }
      });
    }

    destroyed(): void {
      this.subTracker.dispose();
    }

    get waiting(): boolean {
      return !!(this.executable && this.executable.isReady() && this.partOfRunningExecution);
    }

    get disabled(): boolean {
      return this.loadingSession || !this.executable || !this.hasStatement;
    }

    get showExecute(): boolean {
      return (
        !!this.executable &&
        !this.waiting &&
        !this.loadingSession &&
        this.status !== ExecutionStatus.running &&
        this.status !== ExecutionStatus.streaming
      );
    }

    get showStop(): boolean {
      return (
        this.status === ExecutionStatus.running ||
        this.status === ExecutionStatus.streaming ||
        this.waiting
      );
    }

    async execute(): Promise<void> {
      huePubSub.publish('hue.ace.autocompleter.hide');
      if (!this.executable) {
        return;
      }
      if (this.beforeExecute) {
        await this.beforeExecute(this.executable);
      }
      await this.executable.reset();
      this.executable.execute();
    }

    async stop(): Promise<void> {
      if (this.stopping || !this.executable) {
        return;
      }
      this.stopping = true;
      await this.executable.cancelBatchChain(true);
      this.stopping = false;
    }

    @Watch('executable', { immediate: true })
    executableChanged(): void {
      if (this.executable) {
        this.updateFromExecutable(this.executable);
      }
    }

    updateFromExecutable(executable: SqlExecutable): void {
      const waitForSession =
        !this.lastSession || this.lastSession.type !== executable.executor.connector().type;
      this.status = executable.status;
      this.hasStatement =
        !executable.parsedStatement ||
        !WHITE_SPACE_REGEX.test(executable.parsedStatement.statement);
      this.partOfRunningExecution = executable.isPartOfRunningExecution();
      this.limit = (executable.executor.defaultLimit && executable.executor.defaultLimit()) || null;
      if (waitForSession) {
        this.loadingSession = true;
        this.lastSession = null;
        sessionManager.getSession({ type: executable.executor.connector().id }).then(session => {
          this.lastSession = session;
          this.loadingSession = false;
        });
      }
    }
  }
</script>

<style lang="scss" scoped>
  .snippet-execute-actions {
    display: inline-block;

    .limit-input {
      border-radius: 2px;
      height: 13px;
      width: 50px;
      margin: 0 5px;
      padding: 5px 6px;
    }
  }
</style>
