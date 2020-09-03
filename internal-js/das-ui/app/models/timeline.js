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

import DS from 'ember-data';
import Ember from 'ember';

import TimedModel from './timed';

export default TimedModel.extend({

  needs:{
    app: {
      type: ["appRm", "AhsApp"],
      idKey: "appID",
      silent: true
    }
  },

  appID: Ember.computed("entityID", function () {
    var idParts = this.get("entityID").split("_");
    return `application_${idParts[1]}_${idParts[2]}`;
  }),
  app: DS.attr("object"), // Either RMApp or AHSApp

  atsStatus: DS.attr("string"),
  status: Ember.computed("atsStatus", "app.status", "app.finalStatus", function () {
    var status = this.get("atsStatus"),
        yarnStatus = this.get("app.status");

    if (status !== 'RUNNING' || (yarnStatus !== 'FINISHED' && yarnStatus !== 'KILLED' && yarnStatus !== 'FAILED')) {
      return status;
    }

    if (yarnStatus === 'KILLED' || yarnStatus === 'FAILED') {
      return yarnStatus;
    }

    return this.get("app.finalStatus");
  }),

  progress: Ember.computed("status", function () {
    return this.get("status") === "SUCCEEDED" ? 1 : null;
  }),

  // Hash will be created only on demand, till then counters will be stored in _counterGroups
  _counterGroups: DS.attr('object'),
  counterGroupsHash: Ember.computed("_counterGroups", function () {
    var counterHash = {},
        counterGroups = this.get("_counterGroups") || [];

    counterGroups.forEach(function (group) {
      var counters = group.counters,
          groupHash;

      groupHash = counterHash[group.counterGroupName] = counterHash[group.counterGroupName] || {};

      counters.forEach(function (counter) {
        groupHash[counter.counterName] = counter.counterValue;
      });
    });

    return counterHash;
  }),

  diagnostics: DS.attr('string'),

  events: DS.attr('object'),

});
