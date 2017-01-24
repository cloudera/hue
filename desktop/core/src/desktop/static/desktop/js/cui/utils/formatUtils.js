// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module utils/formatUtils
 * @description A set of formatting utility methods.
 */
var humanize = require('cloudera-ui/utils/humanize');
var i18n = require('cloudera-ui/utils/i18n');
var _ = require('_');

// Given a units object, return the first numerator.
var getFirstNumerator = function(units) {
  return units && units.numerators && units.numerators[0];
};

// Given a units object, return the first denominator.
var getFirstDenominator = function(units) {
  return units && units.denominators && units.denominators[0];
};

// Utility function that creates another function. This new function takes a
// single numeric argument. It multiplies that argument by the given number
// and then invokes the given function.
var factorThenInvoke = function(factor, invokeMe) {
  return function(value) {
    return invokeMe(value * factor);
  };
};

// Utility function that creates another function. This new function takes a
// single numeric argument.
var checkForZeroThenInvoke = function(invokeMe) {
  return function(value) {
    if (value === 0) {
      return '0';
    }

    return invokeMe(value);
  };
};

// Utility function to help control the width of a numerical value where space
// is important (e.g. in the tick mark strings on our chart y-axes). This
// returns the input number with no post-decimal digit for values greater than
// or equal to 100 and one post-decimal digit for values under 100.
var formatPrecision = function(y) {
  var digits = (y >= 100) ? 0 : 1;
  return humanize.stringifyNumber(y, digits);
};

var THOUSAND = Math.pow(1000, 1);
var MILLION = Math.pow(1000, 2);
var BILLION = Math.pow(1000, 3);
var TRILLION = Math.pow(1000, 4);

var KILOBYTE = Math.pow(1024, 1);
var MEGABYTE = Math.pow(1024, 2);
var GIGABYTE = Math.pow(1024, 3);
var TERABYTE = Math.pow(1024, 4);
var PETABYTE = Math.pow(1024, 5);

// This is a good default tickFormat function for AxisY that can be used when
// a more specialized function like formatBytesForAxisTick is not called for.
var formatKMBTForAxisTick = function(y) {
  if (y >= TRILLION) {
    return formatPrecision(y / TRILLION) + 'T';
  }

  if (y >= BILLION) {
    return formatPrecision(y / BILLION) + 'B';
  }

  if (y >= MILLION) {
    return formatPrecision(y / MILLION) + 'M';
  }

  if (y >= THOUSAND) {
    return formatPrecision(y / THOUSAND) + 'K';
  }

  if (y >= 1) {
    return formatPrecision(y);
  }

  if (y > 0) {
    return humanize.stringifyNumber(y, 2);
  }

  if (y === 0) {
    return '0';
  }

  if (y < 0) {
    // Negative value, format it as a positive value and prepend '-'
    return '-' + formatKMBTForAxisTick(Math.abs(y));
  }

  // Not a number
  return '';

};

// This is a tickFormat function for a chart AxisY that nicely formats byte
// values, taking care to avoid returning numbers that are too wide. Concern
// for the width of the return string are why this differs from the core byte
// formatting functions available in humanize (and is why this uses M rather
// than MiB for example for mebibytes).
var formatBytesForAxisTick = function(y) {
  if (y >= PETABYTE) {
    return formatPrecision(y / PETABYTE) + 'P';
  }

  if (y >= TERABYTE) {
    return formatPrecision(y / TERABYTE) + 'T';
  }

  if (y >= GIGABYTE) {
    return formatPrecision(y / GIGABYTE) + 'G';
  }

  if (y >= MEGABYTE) {
    return formatPrecision(y / MEGABYTE) + 'M';
  }

  if (y >= KILOBYTE) {
    return formatPrecision(y / KILOBYTE) + 'K';
  }

  if (y >= 1) {
    return formatPrecision(y) + 'b';
  }

  if (y > 0) {
    return humanize.stringifyNumber(y, 2) + 'b';
  }

  if (y === 0) {
    return '0';
  }

  if (y < 0) {
    // Negative value, format it as a positive value and prepend '-'
    return '-' + formatBytesForAxisTick(Math.abs(y));
  }

  // Not a number
  return '';
};

// This is a tickFormat function for a chart AxisY that nicely formats byte
// per second values, taking care to avoid returning numbers that are too
// wide. See formatBytesForAxisTick for more comments.
var formatBytesPerSecondForAxisTick = function(y) {
  if (y === 0) {
    return '0';
  }

  return formatBytesForAxisTick(y) + '/s';
};

