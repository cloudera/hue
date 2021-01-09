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
  <Fragment>
    <button
      v-if="item.handler"
      v-bind="$attrs"
      :class="cssClasses"
      class="sidebar-base-btn"
      @click="onClick"
    >
      <slot />
    </button>
    <a
      v-if="item.url && !item.handler"
      :class="cssClasses"
      :href="item.url"
      v-bind="$attrs"
      class="sidebar-base-link"
      @click="onClick"
    >
      <slot />
    </a>
  </Fragment>
</template>

<script lang="ts">
  import Vue from 'vue';
  import { Fragment } from 'vue-fragment';
  import Component from 'vue-class-component';
  import { Inject, Prop } from 'vue-property-decorator';
  import { SidebarNavigationItem } from './types';

  @Component({
    components: { Fragment }
  })
  export default class BaseNavigationItem extends Vue {
    @Inject()
    selectedItemChanged?: (itemName: string) => void;

    @Prop()
    item!: Pick<SidebarNavigationItem, 'url' | 'handler' | 'name'>;
    @Prop({ default: false })
    disabled?: boolean;
    @Prop({ default: '' })
    cssClasses?: string;

    onClick(event: Event): void {
      if (this.selectedItemChanged) {
        this.selectedItemChanged(this.item.name);
      }
      if (this.item.handler) {
        this.item.handler(event);
      }
      this.$emit('click');
    }
  }
</script>
