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
import ko from 'knockout';

import apiHelper from 'api/apiHelper';
import componentUtils from 'ko/components/componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

const TEMPLATE = `
  <script type="text/html" id="sidebar-item">
    <div class="item-wrapper"><a href="javascript: void(0);" data-bind="hueLink: item.url, attr: { 'aria-label': item.displayName, 'data-tooltip': item.displayName }, css: { 'active': item.active }" class="item">
      <div class="icon" data-bind="template: 'app-icon-template'"></div><span data-bind="text: item.displayName"></span>
    </a></div>
  </script>

  <div class="hue-sidebar-header"></div>
  <div class="hue-sidebar-body">
    <!-- ko foreach: {data: items, as: 'item'} -->
      <!-- ko if: item.isCategory -->
        <!-- ko ifnot: $index() === 0 -->
        <div class="item-spacer"></div>
        <!-- /ko -->
        <!-- ko template: {name: 'sidebar-item', foreach: item.children, as: 'item'} --><!-- /ko -->
      <!-- /ko -->
      <!-- ko ifnot: item.isCategory -->
        <!-- ko template: { name: 'sidebar-item' } --><!-- /ko -->
      <!-- /ko -->
    <!-- /ko -->
  </div>
  <div class="hue-sidebar-footer">
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

    this.active = ko.observable(false);
  }
}

class Sidebar {
  constructor(params, element) {
    this.$element = $(element);

    this.collapsed = ko.observable();

    this.collapsed.subscribe(newVal => {
      if (newVal) {
        this.$element.addClass('collapsed');
      } else {
        this.$element.removeClass('collapsed');
      }
    });

    apiHelper.withTotalStorage('hue.sidebar', 'collabse', this.collapsed, true);

    this.items = ko.observableArray();

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
                icon: 'editor'
              })
            );
          } else {
            appsItems.push(
              new SidebarItem({
                displayName: appConfig['editor']['displayName'],
                url: appConfig['editor']['page'],
                icon: 'editor'
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
                icon: appName
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
            icon: 'documents'
          })
        );
        if (appConfig['browser'] && appConfig['browser']['interpreters']) {
          appConfig['browser']['interpreters'].forEach(browser => {
            browserItems.push(
              new SidebarItem({
                displayName: browser.displayName,
                url: browser.page,
                icon: browser.type
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
          appConfig['sdkapps']['interpreters'].forEach(browser => {
            sdkItems.push(
              new SidebarItem({
                displayName: browser['displayName'],
                url: browser['page']
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
    });

    const updateActive = () => {
      this.items().forEach(item => {
        item.children.forEach(child => {
          child.active(location.href.indexOf(child.url) !== -1)
        });
      });
    };

    let throttle = -1;
    huePubSub.subscribe('set.current.app.name', appName => {
      window.clearTimeout(throttle);
      if (!appName) {
        return;
      }
      throttle = window.setTimeout(updateActive, 20);
    });
    updateActive();
  }

  toggleCollapse() {
    this.$element.toggleClass('collapsed');
  }
}

componentUtils.registerComponent(
  'hue-sidebar',
  {
    createViewModel: function(params, componentInfo) {
      return new Sidebar(params, componentInfo.element);
    }
  },
  TEMPLATE
);
