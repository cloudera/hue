// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @description Provides URL hash functionalities.
 * @module utils/urlHash
 */

var pagebus = require('cloudera-ui/utils/pagebus');
var urlParams = require('cloudera-ui/utils/urlParams');
var $ = require('jquery');
var _ = require('_');

/**
 * @alias module:urlHash
 * @private
 */
var urlHash = {
  /**
   * Path component of the url hash. Ex: /path/goes/here is the path for
   * "#/path/goes/here?a=b&c=d"
   */
  path: '',

  params: {},

  /**
   * The name of the pub/sub event.
   * @const
   */
  HASH_CHANGED_EVENT: 'urlHashChanged',

  /**
   * The event handler when the hash is changed.
   */
  onHashChange: function() {
    this.updateParams();
    this.publishChange();
  },

  /**
   * Notifies subscribers that the hash has changed.
   */
  publishChange: function() {
    pagebus.publish(this.HASH_CHANGED_EVENT, [this.params]);
  },

  /**
   * Extracts the hash value from window.location.href.
   * Firefox decodes the window.location.hash on access which causes
   * encoding issues so we are using this method to get the hash value
   * instead of relying on window.location.hash.
   * See OPSAPS-16614 and https://bugzilla.mozilla.org/show_bug.cgi?id=483304
   */
  getHashValue: function() {
    return window.location.href.split('#')[1] || '';
  },

  /**
   * Updates the hash value with a new value.
   * @param {string} value the new hash value.
   */
  setHashValue: function(value) {
    window.location.hash = value;
  },

  /**
   * Updates the hash value by combining path and params.
   */
  updateHashValue: function() {
    var value = $.param(this.params);
    if (this.path) {
      value = this.path + '?' + value;
    }

    this.setHashValue(value);
  },

  /**
   * Updates the params object from the hash.
   * @private
   */
  updateParams: function() {
    var hash = this.getHashValue();
    if (hash) {
      var parts = hash.split('?');
      var paramStr = parts.pop();
      this.path = _.isEmpty(parts) ? '' : parts[0];
      this.params = urlParams.unparam(paramStr);
    } else {
      this.path = '';
      this.params = {};
    }
  },

  /**
   * Gets the value of a hash key, or the defaultValue otherwise.
   * e.g. if hash is '#foo=F&bar=B', urlHash.get('foo') returns 'F'.
   *
   * @param {string} key The hash key.
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
   * Gets the value of a hash key as an integer.
   *
   * @param {string} key The hash key.
   * @param {string} defaultValue The default value if not present.
   * @return {number}
   */
  getInt: function(key, defaultValue) {
    defaultValue = defaultValue || 0;
    if (!this.params.hasOwnProperty(key)) {
      return defaultValue;
    }

    var value = parseInt(this.params[key], 10);
    return !isNaN(value) ? value : defaultValue;
  },

  /**
   * Sets a single key value hash or a string key and a string value.
   * If the provided value is undefined, the key is removed from the url hash.
   *
   * @param {string|object} key The hash key or the actual object containing
   * all the keys and values as a map.
   * @param {string} value The hash value or undefined if the first argument
   * is an object.
   */
  set: function(key, value) {
    // Get most recent params.
    this.updateParams();

    // Did the user pass in a hash of values to set as params?
    var params = {};
    if (_.isObject(key) && !value) {
      params = key;
    } else {
      params[key] = value;
    }

    _.each(params, function(v, k) {
      if (v === undefined) {
        delete this.params[k];
      } else {
        this.params[k] = v;
      }
    }, this);

    this.updateHashValue();
  },

  /**
   * Removes a key or an array of keys from the url hash.
   *
   * @param {string} key The hash key
   */
  remove: function(key) {
    this.updateParams();
    if (_.isArray(key)) {
      _.each(key, function(k) {
        delete this.params[k];
      }, this);
    } else {
      delete this.params[key];
    }

    this.updateHashValue();
  }
};

// Listens to hashchange events.
if (!window.testMode) {
  $(window).on('hashchange', _.bind(urlHash.onHashChange, urlHash));
}

// Populate params immediately.
urlHash.onHashChange();

module.exports = urlHash;
