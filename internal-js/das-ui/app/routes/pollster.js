/*
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
import AbstractRoute from './abstract';

export default AbstractRoute.extend({
  polling: Ember.inject.service("pollster"),

  // Todo - Change name to recordsToPoll
  polledRecords: null,

  // Must be implemented by inheriting classes
  onRecordPoll: function (val) {return val;},
  onPollSuccess: function (val) {return val;},
  onPollFailure: function (err) {throw(err);},

  pollData: function () {
    var polledRecords = this.get("polledRecords");

    if(!this.get("isLoading") && polledRecords) {
      polledRecords = polledRecords.map(this.onRecordPoll.bind(this));
      return Ember.RSVP.all(polledRecords).
      then(this.updateLoadTime.bind(this)).
      then(this.onPollSuccess.bind(this), this.onPollFailure.bind(this));
    }
    return Ember.RSVP.reject();
  },

  canPoll: Ember.computed("polledRecords", "loadedValue", function () {
    return this.get("polledRecords") && this.get("loadedValue");
  }),

  updateLoadTime: function (value) {
    this.send("setLoadTime", this.getLoadTime(value));
    return value;
  },

  _canPollInit: Ember.on("init", function () {
    // This sets a flag that ensures that the _canPollObserver is called whenever
    // canPoll changes. By default observers on un-used computed properties
    // are not called.
    this.get("canPoll");
  }),

  _canPollObserver: Ember.observer("canPoll", function () {
    if(this.get("canPoll")) {
      this.get("polling").setPoll(this.pollData, this);
    }
    else {
      this.get("polling").resetPoll();
    }
  }),

});
