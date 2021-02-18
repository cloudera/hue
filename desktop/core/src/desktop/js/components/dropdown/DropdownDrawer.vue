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
  <div class="hue-dropdown-drawer" :class="{ open: open }" @click="closeOnClick && closeDrawer()">
    <div
      v-if="open"
      ref="innerPanelElement"
      v-click-outside="closeDrawer"
      class="hue-dropdown-drawer-inner"
      :style="position"
    >
      <slot />
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, nextTick, PropType } from 'vue';

  import { clickOutsideDirective } from '../directives/clickOutsideDirective';

  const isOutsideViewport = (element: Element): { bottom: boolean; right: boolean } => {
    const clientRect = element.getBoundingClientRect();
    return {
      bottom: clientRect.bottom > window.innerHeight,
      right: clientRect.right > window.innerWidth
    };
  };

  type PositionStyle = Pick<CSSStyleDeclaration, 'left' | 'right' | 'top' | 'bottom'>;

  const getDefaultPosition = (): PositionStyle => ({
    top: '100%',
    left: '0',
    right: '',
    bottom: ''
  });

  export default defineComponent({
    name: 'DropdownDrawer',
    directives: {
      'click-outside': clickOutsideDirective
    },
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
        type: Object as PropType<HTMLElement> | null,
        default: null
      }
    },
    emits: ['close'],
    data() {
      return {
        positionTop: false,
        positionLeft: false,
        position: getDefaultPosition()
      };
    },
    watch: {
      async open(newValue) {
        if (!newValue) {
          return;
        }

        this.position = getDefaultPosition();
        await nextTick();

        if (!this.$refs.innerPanelElement) {
          return;
        }
        const { bottom, right } = isOutsideViewport(<HTMLElement>this.$refs.innerPanelElement);
        if (bottom) {
          const bottomOffset = this.triggerElement ? this.triggerElement.offsetHeight : 0;
          this.position.top = '';
          this.position.bottom = `${bottomOffset}px`;
        }
        if (right) {
          const rightOffset = this.triggerElement ? this.triggerElement.offsetWidth : 0;
          this.position.left = '';
          this.position.right = `${rightOffset}px`;
        }
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

<style lang="scss" scoped>
  @import '../styles/colors';
  @import '../styles/mixins';

  .hue-dropdown-drawer {
    position: fixed;
    z-index: 1061;

    &.open {
      .hue-dropdown-drawer-inner {
        display: block;
      }
    }

    .hue-dropdown-drawer-inner {
      display: none;
      position: absolute;
      z-index: 1000;
      margin: 2px 0 0;
      padding: 0;
      background-color: $fluid-white;
      border: 1px solid $hue-border-color;
      border-radius: $hue-panel-border-radius;

      @include box-shadow(0, 5px, 10px, rgba(0, 0, 0, 0.2));
    }
  }
</style>
