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

export const BASE = {
  MINUTE: "minute",
  DAY: "day",
  WEEK: "week",
  MONTH: "month",
  YEAR: "year",
  CUSTOM: "custom",
};

export const RANGE_SETS = [
    [
      { title: "Last 7 days", from: 7, to: -1, base: BASE.DAY },
      { title: "Last 30 days", from: 30, to: -1, base: BASE.DAY },
      { title: "Last 60 days", from: 60, to: -1, base: BASE.DAY },
      { title: "Last 90 days", from: 90, to: -1, base: BASE.DAY },
      { title: "Last 6 months", from: 183, to: -1, base: BASE.DAY },
      { title: "Last 1 year", from: 365, to: -1, base: BASE.DAY },
      { title: "Last 2 year", from: 365 * 2, to: -1, base: BASE.DAY },
      { title: "Last 5 year", from: 365 * 5, to: -1, base: BASE.DAY },
    ], [
      { title: "Yesterday", from: 1, to: 1, base: BASE.DAY },
      { title: "Day before yesterday", from: 2, to: 2, base: BASE.DAY },
      { title: "This day last week", from: 7, to: 7, base: BASE.DAY },
      { title: "Previous week", from: 1, to: 1, base: BASE.WEEK },
      { title: "Previous month", from: 1, to: 1, base: BASE.MONTH },
      { title: "Previous year", from: 1, to: 1, base: BASE.YEAR },
    ], [
      { title: "Today", from: 0, to: 0, base: BASE.DAY },
      { title: "Today so far", from: 0, to: -1, base: BASE.DAY },
      { title: "This week", from: 0, to: 0, base: BASE.WEEK },
      { title: "This week so far", from: 0, to: -1, base: BASE.WEEK },
      { title: "This month", from: 0, to: 0, base: BASE.MONTH },
      { title: "This year", from: 0, to: 0, base: BASE.YEAR },
    ], [
      { title: "Last 5 minutes", from: 5, to: -1, base: BASE.MINUTE },
      { title: "Last 15 minutes", from: 15, to: -1, base: BASE.MINUTE },
      { title: "Last 30 minutes", from: 30, to: -1, base: BASE.MINUTE },
      { title: "Last 1 hour", from: 60, to: -1, base: BASE.MINUTE },
      { title: "Last 3 hours", from: 60 * 3, to: -1, base: BASE.MINUTE },
      { title: "Last 6 hours", from: 60 * 6, to: -1, base: BASE.MINUTE },
      { title: "Last 12 hours", from: 60 * 12, to: -1, base: BASE.MINUTE },
      { title: "Last 24 hours", from: 60 * 24, to: -1, base: BASE.MINUTE },
    ],
  ],
  CUSTOM_RANGE = {
    title: "Custom Range",
    base: BASE.CUSTOM
  };

const DATEPICKER_OPTIONS = {
  minView: 2,
  format: 'mm/dd/yyyy',
  autoclose: true
};

export default Ember.Component.extend({

  tableDefinition: null,

  rangeSets: RANGE_SETS,

  didInsertElement: function () {
    var fromElm = this.$().find('#from-date'),
        toElm = this.$().find('#to-date');

    this.setProperties({
      fromDateElement: fromElm,
      toDateElement: toElm
    });

    fromElm.datetimepicker(DATEPICKER_OPTIONS).on('changeDate', function (event) {
      var fromDate = event.date;

      toElm.datetimepicker('setStartDate', fromDate);

      if(fromDate > toElm.data("datetimepicker").getDate()) {
        toElm.datetimepicker('update', fromDate);
      }
    });

    toElm.datetimepicker(DATEPICKER_OPTIONS);
    toElm.datetimepicker('setStartDate', fromElm.data("datetimepicker").getDate());

    this.rangeDataObserver();
  },

  willDestroyElement: function () {
    this.setProperties({
      fromDateElement: null,
      toDateElement: null
    });
  },

  getUTCDate: function (epoch) {
    var date = new Date(0);
    date.setUTCMilliseconds(epoch);
    return date;
  },

  rangeDataObserver: Ember.observer("tableDefinition.rangeData", function () {
    var rangeData = this.get("tableDefinition.rangeData"),
        fromElm = this.get("fromDateElement"),
        toElm = this.get("toDateElement");

    if(fromElm && toElm) {
      if(rangeData.base === BASE.CUSTOM) {
        if(rangeData.fromTime) {
          fromElm.datetimepicker('update', this.getUTCDate(rangeData.fromTime));
        }
        if(rangeData.toTime) {
          toElm.datetimepicker('update', this.getUTCDate(rangeData.toTime));
        }
      }
      else {
        let now = new Date();
        fromElm.datetimepicker('update', now);
        toElm.datetimepicker('update', now);
        toElm.datetimepicker('setStartDate', now);
      }
    }
  }),

  actions: {
    setRange: function (range) {
      this.get('tableDefinition.parentController').send('setRange', range);
    },
    setCustomRange: function () {
      var range = Ember.$.extend({}, CUSTOM_RANGE, {
        fromTime: this.get("fromDateElement").data("datetimepicker").getDate().setHours(0, 0, 0, 0),
        toTime: this.get("toDateElement").data("datetimepicker").getDate().setHours(24, 0, 0, 0),
      });
      this.get('tableDefinition.parentController').send('setRange', range);
    },
  }
});
