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
  <nav
    ref="sidebarNav"
    v-overflow-on-hover="{ direction: 'y' }"
    class="sidebar-body"
    :class="{
      'sidebar-body-overflow-top': showOverflowIndicatorTop,
      'sidebar-body-overflow-bottom': showOverflowIndicatorBtm
    }"
    @scroll="onScroll"
  >
    <template v-for="(item, index) in items">
      <NavigationItem
        v-if="item.type === 'navigation'"
        :key="item.name"
        :item="item"
        :active-item-name="activeItemName"
        :is-collapsed="isCollapsed"
      />
      <AccordionItem
        v-else-if="item.type === 'accordion'"
        :key="item.name"
        :item="item"
        :active-item-name="activeItemName"
        :is-collapsed="isCollapsed"
      />
      <SectionItem
        v-else-if="item.type === 'section'"
        :key="item.name"
        :item="item"
        :active-item-name="activeItemName"
        :is-collapsed="isCollapsed"
      />
      <SpacerItem v-else :key="'space-' + index" />
    </template>
  </nav>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import { overflowOnHover } from 'components/directives/overflowOnHoverDirective';
  import AccordionItem from './AccordionItem.vue';
  import NavigationItem from './NavigationItem.vue';
  import SectionItem from './SectionItem.vue';
  import SpacerItem from './SpacerItem.vue';
  import { SidebarItem } from './types';
  import { defer } from 'utils/hueUtils';

  export default defineComponent({
    components: { SpacerItem, NavigationItem, SectionItem, AccordionItem },
    directives: {
      'overflow-on-hover': overflowOnHover
    },

    props: {
      items: {
        type: Object as PropType<SidebarItem[]>,
        required: true
      },
      isCollapsed: {
        type: Boolean,
        required: false
      },
      activeItemName: {
        type: String,
        default: ''
      }
    },

    data(): {
      showOverflowIndicatorTop: boolean;
      showOverflowIndicatorBtm: boolean;
    } {
      return {
        showOverflowIndicatorTop: false,
        showOverflowIndicatorBtm: false
      };
    },

    watch: {
      items(): void {
        defer(() => {
          this.detectOverflow(<HTMLElement>this.$refs.sidebarNav);
        });
      }
    },

    methods: {
      onScroll(evt: Event): void {
        const el = <HTMLElement | null>evt.target;
        this.detectOverflow(el);
      },
      detectOverflow(el?: HTMLElement | null): void {
        if (!el) {
          return;
        }
        const hasOverflowOnTop = el.scrollTop > 0;
        const hasOverflowOnBtm = el.scrollHeight - el.scrollTop > el.clientHeight;
        if (hasOverflowOnTop && hasOverflowOnBtm) {
          this.showOverflowIndicatorTop = true;
          this.showOverflowIndicatorBtm = true;
        } else if (hasOverflowOnTop) {
          this.showOverflowIndicatorTop = true;
          this.showOverflowIndicatorBtm = false;
        } else if (hasOverflowOnBtm) {
          this.showOverflowIndicatorTop = false;
          this.showOverflowIndicatorBtm = true;
        } else {
          this.showOverflowIndicatorTop = false;
          this.showOverflowIndicatorBtm = false;
        }
      }
    }
  });
</script>
