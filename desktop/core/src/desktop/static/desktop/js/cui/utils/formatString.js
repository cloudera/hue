// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
var _ = require('_');
/*jslint regexp: true */

// Find {string} or {numeric} placeholders
var expression = /\{(?:(\d*)|([^\}]*))\}/g;
/*jslint regexp: false */

/**
 * Replaces all instances of {property} or {index} with
 * with the equivalent properties of the params object or value from the params array.
 * @param {string} str The template string to formatString.
 * @param {object|array} params The params to formatString the string with.
 * @param {boolean} encode A truthy value will cause the injected values to be encodeURIComponent encoded.
 * @return {string}
 */
module.exports = function(str, params, encode) {
  var result = '',
      lastMatch = 0,
      currentMatch,
      currentValue;

  while (true) {
    currentMatch = expression.exec(str);
    if (!currentMatch) {
      if (lastMatch !== str.length) {
        result += str.substring(lastMatch);
      }

      return result;
    }

    result += str.substring(lastMatch, currentMatch.index);

    if (currentMatch[1]) {
      currentValue = params[parseInt(currentMatch[1], 10)];
    } else {
      currentValue = params[currentMatch[2]];
    }

    if (!_.isUndefined(currentValue)) {
      result += encode ? encodeURIComponent(currentValue).replace(/ /g, '+') : currentValue;
    }

    lastMatch = currentMatch.index + currentMatch[0].length;
  }
};
