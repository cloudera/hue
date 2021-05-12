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
  <div ref="panelElement" class="hue-dropdown-panel">
    <HueLink v-if="link" :disabled="disabled" @click="toggleDrawer">
      {{ text }} <i class="fa fa-caret-down" />
    </HueLink>
    <HueButton v-else :disabled="disabled" @click="toggleDrawer">
      {{ text }} <i class="fa fa-caret-down" />
    </HueButton>
    <DropdownDrawer
      :open="open"
      :trigger-element="triggerElement"
      :close-on-click="closeOnClick"
      @close="closeDrawer"
    >
      <slot :close-panel="closeDrawer" />
    </DropdownDrawer>
  </div>
</template>

<script lang="ts">
  import { defineComponent, onMounted, ref } from 'vue';

  import './DropdownPanel.scss';
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
      closeOnClick: {
        type: Boolean,
        default: true
      },
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
    setup() {
      const panelElement = ref<HTMLElement | undefined>(undefined);
      const triggerElement = ref<HTMLElement | undefined>(undefined);
      const open = ref(false);

      onMounted(() => {
        if (panelElement.value?.firstChild) {
          triggerElement.value = panelElement.value.firstChild as HTMLElement;
        }
      });

      const toggleDrawer = () => {
        open.value = !open.value;
      };

      const closeDrawer = () => {
        open.value = false;
      };

      return {
        closeDrawer,
        open,
        panelElement,
        toggleDrawer,
        triggerElement
      };
    }
  });
</script>
