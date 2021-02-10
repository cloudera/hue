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
    v-if="item.handler"
    v-bind="$attrs"
    :class="cssClasses"
    class="sidebar-base-btn"
    @click="onClick"
  >
    <slot />
  </button>
  <a
    v-if="item.url && !item.handler"
    :class="cssClasses"
    :href="item.url"
    v-bind="$attrs"
    class="sidebar-base-link"
    @click="onClick"
  >
    <slot />
  </a>
</template>

<script lang="ts">
  import { defineComponent, PropType, inject } from 'vue';

  import { SidebarBaseItem } from './types';

  export default defineComponent({
    props: {
      item: {
        type: Object as PropType<SidebarBaseItem>,
        required: true
      },
      disabled: {
        type: Boolean,
        default: false
      },
      cssClasses: {
        type: String,
        default: ''
      }
    },

    emits: ['click'],

    setup(): {
      selectedItemChanged?: (itemName: string) => void;
    } {
      return {
        selectedItemChanged: inject('selectedItemChanged')
      };
    },

    methods: {
      onClick(event: Event): void {
        if (this.selectedItemChanged) {
          this.selectedItemChanged(this.item.name);
        }
        if (this.item.handler) {
          this.item.handler(event);
        }
        this.$emit('click');
      }
    }
  });
</script>
