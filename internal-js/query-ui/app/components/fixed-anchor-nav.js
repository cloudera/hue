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
import UILoggerMixin from '../mixins/ui-logger';
import ENV from '../config/environment';

export default Ember.Component.extend(UILoggerMixin, {
  hiveQuery: Ember.inject.service('hive-query'),
  anchors: [],
  tagName: 'ul',
  classNames: ['fixed-anchor-list'],
  targetId: null,
  pageOffset: 130,
  scrollOffset: 10,
  browserCorrection: 5,

  stoppingQuery: false,
  querymodel: null,

  _addDifference: function (lastTarget, height) {
    $(lastTarget).css('min-height', height);
    //$('.fake-container').css('height', height);
  },

  didInsertElement() {
    var self = this;

    let lastTarget = $('.target').last();
    let lastTargetHeight = $(lastTarget).height();
    let windiwtHeight = $(window).height();

    if(lastTargetHeight <  windiwtHeight) {
      this._addDifference(lastTarget, windiwtHeight);
    }
  },

  willDestroyElement: function() {
    this.set('stoppingQuery', false);
    this._super();
  },

  reloadQueryTillComplete(iterations) {
    var that = this;
    if(iterations && this.get("stoppingQuery")) {
      this.get("querymodel").reload().then(function () {
        Ember.run.later(that, "reloadQueryTillComplete", iterations - 1, 2000);
      });
    }
  },

  _isCompleteObserver: Ember.observer("querymodel.isComplete", function () {
    if(this.get("querymodel.isComplete")) {
      this.set("stoppingQuery", false);
    }
  }),

  actions:{
    stopQuery: function () {
      var that = this;
      this.set("stoppingQuery", true);
      this.get("hiveQuery").stopQuery(this.get("querymodel.queryId")).then(function () {
        that.reloadQueryTillComplete(20);
      });
    },

    moveViewTo(id) {
      this.set('targetId', id);
      $('html, body').animate({
        scrollTop: $("#" +  id).offset().top - this.get('pageOffset') + this.get('browserCorrection')
      }, 200);
    },

    downloadLogs(queryId){
      let win = window.open("", "_self");

      this.get('hiveQuery').getToken()
        .then(tokenJson => {
           let domain = window.location.protocol + "//" + window.location.host;
           let url = domain + ENV.rootURL + '/api/data-bundle/query/' + queryId + '?xsrfToken=' + tokenJson.token;
           win.location.href = url;
           win.focus();
        }) ,(error =>{
          console.log('Error in downloading.');
          this.get('logger').danger('Failed to download logs.', this.extractError(error));
        })
   }
  }
});



