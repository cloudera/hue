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
  <BaseNavigationItem
    v-if="item.type === 'navigation'"
    :key="item.name"
    :css-classes="
      active
        ? 'sidebar-sidebar-item-accordion-sub-item sidebar-sidebar-item-accordion-sub-item-active'
        : 'sidebar-sidebar-item-accordion-sub-item'
    "
    :disabled="disabled"
    :item="item"
  >
    {{ item.displayName }}
  </BaseNavigationItem>
  <SpacerItem v-else-if="item.type === 'spacer'" />
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import SpacerItem from 'components/sidebar/SpacerItem.vue';
  import BaseNavigationItem from './BaseNavigationItem.vue';
  import { SidebarAccordionSubItem } from './types';

  export default defineComponent({
    components: {
      SpacerItem,
      BaseNavigationItem
    },

    props: {
      item: {
        type: Object as PropType<SidebarAccordionSubItem>,
        required: true
      },
      active: Boolean,
      disabled: {
        type: Boolean,
        default: false
      }
    }
  });
</script>
