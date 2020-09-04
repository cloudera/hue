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
import ENV from '../config/environment';
import constants from '../utils/constants';

export default Ember.Component.extend({
  apiAccessError: false,
  productInfo: Ember.A(),
  autoRefreshReplInfo: Ember.inject.service(),
  criticalTime: 15, // in mins
  infoLabels: {
    user : 'User',
    clusterId :'Cluster Id',
    databaseProductName :'Database product',
    databaseProductVersion :'Database product version',
    productName: 'Product name',
    productVersion: 'Product version',
    jdbcConnection:'JDBC connection'
  },

  elementsInserted : function() {
    setInterval((function() {
      Ember.$(".dropdown-toggle").dropdown();
    }), 2000);

    if(ENV.APP.SHOULD_AUTO_REFRESH_REPL_INFO) {
      this.get('autoRefreshReplInfo')._refreshReplInfoRef(this._replInfoRefreshed.bind(this), 20000);
    }

  }.on('didInsertElement'),
  _replInfoRefreshed(data) {
    let mins = Math.floor(data / 60);
    this.set('timeSinceLastUpdate',  mins);
    this.checkForCriticality(mins);
  },
  checkForCriticality(mins) {
    let isCritical = mins >= this.get('criticalTime') ? true : false;
    this.set('isCritical', isCritical);
    this.set('criticalLabel', constants.labels.autorefresherror);
  },
  showAboutDetails:false,

  actions: {
    logout: function() {
      this.sendAction("logout");
    },
    showCloseDialog: function() {
      this.set('showAboutDetails', true);
    },
    closeAboutDialog: function() {
      this.set('showAboutDetails', false);
    },
    saveConnection: function(newConnectionUrl) {
      return this.get('saveConnection')(newConnectionUrl);
    },
    resetConnection: function() {
      return this.get('resetConnection')();
    },
    showCriticialDetails: function() {
      this.set('showCriticialDetailsModal', true);
    },
    hideCriticialDetails: function() {
      this.set('showCriticialDetailsModal', false);
    }
  }
});
