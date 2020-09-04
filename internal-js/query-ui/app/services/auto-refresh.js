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

export default Ember.Service.extend({
  store: Ember.inject.service(),
  isDatabaseRefresherRunning: false,
  tablesRefresherRunningStatus: {},


  startDatabasesAutoRefresh(databaseRefreshStartingCallback, databaseRefreshedCallback, startAfter = 30 * 1000, interval = 30 * 1000) {
    if (this.get('isDatabaseRefresherRunning')) {
      return;
    }

    console.log("Starting database auto refresh");

    this.set('isDatabaseRefresherRunning', true);
    Ember.run.later(() => {
      this._refreshDatabases(databaseRefreshStartingCallback, databaseRefreshedCallback, interval);
    }, startAfter);


  },

  _refreshDatabases(databaseRefreshStartingCallback, databaseRefreshedCallback, interval) {
    let reRun = () => {
      Ember.run.later(() => {
        this._refreshDatabases(databaseRefreshStartingCallback, databaseRefreshedCallback, interval);
      }, interval);
    };

    if (this.get('isDatabaseRefresherRunning')) {
      databaseRefreshStartingCallback();
      let oldDatabases = this.get('store').peekAll('database').mapBy('name');
      this.get('store').query('database', {}).then((data) => {
        let deletedDbCount = 0;
        let newDatabases = data.mapBy('name');
        oldDatabases.forEach((oldDB) => {
          if (!newDatabases.contains(oldDB)) {
            deletedDbCount++;
            let oldRecord = this.get('store').peekRecord('database', oldDB);
            this.get('store').unloadRecord(oldRecord);
          }
        });

        // Hack: Had to wrap the refreshed call inside run later because, unloadRecord is not synchronously unloading
        // records from store.
        Ember.run.later(() => databaseRefreshedCallback(deletedDbCount));
        reRun();
      }).catch((err) => {
        reRun();
      });
    }
  },

  stopDatabasesAutoRefresh() {
    console.log("Stopping database auto refresh");
    this.set('isDatabaseRefresherRunning', false);
  },

  startTablesAutoRefresh(databaseName, tablesRefreshStartingCallback, tablesRefreshedCallback, startAfter = 15 * 1000, interval = 15 * 1000) {
    if(!Ember.isEmpty(this.get('tablesRefresherRunningStatus')[databaseName])) {
      if (this.get('tablesRefresherRunningStatus')[databaseName]["started"]) {
        return;
      }
    }


    console.log("Starting tables auto refresh for " + databaseName);
    this.set('tablesRefresherRunningStatus',{});

    this.get('tablesRefresherRunningStatus')[databaseName] = {};
    this.get('tablesRefresherRunningStatus')[databaseName]["started"] = true;
    Ember.run.later(() => {
      this.refreshTables(databaseName, tablesRefreshStartingCallback, tablesRefreshedCallback, false, interval);
    }, startAfter);
  },

  refreshTables(databaseName, tablesRefreshStartingCallback, tablesRefreshedCallback, runOnce = false, interval) {
    let reRun = () => {
      let intervalRef = Ember.run.later(() => {
        this.refreshTables(databaseName, tablesRefreshStartingCallback, tablesRefreshedCallback, false, interval);
      }, interval);
      this.get('tablesRefresherRunningStatus')[databaseName]["intervalRef"] = intervalRef;
    };

    if (this.get('tablesRefresherRunningStatus')[databaseName]) {
      tablesRefreshStartingCallback(databaseName);
      let oldTableNames = this.get('store').peekAll('table').filterBy('database.name', databaseName).mapBy('name');
      this.get('store').query('table', {databaseId: databaseName}).then((data) => {
        let deletedTablesCount = 0;
        let newTableNames = data.mapBy('name');
        oldTableNames.forEach((oldTable) => {
          if (!newTableNames.contains(oldTable)) {
            deletedTablesCount++;
            let oldRecord = this.get('store').peekRecord('table', `${databaseName}/${oldTable}`);
            this.get('store').unloadRecord(oldRecord);
          }
        });

        newTableNames.forEach((newTable) => {
          if(!oldTableNames.contains(newTable)) {
            //table has been added
            let tableRecord = this.get('store').peekRecord('table', `${databaseName}/${newTable}`);
            let dbRecord = this.get('store').peekRecord('database', databaseName);
            dbRecord.get('tables').pushObject(tableRecord);
          }
        });

        // Hack: Had to wrap the refreshed call inside run later because, unloadRecord is not synchronously unloading
        // records from store.
        Ember.run.later(() => tablesRefreshedCallback(databaseName, deletedTablesCount));
        if(!runOnce) {
          reRun();
        }
      }).catch((err) => {
        if(!runOnce) {
          reRun();
        }
      });
    }
  },

  stopTablesAutoRefresh(databaseName) {
    console.log("Stopping tables auto refresh for " + databaseName);
    this.get('tablesRefresherRunningStatus')[databaseName]["started"] = false;
    let intervalRef = this.get('tablesRefresherRunningStatus')[databaseName]["intervalRef"];
    if (intervalRef) {
      Ember.run.cancel(intervalRef);
    }
  }
});
