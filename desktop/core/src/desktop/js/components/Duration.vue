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
  <span>{{ duration }}</span>
</template>

<script lang="ts">
  import { Duration as LuxonDuration } from 'luxon';
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';

  export const duration = (value: number): string =>
    LuxonDuration.fromMillis(value).toFormat('hh:mm:ss');

  @Component
  export default class Duration extends Vue {
    @Prop({ required: true })
    value!: number;

    get duration(): string {
      return duration(this.value);
    }
  }
</script>

<style lang="scss" scoped></style>
