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
  <editor-resizer :editor="editor" />
</template>

<script lang="ts">
  import { Ace } from 'ext/ace';
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import { wrap } from 'vue/webComponentWrapper';

  import EditorResizer from 'apps/editor/components/EditorResizer.vue';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';

  @Component({
    components: { EditorResizer }
  })
  export default class EditorResizerKoBridge extends Vue {
    @Prop()
    editorObservable?: KnockoutObservable<Ace.Editor | undefined>;

    editor: Ace.Editor | null = null;
    subTracker = new SubscriptionTracker();
    initialized = false;

    updated(): void {
      if (!this.initialized && this.editorObservable) {
        this.editor = this.editorObservable() || null;
        this.subTracker.subscribe(this.editorObservable, editor => {
          this.editor = editor;
        });
        this.initialized = true;
      }
    }

    destroyed(): void {
      this.subTracker.dispose();
    }
  }

  export const COMPONENT_NAME = 'editor-resizer-ko-bridge';
  wrap(COMPONENT_NAME, EditorResizerKoBridge);
</script>
