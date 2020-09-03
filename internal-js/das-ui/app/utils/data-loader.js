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

import SQL from './sql';

/**
 * Handles Sorting, Searching & Pagination
 */
export default Ember.Object.extend({
  isSorting: false,
  isSearching: false,

  tableDefinition: null,

  rows: [],
  facets: [],
  processedRows: Ember.computed.alias("rows"),

  sql: SQL.create(),

  message: Ember.computed("pageDetails.totalRecords", function () {
    if(this.get("pageDetails.totalRecords") == 0) {
      return "No records available in the time window you've selected. Try selecting a wider window such as last 90 days.";
    }
  }),

  facetedFields: Ember.computed("facets.fieldCount", "tableDefinition.columns", function () {
    var columns = this.get("tableDefinition.columns"),
        facets = this.get("facets"),
        fields = [];

    if(columns && facets) {
      columns.forEach(function (column) {
        var facetedData = facets[column.get("id")];
        if(facetedData && facetedData.length) {
          facetedData = facetedData.map(function (facet) {
            return {
              displayText: facet.displayText,
              value: facet.key,
              count: facet.value
            };
          });

          fields.push({
            column: column,
            facets: facetedData
          });
        }
      });
    }

    return fields;
  }),

  pageDetails: Ember.computed("rows.meta", "rows.length", function () {
    var meta = this.get("rows.meta") || {},
        totalRecords = parseInt(meta.size);
    return {
      fromRecord: totalRecords ? parseInt(meta.offset) + 1 : 0,
      toRecord: parseInt(meta.offset) + this.get("rows.length"),
      totalRecords: totalRecords,

      startIndex: parseInt(meta.offset),

      pageNum: this.get("tableDefinition.pageNum"),
      rowCount: meta.limit,
      totalPages: Math.ceil(totalRecords / meta.limit)
    };
  }),
  totalPages: Ember.computed.alias("pageDetails.totalPages"), // Adding an alias for backward compatibility

  _searchTextObserver: Ember.observer("tableDefinition.searchText", function () {
    this.get("tableDefinition.parentController").send("searchTextUpdated");
  }),
  _tableDefinitionObserver: Ember.observer("tableDefinition.searchText",
      "tableDefinition.facetConditions",

      "tableDefinition.sortColumnId",
      "tableDefinition.sortOrder",

      "tableDefinition.pageNum",
      "tableDefinition.rowCount",

  function () {
    this.get("tableDefinition.parentController").send("tableDefinitionUpdated");
  })
});