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
  <div>
    <ul>
      <li v-for="tab in tabs" :key="tab.title" @click="selectTab(tab)">
        {{ tab.title }}
      </li>
    </ul>
    <slot />
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

<style lang="scss" scoped></style>
