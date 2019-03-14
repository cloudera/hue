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
import componentUtils from './componentUtils';
import huePubSub from 'utils/huePubSub';

const TEMPLATE = `
  <div class="hue-dw-brand" data-bind="css: { 'collapsed': collapsed }, toggle: leftNavVisible">
    <img src="${window.STATIC_URLS['desktop/art/cloudera-data-warehouse-3.svg']}">
  </div>

  <div class="sidebar">
    <div class="sidebar-content" data-bind="foreach: items">
      <!-- ko if: $index() !== 0 -->
      <h4 class="sidebar-category-item" data-bind="text: displayName"></h4>
      <!-- /ko -->
      <!-- ko foreach: children -->
      <!-- ko if: $component.collapsed -->
      <a role="button" class="sidebar-item" data-bind="hueLink: url, attr: { title: displayName }, css: { 'active': url === $component.activeUrl() }, tooltip: { placement: 'right' }, click: function() { if (url.startsWith('/jobbrowser')) { huePubSub.publish('context.selector.set.cluster', 'AltusV2'); } }">
        <!-- ko ifnot: $component.collapsed -->
        <span class="sidebar-caret"><i class="fa fa-caret-right"></i></span>
        <!-- /ko -->
        <span class="sidebar-icon with-tooltip"><!-- ko template: { name: 'app-icon-template' } --><!--/ko--></span>
        <span class="sidebar-item-name" data-bind="text: displayName"></span>
      </a>
      <!-- /ko -->
      <!-- ko ifnot: $component.collapsed -->
      <a role="button" class="sidebar-item" data-bind="hueLink: url, attr: { title: displayName }, css: { 'active': url === $component.activeUrl() }, click: function() { if (url.startsWith('/jobbrowser')) { huePubSub.publish('context.selector.set.cluster', 'AltusV2'); } }">
        <!-- ko ifnot: $component.collapsed -->
        <span class="sidebar-caret"><i class="fa fa-caret-right"></i></span>
        <!-- /ko -->
        <span class="sidebar-icon without-tooltip"><!-- ko template: { name: 'app-icon-template' } --><!--/ko--></span>
        <span class="sidebar-item-name" data-bind="text: displayName"></span>
      </a>
      <!-- /ko -->
      <!-- /ko -->
    </div>
    <a class="sidebar-action-button" role="button" data-bind="toggle: collapsed">
      <span aria-hidden="true" class="fa" data-bind="css: { 'fa-angle-double-right': collapsed, 'fa-angle-double-left': !collapsed() }"></span>
    </a>
  </div>
`;

class DwSidebar {
  constructor(params, element) {
    const self = this;
    self.pocClusterMode = params.pocClusterMode;
    // self.items =  params.items; // TODO: Once we have the proper apps in cluster config.

    self.leftNavVisible = ko.observable(false);
    self.leftNavVisible.subscribe(val => {
      huePubSub.publish('hue.toggle.left.nav', val);
    });

    self.items = ko.pureComputed(() => {
      const appCategory = {
        displayName: 'Apps',
        isCategory: true
      };
      if (self.pocClusterMode() === 'dw') {
        appCategory.children = [
          { displayName: 'Editor', url: '/editor/?type=impala', icon: 'editor' },
          { displayName: 'Catalog', url: '/metastore/tables', icon: 'tables' },
          { displayName: 'Importer', url: '/indexer/importer', icon: 'hdfs' },
          { displayName: 'Warehouses', url: '/jobbrowser#!dataware2-clusters', icon: 'warehouses' },
          { displayName: 'Dashboards', url: '/dashboard', icon: 'dashboard' }
        ];
      } else {
        // DE mode
        appCategory.children = [
          { displayName: 'Editor', url: '/editor/?type=hive', icon: 'editor' },
          { displayName: 'Dashboard', url: '/jobbrowser/#!workflows', icon: 'tables' },
          { displayName: 'Workflows', url: '/oozie/editor/workflow/new', icon: 'workflows' },
          {
            displayName: 'Service',
            url: '/hue/jobbrowser/#!dataware2-clusters',
            icon: 'warehouses'
          }
        ];
      }

      return [appCategory];
    });

    self.collapsed = ko.observable();
    self.collapsed.subscribe(newVal => {
      if (newVal) {
        $(element).addClass('collapsed');
      } else {
        $(element).removeClass('collapsed');
      }
    });
    apiHelper.withTotalStorage('sidebar', 'collapsed', self.collapsed, false);

    self.activeUrl = ko.observable();

    // TODO: Figure out why it gets fired 30+ times on load
    let throttle = -1;
    huePubSub.subscribe('set.current.app.name', appName => {
      window.clearTimeout(throttle);
      if (!appName) {
        return;
      }
      throttle = window.setTimeout(() => {
        self.items().some(item => {
          return item.children.some(child => {
            if (location.href.indexOf(child.url) !== -1) {
              if (self.activeUrl !== child.url) {
                self.activeUrl(child.url);
              }
              return true;
            }
          });
        });
      }, 20);
    });
    huePubSub.publish('get.current.app.name');
  }
}

componentUtils.registerComponent(
  'hue-dw-sidebar',
  {
    createViewModel: function(params, componentInfo) {
      return new DwSidebar(params, componentInfo.element);
    }
  },
  TEMPLATE
);
