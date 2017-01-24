// (c) Copyright 2015 Cloudera, Inc. All rights reserved.
/**
 * @module ko/bindings/selectpicker
 * @description Knockout binding to decorate a &lt;select&gt; tag with bootstrap.
 */

var $ = require('jquery');
var ko = require('knockout');
var _ = require('_');
require('bootstrap/dropdown');
require('bootstrap-select');

// this code was stolen from bootstrap-multiselect's implementation of knockout bindings.
// Which does the same thing we want for bootstrap-select.
/**
 * @param {string} nativeBinding The lookup of a binding string.
 * @param {object} allBindingsAccessor All the ko bindings on the &lt;select&gt; node.
 * @param {jQuery} $element A jquery wrapped &lt;select&gt; node.
 * @private
 */
function subscribeToNativeKOBinding(nativeBinding, allBindingsAccessor, $element) {
  if (allBindingsAccessor.has(nativeBinding)) {
    var binding = allBindingsAccessor.get(nativeBinding);
    if (ko.isObservable(binding)) {
      binding.subscribe(function(bindingValue) {
          $element.selectpicker('refresh');
        });
    }
  }
}

ko.bindingHandlers.selectpicker = {
  after: ['options', 'value', 'selectedOptions', 'enable', 'disable'],
  /**
   * @param {Node} element The DOM element for this binding.
   * @param {observable:object} valueAccessor The right-hand side value for the binding handler.  If it is an observable, the binding handler will invoke the update function below.
   * @param {observable} allBindingsAccessor A knockout computed that, when unwrapped, will return all the knockout bindings for this DOM element.
   * @param {*} viewModel Deprecated, use $data in bindingContext.
   * @param {object} bindingContext The current node of the context tree.
   */
  init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    var $element = $(element);
    var config = ko.unwrap(valueAccessor()) || {};

    // if the <select> element emits a change event, refresh the select picker.
    ko.utils.registerEventHandler(element, 'change', function() {
      $element.selectpicker('refresh');
    });

    subscribeToNativeKOBinding('value', allBindingsAccessor, $element);
    subscribeToNativeKOBinding('options', allBindingsAccessor, $element);
    subscribeToNativeKOBinding('enable', allBindingsAccessor, $element);
    subscribeToNativeKOBinding('disable', allBindingsAccessor, $element);

    $element.selectpicker(config);
    var $wrapperElement = $element.parent();

    // Add our own css class so we can override colors
    $wrapperElement.addClass('cui-bootstrap-select');
  },

  /**
   * @param {Node} element The DOM element for this binding.
   * @param {observable:object} valueAccessor The right-hand side value for the binding handler.  If it is an observable, it needs to return an object of attributes that selectpicker accepts.
   */
  update: function(element, valueAccessor) {
    var $element = $(element);
    var config = ko.unwrap(valueAccessor()) || {};

    $element.selectpicker(config);
    $element.selectpicker('refresh');
  }
};
