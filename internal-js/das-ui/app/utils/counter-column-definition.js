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

import isIOCounter from '../utils/misc';
import ColumnDefinition from 'em-table/utils/column-definition';

/*
 * Returns a counter value from for a row
 * @param row
 * @return value
 */
function getCounterContent(row) {
  var counter = Ember.get(row, this.get("contentPath"));

  if(counter) {
    counter = counter[this.get("counterGroupName")];
    if(counter) {
      return counter[this.get("counterName")] || null;
    }
    return null;
  }
}

var CounterColumnDefinition = ColumnDefinition.extend({
  counterName: "",
  counterGroupName: "",

  observePath: true,
  contentPath: "counterGroupsHash",

  getCellContent: getCounterContent,
  getSearchValue: getCounterContent,
  getSortValue: getCounterContent,

  id: Ember.computed("counterName", "counterGroupName", function () {
    var groupName = this.get("counterGroupName"),
        counterName = this.get("counterName");
    return `${groupName}/${counterName}`;
  }),

  groupDisplayName: Ember.computed("counterGroupName", function () {
    var displayName = this.get("counterGroupName");

    // Prune dotted path
    displayName = displayName.substr(displayName.lastIndexOf('.') + 1);

    if(isIOCounter(displayName)) {
      displayName = displayName.replace("_INPUT_", " to Input-");
      displayName = displayName.replace("_OUTPUT_", " to Output-");
    }

    // Prune counter text
    displayName = displayName.replace("Counter_", " - ");
    displayName = displayName.replace("Counter", "");

    return displayName;
  }),

  headerTitle: Ember.computed("groupDisplayName", "counterName", function () {
    var groupName = this.get("groupDisplayName"),
        counterName = this.get("counterName");
    return `${groupName} - ${counterName}`;
  }),
});

CounterColumnDefinition.make = function (rawDefinition) {
  if(Array.isArray(rawDefinition)) {
    return rawDefinition.map(function (def) {
      return CounterColumnDefinition.create(def);
    });
  }
  else if(typeof rawDefinition === 'object') {
    return CounterColumnDefinition.create(rawDefinition);
  }
  else {
    throw new Error("rawDefinition must be an Array or an Object.");
  }
};

export default CounterColumnDefinition;
