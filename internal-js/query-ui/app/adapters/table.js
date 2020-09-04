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
import DDLAdapter from './ddl';

export default DDLAdapter.extend({
  buildURL(modelName, id, snapshot, requestType, query) {
    // Check if the query is to find all tables for a particular database
    if (Ember.isEmpty(id) && (requestType === 'query' || requestType === 'queryRecord')) {
      let dbId = query.databaseId;
      let tableName = query.tableName;
      let origFindAllUrl = this._super(...arguments);
      let prefix = origFindAllUrl.substr(0, origFindAllUrl.lastIndexOf("/"));
      delete query.databaseId;
      delete query.tableName;
      if (query.isFetchAll) {
        return `${prefix}/databases/${dbId}/fetch_names`;
      } else if (Ember.isEmpty(tableName)) {
        return `${prefix}/databases/${dbId}/tables`;
      } else {
        return `${prefix}/databases/${dbId}/tables/${tableName}`;
      }
    }
    return this._super(...arguments);
  },

  fetchAllTables(databaseId, tableName) {
    let url = this.buildURL('table', null, null, 'query', {tableName, databaseId: databaseId, isFetchAll:true});
    return this.ajax(url, 'GET');
  },

  createTable(tableMetaInfo) {
    let postURL = this.buildURL('table', null, null, 'query', { databaseId: tableMetaInfo.database });
    return this.ajax(postURL, 'POST', { data: { tableInfo: tableMetaInfo } });
  },

  editTable(tableMetaInfo) {
    let postURL = this.buildURL('table', null, null, 'query',
      { databaseId: tableMetaInfo.database, tableName: tableMetaInfo.table });
    return this.ajax(postURL, 'PUT', { data: { tableInfo: tableMetaInfo } });
  },

  deleteTable(database, tableName) {
    let deletURL = this.buildURL('table', null, null, 'query', { databaseId: database, tableName: tableName });
    return this.ajax(deletURL, 'DELETE');
  },

  renameTable(database, newTableName, oldTableName) {
    let renameUrl = this.buildURL('table', null, null, 'query', { databaseId: database, tableName: oldTableName }) + '/rename';
    let data = {
      newDatabase: database,
      newTable: newTableName
    };
    return this.ajax(renameUrl, 'PUT', {data: data});
  },

  analyseTable(databaseName, tableName, withColumns = false) {
    let analyseUrl = this.buildURL('table', null, null, 'query', { databaseId: databaseName, tableName: tableName }) +
      '/analyze' +
      (withColumns ? '?analyze_columns=true' : '');
    return this.ajax(analyseUrl, 'PUT');
  },

  generateColumnStats(databaseName, tableName, columnName) {
    let url = this.buildURL('table', null, null, 'query', {databaseId: databaseName, tableName: tableName}) + `/column/${columnName}/stats`;
    return this.ajax(url, 'GET');
  },

  fetchColumnStats(databaseName, tableName, columnName, jobId) {
    let url = this.buildURL('table', null, null, 'query', {databaseId: databaseName, tableName: tableName}) + `/column/${columnName}/fetch_stats?job_id=${jobId}`;
    return this.ajax(url, 'GET');
  },

  fetchTableStats(databaseName, tableName) {
    let url = this.buildURL('table', null, null, 'query', {databaseId: databaseName, tableName: tableName}) + `/fetch_stats`;
    return this.ajax(url, 'GET');
  }
});
