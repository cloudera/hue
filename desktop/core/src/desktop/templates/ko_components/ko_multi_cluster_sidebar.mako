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

<%def name="multiClusterSidebar()">

  <script type="text/html" id="hue-multi-cluster-sidebar-template">
    <div class="sidebar-content" data-bind="foreach: categories">
      <!-- ko if: typeof label !== 'undefined' -->
      <h4 class="sidebar-category-item" data-bind="text: label"></h4>
      <!-- /ko -->
      <!-- ko foreach: items -->
      <!-- ko if: typeof items == 'undefined' -->
      <a role="button" class="sidebar-item" data-bind="css: { 'active': false }, hueLink: url, attr: { 'title': label">
        <span class="sidebar-icon without-tooltip">
          <span data-bind="css: icon"></span>
        </span>
        <span class="sidebar-item-name" data-bind="text: label"></span>
      </a>
      <!-- /ko -->
      <!-- ko if: typeof items !== 'undefined' -->
      <a role="button" class="sidebar-item" href="javascript: void(0);" data-bind="sidebarSubmenuActivator, css: { 'active': false }, attr: {'title': label">
        <span class="sidebar-icon without-tooltip">
          <span data-bind="css: icon"></span>
        </span>
        <span class="sidebar-item-name" data-bind="text: label"></span>
        <i class="submenu-icon fa fa-chevron-right"></i>
      </a>
      <div class="sidebar-submenu" style="display:none;" data-bind="foreach: items">
        <a role="button" class="sidebar-submenu-item" data-bind="hueLink: url, attr: { 'title': label }, text: label"></a>
      </div>
      <!-- /ko -->
      <!-- /ko -->
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      ko.bindingHandlers.sidebarSubmenuActivator = {
        init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
          var $element = $(element);
          var $menu = $element.next();
          var visible = false;
          var hideTimeout = -1;

          var show = function () {
            window.clearTimeout(hideTimeout);
            if (!visible) {
              $menu.css({ 'top': $element.offset().top + 'px' });
              huePubSub.publish('hue.sidebar.hide.submenus');
              $menu.show();
              visible = true;
            }
          };

          var hide = function () {
            hideTimeout = window.setTimeout(function () {
              if (visible) {
                $menu.hide();
                visible = false;
              }
            }, 300);
          };

          var hideSub = huePubSub.subscribe('hue.sidebar.hide.submenus', function () {
            window.clearTimeout(hideTimeout);
            $menu.hide();
            visible = false;
          });

          $element.on('click', show);
          $element.on('mouseover', show);
          $element.on('mouseout', hide);
          $menu.on('mouseover', show);
          $menu.on('mouseout', hide);

          ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
            $menu.hide();
            hideSub.remove();
            $element.off('click');
            $element.off('mouseover');
            $element.off('mouseout');
            $menu.off('mouseover');
            $menu.off('mouseout');
          });
        }
      };

      // TODO: Fetch menu from the backend
      var FIXED_CATEGORIES = [{
        items: [{
          label: '${ _('Home') }',
          url: '/',
          icon: 'fa fa-home'
        }, {
          label: '${ _('Data Assistant') }',
          icon: 'altus-icon altus-adb-query',
          items: [{
              label: '${ _('Editor') }',
              url: '/editor?type=impala'
            },{
              label: '${ _('Catalog') }',
              url: '/metastore/tables'
            },{
              label: '${ _('Files') }',
              url: '/filebrowser/view=S3A://'
            },{
              label: '${ _('Dashboard') }',
              url: '/dashboard/new_search'
            },{
              label: '${ _('Scheduler') }',
              url: '/oozie/editor/coordinator/new/'
            },{
              label: '${ _('Importer') }',
              url: '/indexer/importer'
            }
          ]
        }, {
          label: '${ _('Data Science') }',
          url: '/',
          icon: 'altus-icon altus-ds'
        }
      ]
      }, {
        label: '${ _('Admin') }',
        items: [{
            label: '${ _('Environments') }',
            url: '/',
            icon: 'altus-icon altus-environment'
          },{
            label: '${ _('Directory') }',
            url: 'https://console.altus.cloudera.com/iam/index.html',
            icon: 'altus-icon altus-iam',
            items: [{
                label: '${ _('User') }',
                url: 'https://console.altus.cloudera.com/iam/index.html#/users'
              },{
                label: '${ _('Groups') }',
                url: 'https://console.altus.cloudera.com/iam/index.html#/groups'
              }
            ]
          }
        ]
      }, {
        label: '${ _('Storage') }',
        items: [{
            label: '${ _('Catalog') }',
            url: '/',
            icon: 'altus-icon altus-sdx'
          },{
            label: '${ _('Streaming') }',
            url: '/',
            icon: 'fa fa-sitemap'
          },{
            label: '${ _('Operational DB') }',
            url: '/',
            icon: 'altus-icon altus-adb',
            items: [{
                label: '${ _('Kudu') }',
                url: '/'
              },{
                label: '${ _('HBase') }',
                url: '/'
              }
            ]
          }
        ]
      }, {
        label: '${ _('Compute') }',
        items: [{
            label: '${ _('Data Warehouse') }',
            icon: 'altus-icon altus-dashboard',
            url: '/'
          }, {
            label: '${ _('Data Engineering') }',
            icon: 'altus-icon altus-de',
            items: [{
                label: '${ _('Clusters') }',
                url: '/'
              },{
                label: '${ _('Jobs') }',
                url: '/'
              }
            ]
          }, {
            label: '${ _('Scheduling') }',
            icon: 'altus-icon altus-workload',
            url: '/'
          }
        ]
      }
        ##  , {
        ##    label: '${ _('Icons') }',
        ##    items: [{label: 'altus-adb-cluster', url: '/', icon: 'altus-icon altus-adb-cluster'},
        ##      {label: 'altus-environment', url: '/', icon: 'altus-icon altus-environment'},
        ##      {label: 'altus-dashboard', url: '/', icon: 'altus-icon altus-dashboard'},
        ##      {label: 'altus-iam', url: '/', icon: 'altus-icon altus-iam'},
        ##      {label: 'altus-user-group', url: '/', icon: 'altus-icon altus-user-group'},
        ##      {label: 'altus-de-cluster', url: '/', icon: 'altus-icon altus-de-cluster'},
        ##      {label: 'altus-de-job', url: '/', icon: 'altus-icon altus-de-job'},
        ##      {label: 'altus-adb', url: '/', icon: 'altus-icon altus-adb'},
        ##      {label: 'altus-de', url: '/', icon: 'altus-icon altus-de'},
        ##      {label: 'altus-ds', url: '/', icon: 'altus-icon altus-ds'},
        ##      {label: 'altus-sdx', url: '/', icon: 'altus-icon altus-sdx'},
        ##      {label: 'altus-na', url: '/', icon: 'altus-icon altus-na'},
        ##      {label: 'altus-no-access', url: '/', icon: 'altus-icon altus-no-access'},
        ##      {label: 'altus-user-access', url: '/', icon: 'altus-icon altus-user-access'},
        ##      {label: 'altus-adb-query', url: '/', icon: 'altus-icon altus-adb-query'},
        ##      {label: 'altus-workload', url: '/', icon: 'altus-icon altus-workload'},
        ##      {label: 'altus-azure', url: '/', icon: 'altus-icon altus-azure'},
        ##      {label: 'altus-aws', url: '/', icon: 'altus-icon altus-aws'},
        ##      {label: 'altus-user', url: '/', icon: 'altus-icon altus-user'},
        ##      {label: 'altus-sql-editor', url: '/', icon: 'altus-icon altus-sql-editor'},
        ##      {label: 'altus-feedback', url: '/', icon: 'altus-icon altus-feedback'}]
        ##  }
      ];

      var MultiClusterSidebar = function MultiClusterSidebar() {
        var self = this;
        self.categories = ko.observableArray(FIXED_CATEGORIES);
      };

      ko.components.register('hue-multi-cluster-sidebar', {
        viewModel: MultiClusterSidebar,
        template: { element: 'hue-multi-cluster-sidebar-template' }
      });
    })();
  </script>
</%def>