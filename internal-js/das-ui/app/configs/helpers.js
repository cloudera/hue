/*
 * This file was originally copied from Apache Ambari and has been modified. The modifications are subject to the
 * following provisions.
 *
 * HORTONWORKS DATAPLANE SERVICE AND ITS CONSTITUENT SERVICES
 *
 * (c) 2016-2018 Hortonworks, Inc. All rights reserved.
 *
 * This code is provided to you pursuant to your written agreement with Hortonworks, which may be the terms of the
 * Affero General Public License version 3 (AGPLv3), or pursuant to a written agreement with a third party authorized
 * to distribute this code.  If you do not have a written agreement with Hortonworks or with an authorized and
 * properly licensed third party, you do not have any rights to this code.
 *
 * If this code is provided to you under the terms of the AGPLv3:
 * (A) HORTONWORKS PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY KIND;
 * (B) HORTONWORKS DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT
 *   LIMITED TO IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE;
 * (C) HORTONWORKS IS NOT LIABLE TO YOU, AND WILL NOT DEFEND, INDEMNIFY, OR HOLD YOU HARMLESS FOR ANY CLAIMS ARISING
 *   FROM OR RELATED TO THE CODE; AND
 * (D) WITH RESPECT TO YOUR EXERCISE OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, HORTONWORKS IS NOT LIABLE FOR ANY
 *   DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO,
 *   DAMAGES RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF BUSINESS ADVANTAGE OR UNAVAILABILITY,
 *   OR LOSS OR CORRUPTION OF DATA.
 *
 */

import Ember from 'ember';
import nonPrintableChars from './non-printable-escape-chars';

/* globals moment */

export default Ember.Object.create({
  isInteger: function (x) {
    return !isNaN(x);
  },

  isDate: function (date) {
    return moment(date).isValid();
  },

  regexes: {
    allUppercase: /^[^a-z]*$/,
    whitespaces: /^(\s*).*$/,
    digits: /^\d+$/,
    name: /\w+/ig,
    dotPath: /[a-z.]+/i,
    setSetting: /^set\s+[\w-.]+(\s+|\s?)=(\s+|\s?)[\w-.]+(\s+|\s?);/gim
  },

  validationValues: {
    bool: [
      Ember.Object.create({
        value: 'true'
      }),
      Ember.Object.create({
        value: 'false'
      })
    ],

    execEngine: [
      Ember.Object.create({
        value: 'tez'
      }),
      Ember.Object.create({
        value: 'mr'
      })
    ]
  },

  insensitiveCompare: function (sourceString) {
    var args = Array.prototype.slice.call(arguments, 1);

    if (!sourceString) {
      return false;
    }

    return !!args.find(function (arg) {
      return sourceString.match(new RegExp('^' + arg + '$', 'i'));
    });
  },

  insensitiveContains: function (sourceString, destString) {
    return sourceString.toLowerCase().indexOf(destString.toLowerCase()) > -1;
  },

  convertToArray: function (inputObj) {
    var array = [];

    for (var key in inputObj) {
      if (inputObj.hasOwnProperty(key)) {
        array.pushObject({
          name: key,
          value: inputObj[key]
        });
      }
    }
    return array;
  },

  /**
   * Convert number of seconds into time object HH MM SS
   *
   * @param integer secs Number of seconds to convert
   * @return object
   */
  secondsToHHMMSS: function (secs) {
    var hours = 0,
      minutes = 0,
      seconds = secs,
      divisor_for_minutes,
      divisor_for_seconds,
      formattedVal = [];

    if (seconds < 60) {
      formattedVal.push(Ember.I18n.t('labels.secsShort', {
        seconds: seconds
      }));
    } else {
      hours = Math.floor(seconds / (60 * 60));

      divisor_for_minutes = seconds % (60 * 60);
      minutes = Math.floor(divisor_for_minutes / 60);

      divisor_for_seconds = divisor_for_minutes % 60;
      seconds = Math.ceil(divisor_for_seconds);

      if (hours > 0) {
        formattedVal.push(Ember.I18n.t('labels.hrsShort', {
          hours: hours
        }));
      }
      if (minutes > 0) {
        formattedVal.push(Ember.I18n.t('labels.minsShort', {
          minutes: minutes
        }));
      }
      if (seconds > 0) {
        formattedVal.push(Ember.I18n.t('labels.secsShort', {
          seconds: seconds
        }));
      }

    }

    return formattedVal.join(' ');
  },

  /**
   * Returns all Ascii characters which will be used to fill the termination characters
   */
  getAllTerminationCharacters() {
    let arr = Ember.copy(nonPrintableChars);
    for (let i = 33; i < 127; i++) {
      arr.pushObject({id: i.toString(), name: String.fromCodePoint(i)});
    }
    return arr;
  },

});
