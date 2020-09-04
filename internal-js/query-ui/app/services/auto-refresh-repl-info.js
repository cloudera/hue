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

export default Ember.Service.extend({
  store: Ember.inject.service(),
  isReplRefresherRunning: false,
  replResult: null,
  replCallInterval: 30000,
  timeSinceLastUpdate: Ember.computed('replResult', function(){
    let time = moment().unix() - moment.utc(this.get('replResult.info.lastReplicationStartTime')).unix();
    return time > 0 ? time : 0;
  }),

  startReplAutoRefresh(replRefreshStartingCallback, replRefreshedCallback, startAfter = 5 * 1000, interval = 10 * 1000) {
    if (this.get('isReplRefresherRunning')) {
      return;
    }
    console.log("Starting repl auto refresh");
    this.set('isReplRefresherRunning', true);

    Ember.run.later(() => {
      this._refreshReplInfo(replRefreshStartingCallback, replRefreshedCallback, interval);
    }, startAfter);
  },

  stopReplAutoRefresh(){
    this.set('isReplRefresherRunning', false);
  },

  getReplInfo(){
    return this.get('replResult');
  },

  getTimeSinceLastUpdate(){
    return this.get('timeSinceLastUpdate');
  },

  _refreshReplInfo(replRefreshStartingCallback, replRefreshedCallback, interval){
    let reRun = () => {
      Ember.run.later(() => {
        this._refreshReplInfo(replRefreshStartingCallback, replRefreshedCallback, interval);
      }, this.get('replCallInterval'));
    };

    if (this.get('isReplRefresherRunning')) {
      replRefreshStartingCallback();

      this.get('store').adapterFor('info').getReplInfo()
            .then(data => {
              this.set('replResult', data)
              replRefreshedCallback();
              reRun();
            }, err => {
              reRun(); //Add error callback logic here when passed.
            });
    }
  },
  _refreshReplInfoRef(replRefreshedCallback, interval){
      setInterval(() => {
        this.get('store').adapterFor('info').getReplInfo().then(data => {
            this.set('replResult', data);
            let time = moment().unix() - moment.utc(this.get('replResult.info.lastReplicationStartTime')).unix();
            replRefreshedCallback(time > 0 ? time : 0);
        });
      }, this.get('replCallInterval'));
  }
});
