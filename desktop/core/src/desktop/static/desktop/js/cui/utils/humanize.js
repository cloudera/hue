// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module utils/humanize
 * @description This module provides humanization related functionality.
 * The resources available to this module are controlled by
 * i18n/client.common.txt and the ClientResources component.
 */
var i18n = require('cloudera-ui/utils/i18n');
var timeUtil = require('cloudera-ui/utils/timeUtil');
var moment = require('moment');
var _ = require('_');

// Unit suffixes for values representing only magnitude (pop pop).
var COUNT_UNITS = ['', 'K', 'M', 'G', 'T', 'P', 'E'];

// Unit suffixes for values representing bytes.
var BYTE_UNITS = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB' /* 2 ^ 60 */];

// Unit suffixes for values representing bytes per second.
var BYTE_PER_SECOND_UNITS = ['B/s', 'KiB/s', 'MiB/s', 'GiB/s', 'TiB/s', 'PiB/s', 'EiB/s'];

// Used for abbreviating Role types
var UPPER_CASE_NUMERIC_REGEX = /^[A-Z0-9]*$/;

/**
 * Returns string representation of a given number with trailing zeros removed.
 */
var stringifyNumber = function(y, digits) {
  if (!_.isNumber(y) || _.isNaN(y)) {
    return '';
  }

  var str;
  var precisionLimit = (1 / (2 * Math.pow(10, digits)));
  var absY = Math.abs(y);
  if (digits > 0 && absY > 0 && absY < precisionLimit) {
    // y is too small so Number.toFixed will just return 0. Use Number.toPrecision
    // in order to preserve the value.
    // (i.e., for digits == 2, y is between -0.005 and 0.005 excluding 0)
    str = y.toPrecision(digits);
  } else {
    str = y.toFixed(digits);
  }

  // Remove trailing zeros by converting to numbe and back to string.
  return Number(str).toString();
};

var createUnitHumanizer = function(units, base, useSpace) {
  return function humanizeIt(value) {
    if (value < 0) {
      return '-' + humanizeIt(-1 * value);
    }

    var spacer = useSpace ? ' ' : '';
    var index = 0, resultNum;

    // Coerce to a number.
    value = Number(value);
    if (value < base) {
      if (value < 1) {
        resultNum = stringifyNumber(value, 1);
      } else {
        resultNum = stringifyNumber(value, 2);
      }
    } else {
      index = Math.floor(Math.log(value) / Math.log(base));
      index = Math.min(units.length - 1, index);
      resultNum = stringifyNumber((value / Math.pow(base, index)), 1);
    }

    return resultNum + spacer + units[index];
  };
};

