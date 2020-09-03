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
import moment from 'moment';

export default Ember.Component.extend(UILoggerMixin, {
  columnStatsKeys : [
    {dataKey: 'min', label: 'MIN'},
    {dataKey: 'max', label: 'MAX'},
    {dataKey: 'numNulls', label: 'NUMBER OF NULLS'},
    {dataKey: 'distinctCount', label: 'DISTINCT COUNT'},
    {dataKey: 'avgColLen', label: 'AVERAGE COLUMN LENGTH'},
    {dataKey: 'maxColLen', label: 'MAX COLUMN LENGTH'},
    {dataKey: 'numTrues', label: 'NUMBER OF TRUE'},
    {dataKey: 'numFalse', label: 'NUMBER OF FALSE'},
  ],

  tableStatsKeys : [
    {dataKey: 'numFiles', label: 'Number of Files'},
    {dataKey: 'numRows', label: 'Number of Rows'},
    {dataKey: 'rawDataSize', label: 'Raw Data Size'},
    {dataKey: 'totalSize', label: 'Total Size'}
  ],

  statsService: Ember.inject.service(),
  info: Ember.inject.service(),
  analyseWithStatistics: false,
  partitionStatSupportedVersion: "2.1",
  isTablePartitioned: Ember.computed("table.partitionInfo.columns", function(){
    return this.get("table.partitionInfo.columns") && this.get("table.partitionInfo.columns.length") > 0;
  }),
  partitionStatSupported: Ember.computed(function(){
  let productInfo = this.get("info").get('productInfo');
  let databaseProductVersion = productInfo["databaseProductVersion"];
  let databaseVersion = databaseProductVersion.split(".");
  let databaseMajorVersion = databaseVersion[0];
  let databaseMinorVersion = databaseVersion[1];
    if(databaseMajorVersion> 2){
      return true;
    }else if(databaseMajorVersion === 2
      && databaseMinorVersion >= 1){
      return true;
    }

    return false;
  }),
  lastUpdatedAt: Ember.computed('table.detailedInfo.lastUpdatedAt', function(){
    let lastUpdatedAt = parseInt(this.get("table.detailedInfo.lastUpdatedAt"));
    return !!lastUpdatedAt ? moment(lastUpdatedAt).format("DD MMM YYYY HH:mm:ss") : false;
  }),

//  tableStatisticsEnabled: Ember.computed.oneWay('table.tableStats.tableStatsEnabled'),

  // TODO: Re-enable the one way binding once we get the column stats
  basicStatsAccurate: true, //Ember.computed.oneWay('columnStatsAccurate.BASIC_STATS'),

  columnStatsAccurate: Ember.computed('table.tableStats.columnStatsAccurate', function () {
    let columnStatsJson = this.get('table.tableStats.columnStatsAccurate');
    return Ember.isEmpty(columnStatsJson) ? {} : JSON.parse(columnStatsJson.replace(/\\\"/g, '"'));
  }),

  columnsWithStatistics: Ember.computed('columnStatsAccurate', function () {
    let stats = this.get('columnStatsAccurate.COLUMN_STATS');
    return !stats ? [] : Object.keys(stats);
  }),

  columns: Ember.computed('table.columns', function () {
    let cols = this.get('table.columns');
    if(this.get("table.partitionInfo.columns")){ // show stats for all columns
      cols = cols.concat(this.get("table.partitionInfo.columns"));
    }
    return cols.map((col) => {
      let copy = Ember.Object.create(col);
      copy.set('hasStatistics', true);
      copy.set('isFetchingStats', false);
      copy.set('statsError', false);
      copy.set('showStats', true);
      return copy;
    });
  }),

  performTableAnalysis(withColumns = false) {
    const tableName = this.get('table.table');
    const databaseName = this.get('table.database');

    let title = `Analyse table` + (withColumns ? ' for columns' : '');
    this.set('analyseTitle', title);
    this.set('analyseMessage', `Submitting job to generate statistics for table '${tableName}'`);

    this.set('showAnalyseModal', true);

    this.get('statsService').generateStatistics(databaseName, tableName, withColumns)
      .then((job) => {
        this.set('analyseMessage', 'Waiting for the job to complete');
        return this.get('statsService').waitForStatsGenerationToComplete(job);
      }).then(() => {
      this.set('analyseMessage', 'Finished analysing table for statistics');
      Ember.run.later(() => this.closeAndRefresh(), 2 * 100);
    }).catch((err) => {
      this.set('analyseMessage', 'Job failed for analysing statistics of table');
      this.get('logger').danger(`Job failed for analysing statistics of table '${tableName}'`, this.extractError(err));
      Ember.run.later(() => this.closeAndRefresh(), 2 * 100);
    });
  },

  fetchColumnStats(column) {
    const tableName = this.get('table.table');
    const databaseName = this.get('table.database');

    column.set('isFetchingStats', true);

    this.get('statsService').generateColumnStatistics(databaseName, tableName, column.name).then((job) => {
      return this.get('statsService').waitForStatsGenerationToComplete(job, false);
    }).then((job) => {
      return this.get('statsService').fetchColumnStatsResult(databaseName, tableName, column.name, job);
    }).then((data) => {
      column.set('isFetchingStats', false);

      // TODO: Re-enable following commented lines once we get the column stats
      // let colStatAccurate = data["columnStatsAccurate"];
      // let colStatAccurateJson = Ember.isEmpty(colStatAccurate) ? {} : JSON.parse(colStatAccurate.replace(/\\\"/g, '"'));
      // if(this.get("partitionStatSupported")){
      //   if(!colStatAccurateJson["COLUMN_STATS"] || colStatAccurateJson["COLUMN_STATS"][column.name] === "false"){
      //     column.set('statsWarn', true);
      //     column.set('statsWarnMsg', "Column statistics might be stale. Please  consider recomputing with 'include columns' option checked.");
      //   }
      // }else if( !this.get("partitionStatSupported") && !(this.get("columnsWithStatistics").contains(column.get("name")))){
      //   column.set('statsWarn', true);
      //   column.set('statsWarnMsg', "Column statistics might be stale. Please  consider recomputing with 'include columns' option checked.");
      // }

      let statsData = this.get("columnStatsKeys").map((item) => {
        return {label: item.label, value: data[item.dataKey]};
      });

      column.set('stats', statsData);
    }).catch((err) => {
      column.set('isFetchingStats', false);
      column.set('statsError', true);
      this.get('logger').danger(`Job failed for fetching column statistics for column '${column.name}' of table '${tableName}'`, this.extractError(err));
    });
  },

  fetchTableStatistics() {
    const tableName = this.get('table.table');
    const databaseName = this.get('table.database');
    var _this = this;
    _this.set('tableStats.isFetchingStats', true);

    this.get('statsService').fetchTableStatistics(databaseName, tableName).then((data) => {
      _this.set('tableStats.isFetchingStats', false);

      let statsData = _this.get("tableStatsKeys").map((item) => {
        return {label: item.label, value: data[item.dataKey]};
      });

      _this.set('tableStats.stats', statsData);
      _this.set('tableStats.showStats', true);
    }).catch((err) => {
      _this.set('tableStats.isFetchingStats', false);
      _this.set('tableStats.statsError', true);
      _this.get('logger').danger(`Job failed for fetching table statistics for table '${tableName}'`, _this.extractError(err));
    });
  },

  closeAndRefresh() {
    this.set('showAnalyseModal', false);
    this.sendAction('refresh');
  },

  actions: {
    analyseTable() {
      this.performTableAnalysis(this.get('analyseWithStatistics'));
    },

    fetchStats(column) {
      this.fetchColumnStats(column);
    },

    fetchTableStats() {
      this.fetchTableStatistics();
    },

    toggleShowStats(column) {
      column.toggleProperty('showStats');
    },

    toggleShowTableStats() {
      this.toggleProperty('tableStats.showStats');
    }
  }
});
