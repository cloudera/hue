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
  <ace-editor
    v-if="initialized && editorId"
    :id="editorId"
    :ace-options="aceOptions"
    :executor="executor"
    :initial-cursor-position="cursorPosition"
    :initial-value="value"
    :sql-parser-provider="sqlParserProvider"
    :sql-reference-provider="sqlReferenceProvider"
    @ace-created="aceCreated"
    @create-new-doc="createNewDoc"
    @cursor-changed="cursorChanged"
    @save-doc="saveDoc"
    @toggle-presentation-mode="togglePresentationMode"
    @value-changed="valueChanged"
  />
</template>

<script lang="ts">
  import { Ace } from 'ext/ace';
  import { noop } from 'utils/hueUtils';
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import { wrap } from 'vue/webComponentWrapper';

  import AceEditor from './AceEditor.vue';
  import Executor from 'apps/editor/execution/executor';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import sqlParserRepository from 'parse/sql/sqlParserRepository';
  import sqlReferenceRepository from 'sql/reference/sqlReferenceRepository';

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
    cursorPositionObservable!: KnockoutObservable<Ace.Position | undefined>;
    @Prop()
    aceOptions?: Ace.Options;

    cursorPosition?: Ace.Position;
    editorId?: string;
    initialized = false;
    sqlParserProvider = sqlParserRepository;
    sqlReferenceProvider = sqlReferenceRepository;
    subTracker = new SubscriptionTracker();
    value?: string;

    updated(): void {
      if (!this.initialized) {
        this.value = this.valueObservable();
        this.subTracker.subscribe(this.valueObservable, (value?: string) => {
          this.value = value;
        });

        this.editorId = this.idObservable();
        if (!this.editorId) {
          this.subTracker
            .whenDefined<string>(this.idObservable)
            .then(id => {
              this.editorId = id;
            })
            .catch(noop);
        }

        this.cursorPosition = this.cursorPositionObservable();
        if (!this.cursorPosition) {
          this.subTracker
            .whenDefined<Ace.Position>(this.cursorPositionObservable)
            .then(position => {
              this.cursorPosition = position;
            })
            .catch(noop);
        }
        this.initialized = true;
      }
    }

    destroyed(): void {
      this.subTracker.dispose();
    }

    aceCreated(editor: Ace.Editor): void {
      this.$el.dispatchEvent(new CustomEvent('ace-created', { bubbles: true, detail: editor }));
    }

    createNewDoc(): void {
      this.$el.dispatchEvent(new CustomEvent('create-new-doc', { bubbles: true }));
    }

    cursorChanged(cursorPosition: Ace.Position): void {
      this.$el.dispatchEvent(
        new CustomEvent('cursor-changed', { bubbles: true, detail: cursorPosition })
      );
    }

    saveDoc(): void {
      this.$el.dispatchEvent(new CustomEvent('save-doc', { bubbles: true }));
    }

    togglePresentationMode(): void {
      this.$el.dispatchEvent(new CustomEvent('toggle-presentation-mode', { bubbles: true }));
    }

    valueChanged(value: string): void {
      this.$el.dispatchEvent(new CustomEvent('value-changed', { bubbles: true, detail: value }));
    }
  }

  export const COMPONENT_NAME = 'ace-editor-ko-bridge';
  wrap(COMPONENT_NAME, AceEditorKoBridge);
</script>