var humanize = {
  // The intent of this function is to render the count using only four
  // characters, if possible. Knowing the max length of the output of this
  // function makes it easier to layout the UI in certain cases,
  // e.g. histograms.
  humanizeCount: createUnitHumanizer(COUNT_UNITS, 1000, false),

  humanizeBytes: createUnitHumanizer(BYTE_UNITS, 1024, true),

  humanizeBytesPerSecond: createUnitHumanizer(BYTE_PER_SECOND_UNITS, 1024, true),

  stringifyNumber: stringifyNumber,

  // This function cheats a lot. Until we have a better idea about scaling
  // and how we want to present these values we do this:
  // 1. Display in byte seconds if below the 1024^4 threshold.
  // 2. Convert to gigabyte hours if above the 1024^4 threshold.
  humanizeByteSeconds: function(value) {
    // Coerce to a number.
    value = Number(value);
    if (value < Math.pow(1024, 4)) {
      return humanize.stringifyNumber(value, 0) + ' byte seconds';
    }

    var gbSec = value / Math.pow(1024, 3);
    var gbHours = gbSec / (60 * 60);
    return humanize.stringifyNumber(gbHours, 1) + ' GiB hours';
  },

  humanizeSeconds: function(seconds) {
    return humanize.humanizeMilliseconds(seconds * 1000);
  },

  // Convert nanoseconds to a human-friendly string.
  // It also handles microseconds. Past that, it defers
  // to humanizeMilliseconds.
  humanizeNanoseconds: function(nanos) {
    // Coerce to a number.
    nanos = Number(nanos);
    if (nanos < 1000) {
      return humanize.stringifyNumber(nanos, 0) + 'ns';
    }

    var micros = nanos * Math.pow(10, -3);
    if (micros < 1000) {
      return humanize.stringifyNumber(micros, 2) + '\u00B5s';
    }

    return humanize.humanizeMilliseconds(nanos * Math.pow(10, -6));
  },

  /** Convert milliseconds into human-friendly string. */
  humanizeMilliseconds: function(ms) {
    // Coerce to a number.
    ms = Number(ms);
    if (ms < 1) {
      return humanize.stringifyNumber(ms, 2) + 'ms';
    }

    if (ms < 1000) {
      return humanize.stringifyNumber(ms, 0) + 'ms';
    }

    var val = ms / 1000.0;
    if (val < 120) {
      return humanize.stringifyNumber(val, 2) + 's';
    }

    val = val / 60.0;
    if (val < 120) {
      return humanize.stringifyNumber(val, 1) + 'm';
    }

    val = val / 60.0;
    if (val < 48) {
      return humanize.stringifyNumber(val, 1) + 'h';
    }

    val = val / 24.0;
    return humanize.stringifyNumber(val, 1) + 'd';
  },

  formatDuration: function(value, decimal, type) {
    var key = 'label.duration.' + type;
    if (value !== 1) {
      key += 's';
    }

    return i18n.t(key, humanize.stringifyNumber(value, decimal));
  },

  humanizeMillisecondsLong: function(ms) {
    // Coerce to a number.
    ms = Number(ms);

    // return moment.duration(ms).humanize();
    if (ms < 1) {
      return this.formatDuration(ms, 2, 'millisecond');
    }

    if (ms < 1000) {
      return this.formatDuration(ms, 0, 'millisecond');
    }

    var val = ms / 1000.0;
    if (val < 120) {
      return this.formatDuration(val, 2, 'second');
    }

    val = val / 60.0;
    if (val < 60) {
      return this.formatDuration(val, 1, 'minute');
    }

    val = val / 60.0;
    if (val <= 48) {
      return this.formatDuration(val, 1, 'hour');
    }

    val = val / 24.0;
    return this.formatDuration(val, 1, 'day');
  },

  humanizeDateTimeMedium: function(dateObject) {
    return this._humanizeTimeWithFormat(dateObject, 'LLL');
  },

  humanizeDateLong: function(dateObject) {
    return this._humanizeTimeWithFormat(dateObject, 'LL');
  },

  humanizeDateTimeLong: function(dateObject) {
    return this._humanizeTimeWithFormat(dateObject, 'LLLL');
  },

  humanizeDateShort: function(dateObject) {
    return this._humanizeTimeWithFormat(dateObject, 'L');
  },

  humanizeDateTimeShort: function(dateObject) {
    return this._humanizeTimeWithFormat(dateObject, 'L LT');
  },

  humanizeTimeShort: function(dateObject) {
    return this._humanizeTimeWithFormat(dateObject, 'LT');
  },

  humanizeTimeShortAndMS: function(dateObject) {
    if (dateObject.getMilliseconds() === 0) {
      // Don't show milliseconds if it is 0.
      return this.humanizeTimeMedium(dateObject);
    }

    // This is a special mode that we added locally to moment.
    // This represents showing only the time portion,
    // and add milliseconds after the second.
    return this._humanizeTimeWithFormat(dateObject, 'TT');
  },

  humanizeTimeMedium: function(dateObject) {
    return this._humanizeTimeWithFormat(dateObject, 'h:mm:ss A');
  },

  humanizeTimeLong: function(dateObject) {
    return this._humanizeTimeWithFormat(dateObject, 'H:mm:ss.SSS ZZ');
  },

  /**
   * Displays the Month + Date, e.g. Dec 13
   */
  humanizeDateNoYear: function(dateObject) {
    // TODO: This needs to be handled in an i18n friendly way.
    return this._humanizeTimeWithFormat(dateObject, 'MMM D');
  },

  /**
   * Displays the month of the date. e.g. Dec
   */
  humanizeDateJustMonth: function(dateObject) {
    return this._humanizeTimeWithFormat(dateObject, 'MMM');
  },

  /**
   * Displays the year of the date. e.g. 2012
   */
  humanizeDateJustYear: function(dateObject) {
    return this._humanizeTimeWithFormat(dateObject, 'YYYY');
  },

  humanizeDateTimeAdaptable: function(dateObject, includeSeconds) {
    var today = timeUtil.getServerNow(),
        result = includeSeconds ? this.humanizeTimeMedium(dateObject) : this.humanizeTimeShort(dateObject);

    // If the date is set for today, only show the time.
    if (dateObject.getDate() !== today.getDate() ||
        dateObject.getMonth() !== today.getMonth() ||
        dateObject.getYear() !== today.getYear()) {
      result = this.humanizeDateNoYear(dateObject) + ' ' + result;
    }

    return result;
  },

  humanizeDateTimeForConfig: function(dateObject) {
    return moment(dateObject).format('MM/DD/YYYY HH:mm');
  },

  _humanizeTimeWithFormat: function(dateObject, format) {
    if (format === 'TT') {
      format = moment().localeData().longDateFormat('LT').replace('mm', 'mm:ss.SSS');
    }

    return moment(this.toDisplayDate(dateObject)).format(format);
  },

  /**
   * One place that we want to decide whether to show
   * server timezone or local timezone.
   */
  showServerDate: true,

  /**
   * Converts a local date to a date suitable for display.
   */
  toDisplayDate: function(localDate) {
    if (this.showServerDate) {
      return timeUtil.toServerDate(localDate);
    }

    return localDate;
  },

  /**
   * Converts a display date to a local date.
   */
  fromDisplayDate: function(displayDate) {
    if (this.showServerDate) {
      return timeUtil.fromServerDate(displayDate);
    }

    return displayDate;
  },

  /**
   * Abbreviates a Role type by removing everything
   * but upper-case chars. Example: NameNode = NN
   */
  abbreviateRoleType: function(roleType) {
    return _.filter(roleType.split(''), function(c) {
      return UPPER_CASE_NUMERIC_REGEX.test(c);
    }).join('');
  }
};

module.exports = humanize;
