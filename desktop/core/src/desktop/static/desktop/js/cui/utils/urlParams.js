// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @description Provides URL query parameter functionalities.
 * @module utils/urlParams
 */

var $ = require('jquery');
var _ = require('_');

/**
 * Performs jQuery.param on an object.
 * @alias module:param
 * @param {object} param query parameters as a key-value object.
 * @return {string}
 * @example
 * var res = param({a: 'A', b: 'B'})
 * // res now contains
 * a=A&b=B
 */
var param = function(param) {
  return $.param(param);
};

/**
 * Performs the inverse of jQuery.param
 *
 * The generalized form of this method is more complicated than this.
 * Replace this method with a more generalized form, e.g.
 * @see: http://stackoverflow.com/questions/1131630/javascript-jquery-param-inverse-function
 *
 * @alias module:unparam
 * @param {string} queryParams The query parameters.
 * @return {object}
 * @example
 * var res = unparam('a=A&b=B');
 * // res now contains
 * { a: 'A', b: 'B' }
 */
var unparam = function(queryParams) {
  var ret = {}, i, name, value, eqPos, nv, nvs;

  nvs = queryParams.replace(/\+/g, ' ').split('&');

  for (i = 0; i < nvs.length; ++i) {
    nv = nvs[i];
    eqPos = nv.indexOf('=');
    if (eqPos !== -1) {
      name = decodeURIComponent(nv.substring(0, eqPos));
      value = decodeURIComponent(nv.substring(eqPos + 1));
      ret[name] = value;
    }
  }

  return ret;
};

module.exports = {
  params: unparam(window.location.search.substring(1)),

  /**
   * Gets the value of the location.search as a map. e.g. if location.search is '?foo=F&bar=B',
   * urlParams.get('foo') returns 'F'.
   *
   * @param {string} key The parameter key.
   * @param {string} defaultValue The default value if not present.
   * @return {string}
   */
  get: function(key, defaultValue) {
    if (!this.params.hasOwnProperty(key)) {
      return defaultValue;
    }

    return this.params[key];
  },

  /**
   * Sort params to make them predictable as a lookup key.
   * Returns the params as a sorted string: {b:1, a:2} => 'a=2&b=1'
   * @param {object} params A simple object with non-complex values.
   * @return {string}
   */
  paramSorted: function(params) {
    return _.chain(params)
      .pairs()
      .sortBy(_.first)
      .map(function(a) {
        return a.join('=');
      })
      .value().join('&');
  },

  unparam: unparam,

  param: param
};
