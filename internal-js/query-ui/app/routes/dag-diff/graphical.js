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
import MultiAmPollsterRoute from '../multi-am-pollster';

export default MultiAmPollsterRoute.extend({
  title: "Graphical View",

  loaderNamespace: "dag",

  setupController: function (controller, model) {
    this._super(controller, model);
    Ember.run.later(this, "startCrumbBubble");
  },

  load: function (value, query, options) {
    options = Ember.$.extend({
      demandNeeds: ["info", "dag"]
    }, options);
    return this.get("loader").query('vertex', {
      dagID: this.modelFor("dag").get("id")
    }, options);
  },

  _loadedValueObserver: Ember.observer("loadedValue", function () {
    var loadedValue = this.get("loadedValue"),
        records = [];

    if(loadedValue) {
      loadedValue.forEach(function (record) {
        records.push(record);
      });

      this.set("polledRecords", records);
    }
    Ember.run.later(this, "setViewHeight", 100);
  }),

  setViewHeight: function () {
    var container = Ember.$('#graphical-view-component-container'),
        offset;

    if(container) {
      offset = container.offset();
      container.height(
        Math.max(
          // 50 pixel is left at the bottom
          offset ? Ember.$(window).height() - offset.top - 70 : 0,
          500 // Minimum dag view component container height
        )
      );
    }
  },

  actions: {
    didTransition: function () {
      Ember.$(window).on('resize', this.setViewHeight);
      this._super();
      return true;
    },
    willTransition: function () {
      Ember.$(window).off('resize', this.setViewHeight);
      this._super();
      return true;
    },
  }

});
