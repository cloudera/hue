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
  <div v-if="!lazy || rendered" v-show="isActive">
    <slot />
  </div>
</template>

<script lang="ts">
  import { defineComponent, inject, Component } from 'vue';

  const Tab:Component = defineComponent({
    name: 'Tab',
    props: {
      title: {
        type: String,
        required: true
      },
      lazy: {
        type: Boolean,
        default: false
      }
    },

    setup(): {
      addTab?: (tab: typeof Tab) => void,
      removeTab?: (tab: typeof Tab) => void,

        isActive: boolean,
        rendered: boolean
    } {
      return {
        addTab: inject('addTab'),
        removeTab: inject('removeTab'),

        isActive: false,
        rendered: false
      };
    },

    watch: {
      isActive(): void {
        if (this.isActive) {
          this.rendered = true;
        }
      }
    },

    mounted(): void {
      if (this.addTab) {
        this.addTab(this);
      }
    },

    destroyed(): void {
      if (this.removeTab) {
        this.removeTab(this);
      }
    }
  })

  export default Tab;
</script>

<style lang="scss" scoped></style>
