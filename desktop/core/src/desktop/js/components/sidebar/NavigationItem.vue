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

<!-- eslint-disable vue/no-v-html -->
<template>
  <div @mouseenter="showTooltip" @mouseleave="hideTooltip">
    <BaseNavigationItem
      :item="item"
      :css-classes="isActive ? 'sidebar-sidebar-item sidebar-active' : 'sidebar-sidebar-item'"
      @click="hideTooltip"
    >
      <div v-if="item.iconHtml" class="sidebar-sidebar-item-icon" v-html="item.iconHtml" />

      <span>{{ item.displayName }}</span>
      <div style="flex-grow: 1;" />

      <BaseNavigationItemTooltip
        v-if="tooltip"
        :visible="isCollapsed"
        :style="{ top: tooltip.top + 'px', left: tooltip.right + 'px' }"
        role="tooltip"
      >
        <div
          class="sidebar-sidebar-item-tooltip-primary"
          :class="{ 'sidebar-active': isActive }"
          :style="{ height: tooltip.height + 'px' }"
        >
          {{ item.displayName }}
        </div>
      </BaseNavigationItemTooltip>
    </BaseNavigationItem>
  </div>
</template>
<!-- eslint-enable vue/no-v-html -->

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import BaseNavigationItem from './BaseNavigationItem.vue';
  import BaseNavigationItemTooltip from './BaseNavigationItemTooltip.vue';
  import { SidebarNavigationItem } from './types';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';

  export default defineComponent({
    components: {
      BaseNavigationItemTooltip,
      BaseNavigationItem
    },

    props: {
      isCollapsed: Boolean,
      item: {
        type: Object as PropType<SidebarNavigationItem>,
        required: true
      },
      activeItemName: Object as PropType<String | null>
    },

    setup(): {
      subTracker: SubscriptionTracker,
      tooltip: DOMRect | null
    } {
      return {
        subTracker: new SubscriptionTracker(),
        tooltip: null
      };
    },

    computed: {
      isActive(): Boolean {
        return this.item.name === this.activeItemName;
      }
    },

    methods: {
      showTooltip(event: MouseEvent): void {
        if (!this.isCollapsed) {
          return;
        }
        this.tooltip = (event.target as HTMLElement).getBoundingClientRect();
      },

      hideTooltip(): void {
        this.tooltip = null;
      }
    },

    mounted(): void {
      if(this.$parent) {
        this.subTracker.addEventListener(<HTMLElement>this.$parent.$el, 'scroll', () => {
          this.tooltip = null;
        });
      }
    },

    unmounted(): void {
      this.subTracker.dispose();
    }
  })
</script>
