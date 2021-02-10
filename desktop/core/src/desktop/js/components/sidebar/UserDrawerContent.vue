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
      <li v-for="(childItem, index) in children" :key="index">
        <BaseNavigationItem
          v-if="childItem.type === 'navigation'"
          :item="childItem"
          @click="hideDrawer"
        >
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
  import { defineComponent, PropType } from 'vue';

  import BaseNavigationItem from './BaseNavigationItem.vue';
  import { SidebarAccordionSubItem, SidebarBaseItem, UserDrawerItem } from './types';

  export default defineComponent({
    components: { BaseNavigationItem },

    inject: ['hideDrawer'],

    props: {
      item: {
        type: Object as PropType<UserDrawerItem>,
        required: true
      },
      children: {
        type: Object as PropType<SidebarAccordionSubItem[]>,
        required: false,
        default: []
      }
    },

    data(): {
      hideDrawer?: () => void;
    } {
      return {};
    },

    computed: {
      logoutItem(): SidebarBaseItem {
        return {
          handler: this.item.logoutHandler,
          name: 'logout'
        };
      }
    }
  });
</script>
