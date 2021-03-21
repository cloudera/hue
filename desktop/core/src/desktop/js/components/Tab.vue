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
  import { defineComponent, inject } from 'vue';
  import { SELECTED_TAB_KEY, ADD_TAB_KEY, REMOVE_TAB_KEY } from './Tabs.vue';

  export interface TabRef {
    title: string;
  }

  export default defineComponent({
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

    setup(props) {
      const addTab: ((tab: TabRef) => void) | undefined = inject(ADD_TAB_KEY);
      const removeTab: ((tab: TabRef) => void) | undefined = inject(REMOVE_TAB_KEY);

      const selectedTabRef: TabRef | undefined = inject(SELECTED_TAB_KEY);

      return {
        addTab,
        removeTab,
        selectedTabRef,

        ref: {
          title: props.title
        }
      };
    },

    data() {
      return {
        rendered: false
      };
    },

    computed: {
      isActive(): boolean {
        return this.ref.title === this.selectedTabRef?.title;
      }
    },

    watch: {
      selectedTabRef(): void {
        if (this.isActive) {
          this.rendered = true;
        }
      }
    },

    mounted(): void {
      if (this.addTab) {
        this.addTab(this.ref);
      }
    }

    // TODO
    // destroyed(): was deprecated, need to rearchitect the component.
    // Whenever parent is rendered mount, unmount is called causing an to prevent infinit loop.
    // unmounted(): void {
    //   if (this.removeTab) {
    //     this.removeTab(this.def);
    //   }
    // }
  });
</script>

<style lang="scss" scoped></style>
