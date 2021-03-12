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
  <div class="hue-search-input" :class="{ 'search-input-small': small }">
    <div>
      <i v-if="showMagnify && !spin" class="magnify-icon fa fa-fw fa-search" />
      <i v-else-if="showMagnify && spin" class="magnify-icon fa fa-fw fa-spinner fa-spin" />
      <form autocomplete="off">
        <input
          :value="modelValue"
          class="hue-search-input-el"
          autocorrect="off"
          autocomplete="do-not-autocomplete"
          autocapitalize="off"
          spellcheck="false"
          type="text"
          :placeholder="(!hasFocus && placeholder) || ''"
          :class="{ 'magnify-icon-input': showMagnify }"
          @input="
            event => {
              $emit('input', event.target.value);
              $emit('update:model-value', event.target.value);
            }
          "
          @focusin="hasFocus = true"
          @focusout="hasFocus = false"
          @keyup.enter="$emit('search', $event.target.value)"
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

  import './SearchInput.scss';
  import I18n from '../utils/i18n';

  export default defineComponent({
    name: 'SearchInput',
    props: {
      showMagnify: { type: Boolean, required: false, default: true },
      placeholder: {
        type: String,
        default: I18n('Search...')
      },
      modelValue: {
        type: String,
        default: ''
      },
      small: {
        type: Boolean,
        default: false
      }
    },
    emits: ['input', 'search', 'update:model-value'],
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
  });
</script>
