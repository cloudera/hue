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
  <div ref="root" class="snippet-code-resizer" @mousedown="start">
    <i class="fa fa-ellipsis-h" />
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { HIDE_FIXED_HEADERS_EVENT, REDRAW_FIXED_HEADERS_EVENT } from 'apps/editor/events';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import { Ace } from 'ext/ace';
  import huePubSub from 'utils/huePubSub';

  const CUSTOM_HEIGHT_STORAGE_KEY = 'ace.editor.custom.height';
  const TARGET_ELEMENT_SELECTOR = '.ace-editor-component';
  const CONTENT_PANEL_SELECTOR = '.content-panel';

  export default defineComponent({
    props: {
      editor: {
        type: Object as PropType<Ace.Editor | null>,
        required: false,
        default: null
      }
    },

    setup(): {
      subTracker: SubscriptionTracker;
    } {
      return {
        subTracker: new SubscriptionTracker()
      };
    },

    data(
      thisComp
    ): {
      newHeight: number;
      startHeight: number;
      startY: number;

      targetElement: HTMLElement | null;

      onMouseMove: (event: Event) => void;
      onMouseUp: (event: Event) => void;
    } {
      return {
        newHeight: 0,
        startHeight: 0,
        startY: 0,

        targetElement: null,

        onMouseMove: thisComp.drag.bind(this),
        onMouseUp: thisComp.stop.bind(this)
      };
    },

    unmounted(): void {
      document.removeEventListener('mousemove', this.onMouseMove);
      document.removeEventListener('mouseup', this.onMouseUp);
      this.subTracker.dispose();
    },

    methods: {
      drag(event: MouseEvent): void {
        if (!this.targetElement || !this.editor) {
          return;
        }
        const diff = event.clientY - this.startY;

        this.newHeight = Math.max(this.startHeight + diff, 128);
        this.targetElement.style.height = this.newHeight + 'px';
        this.editor.resize();
      },

      findTarget(): void {
        const contentPanel = (this.$refs.root as HTMLElement).closest<HTMLElement>(
          CONTENT_PANEL_SELECTOR
        );
        if (contentPanel) {
          this.targetElement = contentPanel.querySelector<HTMLElement>(TARGET_ELEMENT_SELECTOR);
        }
        if (!this.targetElement) {
          console.warn(
            `EditorResizer could not find the target element '${TARGET_ELEMENT_SELECTOR}'.`
          );
          return;
        }
      },

      start(event: MouseEvent): void {
        if (!this.targetElement) {
          this.findTarget();
          if (!this.targetElement) {
            return;
          }
        }
        this.startY = event.clientY;
        this.startHeight = this.targetElement.offsetHeight;
        document.addEventListener('mousemove', this.onMouseMove);
        document.addEventListener('mouseup', this.onMouseUp);
        huePubSub.publish(HIDE_FIXED_HEADERS_EVENT);
      },

      stop(): void {
        huePubSub.publish(REDRAW_FIXED_HEADERS_EVENT);
        document.dispatchEvent(new Event('editorSizeChanged')); // TODO: Who listens?
        document.removeEventListener('mousemove', this.onMouseMove);
        document.removeEventListener('mouseup', this.onMouseUp);
        localStorage.setItem(CUSTOM_HEIGHT_STORAGE_KEY, String(this.newHeight));
      }
    }
  });
</script>

<style lang="scss" scoped>
  .snippet-code-resizer {
    user-select: none;
  }
</style>
