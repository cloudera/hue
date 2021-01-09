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
  import { onHueLinkClick } from 'utils/hueUtils';
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';

  interface hueWindow {
    HUE_BASE_URL: string;
  }

  @Component
  export default class HueLink extends Vue {
    @Prop({ required: false })
    url?: string;

    created(): void {
      delete this.$attrs.href;
    }

    clicked(event: Event): void {
      if (this.url) {
        onHueLinkClick(event, this.url, this.$attrs.target);
      } else {
        this.$emit('click');
      }
    }
  }
</script>

<style lang="scss" scoped></style>
