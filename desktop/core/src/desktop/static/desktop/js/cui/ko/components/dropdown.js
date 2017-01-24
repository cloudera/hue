// Copyright (c) 2017 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/dropdown
 * @description Renders a dropdown.
 */
import componentUtils from 'cloudera-ui/ko/components/componentUtils';
import Menu           from 'cloudera-ui/ko/components/menu';

import ko from 'knockout';
import _  from '_';

class Dropdown {
  /**
   * @constructor
   * @alias module:ko/components/dropdown
   * @param {string} params.menuText
   * @param {array} params.menuItems
   * @param {string} [params.menuClass]
   * @param {boolean} [params.disabled]
   */
  constructor(params, componentInfo) {
    var menuClass = '';

    if (params.menuClass !== undefined) {
      menuClass = ko.unwrap(params.menuClass);
    } else {
      menuClass = 'btn btn-default';
    }

    this.params = _.extend({
      menuClass: menuClass
    }, params);
  }
}

var template = `
<div class="dropdown" data-bind="component: { name: 'cui-menu', params: params }"></div>
`;

componentUtils.addComponent(Dropdown, 'cui-dropdown', template);

module.exports = Dropdown;
