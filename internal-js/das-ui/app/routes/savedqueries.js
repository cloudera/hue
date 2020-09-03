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
import UILoggerMixin from '../mixins/ui-logger';
import commons from '../mixins/commons';

export default Ember.Route.extend(UILoggerMixin, commons, {
  breadCrumb: {
    title: 'Saved Queries'
  },
  savedQueries: Ember.inject.service(),
  store: Ember.inject.service(),
  beforeModel() {
    this.closeAutocompleteSuggestion();
  },
  model() {
    return this.store.findAll('savedQuery').then(savedQueries => savedQueries.toArray());
  },

  setupController(controller, model) {
    this.logGA('SAVEDQUERIES');
    this._super(...arguments);

    controller.set('savedQuerylist', model);

    controller.set('showDeleteSaveQueryModal', false);
    controller.set('selectedSavedQueryId', null);
    controller.set('preview', {"noSort":true});
    controller.set('title', {"noSort":true});
    controller.set('selectedDatabase', {"noSort":true});
    controller.set('owner', {"noSort":true});

  },

  actions: {
    sort(sortProp, sortField, key) {
      let perm = {};
      perm[key] = true;
      this.get('controller').set(sortField, perm);
      this.get('controller').set('sortProp', [sortProp]);
    },
    deleteSavedQuery(){
      this.logGA('SAVEDQUERIES_DELETE');

      let self = this;
      let queryId = this.get('controller').get('selectedSavedQueryId');

      console.log('deleteSavedQuery', queryId);
      this.get('store').findRecord('saved-query', queryId, { backgroundReload: false }).then(function(sq) {
        sq.deleteRecord();
        sq.save().then(() => {
          self.send('refreshSavedQueryListAfterDeleteQuery', queryId);
          self.send('closeDeleteSavedQueryModal');
        })
      });
    },

    refreshSavedQueryList(queryId){
      let savedQueryList = [];
      this.get('store').findAll('saved-query').then(data => {
        data.forEach(x => {
          let localSavedQuery = Ember.Object.create({
            'id': x.get('id'),
            'selectedDatabase': x.get('selectedDatabase'),
            'title': x.get('title'),
            'query': x.get('query'),
            'owner': x.get('owner'),
            'shortQuery': x.get('shortQuery')
          });
          savedQueryList.pushObject(localSavedQuery);
        })
      })
      .then(() => {
        this.controllerFor('savedqueries').set('savedQuerylist',savedQueryList);
        this.transitionTo('savedqueries');
      })
    },

    refreshSavedQueryListAfterDeleteQuery(queryId){
      var updatedList = this.controllerFor('savedqueries').get('savedQuerylist').filter(function(item){
        return !(item.get('id').toString() == queryId.toString());
      })
      this.controllerFor('savedqueries').set('savedQuerylist', updatedList);
    },

    deleteSavedQueryDeclined(){
      this.get('controller').set('selectedSavedQueryId', null);
      this.get('controller').set('showDeleteSaveQueryModal', false );
    },

    openDeleteSavedQueryModal(id){
      this.get('controller').set('showDeleteSaveQueryModal', true );
      this.get('controller').set('selectedSavedQueryId', id );
    },

    closeDeleteSavedQueryModal(){
      this.get('controller').set('showDeleteSaveQueryModal', false );
      this.get('controller').set('selectedSavedQueryId', null );
    },

    openAsWorksheet(savedQuery){
    }
  }

});
