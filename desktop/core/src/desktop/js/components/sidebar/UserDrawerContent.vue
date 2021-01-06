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
  <div class="sidebar-drawer-user-content">
    <div class="sidebar-drawer-user-content-header">
      <div class="sidebar-user-icon" role="img">{{ item.displayName[0].toUpperCase() }}</div>
      <div>
        <div>{{ item.displayName }}</div>
        <small v-if="item.userEmail">{{ item.userEmail }}</small>
      </div>
    </div>
    <ul>
      <li v-for="childItem in children" :key="childItem.name">
        <BaseNavigationItem :item="childItem" @click="hideDrawer">
          {{ childItem.displayName }}
        </BaseNavigationItem>
      </li>
      <li>
        <BaseNavigationItem :item="logoutItem" @click="hideDrawer">
          {{ item.logoutLabel }}
        </BaseNavigationItem>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Inject, Prop } from 'vue-property-decorator';
  import BaseNavigationItem from './BaseNavigationItem.vue';
  import { SidebarAccordionSubItem, SidebarNavigationItem, UserDrawerItem } from './types';

  @Component({
    components: { BaseNavigationItem }
  })
  export default class UserDrawerContent extends Vue {
    @Inject()
    hideDrawer!: () => void;

    @Prop()
    item!: UserDrawerItem;
    @Prop({ required: false, default: [] })
    children?: SidebarAccordionSubItem[];

    get logoutItem(): Pick<SidebarNavigationItem, 'handler' | 'name'> {
      return {
        handler: this.item.logoutHandler,
        name: 'logout'
      };
    }
  }
</script>
