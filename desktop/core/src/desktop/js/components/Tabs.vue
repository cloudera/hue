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
  <div class="hue-tabs">
    <ul>
      <li
        v-for="tab in tabs"
        :key="tab.title"
        :class="{ active: selectedTabRef === tab }"
        @click="selectedTabRef = tab"
      >
        {{ tab.title }}
      </li>
    </ul>
    <div class="hue-tab-container">
      <slot />
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, ref, provide } from 'vue';

  import { TabRef } from './Tab.vue';

  export const ADD_TAB_KEY = 'addTab';
  export const REMOVE_TAB_KEY = 'removeTab';

  export const SELECTED_TAB_KEY = 'selectedTabRef';

  export default defineComponent({
    name: 'Tabs',

    setup() {
      const tabs = ref<TabRef[]>([]);
      const selectedTabRef = ref<TabRef | null>(null);

      function addTab(tab: TabRef): void {
        if (!tabs.value.find(t => t.title === tab.title)) {
          tabs.value.push(tab);
          if (tabs.value.length === 1) {
            selectedTabRef.value = tabs.value[0];
          }
        }
      }

      function removeTab(tab: TabRef): void {
        const index = tabs.value.indexOf(tab);
        if (index !== -1) {
          tabs.value.splice(index, 1);
          if (tab === selectedTabRef.value && tabs.value.length) {
            selectedTabRef.value = tabs.value[Math.max(0, index - 1)];
          }
        }
      }

      provide(ADD_TAB_KEY, (tab: TabRef) => addTab(tab));
      provide(REMOVE_TAB_KEY, (tab: TabRef) => removeTab(tab));

      provide(SELECTED_TAB_KEY, selectedTabRef);

      return {
        tabs,
        selectedTabRef
      };
    }
  });
</script>

<style lang="scss" scoped>
  @import './styles/colors';

  .hue-tabs {
    ul {
      border-bottom: 1px solid $hue-border-color;
      list-style: none;
      margin: 0;

      li {
        display: inline-block;
        font-size: 14px;
        padding: 10px;
        border-bottom: 3px solid transparent;
        cursor: pointer;
        margin-right: 10px;
        color: $fluid-gray-700;

        &:hover {
          color: $fluid-blue-500;
        }

        &.active {
          color: $fluid-blue-500;
          border-bottom: 3px solid $fluid-blue-400;
        }
      }
    }
    .hue-tab-container {
      position: relative;
      margin: 12px 0;
      background-color: $fluid-white;
    }
  }
</style>
