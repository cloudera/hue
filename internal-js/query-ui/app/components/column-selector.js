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

import isIOCounter from '../utils/misc';

export default Ember.Component.extend({

  classNames: ['column-selector'],

  searchText: "",
  selectAll: false,

  content: null,

  options: Ember.computed("content.columns", "content.visibleColumnIDs", function () {
    var group,
        highlight = false,
        visibleColumnIDs = this.get('content.visibleColumnIDs') || {};

    return this.get('content.columns').map(function (definition) {
      var css = '';

      highlight = highlight ^ (Ember.get(definition, "counterGroupName") !== group);
      group = Ember.get(definition, "counterGroupName");

      if(highlight) {
        css += ' highlight';
      }
      if(group && isIOCounter(group)) {
        css += ' per-io';
      }

      return Ember.Object.create({
        id: Ember.get(definition, "id"),
        displayText: Ember.get(definition, "headerTitle"),
        css: css,
        selected: visibleColumnIDs[Ember.get(definition, "id")]
      });
    });
  }),

  filteredOptions: Ember.computed("options", "searchText", function () {
    var options = this.get('options'),
        searchText = this.get('searchText');

    if (!searchText) {
      return options;
    }

    return options.filter(function (option) {
      return option.get('displayText').match(searchText);
    });
  }),

  selectedColumnIDs: Ember.computed("options", function () {
    var columnIds = {};
    this.get('options').forEach(function (option) {
      columnIds[option.get("id")] = option.get('selected');
    });

    return columnIds;
  }),

  _selectObserver: Ember.observer('filteredOptions.@each.selected', function () {
    var selectedCount = 0;
    this.get('filteredOptions').forEach(function (option) {
      if(Ember.get(option, 'selected')) {
        selectedCount++;
      }
    });
    this.set('selectAll', selectedCount > 0 && selectedCount === this.get('filteredOptions.length'));
  }),

  actions: {
    selectAll: function (checked) {
      this.get('filteredOptions').forEach(function (option) {
        Ember.set(option, 'selected', checked);
      });
    },
    closeModal: function () {
      this.get("parentController").send("closeModal");
    },
    ok: function () {
      this.get("parentController").send("columnsSelected", this.get("selectedColumnIDs"));
    }
  }
});
