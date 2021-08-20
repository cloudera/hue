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
  <div
    ref="outerPanelElement"
    class="hue-dropdown-drawer"
    :class="{ open: open }"
    :style="parentPosition"
    @click="closeOnClick && closeDrawer()"
  >
    <div v-if="open" ref="innerPanelElement" class="hue-dropdown-drawer-inner" :style="position">
      <slot />
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, nextTick, PropType } from 'vue';

  import './DropdownDrawer.scss';
  import {
    addClickOutsideHandler,
    removeClickOutsideHandler
  } from 'components/directives/clickOutsideDirective';
  import defer from 'utils/timing/defer';

  const isOutsideViewport = (element: Element): { bottom: boolean; right: boolean } => {
    const clientRect = element.getBoundingClientRect();
    return {
      bottom: clientRect.bottom > window.innerHeight,
      right: clientRect.right > window.innerWidth
    };
  };

  type PositionStyle = Pick<CSSStyleDeclaration, 'left' | 'right' | 'top' | 'bottom'>;
  type ParentPositionStyle = Pick<CSSStyleDeclaration, 'position'>;

  const getDefaultPosition = (): PositionStyle => ({
    top: '100%',
    left: '0',
    right: '',
    bottom: ''
  });

  export default defineComponent({
    name: 'DropdownDrawer',
    props: {
      open: {
        type: Boolean,
        required: true
      },
      closeOnClick: {
        type: Boolean,
        default: true
      },
      triggerElement: {
        type: Object as PropType<HTMLElement | null>,
        default: null
      },
      forceBottomPlacement: {
        type: Boolean,
        default: false
      }
    },
    emits: ['close'],
    data() {
      return {
        positionTop: false,
        positionLeft: false,
        position: getDefaultPosition(),
        parentPosition: { position: 'fixed' } as ParentPositionStyle
      };
    },
    watch: {
      async open(newValue) {
        if (!newValue) {
          removeClickOutsideHandler(this.$el);
          return;
        }

        this.position = getDefaultPosition();
        this.parentPosition = { position: 'fixed' };
        await nextTick();

        const { bottom, right } = isOutsideViewport(<HTMLElement>this.$refs.innerPanelElement);
        if (bottom && !this.forceBottomPlacement) {
          const bottomOffset = this.triggerElement?.offsetHeight || 0;
          // position: relative Prevents fixed element from appearing below the window when at the bottom of the page
          this.parentPosition = { position: 'relative' };
          this.position.top = '';
          this.position.bottom = `${bottomOffset}px`;
        }
        if (right) {
          const rightOffset = this.triggerElement ? this.triggerElement.offsetWidth : 0;
          this.position.left = '';
          this.position.right = `${rightOffset}px`;
        }

        defer(() => {
          addClickOutsideHandler(this.$el, event => {
            if (this.triggerElement !== event.target) {
              this.$emit('close');
            }
          });
        });

        this.$forceUpdate();
      }
    },
    methods: {
      closeDrawer(): void {
        if (this.open) {
          this.$emit('close');
        }
      }
    }
  });
</script>