// Map of unit types to functions to format that type for the hover detail.
var formattersForHoverDetail = {
  bytes: humanize.humanizeBytes,
  kilobytes: factorThenInvoke(Math.pow(1024, 1), humanize.humanizeBytes),
  megabytes: factorThenInvoke(Math.pow(1024, 2), humanize.humanizeBytes),
  micros: factorThenInvoke(Math.pow(10, 3), humanize.humanizeNanoseconds),
  nanos: humanize.humanizeNanoseconds,
  ms: humanize.humanizeMilliseconds,
  seconds: humanize.humanizeSeconds,
  timestamp: function(timestamp) {
    return humanize.humanizeDateTimeMedium(new Date(timestamp));
  }
};

// Map of unit types to strings to append for that type for the hover detail.
// Note the extra space before the size related entries, and the lack of space
// before the time related entries. This is necessary to keep things consistent
// with humanize functions.
var rawUnitsForHoverDetail = {
  bytes: ' B',
  kilobytes: ' KiB',
  megabytes: ' MiB',
  micros: '\u00B5s',
  nanos: 'ns',
  ms: 'ms',
  seconds: 's'
};

// Map of unit types to functions to format that type for the y-axis ticks.
// The dictionary perSecondFormattersForAxisTicks should be used for units
// that contain a "seconds" denominator.
var formattersForAxisTicks = {
  bytes: formatBytesForAxisTick,
  kilobytes: factorThenInvoke(Math.pow(1024, 1), formatBytesForAxisTick),
  megabytes: factorThenInvoke(Math.pow(1024, 2), formatBytesForAxisTick),
  micros: checkForZeroThenInvoke(
    factorThenInvoke(Math.pow(10, 3), humanize.humanizeNanoseconds)),
  nanos: checkForZeroThenInvoke(humanize.humanizeNanoseconds),
  ms: checkForZeroThenInvoke(humanize.humanizeMilliseconds),
  seconds: checkForZeroThenInvoke(humanize.humanizeSeconds),
  timestamp: function(timestamp) {
    return humanize.humanizeTimeShort(new Date(timestamp));
  },
  percent: function(value) {
    return formatKMBTForAxisTick(value) + '%';
  }
};

// If the denominator is "seconds" make it "second" so that the units for
// derivative charts like dt0(bytes_transmit_network) are "bytes / second"
// rather than "bytes / seconds".
// This doesn't handle all the cases where we want to convert the denominator
// from its plural form to its singular one, but it handles the most common
// one.
var formatDenominator = function(denom) {
  if (denom === 'seconds') {
    return 'second';
  }

  return denom;
};

// Map of unit types to functions to format that type for the y-axis ticks.
// This dictionary should be used for units that contain a "seconds"
// denominator. See formattersForAxisTicks for units without a "seconds"
// denominator.
var perSecondFormattersForAxisTicks = {
  bytes: formatBytesPerSecondForAxisTick,
  kilobytes: factorThenInvoke(Math.pow(1024, 1),
                              formatBytesPerSecondForAxisTick),
  megabytes: factorThenInvoke(Math.pow(1024, 2),
                              formatBytesPerSecondForAxisTick),

  // Time per second is an odd case. We do not want to have time-humanized
  // axis ticks because the charted value is not a time value anymore. Really
  // things like seconds / second is a terrible unit and should be avoided.
  // Stuff like ms, micros or nanos / second is even worse and should also be
  // avoided, but if we get here, the best we can do is present these ticks
  // as numbers. Note that we do not scale the tick into the seconds domain
  // (i.e. by dividing ms by 1000 for example) since for that to make sense
  // the data would also need to be scaled. Eventually, this entire set of
  // cases should be avoided by allowing the unit of the chart to be set
  // explicitly in the plot. See OPSAPS-11782 and OPSAPS-12303 for more
  // discussion.
  nanos: formatKMBTForAxisTick,
  micros: formatKMBTForAxisTick,
  ms: formatKMBTForAxisTick,
  seconds: formatKMBTForAxisTick
};

