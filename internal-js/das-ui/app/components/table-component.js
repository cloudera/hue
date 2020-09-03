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

import DataProcessor from 'em-table/utils/data-processor';

export default Ember.Component.extend({

  title: null,

  columns: null,
  rows: null,

  searches: null,

  classNames: null,
  classNameBindings: ['enableFaceting'],

  headerComponentNames: ['em-table-header-component'],
  footerComponentNames: ['em-table-footer-component'],

  enableSort: true,
  enableSearch: true,
  enableFaceting: true,

  definition: null,

  scrollColumns: null,

  columnSelectorIsVisible: false,

  init: function () {
    this._super();
    this.set("scrollColumns", Ember.A([]));
  },

  _dataProcessor: null,
  dataProcessor: Ember.computed("definition", "dataLoader", function () {
    var dataProcessor = this.get("dataLoader") || this.get("_dataProcessor");

    if(!dataProcessor) {
      dataProcessor = DataProcessor.create();
      this.set("_dataProcessor", dataProcessor);
    }

    dataProcessor.set("tableDefinition", this.get("definition"));
    dataProcessor.set("scrollColumns", this.get("scrollColumns"));

    return dataProcessor;
  }),

  columnPrefDef: Ember.computed("columns", "definition.columnPreferences", function () {
    var columns = this.get("columns").slice(),
        columnPreferences = this.get("definition.columnPreferences") || [],
        columnPrefDef = [],
        columnIdIndexHash = {};

    columns.forEach(function (column, index) {
      columnIdIndexHash[column.get("id")] = index;
    });

    // Add columns in order from columnPreferences
    columnPreferences.forEach(function (column) {
      var index = columnIdIndexHash[column.id];
      if(index !== undefined) {
        columnPrefDef.push({
          def: columns[index],
          visible: column.visible
        });
        columns[index] = undefined;
      }
    });

    // Add columns that's not there in the columnPreferences
    columns.forEach(function (column) {
      if(column) {
        columnPrefDef.push({
          def: column,
          visible: true
        });
      }
    });

    return columnPrefDef;
  }),

  definitionObserver: Ember.on("init", Ember.observer("definition", "columnPrefDef", function () {
    var columns =[];
    this.get("columnPrefDef").forEach(function (column) {
      if(column.visible) {
        columns.push(column.def);
      }
    });

    this.get("definition").setProperties({
      minRowsForFooter: 0,
      columns: columns,
      title: this.get("title"),

      enableSort: this.get("enableSort"),
      enableSearch: this.get("enableSearch"),
      enableFaceting: this.get("enableFaceting"),

      headerAsSortButton: true,

      table: this
    });
  })),

  actions: {
    search: function (searchText) {
      this.set('definition.searchText', searchText);
      this.get("definition.parentController").send("tableDefinitionUpdated");
    },
    showColumnSelector: function () {
      this.get('definition.parentController').send('openColumnSelector');
    },
    columnWidthChanged: function (width, columnDefinition, index) {
      var scrollColumns = this.get("scrollColumns");
      if(columnDefinition.get("pin") === "center") {
        scrollColumns.replace(index, 1, {
          definition: columnDefinition,
          width: width
        });
      }
    },
    scrollChange: function (scrollData) {
      this.set("dataProcessor.scrollData", scrollData);
    },
    scrollToColumn: function (definition) {
      var scrollColumns = this.get("scrollColumns"),
          scrollPosition = 0;

      scrollColumns.some(function (column) {
        if(column.definition === definition) {
          return true;
        }
        scrollPosition = scrollPosition + column.width;
      });

      this.$().find(".table-body").animate({
        scrollLeft: scrollPosition
      });
    },
    searchSelected: function (search) {
      var clause = search.get("clause");

      this.set("definition.searchText", clause);
      this.set("definition.facetConditions", search.get("facet"));
      this.set("definition.columnPreferences", search.get("columns.preferences"));
      if(search.get("range")) {
        this.set("definition.rangeData", search.get("range"));
      }
      this.set("definition.sortColumnId", search.get("sort.sortColumnId"));
      this.set("definition.sortOrder", search.get("sort.sortOrder"));
    },
    saveSearch: function (search, includeFilterAndColumns) {
      if(includeFilterAndColumns) {
        search.facet = this.get("definition.facetConditions");
        search.columns = {
          preferences: this.get("definition.columnPreferences")
        };
        search.range = this.get("definition.rangeData");
        search.sort = {
          sortColumnId: this.get("definition.sortColumnId"),
          sortOrder: this.get("definition.sortOrder")
        };
      }
      this.sendAction("saveSearch", search);
    },
    showColumnSelector: function (show) {
      this.get("definition.parentController").send("resetTooltip");
      this.set("columnSelectorIsVisible", show);
    }
  }

});
