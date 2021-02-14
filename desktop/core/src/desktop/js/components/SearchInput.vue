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
  <div class="hue-search-input">
    <div>
      <i v-if="showMagnify && !spin" style="top: 6px;" class="magnify-icon fa fa-fw fa-search" />
      <i v-else lass="magnify-icon fa fa-fw fa-spinner fa-spin" />
      <form autocomplete="off">
        <input
          :value="value"
          class="hue-search-input-el"
          autocorrect="off"
          autocomplete="do-not-autocomplete"
          autocapitalize="off"
          spellcheck="false"
          type="text"
          :placeholder="(!hasFocus && placeholder) || ''"
          :class="{ 'magnify-icon-input': showMagnify }"
          @input="$emit('input', $event.target.value)"
          @focusin="hasFocus = true"
          @focusout="hasFocus = false"
          @keyup.enter="$emit('search', value)"
        />
        <input
          v-model="autocomplete"
          class="hue-search-input-overlay"
          disabled
          type="text"
          autocomplete="do-not-autocomplete"
          :class="{ 'magnify-icon-input': showMagnify }"
        />
      </form>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  import I18n from '../utils/i18n';

  export default defineComponent({
    props: {
      showMagnify: { type: Boolean, required: false, default: true },
      placeholder: {
        type: String,
        default: I18n('Search...')
      },
      value: {
        type: String,
        default: ''
      }
    },

    emits: ['input', 'search'],

    data(): {
      spin: boolean;
      autocomplete: string;
      throttle: number;
      hasFocus: boolean;
    } {
      return {
        spin: false,
        autocomplete: '',
        throttle: -1,
        hasFocus: false
      };
    }

    // TODO: Add autocomplete logic...
  });
</script>

<style lang="scss" scoped>
  @import './styles/colors';
  @import './styles/mixins';

  .hue-search-input {
    display: inline-block;
    vertical-align: middle;
    position: relative;
    border-radius: $hue-panel-border-radius;
    border: 1px solid $hue-border-color;
    background-color: $fluid-white;
    height: 30px;
    width: 250px;

    > div {
      position: absolute;
      left: 0;
      right: 0;
      height: 30px;

      form {
        margin: 0;
      }

      .magnify-icon {
        position: absolute;
        left: 10px;
        top: 7px;
        font-size: 16px;
        color: $fluid-gray-700;
      }

      input {
        display: block;
        position: absolute;
        border: none;
        box-shadow: none;
        margin: 0;
        line-height: 15px;
        background-color: transparent;

        width: 100%;
        height: 100%;
        box-sizing: border-box;

        &.magnify-icon-input {
          padding-left: 35px;
        }

        &.hue-search-input-el {
          z-index: 2;
        }

        &.hue-search-input-overlay {
          color: $fluid-gray-500;
          outline: none;
          z-index: 1;
        }
      }
    }
  }
</style>
