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

export default Ember.Component.extend({
  classNames: ["columns-list"],

  filterText: null,
  table: null,

  currentPage: 1,
  pageSize: null,

  filteredColumns: Ember.computed("table.columnNames", "filterText", function () {
    let filterText = this.get("filterText"),
        columnNames = this.get("table.columnNames") || [];

    if(filterText) {
      columnNames = columnNames.filter(function (name) {
        return name.match(filterText);
      });
    }

    return columnNames;
  }),

  willDestroyElement: function () {
    Ember.$(".ui-tooltip-content").parents('div').remove();
  },

  _filterObserver: Ember.observer("filterText", function () {
    this.set("currentPage", 1);

    this.get("parentView.parentView.parentView").send("columnPaginationChanged", {
      currentPage: 1,
      itemCount: this.get("filteredColumns.length")
    });
  }),

  totalPages: Ember.computed("filteredColumns.length", "pageSize", function () {
    return Math.ceil(this.get("filteredColumns.length") / this.get("pageSize"));
  }),
  showPagination: Ember.computed("totalPages", function () {
    return this.get("totalPages") > 1;
  }),
  showPrevious: Ember.computed("currentPage", function () {
    return this.get("currentPage") > 1;
  }),
  showNext: Ember.computed("currentPage", "totalPages", function () {
    return this.get("currentPage") < this.get("totalPages");
  }),

  paginatedColumns: Ember.computed("filteredColumns", "currentPage", "pageSize", function() {
    let currentPage = this.get("currentPage"),
        pageSize = this.get("pageSize");

    return this.get("filteredColumns").slice((currentPage - 1) * pageSize, currentPage * pageSize);
  }),

  actions: {
    changePage: function (factor) {
      var newPage = this.get("currentPage") + factor;
      var totalPages = this.get("totalPages");
      if(newPage > 0 && newPage <= totalPages) {
        this.set("currentPage", newPage);
        this.get("parentView.parentView.parentView").send("columnPaginationChanged", {
          currentPage: newPage,
          itemCount: this.get("filteredColumns.length")
        });
      }
    }
  }

});
