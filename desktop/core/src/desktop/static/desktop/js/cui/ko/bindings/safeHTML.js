// (c) Copyright 2016 Cloudera, Inc. All rights reserved.

/**
 * @module ko/bindings/safeHTML
 * @description This module depends on DOMPurify, which must be
 * installed and added to the require paths config.
 * https://www.npmjs.com/package/dompurify
 */
var ko = require('knockout');
var DOMPurify = require('dompurify');

/**
 * Strips an HTML string of executable JavaScript
 * @param  {string} dirtyString - potentially tainted HTML
 * @return {string}             - safe HTML
 */
var sanitizeHTML = function(dirtyString) {
  if (typeof dirtyString !== 'string') {
    return '';
  }

  return DOMPurify.sanitize(dirtyString, {
    SAFE_FOR_JQUERY: true
  });
};

ko.bindingHandlers.safeHTML = {
  update: function(element, valueAccessor) {
    var rawHTML = ko.unwrap(valueAccessor());
    ko.utils.setHtml(element, sanitizeHTML(rawHTML));
  }
};
