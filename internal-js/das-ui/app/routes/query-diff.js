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
import RSVP from 'rsvp';
import queryDetailsTabs from '../configs/query-details-tabs';
import commons from '../mixins/commons';

export default Ember.Route.extend(commons, {
  model: function (params, transition) {
    return RSVP.hash({
      query1: this.store.queryRecord('hive-query', {queryId: transition.queryParams.query_1, extended: true}),
      query2: this.store.queryRecord('hive-query', {queryId: transition.queryParams.query_2, extended: true})
    });
  },
  breadCrumb: {
    title: '',
  },
  loaderNamespace: "query",
  renderTemplate: function() {

    this.render();
    this.render('query-diff.configs', {
      into: 'query-diff',
      outlet: 'configs',
      controller: 'query-diff.configs'
    });
    this.render('query-diff.timeline', {
      into: 'query-diff',
      outlet: 'timeline',
      controller: 'query-diff.timeline'
    });

    this.render('dag-diff.swimlane', {
      into: 'query-diff',
      outlet: 'dag-swimlane',
      controller: 'dag-diff.swimlane'
    });
    this.render('dag-diff.graphical', {
      into: 'query-diff',
      outlet: 'dag-graphical-view',
      controller: 'dag-diff.graphical',
      model:[]
    });
    this.render('dag-diff.counters', {
      into: 'query-diff',
      outlet: 'dag-counters',
      controller: 'dag-diff.counters'
    });
    this.render('dag-diff.configs', {
      into: 'query-diff',
      outlet: 'dag-configs',
      controller: 'dag-diff.configs'
    });

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
  setupController: function (controller, model) {
  	console.log(model);
    this._super(controller, model);
    this.logGA('QUERY_DIFF');
    this.set('breadCrumb.title', this.getQueryDetailsPage('Query Compare'));
    controller.set('queries', model);

    this.set("queryModel", model);

    model.query1.set('tablesReadWithDatabase', model.query1.get('tablesRead').map(function (data) {
      return `${data.table} (${data.database})`;
    }).join(", "));

    model.query1.set( 'tablesWrittenWithDatabase', model.query1.get('tablesWritten').map(function (data) {
      return `${data.table} (${data.database})`;
    }).join(", "));

    model.query2.set('tablesReadWithDatabase', model.query2.get('tablesRead').map(function (data) {
      return `${data.table} (${data.database})`;
    }).join(", "));

    model.query2.set( 'tablesWrittenWithDatabase', model.query2.get('tablesWritten').map(function (data) {
      return `${data.table} (${data.database})`;
    }).join(", "));

    controller.set('queryDetailsTabs', queryDetailsTabs);
    controller.set('query1', JSON.stringify(model.query1.get('details.explainPlan')));
    controller.set('query2', JSON.stringify(model.query2.get('details.explainPlan')));
    this.controllerFor('query-diff.configs').set('configsmodel', model);
    this.controllerFor('query-diff.timeline').set('timelinemodel', model);

    this.controllerFor('query-diff.dag').set('dagmodel', model.query1);
    //this.controllerFor('query-diff.configs').set('configsmodel', model.query1);

    this.renderDAGTabs(Ember.get(model, "query1.dags.0.dagInfo.dagId"), Ember.get(model, "query2.dags.0.dagInfo.dagId"));

    let isDAGEmpty = Ember.$.isEmptyObject(this.controllerFor('dag-diff.counters').get('model.counterGroupsHash1')) && Ember.$.isEmptyObject(this.controllerFor('dag-diff.counters').get('model.counterGroupsHash2')) && !(model.query1.get('executionMode') === 'LLAP' || model.query1.get('executionMode') === 'TEZ') && !(model.query2.get('executionMode') === 'LLAP' || model.query2.get('executionMode') === 'TEZ');
    let queryDetailsTabsMod = queryDetailsTabs;
    controller.set('isDAGEmpty', isDAGEmpty);
    if(isDAGEmpty) {
      queryDetailsTabsMod = queryDetailsTabsMod.filter(queryDetailsTab => queryDetailsTab.id !== "dag-panel");
    }
    controller.set('queryDetailsTabsMod', queryDetailsTabsMod);
  },
  renderDAGTabs(dagId1, dagId2) {
    let model = this.get("queryModel");

    this.setProperties({
      dagId1: dagId1,
      dagId2: dagId2,
    });

    let dags1 = Ember.get(model, "query1.dags");
    let dags2 = Ember.get(model, "query2.dags");

    let dag1 = dags1.find(dag => dag.dagInfo.dagId === dagId1) || {};
    let dag2 = dags2.find(dag => dag.dagInfo.dagId === dagId2) || {};

    this.controllerFor('dag-diff.counters').set('model', {
      counterGroupsHash1: this.createCounterGroupsHash(Ember.get(dag1, "dagDetails.counters") || []),
      counterGroupsHash2: this.createCounterGroupsHash(Ember.get(dag2, "dagDetails.counters") || [])
    });

    this.controllerFor('dag-diff.counters').set('definition.searchText', '');

    this.controllerFor('dag-diff.configs').set('configsmodel1', dag1.config);
    this.controllerFor('dag-diff.configs').set('configsmodel2', dag2.config);

    var that = this;
    this.controllerFor('dag-diff.swimlane').set('model', {});
    this.controllerFor('dag-diff.graphical').set('model', {});
    let vertices1 = new Promise((resolve, reject) => {
      that.get("loader").query('vertex', {dagId: Ember.get(dag1, "dagInfo.dagId")}, {reload: true}).then(function (vertices) {
        vertices = that.createVerticesData(vertices, Ember.get(dag1, "dagInfo"), Ember.get(dag1, "dagDetails.dagPlan"));
        resolve(vertices);
      }, function () {
        resolve([]);
      });
    });

    let vertices2 = new Promise((resolve, reject) => {
      that.get("loader").query('vertex', {dagId: Ember.get(dag2, "dagInfo.dagId")}, {reload: true}).then(function (vertices) {
        vertices = that.createVerticesData(vertices, Ember.get(dag2, "dagInfo"), Ember.get(dag2, "dagDetails.dagPlan"));
        resolve(vertices);
      }, function () {
        resolve([]);
      });
    });

    Promise.all([vertices1, vertices2]).then(values => {
      that.controllerFor('dag-diff.swimlane').set('model.query1', values[0]);
      that.controllerFor('dag-diff.graphical').set('model.query1', values[0]);
      that.controllerFor('dag-diff.swimlane').set('model.query2', values[1]);
      that.controllerFor('dag-diff.graphical').set('model.query2', values[1]);
    });
  },

  actions: {
    rerenderDAGTabsPanel1: function(dagId){
      this.renderDAGTabs(dagId, this.get("dagId2"));
    },
    rerenderDAGTabsPanel2: function(dagId){
      this.renderDAGTabs(this.get("dagId1"), dagId);
    },
  }

});
