// Copyright (c) 2017 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/link
 * @description Renders a link.
 */
import componentUtils from 'cloudera-ui/ko/components/componentUtils';
import ko             from 'knockout';
import _              from '_';

var RETURN_TRUE = function() {
  return true;
};

class Link {
  /**
   * @param {object} params
   * @param {string} params.text
   * @param {boolean} [params.disabled]
   * @param {boolean} [params.active]
   * @param {string} [params.click]
   * @param {string} [params.title]
   * @param {string} [params.class]
   * @param {string} [params.href]
   * @param {object} [params.attributesMap]
   */
  constructor(params, componentInfo) {
    this.attrs = {};

    this.text = ko.pureComputed(function() {
      return ko.unwrap(params.text);
    }, this);

    if (params.disabled !== undefined) {
      this.disabled = ko.pureComputed(function() {
        return ko.unwrap(params.disabled);
      }, this);
    } else {
      this.disabled = false;
    }

    if (params.active !== undefined) {
      this.active = ko.pureComputed(function() {
        return ko.unwrap(params.active);
      }, this);
    } else {
      this.active = false;
    }

    if (params.click != undefined) {
      this.click = params.click;
    } else {
      this.click = RETURN_TRUE;
    }

    if (params.title !== undefined) {
      this.attrs.title = ko.pureComputed(function() {
        return ko.unwrap(params.title);
      }, this);
    }

    if (params['class'] !== undefined) {
      this.attrs['class'] = ko.pureComputed(function() {
        var result = ko.unwrap(params['class']);
        if (ko.unwrap(this.disabled)) {
          result += ' disabled';
        }

        return result;
      }, this);
    }

    if (params.href !== undefined) {
      this.attrs.href = ko.pureComputed(function() {
        return ko.unwrap(params.href);
      }, this);
    } else {
      this.attrs.href = '#';
    }

    if (params.attributesMap) {
      _.each(ko.unwrap(params.attributesMap), function(v, k) {
        this.attrs[k] = v;
      }, this);
    }
  }
}

var template = `<a data-bind="attr: attrs, click: click, text: text"></a>`;

componentUtils.addComponent(Link, 'cui-link', template);

module.exports = Link;
