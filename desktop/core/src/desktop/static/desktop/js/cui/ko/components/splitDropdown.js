// Copyright (c) 2017 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/SplitDropdown
 * @description Renders a SplitDropdown.
 */
import componentUtils from 'cloudera-ui/ko/components/componentUtils';
import Dropdown       from 'cloudera-ui/ko/components/dropdown';
import ko from 'knockout';
import _  from '_';

class SplitDropdown extends Dropdown {
  /**
   * @constructor
   * @alias module:ko/components/SplitDropdown
   * @param {object} params
   * @param {string} params.linkText
   * @param {function} params.linkClick
   * @param {array} params.menuItems
   * @param {string} [params.menuText]
   * @param {string} [params.menuClass]
   * @param {boolean} [params.disabled]
   */
  constructor(params, componentInfo) {
    super(params, componentInfo);

    this.linkText = ko.pureComputed(function() {
      return ko.unwrap(params.linkText);
    }, this);

    this.linkCss = ko.pureComputed(function() {
      var result = {};

      if (params.menuClass !== undefined) {
        _.each(ko.unwrap(this.params.menuClass).split(' '), function(v) {
          result[v] = true;
        });
      }

      if (params.disabled !== undefined) {
        result.disabled = ko.unwrap(params.disabled);
      }

      return result;
    }, this);

    this.click = params.linkClick;
  }
}

var template = `
<div class="btn-group">
<a href="#" data-bind="css: linkCss, click: click, text: linkText"></a>
<!-- ko component: { name: 'cui-menu', params: params } --><!-- /ko -->
</div>`;

componentUtils.addComponent(SplitDropdown, 'cui-split-dropdown', template);

module.exports = SplitDropdown;
