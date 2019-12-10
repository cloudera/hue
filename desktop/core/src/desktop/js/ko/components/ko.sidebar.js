// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import $ from 'jquery';
import * as ko from 'knockout';

import apiHelper from 'api/apiHelper';
import componentUtils from 'ko/components/componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

export const NAME = 'hue-sidebar';

// prettier-ignore
const TEMPLATE = `
  <script type="text/html" id="sidebar-inner-item">
    <!-- ko if: iconHtml -->
    <div class="icon" data-bind="html: iconHtml"></div><span data-bind="text: displayName"></span>
    <!-- /ko -->
    <!-- ko ifnot: iconHtml -->
    <div class="icon" data-bind="hueAppIcon: icon"></div><span data-bind="text: displayName"></span>
    <!-- /ko -->
  </script>

  <script type="text/html" id="sidebar-item">
    <div class="item-wrapper" data-bind="css: itemClass">
      <!-- ko if: click -->
      <a href="javascript: void(0);" data-bind="click: click, attr: { 'aria-label': displayName, 'data-tooltip': displayName }, css: { 'active': active }" class="item">
        <!-- ko template: 'sidebar-inner-item' --><!-- /ko -->
      </a>
      <!-- /ko -->
      <!-- ko ifnot: click -->
      <a href="javascript: void(0);" data-bind="hueLink: url, publish: 'hue.sidebar.update.active', attr: { 'aria-label': displayName, 'data-tooltip': displayName }, css: { 'active': active }" class="item">
        <!-- ko template: 'sidebar-inner-item' --><!-- /ko -->
      </a>
      <!-- /ko -->
      <!-- ko if: subMenuTemplate -->
      <!-- ko template: subMenuTemplate --><!-- /ko -->
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="user-sub-menu-template">
    <div class="sidebar-menu user-menu" data-bind="css: { 'open' : $component.userMenuOpen }">
      <div class="menu">
        <div class="menu-header">
          <div class="user-icon" style="background-color: #fff">${window.LOGGED_USERNAME[0].toUpperCase()}</div>
          <div>
            <div>${window.LOGGED_USERNAME}</div>
          </div>
        </div>
        <ul class="sidebar-nav-list">
          <!-- ko if: window.USER_VIEW_EDIT_USER_ENABLED -->
          <li><a href="javascript:void(0);" data-bind="
              hueLink: '/useradmin/users/edit/${window.LOGGED_USERNAME}',
              attr: { 
                'title': window.IS_LDAP_SETUP ? '${I18n('View Profile')}' : '${I18n('Edit Profile')}'
              }
            ">${I18n('My Profile')}</a></li>
          <!-- /ko -->
          <!-- ko if: window.USER_IS_ADMIN -->
          <li><a href="javascript: void(0);" data-bind="hueLink: '/useradmin/users/'">${I18n(
            'Manage Users'
          )}</a></li>
          <li><a href="javascript: void(0);" data-bind="hueLink: '/about/'">${I18n(
            'Administration'
          )}</a></li>
          <!-- /ko -->
          <li><a href="javascript: void(0);" data-bind="hueLink: '/accounts/logout'" title="${I18n(
            'Sign out'
          )}" >${I18n('Sign out')}</a></li>
        </ul>
      </div>
    </div>
  </script>

  <script type="text/html" id="support-sub-menu-template">
    <div class="sidebar-menu support-menu" data-bind="css: { 'open' : $component.supportMenuOpen }">
      <div class="menu">
        <ul class="sidebar-nav-list">
          <li><a href="https://docs.gethue.com" target="_blank">${I18n('Documentation')}</a></li>
          <li><a href="javascript:void(0)" data-bind="publish: 'show.welcome.tour'">${I18n(
            'Welcome Tour'
          )}</a></li>
          <li><a href="http://gethue.com" target="_blank">Gethue.com</a></li>
        </ul>
      </div>
    </div>
  </script>

  <!-- ko if: window.DISPLAY_APP_SWITCHER -->
  <!-- ko component: { name: 'hue-app-switcher' } --><!-- /ko -->
  <!-- /ko -->
  <!-- ko ifnot: window.DISPLAY_APP_SWITCHER -->
  <div class="hue-sidebar-header" data-bind="css: { 'hue-sidebar-custom-logo' : window.CUSTOM_LOGO }">
    <a data-bind="hueLink: '/home/'" href="javascript: void(0);" title="${I18n('Documents')}">
      <div class="hue-sidebar-logo"><svg><use xlink:href="#hi-sidebar-logo"></use></svg></div>
    </a>
  </div>
  <!-- /ko -->
  <div class="hue-sidebar-body">
    <!-- ko foreach: items -->
      <!-- ko if: isCategory -->
        <!-- ko ifnot: $index() === 0 -->
        <div class="item-spacer"></div>
        <!-- /ko -->
        <!-- ko template: {name: 'sidebar-item', foreach: children } --><!-- /ko -->
      <!-- /ko -->
      <!-- ko ifnot: isCategory -->
        <!-- ko template: { name: 'sidebar-item' } --><!-- /ko -->
      <!-- /ko -->
    <!-- /ko -->
  </div>
  <div class="hue-sidebar-footer">
    <!-- ko foreach: footerItems -->
    <!-- ko template: { name: 'sidebar-item' } --><!-- /ko -->
    <!-- /ko -->
    <a class="hue-sidebar-trigger" data-bind="toggle: collapsed">
      <svg><use xlink:href="#hi-collapse-nav"></use></svg>
    </a>
  </div>
`;

