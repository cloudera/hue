// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module utils/i18n
 * @description This module provides internationalization related functionality.
 * The resources available to this module are controlled by the i18n/client.label.txt and i18n/client.message.txt
 * files and the ClientResources component.
 */

var formatString = require('cloudera-ui/utils/formatString');
var _ = require('_');

var language = {};

module.exports = {
  /**
   * Retrieves a localized string from the string table and formats it if necessary.
   * @param {string} key The key associated with the string in the string table.
   * @return {string}
   * @see module:formatString
   * @example
   * assume label.properties contains:
   * message.key1=Hello World
   * message.key2=Hello {0}, {1}?
   *
   * var msg1 = i18n.t('message.key1');
   * // msg1 now returns Hello World
   *
   * var msg2 = i18n.t('message.key2', ['Joe', 'How are you?');
   * // msg2 now returns Hello Joe, How are you?
   */
  t: function(key) {
    var args,
        message;

    if (arguments.length > 1) {
      // Convert the arguments to an array.
      args = _.toArray(arguments);

      // If there are more than 2 arguments or argument one is not an object, treat it as a vararg.
      if (args.length > 2 || !_.isObject(args[1])) {

        // Replace the key with its associated string.
        key = args.shift();
        message = language[key] || key;

        args = [message, args];
      } else {

        // Replace the key with its associated string.
        key = args[0];
        args[0] = language[key] || key;
      }

      return formatString.apply(this, args);
    }

    return language[key] || key;
  },

  /**
   * Instead of having to repeat `label.xxxxxxxx.name` for every i18n call
   * create a shorthand. Useful when having many i18n calls all with
   * the same starting key, so only the unique part of the key needs to be
   * repeated e.g.
   *
   *  //direct usage
   *  i18n.t('label.eventWhiteList.log.info')
   *  i18n.t('label.eventWhiteList.log.alert')
   *  i18n.t('label.eventWhiteList.log.warn')
   *  i18n.t('label.eventWhiteList.log.errorMessage', 'Build')
   *
   *  //shorthand usage
   *  var lang = getShortHandFor('label.eventWhiteList.log')
   *  lang('info')
   *  lang('alert')
   *  lang('warn')
   *  lang('errorMessage', 'Build')
   *
   * getShorthandFor() will return a function that creates the proper key
   * and will pass it off to i18n.t() internally so the same arguments/format
   * can be used.
   *
   * @param  {string} path first part of the key/path that is the same
   * for all calls
   * @return {function} wrapper around the regular i18n.t() to construct
   * the key
   */
  getShorthandFor: function(path) {
    return _.bind(function(lastKey) {
      var key = path + '.' + lastKey;
      var newArgs = [key].concat(_.rest(arguments));
      return this.t.apply(this, newArgs);
    }, this);
  },

  /**
   * Extends the common-ui locale with your own product specific locale.
   * Caution, can override common-ui locale keys.
   * @param {object} extendedLocale The locale that we want to add.  Basic string key / string value.
   */
  extend: function(extendedLocale) {
    _.extend(language, extendedLocale);
  }
};
