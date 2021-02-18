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
  <a href="javascript:void(0);" @click="clicked"><slot /></a>
</template>

<script lang="ts">
  import { defineComponent } from 'vue';

  import { onHueLinkClick } from 'utils/hueUtils';

  interface hueWindow {
    HUE_BASE_URL: string;
  }

  export default defineComponent({
    props: {
      url: {
        type: String,
        required: false,
        default: ''
      }
    },

    emits: ['click'],

    methods: {
      clicked(event: Event): void {
        if (this.url && this.$attrs.target) {
          onHueLinkClick(event, this.url, <string>this.$attrs.target);
        } else {
          this.$emit('click');
        }
      }
    }
  });
</script>

<style lang="scss" scoped></style>
