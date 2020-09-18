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
  <div v-show="isActive">
    <slot />
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Inject, Prop } from 'vue-property-decorator';

  @Component
  export default class Tab extends Vue {
    @Inject()
    addTab?: (tab: Tab) => void;
    @Inject()
    removeTab?: (tab: Tab) => void;

    @Prop({ required: true })
    title!: string;

    isActive: boolean = false;

    mounted() {
      if (this.addTab) {
        this.addTab(this)
      }
    }

    destroyed() {
      if (this.removeTab) {
        this.removeTab(this);
      }
    }
  }
</script>

<style lang="scss" scoped></style>
