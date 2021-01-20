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
  <div v-if="contents" class="tool-tip-container">
    <div v-for="(content, index) in contents" :key="index" class="tool-tip-box">
      <div class="tool-tip-title">
        {{ content.title }}
      </div>
      <div class="tool-tip-properties">
        <div v-for="prop in content.properties" :key="prop.name" class="tool-tip-prop">
          {{ prop.name }}&nbsp;:&nbsp;
          {{ prop.type === 'time' ? new Date(prop.value).toUTCString() : prop.value }}
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  /* eslint-disable  @typescript-eslint/no-explicit-any */
  /* eslint-disable @typescript-eslint/explicit-module-boundary-types*/

  import $ from 'jquery';
  import { Component, Prop, Vue } from 'vue-property-decorator';

  @Component
  export default class ToolTip extends Vue {
    @Prop() contents: any;

    mounted(): void {
      document.addEventListener('mousemove', this.onMouseMove, false);
    }
    beforeDestroy(): void {
      document.removeEventListener('mousemove', this.onMouseMove, false);
    }

    onMouseMove(event: MouseEvent): void {
      if (this.contents != null) {
        let offsetX = 0;
        if (event.clientX > window.innerWidth / 2) {
          offsetX = this.$el.getBoundingClientRect().width;
        }

        $(this.$el).css({
          visibility: 'visible',
          left: event.clientX - offsetX,
          top: event.clientY
        });
      }
    }
  }
</script>

<style lang="scss" scoped>
  .tool-tip-container {
    position: fixed;
    display: inline-block;

    z-index: 10000;
    pointer-events: none;
    margin-top: 10px;

    visibility: hidden;

    .tool-tip-box {
      color: #fff;
      padding: 5px 10px;

      margin-top: 5px;

      background-color: rgba(0, 0, 0, 0.8);
      border-radius: 4px;

      text-align: center;

      .tool-tip-title {
        padding-bottom: 5px;
        margin-bottom: 5px;
        border-bottom: 1px solid grey;
      }
    }
  }
</style>
