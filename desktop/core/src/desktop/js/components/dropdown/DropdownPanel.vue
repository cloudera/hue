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
  <div class="hue-dropdown-panel">
    <hue-link v-if="link" ref="triggerLinkElement" :disabled="disabled" @click="toggleDrawer">
      {{ text }} <i class="fa fa-caret-down" />
    </hue-link>
    <hue-button v-else ref="triggerButtonElement" :disabled="disabled" @click="toggleDrawer">
      {{ text }} <i class="fa fa-caret-down" />
    </hue-button>
    <DropdownDrawer
      :open="open"
      :trigger-element="triggerElement"
      :close-on-click="false"
      @close="closeDrawer"
    >
      <slot :close-panel="closeDrawer" />
    </DropdownDrawer>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  import DropdownDrawer from './DropdownDrawer.vue';
  import HueButton from '../HueButton.vue';
  import HueLink from '../HueLink.vue';

  export default defineComponent({
    name: 'DropdownPanel',
    components: {
      DropdownDrawer,
      HueButton,
      HueLink
    },
    props: {
      text: {
        type: String,
        default: ''
      },
      link: {
        type: Boolean,
        default: false
      },
      disabled: {
        type: Boolean,
        default: false
      }
    },
    data() {
      return {
        open: false,
        triggerElement: null as HTMLElement | null
      };
    },
    mounted() {
      this.triggerElement =
        <HTMLElement>(this.$refs.triggerLinkElement || this.$refs.triggerButtonElement) || null;
    },
    methods: {
      toggleDrawer(): void {
        this.open = !this.open;
      },
      closeDrawer(): void {
        this.open = false;
      }
    }
  });
</script>

<style lang="scss" scoped>
  .hue-dropdown-panel {
    display: inline-block;
  }
</style>
