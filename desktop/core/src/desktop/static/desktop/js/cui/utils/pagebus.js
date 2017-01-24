// Copyright (c) 2016 Cloudera, Inc. All rights reserved.
/**
 * @module utils/pagebus
 * @description Provides a common mechanism for inter-module messaging.
 */
var pubsub = require('pubsub');
var _ = require('_');

// This is currently just a pass through the thirdparty pubsub, but the plan is to enrich it in the future.

/**
 * The channel subscription hash, this is a mirror of the pubsub channels.
 * @type {object<string, function[]>}
 */
var channels = {};

var pagebus = {
  /**
   * Publishes some data on a channel.
   *
   * @param {String} channel The channel to publish on.
   * @param {Mixed} argument The data to publish, the function supports.
   * as many data parameters as needed
   *
   * @example
   * pagebus.publish(
   *  'some.channel', 'a', 'b',
   *  {total: 10, min: 1, max: 3}
   * );
   */
  publish: function(channel, ...args) {
    pubsub.publish(channel, args);
  },

  /**
   * Registers a callback on a channel.
   * Returns a handle which can be used to unsubscribe this particular subscription.
   * Wrapping the pagebus function to track channels.
   *
   * @param {string} channel The channel to subscribe to.
   * @param {function} callback The event handler, any time something is
   * published on a subscribed channel, the callback will be called
   * with the published array as ordered arguments.
   *
   * @return {object}
   *
   * @example
   * pagebus.subscribe(
   *   'some.channel',
   *   function(a, b, c){ ... }
   * );
   */
  subscribe: function(channel, callback) {

    // call through first to trigger param validation
    var ret = pubsub.subscribe(channel, callback);

    if (!channels[channel]) {
      channels[channel] = [];
    }

    channels[channel].push(callback);
    return ret;
  },

  /**
   * Unregisters a previously registered callback.
   *
   * @param {Mixed} handle The return value from a subscribe call or the
   * name of a channel as a String.
   * @param {Function} [callback] The event handler originally
   * registered, not needed if handle contains the return value
   * of subscribe.
   *
   * @example
   * var handle = pagebus.subscribe('some.channel', function(){});
   * pagebus.unsubscribe(handle);
   *
   */
  unsubscribe: function(subscription) {
    pubsub.unsubscribe(subscription);

    var subs = channels[subscription.namespace],
        x,
        y = (subs instanceof Array) ? subs.length : 0;

    for (x = 0; x < y; x += 1) {
      if (subs[x] === subscription.event.callback) {
        subs.splice(x, 1);
        break;
      }
    }
  }
};

/**
 * Publishes some data on a channel.
 * If the publication isn't handled, it runs the unhandledHandler.
 *
 * @param {String} channel The channel to publish on.
 * @param {function} unhandledHandler the handler in case the message isn't handled.
 * @param {Mixed} argument The data to publish, the function supports.
 * as many data parameters as needed
 *
 * @example
 * pagebus.publishAndHandleUnhandled(
 *  'some.channel',
 *  function unhandledHandler(a, b, total) {},
 *  'a', 'b', {total: 10, min: 1, max: 3}
 * );
 */
pagebus.publishAndHandleUnhandled = function(channel, unhandledHandler) {
  var args = Array.prototype.slice.call(arguments),
      subs = channels[channel];

  if (args.length < 2) {
    throw 'a channel and an unhandledHandler must be specified';
  }

  if (!_.isFunction(unhandledHandler)) {
    throw 'unhandledHandler must be a function';
  }

  if (subs && subs.length > 0) {
    // throw away the unhandledHandler from args
    args.splice(1, 1);
    pagebus.publish.apply(this, args);
  } else {
    // call the unhandledHandler with data
    unhandledHandler.apply(this, args.slice(2));
  }
};

module.exports = pagebus;
