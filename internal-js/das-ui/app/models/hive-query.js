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
import DS from 'ember-data';

export default DS.Model.extend({
  queryId: DS.attr(),
  query: DS.attr('string'),
  highlightedQuery: DS.attr(),
  startTime: DS.attr(),
  endTime: DS.attr(),
  duration: Ember.computed("startTime", "endTime", function () {
    var duration = this.get("endTime") - this.get("startTime");
    return duration > 0 ? duration : null;
  }),
  status: DS.attr('string'),
  isComplete: Ember.computed("status", function () {
    let status = this.get("status");
    return status == "SUCCESS" || status == "ERROR";
  }),
  queueName: DS.attr('string'),
  userId: DS.attr('string'),
  requestUser: DS.attr('string'),
  numberOfMrJobs: DS.attr('number'),
  numberOfTezJobs: DS.attr('number'),
  operationId: DS.attr('string'),
  clientIpAddress: DS.attr('string'),
  hiveInstanceAddress: DS.attr('string'),
  hiveInstanceType: DS.attr('string'),
  sessionId: DS.attr('string'),
  logId: DS.attr('string'),
  threadId: DS.attr('string'),
  executionMode: DS.attr('string'),
  tablesRead: DS.attr(),
  tablesWritten: DS.attr(),
  databasesUsed: DS.attr(),
//  configuration: DS.attr(),
  domainId: DS.attr('string'),
  llapAppId: DS.attr('string'),
//  dagInfo: DS.attr('object'),
  dags : DS.attr('object'),
  appIds: Ember.computed("dags", function () {
    let dags = this.get("dags") || [];
    return dags.map(dag => Ember.get(dag, "dagInfo.applicationId"));
  }),
  dagIds: Ember.computed("dags", function () {
    let dags = this.get("dags") || [];
    return dags.map(dag => Ember.get(dag, "dagInfo.dagId"));
  }),
  details: DS.attr('object')
  //perf: DS.attr('object'),
  //explainPlan: DS.attr('object')
});
