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

import componentUtils from './componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

const TEMPLATE = `
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
`;

ko.bindingHandlers.sidebarSubmenuActivator = {
  init: function(element) {
    const $element = $(element);
    const $menu = $element.next();
    let visible = false;
    let hideTimeout = -1;

    const show = function() {
      window.clearTimeout(hideTimeout);
      if (!visible) {
        $menu.css({ top: $element.offset().top + 'px' });
        huePubSub.publish('hue.sidebar.hide.submenus');
        $menu.show();
        visible = true;
      }
    };

    const hide = function() {
      hideTimeout = window.setTimeout(() => {
        if (visible) {
          $menu.hide();
          visible = false;
        }
      }, 300);
    };

    const hideSub = huePubSub.subscribe('hue.sidebar.hide.submenus', () => {
      window.clearTimeout(hideTimeout);
      $menu.hide();
      visible = false;
    });

    $element.on('click', show);
    $element.on('mouseover', show);
    $element.on('mouseout', hide);
    $menu.on('mouseover', show);
    $menu.on('mouseout', hide);

    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
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
const FIXED_CATEGORIES = [
  {
    items: [
      {
        label: I18n('Data Warehouse'),
        icon: 'altus-icon altus-adb-query',
        url: '/editor?type=impala'
      },
      {
        label: I18n('Data Science'),
        url: '/',
        icon: 'altus-icon altus-ds'
      },
      {
        label: I18n('Admin'),
        url: '/',
        icon: 'altus-icon altus-de'
      }
    ]
  }
];

class MultiClusterSidebar {
  constructor() {
    const self = this;
    self.categories = ko.observableArray(FIXED_CATEGORIES);
  }
}

componentUtils.registerComponent('hue-multi-cluster-sidebar', MultiClusterSidebar, TEMPLATE);