class SidebarItem {
  constructor(options) {
    this.isCategory = !!options.isCategory;
    this.displayName = options.displayName;
    this.url = options.url;
    this.icon = options.icon;
    this.children = options.children;
    this.name = options.name;
    this.type = options.type;
    this.active = ko.observable(false);
    this.click = options.click;
    this.subMenuTemplate = options.subMenuTemplate;
    this.iconHtml = options.iconHtml;
    this.itemClass = options.itemClass;
  }
}

class Sidebar {
  constructor(params, element) {
    this.$element = $(element);

    this.collapsed = ko.observable();
    this.userMenuOpen = ko.observable(false);
    this.supportMenuOpen = ko.observable(false);

    this.userMenuOpen.subscribe(newVal => {
      if (newVal) {
        window.setTimeout(() => {
          $(document).on('click.userMenu', () => {
            this.userMenuOpen(false);
          });
        }, 0);
        this.supportMenuOpen(false);
      } else {
        $(document).off('click.userMenu');
      }
    });

    this.supportMenuOpen.subscribe(newVal => {
      if (newVal) {
        window.setTimeout(() => {
          $(document).on('click.supportMenu', () => {
            this.supportMenuOpen(false);
          });
        }, 0);
        this.userMenuOpen(false);
      } else {
        $(document).off('click.supportMenu');
      }
    });

    this.collapsed.subscribe(newVal => {
      if (newVal) {
        this.$element.addClass('collapsed');
      } else {
        this.$element.removeClass('collapsed');
      }
    });

    apiHelper.withTotalStorage('hue.sidebar', 'collabse', this.collapsed, true);

    this.items = ko.observableArray();
    this.footerItems = [
      new SidebarItem({
        displayName: 'Support',
        icon: 'support',
        click: () => this.supportMenuOpen(!this.supportMenuOpen()),
        subMenuTemplate: 'support-sub-menu-template'
      }),
      new SidebarItem({
        displayName: window.LOGGED_USERNAME,
        itemClass: 'shepherd-user-menu',
        iconHtml: '<div class="user-icon">' + window.LOGGED_USERNAME[0].toUpperCase() + '</div>',
        click: () => this.userMenuOpen(!this.userMenuOpen()),
        subMenuTemplate: 'user-sub-menu-template'
      })
    ];
    this.lastAppName = undefined;

    const updateActive = () => {
      this.userMenuOpen(false);
      this.supportMenuOpen(false);
      this.items().forEach(item => {
        item.children.forEach(child => {
          let active = false;
          if (this.lastAppName === 'editor') {
            active = child.type === 'editor';
          } else if (this.lastAppName === 'filebrowser') {
            if (location.href.indexOf('=S3A') !== -1) {
              active = child.type === 's3';
            } else if (location.href.indexOf('=adl') !== -1) {
              active = child.type === 'adls';
            } else if (location.href.indexOf('=abfs') !== -1) {
              active = child.type === 'abfs';
            } else {
              active = child.type === 'hdfs';
            }
          } else {
            active = location.pathname == '/hue' + child.url;
          }
          child.active(active);
        });
      });
    };

    huePubSub.subscribe('cluster.config.set.config', clusterConfig => {
      const items = [];
      if (clusterConfig && clusterConfig['app_config']) {
        const appsItems = [];
        const appConfig = clusterConfig['app_config'];
        if (appConfig['editor']) {
          let editor = null;
          if (
            clusterConfig['main_button_action'] &&
            clusterConfig['main_button_action'].page.indexOf('/editor') === 0
          ) {
            editor = clusterConfig['main_button_action'];
          }

          if (!editor) {
            const defaultEditor = appConfig['editor']['default_sql_interpreter'];
            if (defaultEditor) {
              const foundEditor = appConfig['editor']['interpreters'].filter(interpreter => {
                return interpreter.type === defaultEditor;
              });
              if (foundEditor.length === 1) {
                editor = foundEditor[0];
              }
            }
          }

          if (!editor && appConfig['editor']['interpreters'].length > 1) {
            editor = appConfig['editor']['interpreters'][1];
          }

          if (editor) {
            appsItems.push(
              new SidebarItem({
                displayName: I18n('Editor'),
                url: editor['page'],
                icon: 'editor',
                type: 'editor'
              })
            );
          } else {
            appsItems.push(
              new SidebarItem({
                displayName: appConfig['editor']['displayName'],
                url: appConfig['editor']['page'],
                icon: 'editor',
                type: 'editor'
              })
            );
          }
        }
        ['dashboard', 'scheduler'].forEach(appName => {
          if (appConfig[appName]) {
            appsItems.push(
              new SidebarItem({
                displayName: appConfig[appName]['displayName'],
                url: appConfig[appName]['page'],
                icon: appName,
                type: appName
              })
            );
          }
        });
        if (appsItems.length > 0) {
          items.push(
            new SidebarItem({
              isCategory: true,
              displayName: I18n('Apps'),
              children: appsItems
            })
          );
        }

        const browserItems = [];
        browserItems.push(
          new SidebarItem({
            displayName: I18n('Documents'),
            url: '/home/',
            icon: 'documents',
            type: 'home'
          })
        );
        if (appConfig['browser'] && appConfig['browser']['interpreters']) {
          appConfig['browser']['interpreters'].forEach(browser => {
            browserItems.push(
              new SidebarItem({
                displayName: browser.displayName,
                url: browser.page,
                icon: browser.type,
                type: browser.type
              })
            );
          });
        }
        if (browserItems.length > 0) {
          items.push(
            new SidebarItem({
              isCategory: true,
              displayName: I18n('Browsers'),
              children: browserItems
            })
          );
        }

        const sdkItems = [];
        if (appConfig['sdkapps'] && appConfig['sdkapps']['interpreters']) {
          appConfig['sdkapps']['interpreters'].forEach(sdkInterpreter => {
            sdkItems.push(
              new SidebarItem({
                displayName: sdkInterpreter['displayName'],
                url: sdkInterpreter['page'],
                type: sdkInterpreter.type
              })
            );
          });
        }
        if (sdkItems.length > 0) {
          items.push(
            new SidebarItem({
              isCategory: true,
              displayName: appConfig['sdkapps']['displayName'],
              children: sdkItems
            })
          );
        }
      }

      this.items(items);
      updateActive();
    });

    let throttle = -1;
    huePubSub.subscribe('set.current.app.name', appName => {
      if (!appName) {
        return;
      }
      this.lastAppName = appName;
      window.clearTimeout(throttle);
      throttle = window.setTimeout(updateActive, 20);
    });
    updateActive();

    huePubSub.subscribe('hue.sidebar.update.active', updateActive);
  }

  toggleCollapse() {
    this.$element.toggleClass('collapsed');
  }
}

componentUtils.registerComponent(
  NAME,
  {
    createViewModel: function(params, componentInfo) {
      return new Sidebar(params, componentInfo.element);
    }
  },
  TEMPLATE
);
