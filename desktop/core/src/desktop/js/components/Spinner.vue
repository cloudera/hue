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
    <i
      v-if="!overlay"
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
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';

  @Component
  export default class Spinner extends Vue {
    @Prop({ required: false, default: true })
    spin?: boolean;
    @Prop({ required: false, default: 'default' })
    size?: string;
    @Prop({ required: false, default: false })
    center?: boolean;
    @Prop({ required: false, default: false })
    overlay?: boolean;
    @Prop({ required: false, default: false })
    inline?: boolean;
    @Prop({ required: false, default: false })
    blackout?: boolean;
  }
</script>

<style lang="scss" scoped></style>
