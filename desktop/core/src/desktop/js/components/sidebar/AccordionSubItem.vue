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
  <BaseNavigationItem
    :key="item.name"
    :css-classes="
      active
        ? 'sidebar-sidebar-item-accordion-sub-item sidebar-sidebar-item-accordion-sub-item-active'
        : 'sidebar-sidebar-item-accordion-sub-item'
    "
    :disabled="disabled"
    :item="item"
  >
    {{ item.displayName }}
  </BaseNavigationItem>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import BaseNavigationItem from './BaseNavigationItem.vue';
  import { SidebarAccordionSubItem } from './types';

  @Component({
    components: { BaseNavigationItem }
  })
  export default class AccordionSubItem extends Vue {
    @Prop()
    item!: SidebarAccordionSubItem;
    @Prop()
    active!: boolean;
    @Prop({ default: false })
    disabled?: boolean;
  }
</script>
