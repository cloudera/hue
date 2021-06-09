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
    v-if="editorId"
    :id="editorId"
    :ace-options="aceOptions"
    :executor="executor"
    :initial-cursor-position="cursorPosition"
    :initial-value="value"
    :sql-analyzer-provider="sqlAnalyzerProvider"
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
  import { defineComponent, PropType, ref, toRefs } from 'vue';
  import KnockoutObservable from '@types/knockout';

  import { Ace } from 'ext/ace';

  import { wrap } from 'vue/webComponentWrap';

  import AceEditor from './AceEditor.vue';
  import Executor from 'apps/editor/execution/executor';
  import sqlAnalyzerRepository from 'catalog/analyzer/sqlAnalyzerRepository';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import sqlParserRepository from 'parse/sql/sqlParserRepository';
  import sqlReferenceRepository from 'sql/reference/sqlReferenceRepository';

  const AceEditorKoBridge = defineComponent({
    name: 'AceEditorKoBridge',
    components: {
      AceEditor
    },
    props: {
      executor: {
        type: Object as PropType<Executor>,
        default: undefined
      },
      idObservable: {
        type: Object as PropType<KnockoutObservable<string | undefined>>,
        default: undefined
      },
      valueObservable: {
        type: Object as PropType<KnockoutObservable<string | undefined>>,
        default: undefined
      },
      cursorPositionObservable: {
        type: Object as PropType<KnockoutObservable<Ace.Position | undefined>>,
        default: undefined
      },
      aceOptions: {
        type: Object as PropType<Ace.Options>,
        default: undefined
      }
    },
    setup(props) {
      const subTracker = new SubscriptionTracker();
      const { cursorPositionObservable, idObservable, valueObservable } = toRefs(props);

      const cursorPosition = ref<Ace.Position | null>(null);
      const editorId = ref<string | null>(null);
      const value = ref<string | null>(null);

      subTracker.trackObservable(idObservable, editorId);
      subTracker.trackObservable(cursorPositionObservable, cursorPosition);
      subTracker.trackObservable(valueObservable, value);

      return {
        cursorPosition,
        editorId,
        sqlAnalyzerProvider: sqlAnalyzerRepository,
        sqlParserProvider: sqlParserRepository,
        sqlReferenceProvider: sqlReferenceRepository,
        value
      };
    },
    methods: {
      aceCreated(editor: Ace.Editor): void {
        this.$el.dispatchEvent(new CustomEvent('ace-created', { bubbles: true, detail: editor }));
      },
      createNewDoc(): void {
        this.$el.dispatchEvent(new CustomEvent('create-new-doc', { bubbles: true }));
      },
      cursorChanged(cursorPosition: Ace.Position): void {
        this.$el.dispatchEvent(
          new CustomEvent('cursor-changed', { bubbles: true, detail: cursorPosition })
        );
      },
      saveDoc(): void {
        this.$el.dispatchEvent(new CustomEvent('save-doc', { bubbles: true }));
      },
      togglePresentationMode(): void {
        this.$el.dispatchEvent(new CustomEvent('toggle-presentation-mode', { bubbles: true }));
      },
      valueChanged(value: string): void {
        this.$el.dispatchEvent(new CustomEvent('value-changed', { bubbles: true, detail: value }));
      }
    }
  });

  export const COMPONENT_NAME = 'ace-editor-ko-bridge';
  wrap(COMPONENT_NAME, AceEditorKoBridge);

  export default AceEditorKoBridge;
</script>
