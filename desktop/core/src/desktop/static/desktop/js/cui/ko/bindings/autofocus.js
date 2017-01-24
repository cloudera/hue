// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/bindings/autofocus
 * @description Knockout binding handler "autofocus" will apply focus to an element.
 * The element will need to have a tabindex if it is not
 * a form element like input or button etc..
 *
 * @example
 * <span tabindex=0 data-bind="autofocus: true">
 * I get focus when dynamically added to a page
 * </span>
 */
var $ = require('jquery');
var ko = require('knockout');

ko.bindingHandlers.autofocus = {
  init: function(element, valueAccessor) {
    var value = ko.utils.unwrapObservable(valueAccessor());

    if (value) {
      $(element).focus();
    }
  }
};
