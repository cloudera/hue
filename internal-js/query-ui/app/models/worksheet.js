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

import DS from 'ember-data';

let Worksheet = DS.Model.extend({
  title: DS.attr('string'),
  query: DS.attr('string', {defaultValue: ''}),
  selectedDb: DS.attr('string'),
  owner: DS.attr('string'),
  jobState: DS.attr('string'),
  queryResult: DS.attr({defaultValue: {'schema' :[], 'rows' :[]}}),
  currentPage: DS.attr('number', {defaultValue: 0}),
  previousPage: DS.attr('number', {defaultValue: -1}),
  nextPage: DS.attr('number', {defaultValue: 1}),
  selected: DS.attr('boolean', {transient: true, defaultValue: false}),
  jobData: DS.attr({defaultValue: []}),
  currentJobId: DS.attr({defaultValue: null}),
  currentJobData: DS.attr({defaultValue: null}),
  hasNext: DS.attr('boolean', { defaultValue: false}),
  hasPrevious: DS.attr('boolean', { defaultValue: false}),
  selectedTablesModels: DS.attr(),
  selectedMultiDb: DS.attr(),
  logFile: DS.attr('string', {defaultValue: ""}),
  logResults: DS.attr('string', {defaultValue: ""}),
  isQueryRunning: DS.attr('boolean', {defaultValue: false}),
  isQueryDirty: DS.attr('boolean', {defaultValue: false}),
  isQueryResultContainer: DS.attr('boolean', {defaultValue: false}),
  visualExplainJson: DS.attr({defaultValue: null}),
  lastResultRoute: DS.attr({defaultValue: ""}),
  tezUrl: DS.attr('string', {defaultValue: null}),

  isJobInProgress: Ember.computed("jobState", function () {
    switch(this.get("jobState")) {
      case Worksheet.JobStates.CREATED:
      case Worksheet.JobStates.RUNNING:
      case Worksheet.JobStates.CANCELLED:
        return true;
    }
    return false;
  }),
});

Worksheet.JobStates = {
  IDLE: "IDLE",
  CREATED: "CREATED",
  RUNNING: "RUNNING",
  SUCCESS: "SUCCESS",
  CANCELLED: "CANCELLED"
};

const ID_PREFIX = "worksheet";
Worksheet.createNewId = function (existingWorksheets) {
  let id = 1, workSheetCount = existingWorksheets.get("length");

  while(--workSheetCount > 0) {
    let name = existingWorksheets.objectAt(workSheetCount).get("id");
    if(name.indexOf(ID_PREFIX) == 0) {
      let currentId = parseInt(name.slice(ID_PREFIX.length));
      if(currentId != NaN) {
        id = currentId + 1;
        break;
      }
    }
  }

  return ID_PREFIX + id;
}

export default Worksheet;