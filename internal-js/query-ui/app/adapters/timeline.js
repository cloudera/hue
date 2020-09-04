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

import AbstractAdapter from './abstract';

var MoreObject = more.Object;

export default AbstractAdapter.extend({
  serverName: "timeline",
  outOfReachMessage: "Timeline server (ATS) is out of reach. Either it's down, or CORS is not enabled.",

  filters: {
    dagID: 'TEZ_DAG_ID',
    vertexID: 'TEZ_VERTEX_ID',
    taskID: 'TEZ_TASK_ID',
    attemptID: 'TEZ_TASK_ATTEMPT_ID',
    hiveQueryID: 'HIVE_QUERY_ID',
    appID: 'applicationId',

    dagName: 'dagName',
    user: "user",
    status: "status",
    callerID: "callerId",
    requestuser: "requestuser",
    executionMode: "executionmode",
    callerId: "callerId",
    queueName: "queueName",

    tablesRead: "tablesread",
    tablesWritten: "tableswritten",
    operationID: "operationid",
    queue: "queue",
  },

  stringifyFilters: function (filters) {
    var filterStrs = [];

    MoreObject.forEach(filters, function (key, value) {
      value = JSON.stringify(String(value));
      filterStrs.push(`${key}:${value}`);
    });

    return filterStrs.join(",");
  },

  normalizeQuery: function(query) {
    var primaryFilter = null, // Primary must have just one single filter
        secondaryFilters = {},
        normalQuery = {},
        filterStr;

    MoreObject.forEach(query, function (key, value) {
      var filter = this.get(`filters.${key}`);

      if(filter) {
        if(!primaryFilter) {
          primaryFilter = {};
          primaryFilter[filter] = value;
        }
        else {
          secondaryFilters[filter] = value;
        }
      }
      else {
        normalQuery[key] = value;
      }
    }, this);

    // primaryFilter
    if(primaryFilter) {
      filterStr = this.stringifyFilters(primaryFilter);
    }
    if(filterStr) {
      normalQuery.primaryFilter = filterStr;
    }

    // secondaryFilters
    filterStr = this.stringifyFilters(secondaryFilters);
    if(filterStr) {
      normalQuery.secondaryFilter = filterStr;
    }

    // Limit
    normalQuery.limit = normalQuery.limit || this.get("env.app.rowLoadLimit");

    return normalQuery;
  },

  query: function (store, type, query/*, recordArray*/) {
    var queryParams = query.params,
        url = this.buildURL(type.modelName, null, null, 'query', queryParams, query.urlParams);

    if(query) {
      queryParams = this.normalizeQuery(queryParams);
    }

    return this._loaderAjax(url, queryParams, query.nameSpace);
  }
});
