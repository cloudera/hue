// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module utils/localStorage
 * @description This module provides local storage abstraction.
 */
var _ = require('_');

module.exports = {
  /**
   * Stores an item into localStorage.
   *
   * @param {string} key
   * @param {object} value - the item to store.
   * Today, we support only strings or a JavaScript object.
   * To store boolean/a number, construct a JavaScript object instead.
   * e.g.:{
   *   value = true;
   * };
   */
  setItem: function(key, value) {
    if (localStorage) {
      if (_.isNull(value)) {
        localStorage.removeItem(key);
      } else if (_.isString(value)) {
        localStorage.setItem(key, value);
      } else if (_.isNumber(value)) {
        localStorage.setItem(key, value);
      } else if (_.isBoolean(value)) {
        localStorage.setItem(key, value ? 'true' : 'false');
      } else if (_.isObject(value) || _.isArray(value)) {
        localStorage.setItem(key, JSON.stringify(value));
      }
    }
  },

  /**
   * Retrieves an item from localStorage.
   *
   * @param key
   * @param return a JavaScript object if the string value
   * stored is in JSON format, else returns the value as a string.
   */
  getItem: function(key) {
    if (localStorage) {
      var result, value = localStorage.getItem(key);
      if (value === null || _.isUndefined(value)) {
        return null;
      }

      if (_.isEmpty(value)) {
        return '';
      }

      try {
        result = JSON.parse(value);
        if (result !== null) {
          return result;
        }
      } catch (ex) {
        result = value;
      }

      return result;
    }

    return undefined;
  }
};
