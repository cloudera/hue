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
  <button
    class="hue-btn"
    type="button"
    :class="{
      'hue-btn-primary': primary,
      'hue-btn-alert': alert,
      'hue-btn-borderless': borderless,
      'hue-btn-small': small,
      'hue-btn-large': large
    }"
    :disabled="disabled"
    @click="$emit('click')"
  >
    <slot />
  </button>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  export default defineComponent({
    props: {
      primary: {
        type: Boolean,
        required: false
      },
      alert: {
        type: Boolean,
        required: false
      },
      borderless: {
        type: Boolean,
        required: false
      },
      small: {
        type: Boolean,
        required: false
      },
      large: {
        type: Boolean,
        required: false
      },
      disabled: {
        type: Boolean,
        required: false
      }
    },

    emits: ['click']
  });
</script>

<style lang="scss" scoped>
  @import './styles/colors';
  @import './styles/variables';

  .hue-btn {
    height: 32px;
    border-radius: $fluid-border-radius;
    border: solid 1px $fluid-gray-300;
    background-color: $fluid-white;
    color: $fluid-blue-500;
    padding: 0 12px;

    &.hue-btn-small {
      font-size: 12px;
      height: 24px;
      padding: 0 8px;
    }

    &.hue-btn-large {
      font-size: 16px;
      height: 40px;
      padding: 0 20px;
    }

    &:hover {
      border: solid 1px $fluid-blue-700;
    }

    &:active {
      border: solid 1px $fluid-blue-800;
    }

    &[disabled] {
      cursor: default;
      color: $fluid-gray-400;
      border: solid 1px $fluid-gray-200;
    }

    &:focus {
      outline: none;
    }

    &:focus-visible {
      border: solid 1px $fluid-blue-800;
      outline: $fluid-blue-100 auto 4px;
    }

    &.hue-btn-primary:not([disabled]) {
      color: $fluid-white;
      background-color: $fluid-blue-500;
      border: solid 1px $fluid-blue-500;

      &:hover {
        background-color: $fluid-blue-700;
        border: solid 1px $fluid-blue-700;
      }

      &.active {
        background-color: $fluid-blue-800;
        border: solid 1px $fluid-blue-800;
      }

      &:focus-visible {
        border: solid 1px $fluid-gray-900;
      }
    }

    &.hue-btn-alert:not([disabled]) {
      color: $fluid-white;
      background-color: $fluid-red-500;
      border: solid 1px $fluid-red-500;

      &:hover {
        background-color: $fluid-red-700;
        border: solid 1px $fluid-red-700;
      }

      &:active {
        background-color: $fluid-red-800;
        border: solid 1px $fluid-red-800;
      }

      &:focus-visible {
        border: solid 1px $fluid-red-800;
        outline-color: $fluid-red-100;
        outline-width: 4px;
      }
    }

    &.hue-btn-borderless:not([disabled]) {
      border: solid 1px transparent;

      &:hover {
        border: solid 1px $fluid-gray-300;
      }

      &:active {
        border: solid 1px $fluid-gray-400;
      }
    }

    &.hue-btn-borderless[disabled] {
      border: solid 1px transparent;
      color: $fluid-gray-400;
    }

    &.hue-btn-alert[disabled],
    &.hue-btn-primary[disabled] {
      background-color: $fluid-gray-200;
      border: solid 1px $fluid-gray-200;
    }
  }
</style>
