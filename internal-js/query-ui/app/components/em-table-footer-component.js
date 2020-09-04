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

  classNames: ["em-table-footer-component"],
  classNameBindings: ['noPreviousPage', 'noNextPage'],

  tableDefinition: null,
  dataProcessor: null,

  noPreviousPage: Ember.computed("tableDefinition.pageNum", function () {
    return this.get("tableDefinition.pageNum") <= 1;
  }),
  noNextPage: Ember.computed("tableDefinition.pageNum", "dataProcessor.totalPages", function () {
    return this.get("tableDefinition.pageNum") >= this.get("dataProcessor.totalPages");
  }),

  pageNum: Ember.computed.oneWay("tableDefinition.pageNum"),

  pageSelectRangeEnd: Ember.computed("dataProcessor.totalPages", function () {
    return this.get("dataProcessor.totalPages") + 1;
  }),

  scrollColumns: Ember.computed("dataProcessor.scrollColumns.[]", function () {
    var scrollColumns = this.get("dataProcessor.scrollColumns"),
        total = 0;

    scrollColumns.forEach(function (column) {
      total = total + column.width;
    });

    // Taking out the 'factor * 100' form the following map function
    total = total / 100;

    return scrollColumns.map(function (column) {
      var width = column.width / total;
      return {
        definition: column.definition,
        width: Ember.String.htmlSafe(`width: ${width}%`)
      };
    });
  }),

  scrollThumbStyles: Ember.computed("dataProcessor.scrollData.left", "dataProcessor.scrollData.width", "dataProcessor.scrollData.viewPortWidth", function () {
    var scrollData = this.get("dataProcessor.scrollData"),
        left, width;

    if(scrollData) {
      left = scrollData.left / scrollData.width * 100,
      width = scrollData.viewPortWidth / scrollData.width * 100;
      return Ember.String.htmlSafe(`left: ${left}%; width: ${width}%`);
    }
  }),

  actions: {
    rowCountChanged: function (rowCount) {
      this.set("tableDefinition.rowCount", parseInt(rowCount));
    },
    pageNumChanged: function () {
      var pageNum = parseInt(Ember.$(this.get("element")).find(".pagenum-text").val());

      if(pageNum < 1) {
        pageNum = 1;
      }
      else if(pageNum > this.get("dataProcessor.totalPages")) {
        pageNum = this.get("dataProcessor.totalPages");
      }

      this.set("tableDefinition.pageNum", pageNum);
    },
    previousPage: function () {
      if(!this.get("hasPreviousPage")) {
        this.decrementProperty("tableDefinition.pageNum");
      }
    },
    nextPage: function () {
      if(!this.get("hasNextPage")) {
        this.incrementProperty("tableDefinition.pageNum");
      }
    },
    columnDivisionClicked: function (definition, index) {
      this.get("tableDefinition.table").send("scrollToColumn", definition, index);
    }
  }

});
