/*
 * This file was originally copied from Apache Tez and has been modified. The modifications are subject to the
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

export default Ember.Component.extend({
  tableDefinition: null,
  dataProcessor: null,

  classNames: ['pagination-ui'],
  isVisible: Ember.computed.alias('tableDefinition.enablePagination'),

  showFirst: Ember.computed('_possiblePages', function () {
    return this.get("dataProcessor.totalPages") && this.get('_possiblePages.0.pageNum') !== 1;
  }),

  rowCountOptions: Ember.computed('tableDefinition.rowCountOptions', 'tableDefinition.rowCount', function () {
    var options = this.get('tableDefinition.rowCountOptions'),
        rowCount = this.get('tableDefinition.rowCount');

    return options.map(function (option) {
      return {
        value: option,
        selected: option === rowCount
      };
    });
  }),

  _possiblePages: Ember.computed('tableDefinition.pageNum',
      'tableDefinition.moreAvailable',
      'dataProcessor.totalPages', function () {
    var pageNum = this.get('tableDefinition.pageNum'),
        totalPages = this.get('dataProcessor.totalPages'),
        possiblePages = [],
        startPage = 1,
        endPage = totalPages,
        delta = 0;

    if(this.get('tableDefinition.moreAvailable')) {
      totalPages++;
    }

    if(totalPages > 1) {
      startPage = pageNum - 1;
      endPage = pageNum + 1;

      if(startPage < 1) {
        delta = 1 - startPage;
      }
      else if(endPage > totalPages) {
        delta = totalPages - endPage;
      }

      startPage += delta;
      endPage += delta;
    }

    startPage = Math.max(startPage, 1);
    endPage = Math.min(endPage, totalPages);

    while(startPage <= endPage) {
      possiblePages.push({
        isCurrent: startPage === pageNum,
        isLoadPage: startPage === totalPages,
        pageNum: startPage++,
      });
    }

    return possiblePages;
  }),

  actions: {
    rowSelected: function (value) {
      value = parseInt(value);
      if(this.get('tableDefinition.rowCount') !== value) {
        this.get('parentView').send('rowChanged', value);
      }
    },
    changePage: function (value) {
      if(value === 1) {
        this.get('parentView').sendAction('reload');
      }
      else if(this.get('dataProcessor.totalPages') < value) {
        this.get('parentView').sendAction('loadPage', value);
      }
      else {
        this.get('parentView').send('pageChanged', value);
      }
    },
  }
});
