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

export default Ember.Service.extend({
  jobs: Ember.inject.service(),
  store: Ember.inject.service(),

  generateStatistics(databaseName, tableName, withColumns = false) {
    return new Ember.RSVP.Promise((resolve, reject) => {
      this.get('store').adapterFor('table').analyseTable(databaseName, tableName, withColumns).then((data) => {
        this.get('store').pushPayload(data);
        resolve(this.get('store').peekRecord('job', data.job.id));
      }, (err) => {
        reject(err);
      });
    });
  },

  generateColumnStatistics(databaseName, tableName, columnName) {
    return new Ember.RSVP.Promise((resolve, reject) => {
      this.get('store').adapterFor('table').generateColumnStats(databaseName, tableName, columnName).then((data) => {
        this.get('store').pushPayload(data);
        resolve(this.get('store').peekRecord('job', data.job.id));
      }, (err) => {
        reject(err);
      });
    });
  },

  waitForStatsGenerationToComplete(job, fetchDummyResult = true) {
    return new Ember.RSVP.Promise((resolve, reject) => {
      this.get('jobs').waitForJobToComplete(job.get('id'), 5 * 100, fetchDummyResult, true).then((data) => {
        resolve(job);
      }, (err) => {
        reject(err);
      });
    });
  },

  fetchColumnStatsResult(databaseName, tableName, columnName, job) {
    return this.get('store').adapterFor('table').fetchColumnStats(databaseName, tableName, columnName, job.get('id')).then((data) => {
      let columnStats = data.columnStats;
      return columnStats;
    });
  },

  fetchTableStatistics(databaseName, tableName) {
    return this.get('store').adapterFor('table').fetchTableStats(databaseName, tableName).then((data) => {
      return data.tableStats;
    });
  }
});
