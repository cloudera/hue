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
import SingleAmPollsterRoute from '../single-am-pollster';
import queryDetailsTabs from '../../configs/query-details-tabs';
import commons from '../../mixins/commons';
import ENV from '../../config/environment';
import Worksheet from '../../models/worksheet';

import { getDominantDatabase } from '../../utils/databases';

export default SingleAmPollsterRoute.extend(commons, ENV, {

  breadCrumb: {
    title: '',
  },
  renderTemplate: function() {


    this.render();

    this.render('query.visual-explain', {
      into: 'query.index',
      outlet: 'visual-explain',
      controller: 'query.visual-explain'
    });

    this.render('query.timeline', {
      into: 'query.index',
      outlet: 'timeline',
      controller: 'query.timeline'
    });

    this.render('query.dag', {
      into: 'query.index',
      outlet: 'dag',
      controller: 'query.dag'
    });

    this.render('query.configs', {
      into: 'query.index',
      outlet: 'configs',
      controller: 'query.configs'
    });

    // DAG panel
    this.render('dag.swimlane', {
      into: 'query.index',
      outlet: 'dag-swimlane',
      controller: 'dag.swimlane'
    });
    this.render('dag.graphical', {
      into: 'query.index',
      outlet: 'dag-graphical-view',
      controller: 'dag.graphical',
      model: []
    });
    this.render('dag.counters', {
      into: 'query.index',
      outlet: 'dag-counters',
      controller: 'dag.counters'
    });

    this.render('dag.configs', {
      into: 'query.index',
      outlet: 'dag-configs',
      controller: 'dag.configs'
    });

  },

  title: "Query Details",

  loaderNamespace: "query",

  getDiagnostics: function (source) {
    var diagnostics = Ember.get(source, 'diagnostics') || "";

    // To strip out HTML tags
    var div = document.createElement("div");
    div.innerHTML = diagnostics;
    diagnostics = div.textContent || div.innerText || "";

    diagnostics = diagnostics.replace(/\t/g, "&emsp;&emsp;");
    diagnostics = diagnostics.replace(/\[/g, "<div>&#187; ");
    diagnostics = diagnostics.replace(/\]/g, "</div>");

    return diagnostics;
  },

  setupController: function (controller, model) {
    this._super(controller, model);
    this.controllerFor('query.index').set('queryDetailsTabs', queryDetailsTabs);
    this.set('breadCrumb.title', this.getQueryDetailsPage(this.controllerFor('query').get('hiveQueryId')));
    let querymodel = this.modelFor("query");

    querymodel.set('tablesReadWithDatabase', querymodel.get('tablesRead').map(function (data) {
      return `${data.table} (${data.database})`;
    }).join(", "));

    querymodel.set( 'tablesWrittenWithDatabase', querymodel.get('tablesWritten').map(function (data) {
      return `${data.table} (${data.database})`;
    }).join(", "));

    if(querymodel.get("details")) {
      querymodel.set("details.diagnostics", this.getDiagnostics(querymodel.get("details")));
    }

    this.controllerFor('query.index').set('querymodel', querymodel);
    this.controllerFor('query.index').set('isDASLITE', ENV.APP.DASLITE);
    this.controllerFor('query.visual-explain').set('model', querymodel);
    this.controllerFor('query.timeline').set('timelinemodel', querymodel);
    this.controllerFor('query.dag').set('dagmodel', querymodel);
    this.controllerFor('query.configs').set('configsmodel', querymodel);

    this.renderDAGTabs(querymodel.get("dags.0.dagInfo.dagId"));

    let isDAGEmpty = Ember.$.isEmptyObject(this.controllerFor('dag.counters').get('model.counterGroupsHash')) && !(querymodel.get('executionMode') === 'LLAP' || querymodel.get('executionMode') === 'TEZ');
    let queryDetailsTabsMod = queryDetailsTabs;
    controller.set('isDAGEmpty', isDAGEmpty);
    if(isDAGEmpty) {
      queryDetailsTabsMod = queryDetailsTabsMod.filter(queryDetailsTab => queryDetailsTab.id !== "dag-panel");
    }
    controller.set('queryDetailsTabsMod', queryDetailsTabsMod);
  },

  renderDAGTabs(dagId) {
    let querymodel = this.modelFor("query");
    let dags = querymodel.get("dags");
    if(!dags) return;
    let dag = dags.find(dag => dag.dagInfo.dagId === dagId);
    if(!dag) return;

    this.controllerFor('dag.counters').set('model', {
      counterGroupsHash: this.createCounterGroupsHash(Ember.get(dag, "dagDetails.counters") || [])
    });

    this.controllerFor('dag.counters').set('definition.searchText', '');
    if(this.controllerFor('query.configs').get('definition.searchText') !== 'hive.') {
      this.controllerFor('query.configs').set('definition.searchText', '');
    }

    this.controllerFor('dag.configs').set('configsmodel', dag.config);

    var that = this;
    that.controllerFor('dag.graphical').set('loaded', false);
    this.get("loader").query('vertex', {dagId: Ember.get(dag, "dagInfo.dagId")}, {reload: true}).then(function (vertices) {
      vertices = that.createVerticesData(vertices, Ember.get(dag, "dagInfo"), Ember.get(dag, "dagDetails.dagPlan"));
      that.controllerFor('dag.swimlane').set('model', vertices);
      that.controllerFor('dag.swimlane').set('query', querymodel);
      that.controllerFor('dag.graphical').set('model', vertices);
      that.controllerFor('dag.graphical').set('loaded', true);
    }, function () {
      that.controllerFor('dag.swimlane').set('model', []);
      that.controllerFor('dag.swimlane').set('query', null);
      that.controllerFor('dag.graphical').set('model', []);
    });
  },

  deactivate() {
    this.controllerFor('query.index').set('querymodel', []);
    this.controllerFor('query.index').set('isDASLITE', "");
    this.controllerFor('query.visual-explain').set('model', []);
    this.controllerFor('query.timeline').set('timelinemodel', []);
    this.controllerFor('query.dag').set('model', []);
    this.controllerFor('query.configs').set('configsmodel', []);
    this.controllerFor('dag.counters').set('model', {
      counterGroupsHash: []
    });

    var controller = this.controllerFor('dag.swimlane');
    controller.set("selectedVertex", null);
    controller.set("taskAttempts", null);
  },
  isDAGComplete: function (status) {
    switch(status) {
      case "SUCCEEDED":
      case "FINISHED":
      case "FAILED":
      case "KILLED":
      case "ERROR":
        return true;
    }
    return false;
  },

  createVerticesData: function (vertices, dagInfo, dagPlan) {

    if (!dagPlan || !dagPlan.vertices) {
      return []
    }

    var dagObj = Ember.Object.create({
      amWsVersion: 2,
      isComplete: this.isDAGComplete(dagInfo.status),

      edges: dagPlan.edges,
      vertices: dagPlan.vertices,
    });

    vertices.forEach(function (vertex) {
      vertex.set("dag", dagObj);
    });

    return vertices;
  },


  createCounterGroupsHash: function(counterGroups) {
    var counterHash = {};

    counterGroups.forEach(function (group) {
      var counters = group.counters,
          groupHash;

      groupHash = counterHash[group.counterGroupName] = counterHash[group.counterGroupName] || {};

      counters.forEach(function (counter) {
        groupHash[counter.counterName] = counter.counterValue;
      });
    });

    return counterHash;
  },


  load: function (value, query, options) {
    //return this.get("loader").queryRecord('hive-query', this.modelFor("query").get("id"), options);
  },

  actions: {
    rerenderDAGTabsPanel: function(dagId){
      this.renderDAGTabs(dagId);
    },
    loadTaskAttempts: function (vertex, status, sort, limit) {
      var controller = this.controllerFor('dag.swimlane');
      controller.set("taskAttempts", undefined);
      this.get("store").query('task-attempt', {
        params: {
          vertexId: vertex.get("entityID"),
          status: status,
          sort: sort,
          limit: limit
        }
      }).then(function (taskAttempts) {
        controller.set("taskAttempts", taskAttempts);
      }).catch(function () {
        controller.set("taskAttempts", null);
      });
    }
  },
});



