// Copyright (c) 2017 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/menuList
 * @description Renders a list of menu items.
 */
import componentUtils from 'cloudera-ui/ko/components/componentUtils';
import Link           from 'cloudera-ui/ko/components/link';
import ko from 'knockout';
import _  from '_';

var RETURN_TRUE = function() {
  return true;
};

const DIVIDER = 'divider';
const LINK = 'link';
const DROPDOWN = 'dropdown';

class LinkMenuItem extends Link {
  constructor(params, componentInfo) {
    super(params, componentInfo);
    this.params = params;
    this.type = LINK;
  }
}

class CompositeMenuItem {
  constructor(params) {
    this.type = DROPDOWN;
    this.params = _.extend({
      menuText: ko.unwrap(params.text),
      menuItems: ko.unwrap(params.menuItems),
      disabled: ko.unwrap(params.disabled)
    }, params);
  }
}

class DividerMenuItem {
  constructor() {
    this.type = 'divider';
  }
}

class MenuList {
  /**
   * @constructor
   * @alias module:ko/components/menuList
   * @param {object} params.menuItems
   */
  constructor(params, componentInfo) {
    this.menuItems = ko.pureComputed(function() {
      return _.map(ko.unwrap(params.menuItems), function(item) {
        if (item.type === DIVIDER) {
          return new DividerMenuItem();
        } else if (item.type === LINK) {
          return new LinkMenuItem(item);
        } else if (item.type === DROPDOWN) {
          return new CompositeMenuItem(item);
        }
      });
    }, this);
  }
}

var template = `
<!-- ko foreach: menuItems -->
  <!-- ko if: type === 'link' -->
  <li data-bind="css: { disabled: disabled, active: active }">
    <!-- ko component: { name : 'cui-link', params: params } --><!-- /ko -->
  </li>
  <!-- /ko -->
  <!-- ko if: type === 'divider' -->
  <li class="divider"></li>
  <!-- /ko -->
  <!-- ko if: type === 'dropdown' -->
  <li class="dropdown">
    <!-- ko component: { name: 'cui-menu', params: params } --><!-- /ko -->
  </li>
  <!-- /ko -->
<!-- /ko -->
`;

componentUtils.addComponent(MenuList, 'cui-menu-list', template);

module.exports = MenuList;
