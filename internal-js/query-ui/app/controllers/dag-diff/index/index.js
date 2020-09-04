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

import Ember from 'ember';

import MultiTableController from '../../multi-table';
import ColumnDefinition from 'em-table/utils/column-definition';

export default MultiTableController.extend({
  columns: ColumnDefinition.make([{
    id: 'name',
    headerTitle: 'Vertex Name',
    contentPath: 'name',
    cellComponentName: 'em-table-linked-cell',
    getCellContent: function (row) {
      return {
        routeName: "vertex",
        model: row.get("entityID"),
        text: row.get("name")
      };
    }
  },{
    id: 'status',
    headerTitle: 'Status',
    contentPath: 'status',
    cellComponentName: 'em-table-status-cell',
    observePath: true
  },{
    id: 'progress',
    headerTitle: 'Progress',
    contentPath: 'progress',
    cellComponentName: 'em-table-progress-cell',
    observePath: true
  },{
    id: 'totalTasks',
    headerTitle: 'Total Tasks',
    contentPath: 'totalTasks',
    observePath: true
  },{
    id: 'succeededTasks',
    headerTitle: 'Succeeded Tasks',
    contentPath: 'succeededTasks',
    observePath: true
  },{
    id: 'runningTasks',
    headerTitle: 'Running Tasks',
    contentPath: 'runningTasks',
    observePath: true
  },{
    id: 'pendingTasks',
    headerTitle: 'Pending Tasks',
    contentPath: 'pendingTasks',
    observePath: true
  },{
    id: 'failedTaskAttempts',
    headerTitle: 'Failed Task Attempts',
    contentPath: 'failedTaskAttempts',
    observePath: true
  },{
    id: 'killedTaskAttempts',
    headerTitle: 'Killed Task Attempts',
    contentPath: 'killedTaskAttempts',
    observePath: true
  }]),

  definition: Ember.computed("model", function () {
    var definition = this._super();
    definition.set("recordType", "vertex");
    return definition;
  }),

  stats: Ember.computed("model.@each.loadTime", function () {
    var vertices = this.get("model");

    if(vertices) {
      let succeededVertices = 0,
          succeededTasks = 0,
          totalTasks =0,

          failedTasks = 0,
          killedTasks = 0,
          failedTaskAttempts = 0,
          killedTaskAttempts = 0;

      vertices.forEach(function (vertex) {
        if(vertex.get("status") === "SUCCEEDED") {
          succeededVertices++;
        }

        succeededTasks += vertex.get("succeededTasks");
        totalTasks += vertex.get("totalTasks");

        failedTasks += vertex.get("failedTasks");
        killedTasks += vertex.get("killedTasks");

        failedTaskAttempts += vertex.get("failedTaskAttempts");
        killedTaskAttempts += vertex.get("killedTaskAttempts");
      });

      return {
        succeededVertices: succeededVertices,
        totalVertices: vertices.get("length"),

        succeededTasks: succeededTasks,
        totalTasks: totalTasks,

        failedTasks: failedTasks,
        killedTasks: killedTasks,

        failedTaskAttempts: failedTaskAttempts,
        killedTaskAttempts: killedTaskAttempts
      };
    }
  }),

  beforeSort: function () {
    return true;
  }

});
