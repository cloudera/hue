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
import VertexProcess from '../../utils/vertex-process';

import fullscreen from 'em-tgraph/utils/fullscreen';

export default MultiTableController.extend({

  zoomQuery1: 100,
  zoomQuery2: 100,

  columnSelectorTitle: 'Customize vertex tooltip',

  breadcrumbs: [{
    text: "Vertex Swimlane",
    routeName: "dag.swimlane",
  }],

  columns: ColumnDefinition.make([{
    id: 'entityID',
    headerTitle: 'Vertex Id',
    contentPath: 'entityID'
  },{
    id: 'status',
    headerTitle: 'Status',
    contentPath: 'finalStatus',
  },{
    id: 'progress',
    headerTitle: 'Progress',
    contentPath: 'progress',
    cellDefinition: {
      type: 'number',
      format: '0%'
    }
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
  },{
    id: 'runningTasks',
    headerTitle: 'Running Tasks',
    contentPath: 'runningTasks',
  },{
    id: 'pendingTasks',
    headerTitle: 'Pending Tasks',
    contentPath: 'pendingTasks',
  },{
    id: 'processorClassName',
    headerTitle: 'Processor Class',
    contentPath: 'processorClassName',
  }]),

  dataAvailableForQuery1: Ember.computed("model.query1.firstObject.dag.amWsVersion",
      "model.query1.firstObject.dag.isComplete",
      "model.query1.firstObject.am.initTime", function () {
    let vertex = this.get("model.query1.firstObject"),
        dag = this.get("model.query1.firstObject.dag"),
        dataAvailable = true;

    if(vertex && dag && !dag.get("isComplete")) {
      let amWsVersion = dag.get("amWsVersion");
      // amWsVersion = undefined or 1
      if(!amWsVersion || amWsVersion === 1) {
        dataAvailable = false;
      }
      // amWsVersion >= 2, but without event/time data
      if(vertex.get("am") && !vertex.get("am.initTime")) {
        dataAvailable = false;
      }
    }

    return dataAvailable;
  }),


  dataAvailableForQuery2: Ember.computed("model.query2.firstObject.dag.amWsVersion",
      "model.query2.firstObject.dag.isComplete",
      "model.query2.firstObject.am.initTime", function () {
    let vertex = this.get("model.query2.firstObject"),
        dag = this.get("model.query2.firstObject.dag"),
        dataAvailable = true;

    if(vertex && dag && !dag.get("isComplete")) {
      let amWsVersion = dag.get("amWsVersion");
      // amWsVersion = undefined or 1
      if(!amWsVersion || amWsVersion === 1) {
        dataAvailable = false;
      }
      // amWsVersion >= 2, but without event/time data
      if(vertex.get("am") && !vertex.get("am.initTime")) {
        dataAvailable = false;
      }
    }

    return dataAvailable;
  }),

  processes1: Ember.computed("model.query1", function () {
    let processes = [],
        processHash = {},

        dagPlanEdges = this.get("model.query1.firstObject.dag.edges"),

        that = this,
        getVisibleProps = function () {
          return that.get("visibleColumns");
        };

    // Create process instances for each vertices
    if(this.get("model.query1")) {
      this.get("model.query1").forEach(function (vertex) {
        var process = VertexProcess.create({
          vertex: vertex,
          getVisibleProps: getVisibleProps,
          blockers: Ember.A()
        });
        processHash[vertex.get("name")] = process;
        processes.push(process);
      });

      // Add process(vertex) dependencies based on dagPlan
      if(dagPlanEdges) {
        dagPlanEdges.forEach(function (edge) {
          var process = processHash[edge.outputVertexName];
          if(process && processHash[edge.inputVertexName]) {
            process.blockers.push(processHash[edge.inputVertexName]);
            process.edgeHash.set(edge.inputVertexName, edge);
          }
        });
      }
    }
    console.log("returning processes1");

    return Ember.A(processes);
  }),
  processes2: Ember.computed("model.query2", function () {
    let processes = [],
        processHash = {},

        dagPlanEdges = this.get("model.query2.firstObject.dag.edges"),

        that = this,
        getVisibleProps = function () {
          return that.get("visibleColumns");
        };

    // Create process instances for each vertices
    if(this.get("model.query2")) {
      this.get("model.query2").forEach(function (vertex) {
        var process = VertexProcess.create({
          vertex: vertex,
          getVisibleProps: getVisibleProps,
          blockers: Ember.A()
        });
        processHash[vertex.get("name")] = process;
        processes.push(process);
      });

      // Add process(vertex) dependencies based on dagPlan
      if(dagPlanEdges) {
        dagPlanEdges.forEach(function (edge) {
          var process = processHash[edge.outputVertexName];
          if(process && processHash[edge.inputVertexName]) {
            process.blockers.push(processHash[edge.inputVertexName]);
            process.edgeHash.set(edge.inputVertexName, edge);
          }
        });
      }
    }
    console.log("returning processes2");
    return Ember.A(processes);
  }),
  actions: {
    toggleFullscreen: function (index) {
      var swimlaneElement = Ember.$(".swimlane-page").get(index);
      if(swimlaneElement){
        fullscreen.toggle(swimlaneElement);
      }
    },
    click: function (type, process) {
      // TODO: Right now there are no pages to redirect. Enable once they are added.
      // this.transitionToRoute('vertex.index', process.get('vertex.entityID'));
    }
  }
});
