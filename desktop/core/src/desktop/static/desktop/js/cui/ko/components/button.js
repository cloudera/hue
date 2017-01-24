// Copyright (c) 2017 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/button
 * @description Renders a button.
 */
import componentUtils from 'cloudera-ui/ko/components/componentUtils';
import ko             from 'knockout';
import _              from '_';

class Button {
  /**
   * @param {object} params
   * @param {string} params.text
   * @param {boolean} [params.disabled]
   * @param {string} [params.click]
   * @param {string} [params.class]
   */
  constructor(params, componentInfo) {
    this.attrs = {};

    this.text = ko.pureComputed(function() {
      return ko.unwrap(params.text);
    }, this);

    if (params.disabled !== undefined) {
      this.attrs.disabled = ko.pureComputed(function() {
        return ko.unwrap(params.disabled);
      }, this);
    } else {
      this.attrs.disabled = false;
    }

    if (params.click != undefined) {
      this.click = params.click;
    } else {
      this.click = _.noop;
    }

    if (params['class'] !== undefined) {
      this.attrs['class'] = ko.pureComputed(function() {
        return 'btn ' + ko.unwrap(params['class']);
      }, this);
    } else {
      this.attrs['class'] = 'btn btn-default';
    }
  }
}

var template = `<button data-bind="attr: attrs, disabled: disabled, click: click, text: text"></button>`;

componentUtils.addComponent(Button, 'cui-button', template);

module.exports = Button;
