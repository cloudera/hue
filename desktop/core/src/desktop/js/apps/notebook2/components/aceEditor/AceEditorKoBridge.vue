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
  <div v-if="initialized && editorId">
    <ace-editor
      :id="editorId"
      :executor="executor"
      :ace-options="aceOptions"
      @ace-created="aceCreated"
    />
  </div>
</template>

<script lang="ts">
  import { Ace } from 'ext/ace';
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import { wrap } from 'vue/webComponentWrapper';

  import AceEditor from './AceEditor.vue';
  import Executor from 'apps/notebook2/execution/executor';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';

  @Component({
    components: { AceEditor }
  })
  export default class AceEditorKoBridge extends Vue {
    @Prop()
    executor!: Executor;
    @Prop()
    idObservable!: KnockoutObservable<string | undefined>;
    @Prop()
    valueObservable!: KnockoutObservable<string | undefined>;
    @Prop()
    aceOptions?: Ace.Options;

    value?: string;
    editorId?: string;
    subTracker = new SubscriptionTracker();
    initialized = false;

    updated(): void {
      if (!this.initialized) {
        this.value = this.valueObservable();
        this.subTracker.subscribe(this.valueObservable, (value: string) => {
          this.value = value;
        });
        this.editorId = this.idObservable();
        this.subTracker.subscribe(this.idObservable, (id: string) => {
          this.editorId = id;
        });
        this.initialized = true;
      }
    }

    aceCreated(editor: Ace.Editor): void {
      this.$el.dispatchEvent(new CustomEvent('ace-created', { bubbles: true, detail: editor }));
    }

    destroyed(): void {
      this.subTracker.dispose();
    }
  }

  export const COMPONENT_NAME = 'ace-editor-ko-bridge';
  wrap(COMPONENT_NAME, AceEditorKoBridge);
</script>
