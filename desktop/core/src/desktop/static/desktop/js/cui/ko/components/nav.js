// Copyright (c) 2017 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/nav
 * @description Renders a nav.
 */
import componentUtils from 'cloudera-ui/ko/components/componentUtils';
import Menu from 'cloudera-ui/ko/components/menu';
import ko from 'knockout';
import _ from '_';

class Nav {
  /**
   * @constructor
   * @alias module:ko/components/nav
   * @param {object} params
   * @param {array}  params.items
   * @param {string} [params.navClass]
   */
  constructor(params, componentInfo) {

    this.navCss = ko.pureComputed(function() {
      var result = {
        nav: true
      };

      if (_.isString(params.navClass)) {
        _.each(params.navClass.split(' '), function(v) {
          result[v] = true;
        });
      } else {
        result['nav-tabs'] = true;
      }

      return result;
    }, this);

    this.params = {
      menuItems: params.items
    };
  }
}

var template = `
<ul data-bind="css: navCss, component: { name: 'cui-menu-list', params: params }"></ul>
`;

componentUtils.addComponent(Nav, 'cui-nav', template);

module.exports = Nav;
