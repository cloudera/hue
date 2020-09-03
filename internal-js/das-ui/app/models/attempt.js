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

import AMTimelineModel from './am-timeline';

export default AMTimelineModel.extend({
  needs: {
    dag: {
      type: "dag",
      idKey: "dagID",
      silent: true
    },
    am: {
      type: "attemptAm",
      idKey: "entityID",
      loadType: "demand",
      queryParams: function (model) {
        var vertexIndex = parseInt(model.get("vertexIndex")),
            taskIndex = parseInt(model.get("taskIndex")),
            attemptIndex = parseInt(model.get("index"));
        return {
          attemptID: `${vertexIndex}_${taskIndex}_${attemptIndex}`,
          dagID: parseInt(model.get("dag.index")),
          counters: "*"
        };
      },
      urlParams: function (model) {
        return {
          app_id: model.get("appID")
        };
      }
    }
  },

  taskID: DS.attr('string'),
  taskIndex: Ember.computed("taskID", function () {
    var id = this.get("taskID") || "";
    return id.substr(id.lastIndexOf('_') + 1);
  }),

  vertexID: DS.attr('string'),
  vertexIndex: Ember.computed("vertexID", function () {
    var id = this.get("vertexID") || "";
    return id.substr(id.lastIndexOf('_') + 1);
  }),
  vertexName: Ember.computed("vertexID", "dag", function () {
    var vertexID = this.get("vertexID");
    return this.get(`dag.vertexIdNameMap.${vertexID}`);
  }),

  dagID: DS.attr('string'),
  dag: DS.attr('object'), // Auto-loaded by need

  containerID: DS.attr('string'),
  nodeID: DS.attr('string'),

  inProgressLogsURL: DS.attr('string'),
  completedLogsURL: DS.attr('string'),
  logURL: Ember.computed("entityID", "inProgressLogsURL", "completedLogsURL", "dag.isComplete", function () {
    var logURL = this.get("inProgressLogsURL");

    if(logURL) {
      if(logURL.indexOf("://") === -1) {
        let attemptID = this.get("entityID"),
            yarnProtocol = this.get('env.app.yarnProtocol');
        return `${yarnProtocol}://${logURL}/syslog_${attemptID}`;
      }
      else { // LLAP log link
        return this.get("dag.isComplete") ? this.get("completedLogsURL") : logURL;
      }
    }
  }),

  containerLogURL: DS.attr('string'),
});
