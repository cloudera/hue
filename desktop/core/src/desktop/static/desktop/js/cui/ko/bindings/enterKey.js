// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/bindings/enterKey
 * @description Knockout binding handler to handle ENTER key pressed.
 * It lets you easily bind DOM elements to some behavior on the model.
 *
 * @example
 * <input type="text" data-bind="value: myValue,
 *                               valueUpdate: 'afterkeydown',
 *                               enterKey: handleEnterKey" />
 */
var $ = require('jquery');
var ko = require('knockout');

var ENTER_KEY_CODE = 13;

ko.bindingHandlers.enterKey = {
  init: function(element, valueAccessor, allBindings, data, context) {
    var wrapper = function(data, evt) {
      var code = evt.keyCode || evt.which;
      if (code === ENTER_KEY_CODE) {
        valueAccessor().call(this, data, evt);
        return false;
      }

      return true;
    };

    ko.applyBindingsToNode(element, { event: { keypress: wrapper } }, context);
  }
};