module.exports = {
  formatYValueForHoverDetail: function(series, value, originalYValue, unitOverride) {
    if (value === null || value === undefined) {
      return '-';
    }

    if (originalYValue && _.isString(originalYValue)) {
      // The back-end returns NaN in case it could not compute the value
      // of a point. Usually it is due to division by zero. We will assume
      // that all strings returned by the back-for values are NaN.
      return i18n.t('label.NaN');
    }

    // Truncate to two decimal places and remove trailing zeros.
    var twoDecimalsVal = humanize.stringifyNumber(value, 2);

    // we do not handle more than one numerator or denominator for now.
    var numeratorUnit;
    var denominatorUnit;
    if (unitOverride) {
      numeratorUnit = unitOverride;
    } else {
      numeratorUnit = series && getFirstNumerator(series.units);
      denominatorUnit = series && getFirstDenominator(series.units);
    }

    var numeratorString = '';
    if (!numeratorUnit) {
      // No numeratorUnits, just return the value.
      return twoDecimalsVal;
    }

    if (formattersForHoverDetail.hasOwnProperty(numeratorUnit)) {
      numeratorString = formattersForHoverDetail[numeratorUnit](value);
    } else {
      numeratorString = twoDecimalsVal + ' ' + numeratorUnit;
    }

    var denominatorString = '';
    if (denominatorUnit) {
      denominatorString = ' / ' + formatDenominator(denominatorUnit);
    }

    return numeratorString + denominatorString;
  },

  rawYValueForHoverDetail: function(series, value, originalYValue, unitOverride) {
    if (originalYValue && _.isString(originalYValue)) {
      return '';
    }

    var twoDecimalsVal = humanize.stringifyNumber(value, 2);

    // we do not handle more than one numerator or denominator for now.
    var numeratorUnit;
    var denominatorUnit;
    if (unitOverride) {
      numeratorUnit = unitOverride;
    } else {
      numeratorUnit = series && getFirstNumerator(series.units);
      denominatorUnit = series && getFirstDenominator(series.units);
    }

    var numeratorString = '';
    if (!numeratorUnit) {
      // No numeratorUnits, just return the value.
      return twoDecimalsVal;
    }

    if (rawUnitsForHoverDetail.hasOwnProperty(numeratorUnit)) {
      // Can't always have a space in between the two parts.
      numeratorString = twoDecimalsVal + rawUnitsForHoverDetail[numeratorUnit];
    } else {
      numeratorString = twoDecimalsVal + ' ' + numeratorUnit;
    }

    var denominatorString = '';
    if (denominatorUnit) {
      denominatorString = ' / ' + formatDenominator(denominatorUnit);
    }

    return numeratorString + denominatorString;
  },

  getYAxisTickFormatFunction: function(units) {
    var tickFormat = formatKMBTForAxisTick;
    var numeratorUnit = getFirstNumerator(units);
    var denominatorUnit = getFirstDenominator(units);
    if (denominatorUnit === 'seconds' &&
        perSecondFormattersForAxisTicks.hasOwnProperty(numeratorUnit)) {
      tickFormat = perSecondFormattersForAxisTicks[numeratorUnit];
    } else if (numeratorUnit &&
               formattersForAxisTicks.hasOwnProperty(numeratorUnit)) {
      tickFormat = formattersForAxisTicks[numeratorUnit];
    }

    return tickFormat;
  },

  /**
   * Returns the y-axis label for the given units in the following format:
   * {numerator: [<numerator>, ...], denominators: [<denominator>, ...]}
   */
  getYAxisLabelForUnits: function(units) {
    units = units || {};
    var buf = [];
    _.each(units.numerators, function(u) {
      buf.push(u);
    });
    if (units.denominators && units.denominators.length > 0) {
      buf.push('/');
      _.each(units.denominators, function(u) {
        buf.push(formatDenominator(u));
      });
    }

    return buf.join(' ');
  },

  /**
   * Returns the y-axis label for the given grouped tsquery response. If all
   * streams in the response don't have the same unit it will return "label.mixedUnits".
   */
  getYAxisLabel: function(groupTs) {
    var distinctUnitsList = this.getDistinctUnitsList(groupTs);
    var yAxisLabel = '';

    if (distinctUnitsList.length > 1) {
      yAxisLabel = i18n.t('label.mixedUnits');
    } else if (distinctUnitsList.length === 1) {
      yAxisLabel = this.getYAxisLabelForUnits(distinctUnitsList[0]);
    }

    return yAxisLabel;
  },

  /**
   * Get a distinct list of time series units.
   * Caller can check the length to identify the different cases (no units, single set of units, mixed units)
   * Returns an array of units
   */
  getDistinctUnitsList: function(groupTs) {
    var distinctUnitsHash = {};
    _.each(groupTs, function(ts) {
      var units = ts.metadata.units;
      if (units) {
        var key = units.numerators.join(' ') + ' / ' +
              units.denominators.join(' ');
        distinctUnitsHash[key] = units;
      }
    });
    return _.values(distinctUnitsHash);
  }
};
