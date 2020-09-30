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
  <li>
    <header class="dropdown-group-header">{{ header }}</header>
    <ul>
      <slot />
    </ul>
  </li>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';

  @Component
  export default class DropdownGroup extends Vue {
    @Prop({ required: true })
    header!: string;
  }
</script>

<style lang="scss" scoped>
  @import '../styles/colors';

  .dropdown-group-header {
    color: $cui-gray-800;
    font-weight: 500;
    padding: 6px 10px;
  }
</style>
