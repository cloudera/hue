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

import TableController from './table';
import ColumnDefinition from 'em-table/utils/column-definition';
import TableDefinition from 'em-table/utils/table-definition';
import formatter from 'em-helpers/utils/formatters';
import DataLoader from '../utils/data-loader';

import { RANGE_SETS } from '../components/range-panel';

const STORE_KEY = "Query:columnPreferences";

export default TableController.extend({

  breadcrumbs: [],

  rowCount: 25,

  headerComponentNames: ['queries-page-search', 'table-controls'],
  footerComponentNames: ['em-table-footer-component'],

  definition: Ember.computed(function () {
    var columnPreferences = this.get("localStorage").get(STORE_KEY) || [];
    return TableDefinition.create({
      parentController: this,
      columnPreferences: columnPreferences,
      minValuesToDisplay: 1,
      rangeData: RANGE_SETS[0][1],
      sortColumnId: 'startTime',
      sortOrder: 'desc'
    });
  }),
  dataLoader: Ember.computed(function () {
    return DataLoader.create({
      tableDefinition: this.get("definition")
    });
  }),

  columns: Ember.computed(function () {

  var parentComponent = this;

  return ColumnDefinition.make([{
    id: 'statusIcon',
    headerTitle: ' ',
    contentPath: 'status',
    cellComponentName: 'em-table-query-text-cell',
    classNames: ["em-table-query-text-column"],
    width: "0px",
    minWidth: "0px",
    enableSort: false,
    enableColumnResize: false,
    observePath: true,
    getCellContent: function (row) {
      return {
        status: row.get("status")
      };
    },
    facetType: null,
    pin: "left"
  },{
    id: 'queryText',
    headerTitle: 'Query',
    contentPath: 'queryText',
    width: "250px",
    facetType: null,
    enableSort: false,
    cellComponentName: 'em-table-linked-cell',
    pin:"left",
    observePath: true,
    getCellContent: function (row) {
      return {
        routeName: "query",
        model: row.get("queryID"),
        text: row.get("queryText")
      };
    },
  }/*,{
    id: 'progress',
    headerTitle: 'Progress',
    contentPath: 'progress',
    cellComponentName: 'em-table-progress-cell',
    observePath: true,
    enableSort: false,
    minWidth: "100px",
  }*/,{
    id: 'status',
    headerTitle: 'Status',
    contentPath: 'status',
    observePath: true,
    minWidth: "100px",
  },{
    id: 'queueName',
    headerTitle: 'Queue',
    contentPath: 'queueName',
    minWidth: "100px",
    observePath: true,
    cellComponentName: 'none-txt',
  },{
    id: 'requestUser',
    headerTitle: 'User',
    contentPath: 'requestUser',
    observePath: true,
    minWidth: "100px",
  },{
    id: 'tablesRead',
    headerTitle: 'Tables Read',
    contentPath: 'tablesRead',
    enableSort: false,
    observePath: true,
    getCellContent: function (row) {
      var tables = row.get("tablesRead");
      if(!tables.length) {
        return null;
      } else  {
        return tables.map(function (data) {
          return `${data.table} (${data.database})`;
        }).join(", ");
      }

    }
  },{
    id: 'tablesWritten',
    headerTitle: 'Tables Written',
    contentPath: 'tablesWritten',
    enableSort: false,
    observePath: true,
    getCellContent: function (row) {
      var tables = row.get("tablesWritten");
      if(!tables.length) {
        return null;
      } else  {
        return tables.map(function (data) {
          return `${data.table} (${data.database})`;
        }).join(", ");
      }
    }
  },/*{
    id: 'clientAddress',
    headerTitle: 'Client Address',
    contentPath: 'clientAddress',
    hiddenByDefault: true,
    enableSort: false,
  }*/,{
    id: 'startTime',
    headerTitle: 'Start Time',
    contentPath: 'startTime',
    observePath: true,
    getCellContent: function (row) {
      var timeParts = moment.duration(Date.now() - row.get("startTime")).format("d [days],h [hours],m [minutes],s [seconds]").split(",");
      timeParts = timeParts.slice(0, timeParts.length == 4 ? 2 : 1);
      return timeParts.join(", ") + " ago";
    }
  },{
    id: 'duration',
    headerTitle: 'Duration',
    contentPath: 'duration',
    observePath: true,
    getCellContent: function (row) {
      if(row.get("duration")) {
        return moment.duration(row.get("duration")).format('hh:mm:ss', {
          trim: false
        });
      }
      return null;
    }
  },{
    id: 'dagID',
    headerTitle: 'DAG Id',
    contentPath: 'dagIDs',
    observePath: true,
    enableSort: false,
  },{
    id: 'appID',
    headerTitle: 'Application Id',
    contentPath: 'appIDs',
    observePath: true,
    enableSort: false,
  },{
    id: 'cpuTime',
    headerTitle: 'CPU Time',
    contentPath: 'cpuTime',
    minWidth: "100px",
    observePath: true,
    cellDefinition: {
      type: "duration"
    },
  },{
    id: 'physicalMemory',
    headerTitle: 'Physical Memory',
    contentPath: 'physicalMemory',
    minWidth: "100px",
    observePath: true,
    cellDefinition: {
      type: "memory"
    },
  },{
    id: 'virtualMemory',
    headerTitle: 'Virtual Memory',
    contentPath: 'virtualMemory',
    minWidth: "100px",
    observePath: true,
    cellDefinition: {
      type: "memory"
    },
  },{
    id: 'dataRead',
    headerTitle: 'Data Read',
    contentPath: 'dataRead',
    minWidth: "100px",
    observePath: true,
    cellDefinition: {
      type: "memory"
    },
  },{
    id: 'dataWritten',
    headerTitle: 'Data Written',
    contentPath: 'dataWritten',
    minWidth: "100px",
    observePath: true,
    cellDefinition: {
      type: "memory"
    },
  },{
    id: 'executionMode',
    headerTitle: 'Execution Mode',
    contentPath: 'executionMode',
    minWidth: "100px",
    enableSort: false,
    observePath: true,
    cellComponentName: 'none-txt',
  },{
    id: 'usedCBO',
    headerTitle: 'Cost Based Optimizer (CBO)',
    contentPath: 'usedCBO',
    minWidth: "100px",
    observePath: true,
    enableSort: false,
  },{
    id: 'actions',
    headerTitle: 'Actions',
    contentPath: 'actions',
    cellComponentName: 'em-table-query-actions-cell',
    enableSort: false,
    enableColumnResize: false,
    getCellContent: function (row) {

    return {
        parentComponent: parentComponent,
        row: row
    }

    },
    minWidth: "100px",
    pin: "right"
  }])
  }),

  getCounterColumns: function () {
    return [];
  },

  actions: {
    search: function (properties) {
      this.setProperties(properties);
    },
    pageChanged: function (pageNum) {
      this.set("pageNum", pageNum);
    },
    setColumnPreferences: function (columnPreferences) {
      this.get("localStorage").set(STORE_KEY, columnPreferences);
      this.set("definition.columnPreferences", columnPreferences);
    }
  }

});
