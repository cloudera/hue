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
import DS from 'ember-data';

import DAGInfoModel from './dag-info';

export default DAGInfoModel.extend({
  needs: {
    am: {
      type: "dagAm",
      idKey: "entityID",
      loadType: "demand",
      queryParams: function (model) {
        return {
          dagID: parseInt(model.get("index")),
          counters: "*"
        };
      },
      urlParams: function (model) {
        return {
          app_id: model.get("appID"),
          version: model.get("amWsVersion") || "1"
        };
      }
    },
    app: {
      type: ["AhsApp", "appRm"],
      idKey: "appID",
      loadType: function (record) {
        if(record.get("queueName") && record.get("atsStatus") !== "RUNNING") {
          return "demand";
        }
      },
      silent: true
    },
    info: {
      type: "dagInfo",
      idKey: "entityID",
      loadType: "demand",
      silent: true
    }
  },

  name: DS.attr("string"),

  submitter: DS.attr("string"),

  // Serialize when required
  vertices: Ember.computed.or("dagPlan.vertices", "info.dagPlan.vertices"),
  edges: Ember.computed.or("dagPlan.edges", "info.dagPlan.edges"),
  vertexGroups: Ember.computed.or("dagPlan.vertexGroups", "info.dagPlan.vertexGroups"),

  domain: DS.attr("string"),
  containerLogs: DS.attr("object"),
  queueName: DS.attr("string"),
  queue: Ember.computed("queueName", "app", function () {
    return this.get("queueName") || this.get("app.queue");
  }),

  vertexIdNameMap: DS.attr("object"),
  vertexNameIdMap: DS.attr("object"),

  callerID: DS.attr("string"),
  callerContext: Ember.computed.or("callerData.callerContext", "info.callerData.callerContext"),
  callerDescription: Ember.computed.or("callerData.callerDescription", "info.callerData.callerDescription"),
  callerType: Ember.computed.or("callerData.callerType", "info.callerData.callerType"),

  amWsVersion: DS.attr("string"),

  info: DS.attr("object"),

  counterGroupsHash: Ember.computed("am.counterGroupsHash", "_counterGroups", "info.counterGroupsHash", function () {
    var amCounters = this.get("am.counterGroupsHash"),
        atsCounters = this.get("info.counterGroupsHash") || this._super();
    return amCounters ? Ember.$.extend({}, atsCounters, amCounters) : atsCounters;
  })
});
