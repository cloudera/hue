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

export default Ember.Route.extend({
  moment: Ember.inject.service(),
  timeInitializedTo: null,
  queryParams: {
    startTime: {
      refreshModel: true
    },
    endTime: {
      refreshModel: true
    }
  },


  model(params) {
    let now = this.get('moment').moment();
    if(Ember.isEmpty(params.startTime) || Ember.isEmpty(params.endTime)) {
      let clone = now.clone();
      params.endTime = now.endOf('day').valueOf();
      params.startTime = clone.subtract('7', 'days').startOf('day').valueOf();
      this.set('startInitTo', params.startTime);
      this.set('endInitTo', params.endTime);
    }

    return this.store.query('job', params);
  },

  setupController(controller) {
    if(!(Ember.isEmpty(this.get('startInitTo')) || Ember.isEmpty(this.get('endInitTo')))) {

      controller.set('endTime', this.get('endInitTo'));
      controller.set('startTime', this.get('startInitTo'));
      //unset timeInitializedTo
      this.set('endInitTo');
      this.set('startInitTo');
    }

    this._super(...arguments);

  },

  actions: {
    dateFilterChanged(startTime, endTime) {
      this.controller.set('startTime', this.get('moment').moment(startTime, 'YYYY-MM-DD').startOf('day').valueOf());
      this.controller.set('endTime', this.get('moment').moment(endTime, 'YYYY-MM-DD').endOf('day').valueOf());
      this.refresh();
    }
  }



});
