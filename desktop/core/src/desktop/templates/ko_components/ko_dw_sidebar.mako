## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%!
  from desktop import conf
  from desktop.lib.i18n import smart_unicode

  from django.utils.translation import ugettext as _
  from desktop.views import _ko
%>

<%def name="dwSidebar()">
  <script type="text/html" id="hue-dw-sidebar-template">
    <div class="sidebar">
      <div class="sidebar-content" data-bind="foreach: items">
        <!-- ko if: $index() !== 0 -->
        <h4 class="sidebar-category-item" data-bind="text: displayName"></h4>
        <!-- /ko -->
        <!-- ko foreach: children -->
        <!-- ko if: $component.collapsed -->
        <a role="button" class="sidebar-item" data-bind="hueLink: url, attr: { title: displayName }, css: { 'active': url === $component.activeUrl() }, tooltip: { placement: 'right' }">
          <span class="sidebar-icon with-tooltip"><!-- ko template: { name: 'app-icon-template' } --><!--/ko--></span>
          <span class="sidebar-item-name" data-bind="text: displayName"></span>
        </a>
        <!-- /ko -->
        <!-- ko ifnot: $component.collapsed -->
        <a role="button" class="sidebar-item" data-bind="hueLink: url, attr: { title: displayName }, css: { 'active': url === $component.activeUrl() }">
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
  </script>

  <script type="text/javascript">
    (function () {

      var DwSidebar = function DwSidebar(params, element) {
        var self = this;
        // self.items =  params.items; // TODO: Once we have the proper apps in cluster config.
        self.items = ko.observableArray([{
          displayName: 'Apps',
          isCategory: true,
          children: [
            { displayName: 'Editor', url: '/editor/?type=impala', icon: 'editor' },
            { displayName: 'Catalog', url: '/metastore/tables', icon: 'tables' },
            { displayName: 'Warehouses', url: '/hue/jobbrowser', icon: 'warehouses' },
            { displayName: 'Importer', url: '/indexer/importer', icon: 'hdfs' }
          ]
        }]);
        self.collapsed = ko.observable(true);
        self.collapsed.subscribe(function (newVal) {
          if (newVal) {
            $(element).addClass('collapsed')
          } else {
            $(element).removeClass('collapsed')
          }
        });

        self.activeUrl = ko.observable();

        // TODO: Figure out why it gets fired 30+ times on load
        var throttle = -1;
        huePubSub.subscribe('set.current.app.name', function (appName) {
          window.clearTimeout(throttle);
          if (!appName) {
            return;
          }
          throttle = window.setTimeout(function () {
            self.items().some(function (item) {
              return item.children.some(function (child) {
                if (child.url.indexOf(appName.replace('_', '/')) !== -1) {
                  if (self.activeUrl !== child.url) {
                    self.activeUrl(child.url);
                  }
                  return true;
                }
              })
            });
          }, 20);
        });
        huePubSub.publish('get.current.app.name');
      };

      ko.components.register('hue-dw-sidebar', {
        viewModel: {
          createViewModel: function (params, componentInfo) {
            return new DwSidebar(params, componentInfo.element);
          }
        },
        template: { element: 'hue-dw-sidebar-template' }
      });
    })();
  </script>
</%def>