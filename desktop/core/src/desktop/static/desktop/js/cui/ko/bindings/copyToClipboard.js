// (c) Copyright 2016 Cloudera, Inc. All rights reserved.

var ko = require('knockout');
var $ = require('jquery');
var _ = require('_');
var i18n = require('cloudera-ui/utils/i18n');

/**
 * Note: This module has a third party dependency on: https://github.com/zenorocha/document.queryCommandSupported
 * This module provides a cross browser polyfill for detecting browser copy/cut support.
 */
require('query-command-supported');

var copyPasteTemplate = `
<a title="${i18n.t('ko.bindings.copyToClipboard.title')}"
  data-bind="click: copyToClipboard, css: {'glyphicon glyphicon-copy': useGlyphicon}, text: copyButtonLabel"
  class="cui-copy-to-clipboard btn btn-default"></a>
<span class="copyMessage">${i18n.t('ko.bindings.copyToClipboard.success')}</span>
`;

ko.bindingHandlers.copyToClipboard = {
  execCopy: function execCopy() {
    return document.execCommand('copy');
  },

  /**
   * @param {Node} element A dom element we are binding to.
   * @param {object} valueAccessor The observable data passed into the right hand side of the binding name.
   * @param {boolean} valueAccessor.resetWhen Boolean observable that signals to reset the widget.
   * @param {Node|string} valueAccessor.container The element to append to. Otherwise, we insert it after the input.
   * @param {string} [valueAccessor.label] The desired text to go in the copy/paste button. Defaults to copy/paste glyphicon.
   */
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    var isSupported = document.queryCommandSupported('copy');
    if (!isSupported) {
      // no browser support, don't inject the button.
      return undefined;
    }

    var value = valueAccessor() || {};

    var $element = $(element);
    var $input = $element.find(':input:first');

    var $container;
    var $copyPaste;
    if (value.container) {
      $container = $(ko.unwrap(value.container));
      $copyPaste = $(copyPasteTemplate).appendTo($container);
    } else {
      $container = $input;
      $copyPaste = $(copyPasteTemplate).insertAfter($container);
    }

    var $message = $copyPaste.last();
    $message.hide();
    if (ko.isObservable(value.resetWhen)) {
      value.resetWhen.subscribe(function() {
        $message.hide();
      });
    }

    $input.addClass('cui-clipboard-input');

    var label = value.label || '';

    var innerBindingContext = bindingContext.extend({
      useGlyphicon: _.isEmpty(label),
      copyButtonLabel: label,
      copyToClipboard: function(viewModel, event) {
        var $button = $(event.target);
        $input.focus().select();
        ko.bindingHandlers.copyToClipboard.execCopy();
        $message.show();
      }
    });
    ko.applyBindingsToDescendants(innerBindingContext, element);

    return { controlsDescendantBindings: true };
  }
};
