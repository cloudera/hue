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
  <div :class="{ 'dropdown-inline': inline }">
    <a v-if="inline" href="javascript: void(0);" @click="toggleMenu">
      {{ text }} <i class="fa fa-caret-down" />
    </a>
    <button v-else class="btn" type="button" @click="toggleMenu">
      {{ text }} <i class="fa fa-caret-down" />
    </button>
    <div :class="{ open: menuOpen }" class="hue-dropdown-container" @click="toggleMenu">
      <div class="hue-dropdown-menu">
        <ul>
          <slot />
        </ul>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';

  @Component
  export default class Dropdown extends Vue {
    @Prop({ required: false, default: '' })
    text: string;
    @Prop({ required: false, default: false })
    inline: boolean;

    menuOpen = false;

    toggleMenu(): void {
      this.menuOpen = !this.menuOpen;
    }
  }
</script>

<style lang="scss" scoped>
  @import '../styles/colors';
  @import '../styles/mixins';

  .dropdown-inline {
    display: inline-block;
  }

  .hue-dropdown-container {
    position: fixed;
    z-index: 1061;

    &.open {
      position: absolute;
      .hue-dropdown-menu {
        display: block;
      }
    }

    &.hue-dropdown-fixed {
      position: fixed !important;
    }

    /deep/ .hue-dropdown-menu {
      display: none;
      z-index: 1000;
      float: left;

      position: absolute;
      top: 100%;
      left: 0;
      margin: 2px 0 0;
      padding: 0;
      min-width: 160px;
      max-width: 250px;
      min-height: 34px;
      max-height: 200px;

      background-color: $cui-white;
      overflow-x: hidden;
      overflow-y: auto;
      list-style: none;
      border: 1px solid $cui-gray;
      border-radius: $hue-panel-border-radius;

      @include box-shadow(0, 5px, 10px, rgba(0, 0, 0, 0.2));

      ul {
        overflow-x: hidden;
        margin: 0 !important;
        padding: 0;
        list-style: none;
        font-size: 13px;

        li {
          color: $cui-gray-800;

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
