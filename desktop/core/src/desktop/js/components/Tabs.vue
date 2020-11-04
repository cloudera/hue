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
        :class="{ active: tab.isActive }"
        @click="selectTab(tab)"
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
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Provide } from 'vue-property-decorator';
  import Tab from './Tab.vue';

  @Component
  export default class Tabs extends Vue {
    tabs: Tab[] = [];

    @Provide()
    addTab(tab: Tab): void {
      this.tabs.push(tab);
      if (this.tabs.length === 1) {
        this.selectTab(this.tabs[0]);
      }
    }

    @Provide()
    removeTab(tab: Tab): void {
      const index = this.tabs.indexOf(tab);
      if (index !== -1) {
        this.$delete(this.tabs, index);
        if (tab.isActive && this.tabs.length) {
          this.tabs[Math.max(0, index - 1)].isActive = true;
        }
      }
    }

    selectTab(tab: Tab): void {
      this.tabs.forEach(other => {
        other.isActive = other === tab;
      });
    }
  }
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
