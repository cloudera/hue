// Copyright (c) 2017 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/menu
 * @description Renders a link and a menu.
 */
import componentUtils from 'cloudera-ui/ko/components/componentUtils';
import MenuList       from 'cloudera-ui/ko/components/menuList';

import ko from 'knockout';
import _  from '_';

class Menu {
  /**
   * @constructor
   * @alias module:ko/components/menu
   * @param {string} params.menuText
   * @param {array} params.menuItems
   * @param {string} [params.menuClass]
   * @param {boolean} [params.disabled]
   */
  constructor(params, componentInfo) {
    this.menuItems = ko.pureComputed(function() {
      return ko.unwrap(params.menuItems);
    }, this);

    this.menuText = ko.pureComputed(function() {
      return ko.unwrap(params.menuText);
    }, this);

    this.menuCss = ko.pureComputed(function() {
      var result = {
        'dropdown-toggle': true
      };

      if (params.menuClass !== undefined) {
        _.each(ko.unwrap(params.menuClass).split(' '), function(v, k) {
          result[v] = true;
        });
      }

      if (params.disabled !== undefined) {
        result.disabled = ko.unwrap(params.disabled);
      }

      return result;
    }, this);
  }
}

var template = `
<a href="#" data-bind="css: menuCss" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">
<span data-bind="text: menuText"></span> <span class="caret"></span></a>
<ul class="dropdown-menu" data-bind="component: {name: 'cui-menu-list', params: { menuItems: menuItems }}"></ul>
`;

componentUtils.addComponent(Menu, 'cui-menu', template);

module.exports = Menu;
