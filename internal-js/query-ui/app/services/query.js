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
  isColumnPromiseCancelled: false,
  dataBaseTableColumns:{},
  tableMetaDataList: {},
  autoRefreshTime: 30000,
  enableBrowserStorage: false,
  autorefresh: true,

  createJob(payload){
    return new Ember.RSVP.Promise( (resolve, reject) => {
      this.get('store').adapterFor('query').createJob(payload).then(function(data) {
        resolve(data);
      }, function(err) {
        reject(err);
      });
    });
  },
  getJob(jobId, firstCall){
    return new Ember.RSVP.Promise( (resolve, reject) => {
      this.get('store').adapterFor('query').getJob(jobId, firstCall).then(function(data) {
        resolve(data);
      }, function(err) {
          reject(err);
      });
    });
  },

  saveToHDFS(jobId, path){
    return this.get('store').adapterFor('job').saveToHDFS(jobId, path);
  },

  downloadAsCsv(jobId, path){
    return this.get('store').adapterFor('job').downloadAsCsv(jobId, path);
  },

  retrieveQueryLog(jobId){
    return new Ember.RSVP.Promise( (resolve, reject) => {
      this.get('store').adapterFor('query').retrieveQueryLog(jobId).then(function(data) {
        resolve(data);
      }, function(err) {
        reject(err);
      });
    });
  },

  getVisualExplainJson(jobId){
    return new Ember.RSVP.Promise( (resolve, reject) => {
      this.get('store').adapterFor('query').getVisualExplainJson(jobId).then(function(data) {
          resolve(data);
        }, function(err) {
          reject(err);
        });
    });
  },

  refreshTableData(setDatabaseDetails, setTableDetails, interval, filteredItems) {
    if(this.checkIfDataExistsAlready(filteredItems)) {
      this.synchTableMetaDataToComp(filteredItems, setTableDetails);
    } else {
      this.fetchDatabaseAndTableDetails(filteredItems, setTableDetails, setDatabaseDetails);
    }
  },

  fetchDatabaseAndTableDetails(filteredItems, setTableDetails, setDatabaseDetails) {
    this.fetchDatabaseDetails(setDatabaseDetails);
    this.synchTableMetaDataToComp(filteredItems, setTableDetails);
    this.getDataBaseAndTableInfo(filteredItems, this.synchTableMetaDataToComp.bind(this), setTableDetails, setDatabaseDetails);
  },

  fetchDatabaseDetails(callback) {
    this.get("store").findAll('database').then((data) => {
      callback(data);
    });
  },
  checkIfDataExistsAlready(filteredItems) {
    return this.get(`tableMetaDataList.${filteredItems[0].dbName}`) || this.get(`tableMetaDataList.${filteredItems[0].dbname}`);
  },
  synchTableMetaDataToComp(filteredItems, callback) {
    const data = this.checkIfDataExistsAlready(filteredItems);
    if(data) {
      callback(data.tableMetadata);
    }
  },

  setTableMetaDataAfterFetch(tableMetadata) {
    this.set("tableMetaData", tableMetadata);
    this.set(`tableMetaDataList.${tableMetadata.dbname}`, {dbname:tableMetadata.dbname, tableMetadata:tableMetadata});
  },

  getDataBaseAndTableInfo(filteredItems, synchTableMetaDataToComp, setTableDetails, setDatabaseDetails) {
    if(!this.get('autorefresh')) {
      return;
    }
    var self = this;
    filteredItems.forEach(function(item, index){
      let db = item.dbName?item.dbName:item.dbname;
      self.get('store').adapterFor('table').fetchAllTables(item.id, db).then(function(tableMetaData){

        var tableData = tableMetaData.tcInfo;
        var tableCount = tableData.length;
        if(tableCount === 0) {
          self.setTableMetaDataAfterFetch({dbname:db, tables: []});
          synchTableMetaDataToComp(filteredItems, setTableDetails);
        }

        let extractedData = {dbname:db, tables:tableData, autocomplete:tableMetaData.autocomplete};

        if(self.get('enableBrowserStorage')) {
          self.saveColumnData(db, extractedData);
        } else {
          self.set(`dataBaseTableColumns.${db}`, extractedData);
        }

        self.setTableMetaDataAfterFetch(extractedData);
        synchTableMetaDataToComp(filteredItems, setTableDetails);
        setTimeout(() => {
          self.fetchDatabaseAndTableDetails(filteredItems, setTableDetails, setDatabaseDetails);
        }, self.get('autoRefreshTime'));
      });
    });
  },
  saveColumnData(db, extractedData) {
    localStorage.setItem(`dataBaseTableColumns.${db}`, JSON.stringify(extractedData));
  },
  extractColumnData(db){
    if(this.get('enableBrowserStorage')) {
      return [JSON.parse(localStorage.getItem(`dataBaseTableColumns.${db}`))];
    } else {
      return [this.get("dataBaseTableColumns")[db[0]]];
    }
  },
  extractTableNamesAndColumns(database){
    const dataBaseTableColumns = this.extractColumnData(database);
    if(this.get('enableIndexDbStorage')) {
      return new Ember.RSVP.Promise( (resolve, reject) => {
        return dataBaseTableColumns.then((data)=>{
          resolve(data);
        });
      });
    } else {
      return new Ember.RSVP.Promise( (resolve, reject) => {
        resolve(dataBaseTableColumns);
      });
    }

  },

  getRecommendations(queryId){
    return new Ember.RSVP.Promise();
  },

  startRefresh() {
    this.set("autorefresh", true);
  },

  stopRefresh() {
    this.set("autorefresh", false);
  }

});
