// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module utils/timeUtil
 * @description A set of time utility methods.
 */
var _ = require('_');

// Defines a series of utility functions having to do with time.
module.exports = {
  /**
   * Stores the current time information of the server.
   * @param {Date} date - a JavaScript date object that represents the current time
   * of the server.
   *
   * We need to do this in case the browser's clock is misconfigured (e.g.
   * Ahead by 1 hour or behind by 15 minutes).
   * We assume the server's time is accurate since that is where the timestamp
   * values are coming from anyway.
   */
  setServerNow: function(date) {
    // We need to compute the delta between this date from the server and the local
    // machine's current time; This delta will be used to compute the equivalent server's time as of now
    // on the local machine.
    var browserNow = new Date();
    window._timeDelta = browserNow.getTime() - date.getTime();
  },

  /**
   * This is the server's timezone offset from UTC. If the server
   * is in Californica and it is not DST, this value would be -8.
   */
  setServerTimezoneOffset: function(offset) {
    if (_.isNumber(offset) && !_.isNaN(offset)) {
      window._timezoneOffset = offset;
      var browserNow = new Date();
      var delta = browserNow.getTimezoneOffset() * 60 * 1000 + window._timezoneOffset;
      this.setTimezoneDelta(delta);
    }
  },

  /**
   * This is the server's timezone offset from UTC. If the server
   * is in Californica and it is not DST, this value would be -8.
   */
  getServerTimezoneOffset: function() {
    if (_.isNumber(window._timezoneOffset) && !_.isNaN(window._timezoneOffset)) {
      return window._timezoneOffset;
    }

    return 0;
  },
  /**
   * This returns the current server timezone offset formatted for use in an ISO 8601 formatted
   * date/time string. This probably shouldn't be used for user display.
   */
  getServerIso8601Timezone: function() {
    var timezoneOffset = this.getServerTimezoneOffset(),
        formattedTimezone;

    if (timezoneOffset === 0) {
      formattedTimezone = 'Z';
    } else {
      if (timezoneOffset < 0) {
        timezoneOffset *= -1;
        formattedTimezone = '-';
      } else {
        formattedTimezone = '+';
      }

      formattedTimezone += (timezoneOffset < 10 ? '0' + timezoneOffset : timezoneOffset) + '00';
    }

    return formattedTimezone;
  },

  /**
   * @return the current time from the server.
   *
   * The return result is not the same value as the input of setServerNow(date).
   * If setServerNow(someServerTime) is called at time t1, and getServerNow()
   * is called at time t2, where (t2 - t1) milliseconds have elapsed,
   * getServerNow() would return someServerTime + (t2 - t1),
   * or t2 + _timeDelta where _timeDelta = someServerTime - t1.
   */
  getServerNow: function() {
    var browserNow = new Date();
    var _timeDelta = window._timeDelta;
    if (!_timeDelta) {
      _timeDelta = 0;
    }

    return new Date(browserNow.getTime() - _timeDelta);
  },

  /**
   * @param delta (in milliseconds).
   */
  setTimezoneDelta: function(delta) {
    window._timezoneDelta = delta;
  },

  getTimezoneDelta: function() {
    return window._timezoneDelta;
  },

  setTimezoneDisplayName: function(displayName) {
    if (displayName) {
      window._timezoneDisplayName = displayName;
    }
  },

  getTimezoneDisplayName: function() {
    return window._timezoneDisplayName;
  },

  fromServerDate: function(serverDate) {
    return new Date(serverDate.getTime() - this.getTimezoneDelta());
  },

  toServerDate: function(localDate) {
    return new Date(localDate.getTime() + this.getTimezoneDelta());
  }
};
