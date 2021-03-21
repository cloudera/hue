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
    class="spinner-container"
    :class="{
      'spinner-overlay': overlay,
      'spinner-inline': inline,
      spinner: !overlay && !inline,
      'spinner-blackout': blackout
    }"
  >
    <div :style="{ width: center && inline ? '100%' : null }" :class="{ 'spinner-center': center }">
      <i
        class="fa fa-spinner fa-spin"
        :class="{
          'spinner-large': size === 'large',
          'spinner-xlarge': size === 'xlarge'
        }"
      />
      <span
        v-if="label"
        :class="{
          'spinner-large': size === 'large',
          'spinner-xlarge': size === 'xlarge'
        }"
      >
        {{ label }}
      </span>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  import './Spinner.scss';

  export default defineComponent({
    name: 'Spinner',
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
      label: {
        type: String,
        default: ''
      },
      blackout: {
        type: Boolean,
        default: false
      }
    }
  });
</script>
