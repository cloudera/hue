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
  <div v-click-outside="clickOutside" class="hue-dropdown-panel">
    <hue-link v-if="link" :disabled="disabled" @click="togglePanel">
      {{ text }} <i class="fa fa-caret-down" />
    </hue-link>
    <hue-button v-else :disabled="disabled" @click="togglePanel">
      {{ text }} <i class="fa fa-caret-down" />
    </hue-button>
    <div class="hue-dropdown-container" :class="{ open: panelOpen }">
      <div
        class="hue-dropdown-inner"
        :class="{ 'position-top': positionTop, 'position-left': positionLeft }"
      >
        <slot name="contents" :closePanel="closePanel" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  import { clickOutsideDirective } from '../directives/clickOutsideDirective';
  import HueButton from '../HueButton.vue';
  import HueLink from '../HueLink.vue';

  interface OutsideStatus {
    left: boolean;
    right: boolean;
    top: boolean;
    bottom: boolean;
  }

  const isOutsideViewport = (element: Element): OutsideStatus => {
    const clientRect = element.getBoundingClientRect();
    return {
      top: clientRect.top < 0,
      right: clientRect.right > window.innerWidth,
      bottom: clientRect.bottom > window.innerHeight,
      left: clientRect.left < 0
    };
  };

  export default defineComponent({
    components: {
      HueButton,
      HueLink
    },

    directives: {
      'click-outside': clickOutsideDirective
    },

    props: {
      text: {
        type: String,
        default: ''
      },
      link: {
        type: Boolean,
        default: false
      },
      disabled: {
        type: Boolean,
        default: false
      }
    },

    data(): {
      panelOpen: boolean;

      positionTop: boolean;
      positionLeft: boolean;
    } {
      return {
        panelOpen: false,

        positionTop: false,
        positionLeft: false
      };
    },

    methods: {
      togglePanel(): void {
        if (!this.panelOpen) {
          const dropdownElement = this.$el.getElementsByClassName('hue-dropdown-container');
          if (dropdownElement.length) {
            const outsideStatus = isOutsideViewport(dropdownElement[0]);
            this.positionTop = outsideStatus.bottom;
            this.positionLeft = outsideStatus.right;
          }
        }
        this.panelOpen = !this.panelOpen;
      },

      closePanel(): void {
        if (this.panelOpen) {
          this.togglePanel();
        }
      },

      clickOutside(): void {
        if (this.panelOpen) {
          this.panelOpen = false;
        }
      }
    }
  });
</script>

<style lang="scss" scoped>
  @import '../styles/colors';
  @import '../styles/mixins';

  .hue-dropdown-panel {
    display: inline-block;

    .hue-dropdown-container {
      position: fixed;
      z-index: 1061;

      &.open {
        position: absolute;
        .hue-dropdown-inner {
          display: block;
        }
      }

      .hue-dropdown-inner {
        display: none;
        z-index: 1000;
        float: left;
        position: absolute;
        margin: 2px 0 0;
        padding: 0;
        background-color: $fluid-white;
        border: 1px solid $hue-border-color;
        border-radius: $hue-panel-border-radius;

        @include box-shadow(0, 5px, 10px, rgba(0, 0, 0, 0.2));

        &:not(.position-top) {
          top: 100%;
        }

        &.position-top {
          bottom: 20px; // TODO: Calculate based on link/button dimensions
        }

        &:not(.position-left) {
          left: 0;
        }

        &.position-left {
          right: 0; // TODO: Calculate based on link/button dimensions
        }
      }
    }
  }
</style>
