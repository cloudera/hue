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
  <span>
    <i v-if="spin" class="fa fa-spinner fa-spin" />
    <hue-icon v-else-if="icon" :type="icon" />
  </span>
</template>

<script lang="ts">
  import HueIcon from './HueIcon.vue';

  import { defineComponent } from 'vue';

  // TODO: Support additional statuses
  // TODO: Support spinner
  const ICON_MAPPING: { [value: string]: string } = {
    success: 'hi-status-success',
    error: 'hi-status-error',
    warning: 'hi-status-warning',
    stopped: 'hi-status-stopped'
  };

  export default defineComponent({
    components: {
      HueIcon
    },

    props: {
      value: {
        type: String,
        required: true,
        default: 'unknown'
      }
    },

    computed: {
      icon(): string | undefined {
        return ICON_MAPPING[this.value.toLowerCase()];
      },

      spin(): boolean {
        const lowerValue = this.value.toLowerCase();
        return lowerValue === 'started' || lowerValue === 'running';
      }
    }
  });
</script>

<style lang="scss" scoped></style>
