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
  <Sidebar
    :sidebar-items="sidebarItems"
    :use-drawer-for-user="false"
    :user-drawer-item="userDrawerItem"
    :user-drawer-children="userDrawerChildren"
    :use-drawer-for-help="false"
    :help-drawer-item="helpDrawerItem"
    :help-drawer-children="helpDrawerChildren"
    :active-item-name="activeItemName"
    :is-collapsed="isCollapsed"
    :drawer-topic="drawerTopic"
    @toggle-collapsed="toggleCollapsed"
    @header-click="onHeaderClick"
  />
</template>

<script lang="ts">
  import { defineComponent } from 'vue';
  import {
    HelpDrawerItem,
    SidebarAccordionItem,
    SidebarAccordionSubItem,
    SidebarItem,
    SidebarNavigationItem,
    UserDrawerItem
  } from './types';

  import Sidebar from './Sidebar.vue';

  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import {
    ASSIST_ACTIVE_DB_CHANGED_EVENT,
    ASSIST_SET_DATABASE_EVENT
  } from 'ko/components/assist/events';
  import { AppType, Connector, HueConfig, Namespace } from 'types/config';
  import { hueWindow } from 'types/types';
  import { CONFIG_REFRESHED_EVENT, getLastKnownConfig } from 'utils/hueConfig';
  import huePubSub from 'utils/huePubSub';
  import { onHueLinkClick } from 'utils/hueUtils';
  import I18n from 'utils/i18n';
  import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';

  interface EditorDatabaseDetails {
    connector: Connector;
    namespace: Namespace;
    name: string;
  }

  interface AssistDatabaseDetails {
    connector: Connector;
    namespace: Namespace;
    database: string;
  }

  const APP_ICON_INDEX: { [name: string]: string } = {
    abfs: `<svg class="hi hi-fw"><use xlink:href="#hi-adls"></use></svg>`,
    adls: `<svg class="hi hi-fw"><use xlink:href="#hi-adls"></use></svg>`,
    dashboard: `<svg class="hi hi-fw"><use xlink:href="#hi-dashboard"></use></svg>`,
    default: `<i class="fa fa-fw fa-database"></i>`,
    'dist-cp': `<i class="fa fa-fw fa-files-o"></i>`,
    documents: `<svg class="hi hi-fw"><use xlink:href="#hi-documents"></use></svg>`,
    editor: `<svg class="hi hi-fw"><use xlink:href="#hi-editor"></use></svg>`,
    hbase: `<i class="fa fa-fw fa-th-large"></i>`,
    hdfs: `<i class="fa fa-fw fa-files-o"></i>`,
    hive: `<svg class="hi hi-fw"><use xlink:href="#hi-hive"></use></svg>`,
    impala: `<svg class="hi hi-fw"><use xlink:href="#hi-impala"></use></svg>`,
    importer: `<i class="fa fa-fw fa-cloud-upload"></i>`,
    indexes: `<i class="fa fa-fw fa-search-plus"></i>`,
    jar: `<svg class="hi hi-fw"><use xlink:href="#hi-spark"></use></svg>`,
    java: `<i class="fa fa-fw fa-file-code-o"></i>`,
    'job-designer': `<svg class="hi hi-fw"><use xlink:href="#hi-job-designer"></use></svg>`,
    kafka: `<i class="fa fa-fw fa-sitemap"></i>`,
    mapreduce: `<i class="fa fa-fw fa-file-archive-o"></i>`,
    markdown: `<svg class="hi hi-fw"><use xlink:href="#hi-markdown"></use></svg>`,
    notebook: `<svg class="hi hi-fw"><use xlink:href="#hi-file-notebook"></use></svg>`,
    oozie: `<svg class="hi hi-fw"><use xlink:href="#hi-oozie"></use></svg>`,
    'oozie-bundle': `<svg class="hi hi-fw"><use xlink:href="#hi-oozie-bundle"></use></svg>`,
    'oozie-coordinator': `<svg class="hi hi-fw"><use xlink:href="#hi-oozie-coordinator"></use></svg>`,
    'oozie-workflow': `<svg class="hi hi-fw"><use xlink:href="#hi-oozie-workflow"></use></svg>`,
    pig: `<svg class="hi hi-fw"><use xlink:href="#hi-pig"></use></svg>`,
    py: `<svg class="hi hi-fw"><use xlink:href="#hi-py"></use></svg>`,
    pyspark: `<svg class="hi hi-fw"><use xlink:href="#hi-spark"></use></svg>`,
    queries: `<i class="fa fa-fw fa-tasks"></i>`,
    r: `<svg class="hi hi-fw"><use xlink:href="#hi-r"></use></svg>`,
    report: `<i class="fa fa-fw fa-area-chart"></i>`,
    s3: `<i class="fa fa-fw fa-cubes"></i>`,
    scala: `<svg class="hi hi-fw"><use xlink:href="#hi-scala"></use></svg>`,
    scheduler: `<svg class="hi hi-fw"><use xlink:href="#hi-oozie"></use></svg>`,
    security: `<i class="fa fa-fw fa-lock"></i>`,
    shell: `<i class="fa fa-fw fa-terminal"></i>`,
    solr: `<i class="fa fa-fw fa-search-plus"></i>`,
    spark2: `<svg class="hi hi-fw"><use xlink:href="#hi-spark"></use></svg>`,
    spark: `<svg class="hi hi-fw"><use xlink:href="#hi-spark"></use></svg>`,
    sqoop1: `<svg class="hi hi-fw"><use xlink:href="#hi-sqoop"></use></svg>`,
    sqoop: `<svg class="hi hi-fw"><use xlink:href="#hi-sqoop"></use></svg>`,
    support: `<svg class="hi hi-fw"><use xlink:href="#hi-support"></use></svg>`,
    tables: `<i class="fa fa-fw fa-database"></i>`,
    text: `<i class="fa fa-fw fa-i-cursor"></i>`,
    warehouses: `<i class="altus-icon altus-adb-cluster" style="margin: 0 1px 0 3px"></i>`,
    workflows: `<svg class="hi hi-fw"><use xlink:href="#hi-oozie"></use></svg>`,
    yarn: `<i class="fa fa-fw fa-tasks"></i>`
  };

  const getIconHtml = (name: string): string => APP_ICON_INDEX[name] || APP_ICON_INDEX.default;

  const USER_DRAWER_CHILDREN: Omit<SidebarNavigationItem, 'iconHtml'>[] = [];

  if ((<hueWindow>window).USER_VIEW_EDIT_USER_ENABLED) {
    USER_DRAWER_CHILDREN.push({
      type: 'navigation',
      name: 'userEdit',
      displayName: I18n('My Profile'),
      handler: (event: Event) =>
        onHueLinkClick(event, '/useradmin/users/edit/' + (<hueWindow>window).LOGGED_USERNAME)
    });
  }

  if ((<hueWindow>window).USER_IS_ADMIN || (<hueWindow>window).USER_IS_HUE_ADMIN) {
    USER_DRAWER_CHILDREN.push({
      type: 'navigation',
      name: 'userAdmin',
      displayName: I18n('Administer Users'),
      handler: (event: Event) => onHueLinkClick(event, '/useradmin/users/')
    });
    USER_DRAWER_CHILDREN.push({
      type: 'navigation',
      name: 'serverAdmin',
      displayName: I18n('Administer Server'),
      handler: (event: Event) => onHueLinkClick(event, '/about/')
    });
  }

  USER_DRAWER_CHILDREN.push({
    type: 'navigation',
    name: 'logOut',
    displayName: I18n('Log Out'),
    handler: (event: Event) => onHueLinkClick(event, '/accounts/logout')
  });

  const HELP_DRAWER_CHILDREN: Omit<SidebarNavigationItem, 'iconHtml'>[] = [
    {
      type: 'navigation',
      name: 'documentation',
      displayName: I18n('Documentation'),
      handler: (event: Event): void => onHueLinkClick(event, 'https://docs.gethue.com', '_blank')
    },
    {
      type: 'navigation',
      name: 'welcomeTour',
      displayName: I18n('Welcome Tour'),
      handler: (): void => {
        huePubSub.publish('show.welcome.tour');
      }
    },
    {
      type: 'navigation',
      name: 'gethue.com',
      displayName: 'gethue.com',
      handler: (event: Event): void => onHueLinkClick(event, 'https://gethue.com', '_blank')
    }
  ];

  export default defineComponent({
    components: {
      Sidebar
    },

    provide(): {
      selectedItemChanged: (itemName: string) => void;
    } {
      return {
        selectedItemChanged: (itemName: string): void => {
          if (
            itemName !== 'user' &&
            itemName !== 'help' &&
            itemName !== 'sidebar-collapse-btn' &&
            this.activeItemName !== itemName
          ) {
            this.activeItemName = itemName;
          }
        }
      };
    },

    setup(): {
      userDrawerItem: UserDrawerItem;
      userDrawerChildren: SidebarAccordionSubItem[];

      helpDrawerItem: HelpDrawerItem;
      helpDrawerChildren: SidebarAccordionSubItem[];

      lastEditorDatabase?: EditorDatabaseDetails;
      lastAssistDatabase?: AssistDatabaseDetails;

      subTracker: SubscriptionTracker;
    } {
      return {
        userDrawerItem: {
          displayName: (<hueWindow>window).LOGGED_USERNAME || '',
          logoutLabel: I18n('Log Out'),
          logoutHandler: (event: Event) => onHueLinkClick(event, '/accounts/logout')
        },
        userDrawerChildren: USER_DRAWER_CHILDREN,

        helpDrawerItem: {
          displayName: I18n('Help'),
          iconHtml: getIconHtml('support')
        },
        helpDrawerChildren: HELP_DRAWER_CHILDREN,

        subTracker: new SubscriptionTracker()
      };
    },

    data(): {
      sidebarItems: SidebarItem[];
      activeItemName: string;
      isCollapsed: boolean;
      drawerTopic: string | null;
    } {
      return {
        sidebarItems: [],
        activeItemName: '',
        isCollapsed: getFromLocalStorage('hue.sidebar.collapse', true),
        drawerTopic: null
      };
    },

    mounted(): void {
      const config = getLastKnownConfig();
      if (config) {
        this.hueConfigUpdated(config);
      }
      this.subTracker.subscribe(CONFIG_REFRESHED_EVENT, (refreshedConfig: HueConfig) => {
        this.hueConfigUpdated(refreshedConfig);
      });
      this.subTracker.subscribe(
        ASSIST_ACTIVE_DB_CHANGED_EVENT,
        (details: AssistDatabaseDetails) => {
          this.lastAssistDatabase = details;
        }
      );
      this.subTracker.subscribe(ASSIST_SET_DATABASE_EVENT, (details: EditorDatabaseDetails) => {
        this.lastEditorDatabase = details;
      });

      this.subTracker.subscribe('set.current.app.name', this.currentAppChanged.bind(this));
      huePubSub.publish('get.current.app.name', this.currentAppChanged.bind(this));
    },

    unmounted(): void {
      this.subTracker.dispose();
    },

    methods: {
      onHeaderClick(event: MouseEvent): void {
        onHueLinkClick(event, '/home');
      },
      toggleCollapsed(): void {
        this.isCollapsed = !this.isCollapsed;
        setInLocalStorage('hue.sidebar.collapse', this.isCollapsed);
      },
      currentAppChanged(appName: string): void {
        let adaptedName;

        const params = new URLSearchParams(location.search);
        switch (appName) {
          case 'dashboard':
            adaptedName = params.get('engine') ? `${appName}-${params.get('engine')}` : appName;
            break;
          case 'editor':
            adaptedName = params.get('type') ? `${appName}-${params.get('type')}` : appName;
            break;
          case 'filebrowser':
            if (location.href.indexOf('=S3A') !== -1) {
              adaptedName = 's3';
            } else if (location.href.indexOf('=adl') !== -1) {
              adaptedName = 'adls';
            } else if (location.href.indexOf('=abfs') !== -1) {
              adaptedName = 'abfs';
            } else {
              adaptedName = 'hdfs';
            }
            break;
          case 'jobbrowser':
            adaptedName = 'yarn';
            break;
          case 'home':
            adaptedName = 'documents';
            break;
          case 'metastore':
            adaptedName = 'tables';
            break;
          case 'oozie_bundle':
            adaptedName = 'scheduler-oozie-bundle';
            break;
          case 'oozie_coordinator':
            adaptedName = 'scheduler-oozie-coordinator';
            break;
          case 'oozie_workflow':
            adaptedName = 'scheduler-oozie-workflow';
            break;
          case 'security_hive':
            adaptedName = 'security';
            break;
          case 'admin_wizard':
          case 'userAdmin':
          case 'userEdit':
          case 'useradmin_edituser':
          case 'useradmin_users':
            adaptedName = 'user';
            break;
          case 'hbase':
          case 'importer':
          case 'indexes':
          case 'kafka':
            break;
          default:
            console.warn('No sidebar alternative for app: ' + appName);
        }

        if (this.activeItemName !== adaptedName) {
          this.identifyActive(adaptedName || appName);
        }
      },

      identifyActive(possibleItemName: string): void {
        if (!possibleItemName) {
          return;
        }

        const findInside = (
          items: (SidebarItem | SidebarAccordionSubItem)[]
        ): string | undefined => {
          let found: string | undefined = undefined;
          items.some(item => {
            if ((<SidebarAccordionItem>item).children) {
              found = findInside((<SidebarAccordionItem>item).children);
            }
            const navigationItem = <SidebarNavigationItem>item;
            if (!found && navigationItem.name === possibleItemName) {
              found = navigationItem.name;
            }
            return found;
          });
          return found;
        };

        const foundName = findInside(this.sidebarItems);
        if (foundName) {
          this.activeItemName = foundName;
        }
      },

      hueConfigUpdated(clusterConfig: HueConfig): void {
        const items: SidebarItem[] = [];

        if (clusterConfig && clusterConfig.app_config) {
          const favourite = clusterConfig.main_button_action;
          const appsItems: SidebarItem[] = [];
          const appConfig = clusterConfig.app_config;

          [AppType.editor, AppType.dashboard, AppType.scheduler, AppType.sdkapps].forEach(
            appName => {
              const config = appConfig[appName];

              if ((<hueWindow>window).CUSTOM_DASHBOARD_URL && appName === 'dashboard') {
                appsItems.push({
                  type: 'navigation',
                  name: 'dashboard',
                  displayName: I18n('Dashboard'),
                  iconHtml: getIconHtml('dashboard'),
                  handler: () => {
                    window.open((<hueWindow>window).CUSTOM_DASHBOARD_URL, '_blank');
                  }
                });
                return;
              }
              if (config && config.interpreters.length) {
                if (config.interpreters.length === 1) {
                  appsItems.push({
                    type: 'navigation',
                    name: `${appName}-${config.name}`,
                    displayName: config.displayName,
                    iconHtml: getIconHtml(config.name),
                    url: config.page,
                    handler: (event: Event) => onHueLinkClick(event, <string>config.page)
                  });
                } else {
                  const subApps: SidebarAccordionSubItem[] = [];
                  config.interpreters.forEach(interpreter => {
                    const interpreterItem: SidebarAccordionSubItem = {
                      type: 'navigation',
                      name: `${appName}-${interpreter.type}`,
                      displayName: interpreter.displayName,
                      url: interpreter.page,
                      handler: (event: Event) => onHueLinkClick(event, interpreter.page)
                    };
                    if (favourite && favourite.page === interpreter.page) {
                      // Put the favourite on top
                      subApps.unshift(interpreterItem);
                    } else {
                      subApps.push(interpreterItem);
                    }
                  });

                  if (appName === 'editor' && (<hueWindow>window).SHOW_ADD_MORE_EDITORS) {
                    subApps.push({ type: 'spacer' });
                    const url = (<hueWindow>window).HAS_CONNECTORS
                      ? '/desktop/connectors'
                      : 'https://docs.gethue.com/administrator/configuration/connectors/';
                    subApps.push({
                      type: 'navigation',
                      name: 'editor-AddMoreInterpreters',
                      displayName: I18n('Edit list...'),
                      url,
                      handler: (event: Event) => onHueLinkClick(event, url)
                    });
                  }
                  const mainUrl = (<SidebarNavigationItem>subApps[0]).url || config.page || '/';
                  appsItems.push({
                    type: 'accordion',
                    name: config.name,
                    displayName: config.displayName,
                    url: mainUrl,
                    handler: (event: Event) => onHueLinkClick(event, mainUrl),
                    iconHtml: getIconHtml(config.name),
                    children: subApps
                  });
                }
              }
            }
          );

          items.push(...appsItems);

          const browserItems: SidebarItem[] = [];
          if (appConfig.home) {
            const url = appConfig.home.page || '/';
            browserItems.push({
              type: 'navigation',
              name: 'documents',
              displayName: appConfig.home.buttonName,
              url,
              handler: (event: Event) => onHueLinkClick(event, url),
              iconHtml: getIconHtml('documents')
            });
          }
          if (appConfig.browser && appConfig.browser.interpreters) {
            appConfig.browser.interpreters.forEach(browser => {
              if (browser.type === 'tables') {
                browserItems.push({
                  type: 'navigation',
                  name: browser.type,
                  displayName: browser.displayName,
                  url: browser.page,
                  handler: (event: Event) => {
                    const details = this.lastEditorDatabase || this.lastAssistDatabase;
                    let url = browser.page;
                    if (details) {
                      url += `/${
                        (<EditorDatabaseDetails>details).name ||
                        (<AssistDatabaseDetails>details).database
                      }?connector_id=${details.connector.id}`;
                    }
                    onHueLinkClick(event, url);
                  },
                  iconHtml: getIconHtml(browser.type)
                });
              } else {
                browserItems.push({
                  type: 'navigation',
                  name: browser.type,
                  displayName: browser.displayName,
                  url: browser.page,
                  handler: (event: Event) => onHueLinkClick(event, browser.page),
                  iconHtml: getIconHtml(browser.type)
                });
              }
            });
          }
          if (browserItems.length) {
            if (items.length) {
              items.push({ type: 'spacer' });
            }

            items.push(...browserItems);
          }

          this.sidebarItems = items;
          if (!this.activeItemName) {
            huePubSub.publish('get.current.app.name', this.currentAppChanged.bind(this));
          }
        }
      }
    }
  });
</script>

<style lang="scss">
  @import './hueSidebar.scss';
</style>
