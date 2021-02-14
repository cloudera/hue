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
  <span>{{ humanSize }}</span>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  const UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB'];

  export const humanSize = (value?: number): string => {
    if (value === 0) {
      return '0 B';
    }
    if (!value) {
      return '';
    }
    if (value < 1024) {
      return `${value} B`;
    }
    const unitIndex = Math.min(Math.floor(Math.log(value) / Math.log(1024)), UNITS.length - 1);
    const unitValue = Math.round((value / Math.pow(1024, unitIndex)) * 10) / 10;
    return `${unitValue} ${UNITS[unitIndex]}`;
  };

  export default defineComponent({
    props: {
      value: {
        type: Number,
        default: 0
      }
    },

    computed: {
      humanSize(): string {
        return humanSize(this.value);
      }
    }
  });
</script>

<style lang="scss" scoped></style>
