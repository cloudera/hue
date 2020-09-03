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

const DISPLAY_TIME = 30 * 1000;

export default Ember.Component.extend({

  error: null,

  visible: false,
  detailsAvailable: false,
  showDetails: false,
  displayTimerId: 0,

  classNames: ['error-bar'],
  classNameBindings: ['visible', 'detailsAvailable'],

  message: null,

  _errorObserver: Ember.on("init", Ember.observer("error", function () {
    var error = this.get("error");

    if(error) {
      this.setProperties({
        message: error.message || "Error",
        detailsAvailable: !!(error.details || error.requestInfo || error.stack),
        visible: true
      });

      this.clearTimer();
      this.set("displayTimerId", setTimeout(this.close.bind(this), DISPLAY_TIME));
    }
    else {
      this.close();
    }
  })),

  clearTimer: function () {
    clearTimeout(this.get("displayTimerId"));
  },
  close: function () {
    this.set("visible", false);
    this.clearTimer();
  },

  actions: {
    toggleDetailsDisplay: function () {
      this.toggleProperty("showDetails");
      this.clearTimer();
    },
    close: function () {
      this.close();
    }
  }
});
