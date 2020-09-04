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
import moment from 'moment';

export default Ember.Component.extend({

  tableDefinition: null,

  classNames: ["queries-search"],
  isVisible: Ember.computed.alias('tableDefinition.enableSearch'),

  text: Ember.computed.oneWay('tableDefinition.searchText'),

  isShowingSaveModal: false,
  searchName: null,
  includeFilterAndColumns: true,

  searches: null,
  _search: Ember.computed("searches.length", function () {
    var searches = this.get("searches") || [],
        suggestedSearches = [],
        savedSearches = [];

    searches.forEach(function (search) {
      switch(search.get("category")) {
        case "SUGGEST":
          suggestedSearches.push(search);
        break;
        case "SAVED":
          savedSearches.push(search);
        break;
      }
    });

    return {
      suggest: suggestedSearches,
      saved: savedSearches
    };
  }),

  didInsertElement: function () {
    this.$().find('.dropdown-toggle').dropdown();
  },

  actions: {
    search: function () {
      this.get('parentView').send('search', this.get('text'));
    },
    searchSelected: function (search) {
      this.get('parentView').send('searchSelected', search);
      this.set('text', search.get('clause'));
    },
    deleteSearch: function (search) {
      this.get('parentView').sendAction('deleteSearch', search);
    },
    toggleSaveModal: function () {
      this.set("searchName", null);
      this.toggleProperty("isShowingSaveModal");
    },
    saveSearch: function() {
      var searchName = this.get("searchName");

      if(searchName) {
        this.get('parentView').send('saveSearch', {
          name: searchName,
          category: "SAVED",
          type: "ADVANCED",
          entity: "query",
          clause: this.get("text")
        }, this.get("includeFilterAndColumns"));
      }

      this.set("searchName", null);
      this.toggleProperty("isShowingSaveModal");
    }
  }

});
