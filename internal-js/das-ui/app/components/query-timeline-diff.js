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

export default Ember.Component.extend({
  classNames: ['query-timeline'],

  perf: null,

  normalizedPerf1: Ember.computed("perf", function () {
    var perf = this.get("perf") || {};
    perf['PostHiveProtoLoggingHook'] = perf['PostHook.org.apache.hadoop.hive.ql.hooks.HiveProtoLoggingHook'];

    // Create a copy of perf with default values
    perf = Ember.$.extend({
      compile: 0,
      parse: 0,
      TezBuildDag: 0,

      TezSubmitDag: 0,
      TezSubmitToRunningDag: 0,

      TezRunDag: 0,

      PostHiveProtoLoggingHook: 0,
      RemoveTempOrDuplicateFiles: 0,
      RenameOrMoveFiles: 0
    }, perf);

    perf.groupTotal = {
      pre: perf.compile + perf.parse + perf.TezBuildDag,
      submit: perf.TezSubmitDag + perf.TezSubmitToRunningDag,
      running: perf.TezRunDag,
      post: perf.PostHiveProtoLoggingHook + perf.RemoveTempOrDuplicateFiles + perf.RenameOrMoveFiles,
    };

    perf.total = perf.groupTotal.pre +
        perf.groupTotal.submit +
        perf.groupTotal.running +
        perf.groupTotal.post;

    return perf;
  }),

  normalizedPerf2: Ember.computed("perf1", function () {
    var perf = this.get("perf1") || {};
    perf['PostHiveProtoLoggingHook'] = perf['PostHook.org.apache.hadoop.hive.ql.hooks.HiveProtoLoggingHook'];

    // Create a copy of perf with default values
    perf = Ember.$.extend({
      compile: 0,
      parse: 0,
      TezBuildDag: 0,

      TezSubmitDag: 0,
      TezSubmitToRunningDag: 0,

      TezRunDag: 0,

      PostHiveProtoLoggingHook: 0,
      RemoveTempOrDuplicateFiles: 0,
      RenameOrMoveFiles: 0
    }, perf);

    perf.groupTotal = {
      pre: perf.compile + perf.parse + perf.TezBuildDag,
      submit: perf.TezSubmitDag + perf.TezSubmitToRunningDag,
      running: perf.TezRunDag,
      post: perf.PostHiveProtoLoggingHook + perf.RemoveTempOrDuplicateFiles + perf.RenameOrMoveFiles,
    };

    perf.total = perf.groupTotal.pre +
        perf.groupTotal.submit +
        perf.groupTotal.running +
        perf.groupTotal.post;

    return perf;
  }),

  alignBars: function (bars, perf) {
    bars.each(function (index, bar) {
      var width;

      bar = Ember.$(bar);
      width = (Ember.get(perf, bar.attr("data")) / perf.total) * 100;

      bar.css({
        width: `${width}%`
      });
    });
  },

  didInsertElement: Ember.observer("normalizePerf1", "normalizePerf2", function () {
    var perf = this.get("normalizedPerf1");

    this.alignBars(this.$().find(".sub-groups").find(".bar"), perf);
    this.alignBars(this.$().find(".groups").find(".bar"), perf);

    var highestTotal = Math.max(perf.total, this.get("normalizedPerf2.total"));
    this.$().find(".timeline-bars").css("width", (perf.total / highestTotal) * 100 + "%");
  })
});
