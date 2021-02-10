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
    <div class="sidebar-drawers" :class="{ 'sidebar-collapsed': isCollapsed }">
      <SidebarDrawer
        :show="drawerTopic === 'help'"
        class="sidebar-user-drawer sidebar-right-drawer"
        aria-label="Help"
        @close="() => closeDrawer('help')"
      >
        <HelpDrawerContent :children="helpDrawerChildren" />
      </SidebarDrawer>
      <SidebarDrawer
        :show="drawerTopic === 'user'"
        class="sidebar-user-drawer sidebar-right-drawer"
        aria-label="User Info"
        @close="() => closeDrawer('user')"
      >
        <UserDrawerContent :item="userDrawerItem" :children="userDrawerChildren" />
      </SidebarDrawer>
    </div>
    <div class="sidebar" :class="{ 'sidebar-collapsed': isCollapsed }">
      <div class="sidebar-header">
        <a href="javascript:void(0);" @click="$emit('header-click', $event)">
          <svg>
            <use xlink:href="#hi-sidebar-logo" />
          </svg>
        </a>
      </div>
      <SidebarBody
        :items="sidebarItems"
        :is-collapsed="isCollapsed"
        :active-item-name="activeItemName"
      />
      <div class="sidebar-footer">
        <NavigationItem
          v-if="helpItem && useDrawerForHelp"
          :item="helpItem"
          :is-collapsed="isCollapsed"
          :active-item-name="activeItemName"
        />
        <AccordionItem
          v-if="helpItem && !useDrawerForHelp"
          :item="helpItem"
          :is-collapsed="isCollapsed"
          :active-item-name="activeItemName"
        />
        <NavigationItem
          v-if="userItem && useDrawerForUser"
          :item="userItem"
          :is-collapsed="isCollapsed"
          :active-item-name="activeItemName"
        />
        <AccordionItem
          v-if="userItem && !useDrawerForUser"
          :item="userItem"
          :is-collapsed="isCollapsed"
          :active-item-name="activeItemName"
        />
        <div class="sidebar-footer-bottom-row">
          <BaseNavigationItem
            :css-classes="'sidebar-footer-collapse-btn'"
            :item="{
              handler: () => $emit('toggle-collapsed'),
              name: 'sidebar-collapse-btn'
            }"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
              <path
                fill="#adb2b6"
                fill-rule="evenodd"
                d="M18.62 4l-7.903 7.956L18.615 20 20 18.516l-6.432-6.552 6.426-6.47L18.62 4zm-6.719 0L4 11.956 11.897 20l1.385-1.484-6.432-6.552 6.427-6.47L11.901 4z"
              />
            </svg>
          </BaseNavigationItem>
        </div>
        <div class="sidebar-footer-bottom-color-line" />
      </div>
    </div>
  </Fragment>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Fragment } from 'vue-fragment';
  import { Prop } from 'vue-property-decorator';

  import AccordionItem from './AccordionItem.vue';
  import BaseNavigationItem from './BaseNavigationItem.vue';
  import './drawer.scss';
  import HelpDrawerContent from './HelpDrawerContent.vue';
  import NavigationItem from './NavigationItem.vue';
  import './sidebar.scss';
  import SidebarBody from './SidebarBody.vue';
  import SidebarDrawer from './SidebarDrawer.vue';
  import {
    HelpDrawerItem,
    SidebarAccordionItem,
    SidebarAccordionSubItem,
    SidebarItem,
    SidebarNavigationItem,
    UserDrawerItem
  } from './types';
  import UserDrawerContent from './UserDrawerContent.vue';

  @Component({
    components: {
      AccordionItem,
      HelpDrawerContent,
      UserDrawerContent,
      SidebarDrawer,
      Fragment,
      NavigationItem,
      BaseNavigationItem,
      SidebarBody
    }
  })
  export default class Sidebar extends Vue {
    @Prop()
    sidebarItems!: SidebarItem[];

    @Prop({ required: false, default: true })
    useDrawerForUser?: boolean;
    @Prop({ required: false })
    userDrawerItem: UserDrawerItem | null = null;
    @Prop({ required: false })
    userDrawerChildren: SidebarAccordionSubItem[] = [];

    @Prop({ required: false, default: true })
    useDrawerForHelp?: boolean;
    @Prop({ required: false })
    helpDrawerItem: HelpDrawerItem | null = null;
    @Prop({ required: false })
    helpDrawerChildren: SidebarAccordionSubItem[] = [];

    @Prop({ required: false })
    activeItemName?: string;
    @Prop({ required: false, default: true })
    isCollapsed?: boolean;

    drawerTopic: string | null = null;

    closeDrawer(topic: string): void {
      if (this.drawerTopic === topic) {
        this.drawerTopic = null;
      }
    }

    get helpItem(): SidebarAccordionItem | SidebarNavigationItem | null {
      if (!this.helpDrawerItem) {
        return null;
      }
      const sharedProps = {
        name: 'help',
        displayName: this.helpDrawerItem.displayName,
        iconHtml: this.helpDrawerItem.iconHtml
      };
      if (this.useDrawerForHelp) {
        return {
          type: 'navigation',
          ...sharedProps,
          handler: () => {
            this.drawerTopic = 'help';
          }
        };
      }
      return {
        type: 'accordion',
        ...sharedProps,
        children: this.helpDrawerChildren
      };
    }

    get userItem(): SidebarAccordionItem | SidebarNavigationItem | null {
      if (!this.userDrawerItem) {
        return null;
      }
      const sharedProps = {
        name: 'user',
        displayName: this.userDrawerItem.displayName,
        iconHtml: `<div class="sidebar-user-icon" role="img">${this.userDrawerItem.displayName[0].toUpperCase()}</div>`
      };
      if (this.useDrawerForUser) {
        return {
          type: 'navigation',
          ...sharedProps,
          handler: () => {
            this.drawerTopic = 'user';
          }
        };
      }
      return {
        type: 'accordion',
        ...sharedProps,
        children: this.userDrawerChildren
      };
    }
  }
</script>
