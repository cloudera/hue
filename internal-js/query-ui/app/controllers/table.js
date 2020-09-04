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

import AbstractController from './abstract';
import TableDefinition from 'em-table/utils/table-definition';
import isIOCounter from '../utils/misc';

import CounterColumnDefinition from '../utils/counter-column-definition';

var MoreObject = more.Object;

export default AbstractController.extend({
  queryParams: ["rowCount", "searchText", "sortColumnId", "sortOrder", "pageNo"],
  rowCount: 10,
  searchText: "",
  sortColumnId: "",
  sortOrder: "",
  pageNo: 1,

  columns: [],

  visibleColumnIDs: {},
  columnSelectorTitle: 'Column Selector',
  columnSelectorMessage: "",

  polling: Ember.inject.service("pollster"),

  definition: Ember.computed("model", function () {
    return TableDefinition.create({
      parentController: this,

      rowCount: this.get("rowCount"),
      searchText: this.get("searchText"),
      sortColumnId: this.get("sortColumnId"),
      sortOrder: this.get("sortOrder"),
      pageNo: this.get("pageNo")
    });
  }),

  storageID: Ember.computed("name", function () {
    return this.get("name") + ":visibleColumnIDs";
  }),

  initVisibleColumns: Ember.on("init", Ember.observer("columns", function () { //To reset on entity change
    var visibleColumnIDs = this.get("localStorage").get(this.get("storageID")) || {};

    this.get('columns').forEach(function (config) {
      if(visibleColumnIDs[config.id] === undefined) {
        visibleColumnIDs[config.id] = !Ember.get(config, "hiddenByDefault");
      }
    });

    this.set('visibleColumnIDs', visibleColumnIDs);
  })),

  beforeSort: function (columnDefinition) {
    if(this.get("polling.isReady")) {
      let columnName = columnDefinition.get("headerTitle");
      switch(columnDefinition.get("contentPath")) {
        case "counterGroupsHash":
          columnName = "Counters";
          /* falls through */
        case "status":
        case "progress":
          this.send("openModal", {
            title: "Cannot sort!",
            content: `Sorting on ${columnName} is disabled for running DAGs while Auto Refresh is enabled!`
          });
          return false;
      }
    }
    return true;
  },

  allColumns: Ember.computed("columns", function () {
    var columns = this.get("columns"),
        counters = this.getCounterColumns(),
        beforeSort = this.get("beforeSort").bind(this);

    columns = columns.concat(CounterColumnDefinition.make(counters));

    columns.forEach(function (column) {
      column.set("beforeSort", beforeSort);
    });

    return columns;
  }),

  visibleColumns: Ember.computed('visibleColumnIDs', 'allColumns', function() {
    var visibleColumnIDs = this.visibleColumnIDs;
    return this.get('allColumns').filter(function (column) {
      return visibleColumnIDs[column.get("id")];
    });
  }),

  getCounterColumns: function () {
    return this.get('env.app.tables.defaultColumns.counters');
  },

  actions: {
    searchChanged: function (searchText) {
      this.set("searchText", searchText);
    },
    sortChanged: function (sortColumnId, sortOrder) {
      this.setProperties({
        sortColumnId,
        sortOrder
      });
    },
    rowCountChanged: function (rowCount) {
      this.set("rowCount", rowCount);
    },
    pageChanged: function (pageNum) {
      this.set("pageNo", pageNum);
    },

    rowsChanged: function (rows) {
      this.send("setPollingRecords", rows);
    },

    // Column selection actions
    openColumnSelector: function () {
      this.send("openModal", "column-selector", {
        title: this.get('columnSelectorTitle'),
        parentController: this,
        content: {
          message: this.get('columnSelectorMessage'),
          columns: this.get('allColumns'),
          visibleColumnIDs: this.get('visibleColumnIDs')
        }
      });
    },
    columnsSelected: function (visibleColumnIDs) {
      var columnIDs = {};

      MoreObject.forEach(visibleColumnIDs, function (key, value) {
        if(!isIOCounter(key)) {
          columnIDs[key] = value;
        }
      });

      if(!MoreObject.equals(columnIDs, this.get("visibleColumnIDs"))) {
        this.get("localStorage").set(this.get("storageID"), columnIDs);
        this.set('visibleColumnIDs', columnIDs);
      }
    }
  }
});
