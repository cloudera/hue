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
  <div
    v-if="spin"
    :class="{
      'hue-spinner-overlay': overlay,
      'hue-spinner-inline': inline,
      'hue-spinner': !overlay && !inline,
      'hue-spinner-blackout': blackout
    }"
  >
    <em
      class="fa fa-spinner fa-spin"
      :style="{ width: center && inline ? '100%' : null }"
      :class="{
        'hue-spinner-large': size === 'large',
        'hue-spinner-xlarge': size === 'xlarge',
        'hue-spinner-center': center
      }"
    />
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  export default defineComponent({
    props: {
      spin: {
        type: Boolean,
        default: true
      },
      size: {
        type: String,
        default: 'default'
      },
      center: {
        type: Boolean,
        default: false
      },
      overlay: {
        type: Boolean,
        default: false
      },
      inline: {
        type: Boolean,
        default: false
      },
      blackout: {
        type: Boolean,
        default: false
      }
    }
  });
</script>

<style lang="scss" scoped></style>
