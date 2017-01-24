// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module utils/sessionStorage
 * @description This module provides session storage abstraction.
 */
var _ = require('_');

module.exports = {
  /**
   * Stores an item into sessionStorage.
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
    if (sessionStorage) {
      if (_.isNull(value) || _.isUndefined(value)) {
        sessionStorage.removeItem(key);
      } else if (_.isString(value)) {
        sessionStorage.setItem(key, value);
      } else if (_.isNumber(value)) {
        sessionStorage.setItem(key, value);
      } else if (_.isBoolean(value)) {
        sessionStorage.setItem(key, value ? 'true' : 'false');
      } else if (_.isObject(value) || _.isArray(value)) {
        sessionStorage.setItem(key, JSON.stringify(value));
      }
    }
  },

  /**
   * Retrieves an item from sessionStorage.
   *
   * @param key
   * @param return a JavaScript object if the string value
   * stored is in JSON format, else returns the value as a string.
   */
  getItem: function(key) {
    if (sessionStorage) {
      var result, value = sessionStorage.getItem(key);
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
