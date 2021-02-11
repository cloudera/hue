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
  <dropdown-panel class="hue-dropdown-menu" :text="text" :link="link">
    <template #contents="{ closePanel }">
      <div class="hue-dropdown-menu-inner" @click="closePanel">
        <ul>
          <slot />
        </ul>
      </div>
    </template>
  </dropdown-panel>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  import DropdownPanel from './DropdownPanel.vue';

  export default defineComponent({
    components: {
      DropdownPanel
    },

    props: {
      text: {
        type: String,
        required: false,
        default: ''
      },
      link: {
        type: Boolean,
        required: false,
        default: false
      }
    }
  });
</script>

<style lang="scss" scoped>
  @import '../styles/colors';

  .hue-dropdown-menu {
    .hue-dropdown-menu-inner {
      min-width: 160px;
      max-width: 250px;
      min-height: 34px;
      max-height: 200px;

      overflow-x: hidden;
      overflow-y: auto;

      /deep/ ul {
        overflow-x: hidden;
        margin: 0 !important;
        padding: 0;
        list-style: none;
        font-size: 13px;

        li {
          color: $fluid-gray-800;

          button,
          a {
            display: block;
            width: 100%;
            padding: 6px 16px;
            clear: both;
            font-weight: 400;
            text-align: inherit;
            white-space: nowrap;
            background-color: transparent;
            border: 0;
            position: relative;
            outline: 0;

            &:hover,
            &.active,
            &.focus {
              background-color: $hue-primary-color-light;
            }
          }
        }
      }
    }
  }
</style>
