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

import TimedModel from './timed';

export default TimedModel.extend({

  name: DS.attr('string'),

  initTime: DS.attr('number'),
  firstTaskStartTime: DS.attr('number'),
  lastTaskFinishTime: DS.attr('number'),

  totalTasks: DS.attr('number'),
  failedTasks: DS.attr('number'),
  succeededTasks: DS.attr('number'),
  killedTasks: DS.attr('number'),

  finalStatus: Ember.computed("status", "failedTaskAttempts", function () {
    var status = this.get("status");
    if(status === "SUCCEEDED" && this.get("failedTaskAttempts")) {
      status = "SUCCEEDED_WITH_FAILURES";
    }
    return status;
  }),

  runningTasks: Ember.computed("am.runningTasks", "status", function () {
    var runningTasks = this.get("am.runningTasks");
    if(runningTasks === undefined) {
      runningTasks = this.get("status") === 'SUCCEEDED' ? 0 : null;
    }
    return  runningTasks;
  }),
  pendingTasks: Ember.computed("totalTasks", "succeededTasks", "runningTasks", function () {
    var pendingTasks = null,
        runningTasks = this.get("runningTasks"),
        totalTasks = this.get("totalTasks");
    if(totalTasks!== null && runningTasks !== null) {
      pendingTasks = totalTasks - this.get("succeededTasks") - runningTasks;
    }
    return pendingTasks;
  }),

  failedTaskAttempts: DS.attr('number'),
  killedTaskAttempts: DS.attr('number'),

  minDuration: DS.attr('number'),
  maxDuration: DS.attr('number'),
  avgDuration: DS.attr('number'),

  firstTasksToStart: DS.attr("object"),
  lastTasksToFinish: DS.attr("object"),
  shortestDurationTasks: DS.attr("object"),
  longestDurationTasks: DS.attr("object"),

  processorClassName: DS.attr('string'),

  dagID: DS.attr('string'),
  dag: DS.attr('object'), // Auto-loaded by need

  description: Ember.computed("dag.vertices", "name", function () {
    try {
      let vertex = this.get("dag.vertices").findBy("vertexName", this.get("name"));
      return JSON.parse(vertex.userPayloadAsText).desc;
    }catch(e) {}
  }),

  servicePlugin: DS.attr('object'),
});
