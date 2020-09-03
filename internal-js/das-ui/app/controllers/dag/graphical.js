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

import MultiTableController from '../multi-table';
import ColumnDefinition from 'em-table/utils/column-definition';

export default MultiTableController.extend({

  columnSelectorTitle: 'Customize vertex tooltip',

  breadcrumbs: [{
    text: "Graphical View",
    routeName: "dag.graphical",
  }],

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
    id: 'entityID',
    headerTitle: 'Vertex Id',
    contentPath: 'entityID'
  },{
    id: 'status',
    headerTitle: 'Status',
    contentPath: 'finalStatus',
    cellComponentName: 'em-table-status-cell',
    observePath: true
  },{
    id: 'progress',
    headerTitle: 'Progress',
    contentPath: 'progress',
    cellComponentName: 'em-table-progress-cell',
    observePath: true
  },{
    id: 'startTime',
    headerTitle: 'Start Time',
    contentPath: 'startTime',
    cellComponentName: 'date-formatter',
  },{
    id: 'endTime',
    headerTitle: 'End Time',
    contentPath: 'endTime',
    cellComponentName: 'date-formatter',
  },{
    id: 'duration',
    headerTitle: 'Duration',
    contentPath: 'duration',
    cellDefinition: {
      type: 'duration'
    }
  },{
    id: 'description',
    headerTitle: 'Description',
    contentPath: 'description',
  },{
    id: 'firstTaskStartTime',
    headerTitle: 'First Task Start Time',
    contentPath: 'firstTaskStartTime',
    cellComponentName: 'date-formatter',
  },{
    id: 'totalTasks',
    headerTitle: 'Tasks',
    contentPath: 'totalTasks',
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
    id: 'processorClassName',
    headerTitle: 'Processor Class',
    contentPath: 'processorClassName',
  }]),

  redirect: function (details) {
    switch(details.type) {
      case 'vertex':
        this.transitionToRoute('vertex.index', details.d.get('data.entityID'));
      break;
      case 'task':
        this.transitionToRoute('vertex.tasks', details.d.get('data.entityID'));
      break;
      case 'io':
      break;
      case 'input':
      break;
      case 'output':
      break;
    }
  },

  actions: {
    entityClicked: function (details) {

      /**
       * In IE 11 under Windows 7, mouse events are not delivered to the page
       * anymore at all after a SVG use element that was under the mouse is
       * removed from the DOM in the event listener in response to a mouse click.
       * See https://connect.microsoft.com/IE/feedback/details/796745
       *
       * This condition and related actions must be removed once the bug is fixed
       * in all supported IE versions
       */

      // TODO: Right now there are no pages to redirect. Enable once they are added.
      // if(this.get("env.ENV.isIE")) {
      //   var pageType = details.type === "io" ? "additionals" : details.type,
      //       message = `You will be redirected to ${pageType} page`;
      //
      //   alert(message);
      // }
      // this.redirect(details);
    }
  },

  viewData: Ember.computed("model", function () {
    var model = this.get("model"),
        dag, vertices, entities;

    if(!model) {
      return {};
    }

    dag = this.get('model.firstObject.dag');
    vertices = this.get('model.firstObject.dag.vertices') || [];
    entities = {};

    model.forEach(function (vertexData) {
      entities[vertexData.get('name')] = vertexData;
    });

    vertices.forEach(function (vertex) {
      vertex.data = entities[vertex.vertexName];
    });

    return {
      vertices: vertices,
      edges: dag.get('edges'),
      vertexGroups: dag.get('vertexGroups')
    };
  })

});
