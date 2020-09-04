/*
 * This file was originally copied from Apache Tez and has been modified. The modifications are subject to the
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

const STATE_STORAGE_KEY = "pollingIsActive",
      DEFAULT_LABEL = "default_label";

var MoreObject = more.Object;

export default Ember.Service.extend({
  localStorage: Ember.inject.service("localStorage"),
  env: Ember.inject.service("env"),

  interval: Ember.computed.oneWay("env.app.pollingInterval"),

  active: false,
  isPolling: false,
  scheduleID: null,

  polls: {},
  pollCount: 0,

  initState: Ember.on("init", function () {
    var state = this.get("localStorage").get(STATE_STORAGE_KEY);

    if(state === undefined || state === null) {
      state = true;
    }
    Ember.run.later(this, function () {
      this.set("active", state);
    });
  }),
  stateObserver: Ember.observer("active", function () {
    this.get("localStorage").set(STATE_STORAGE_KEY, this.get("active"));
    this.callPoll();
  }),

  isReady: Ember.computed("active", "pollCount", function () {
    return !!(this.get("active") && this.get("pollCount"));
  }),

  callPoll: function () {
    var that = this;
    this.unSchedulePoll();
    if(this.get("isReady") && !this.get("isPolling")) {
      var pollsPromises = [];

      this.set("isPolling", true);

      MoreObject.forEach(this.get("polls"), function (label, pollDef) {
        pollsPromises.push(pollDef.callback.call(pollDef.context));
      });

      Ember.RSVP.allSettled(pollsPromises).finally(function () {
        that.set("isPolling", false);
        that.schedulePoll();
      });
    }
  },

  schedulePoll: function () {
    this.set("scheduleID", setTimeout(this.callPoll.bind(this), this.get("interval")));
  },
  unSchedulePoll: function () {
    clearTimeout(this.get("scheduleID"));
  },

  setPoll: function (pollFunction, context, label) {
    var polls = this.get("polls"),
        pollCount;

    label = label || DEFAULT_LABEL;
    polls[label] = {
      context: context,
      callback: pollFunction,
    };
    this.set("pollCount", pollCount = Object.keys(polls).length);

    this.callPoll();
  },
  resetPoll: function (label) {
    var polls = this.get("polls"),
        pollCount;

    label = label || DEFAULT_LABEL;
    delete polls[label];
    this.set("pollCount", pollCount = Object.keys(polls).length);

    if(!pollCount) {
      this.unSchedulePoll();
    }
  }
});
