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

var MoreObject = more.Object;

export default TableController.extend({
  counters: Ember.A(),
  countersCount: 0, // Because Ember.Array doesn't handle length well

  columns: ColumnDefinition.make([{
    id: 'groupName',
    headerTitle: 'Group Name',
    contentPath: 'uid',
  }, {
    id: 'counterName1',
    headerTitle: 'Counter Name',
    contentPath: 'counterName',
  }, {
    id: 'counterValue1',
    headerTitle: 'Counter Value - A',
    contentPath: 'counterValue1'
  }, {
    id: 'counterValue2',
    headerTitle: 'Counter Value - B',
    contentPath: 'counterValue2'
  }]),
  isShowDuplicate: true,

  _countersObserver: Ember.observer("model.counterGroupsHash1", "model.counterGroupsHash2", function () {
    var counterGroupsHash1 = this.get("model.counterGroupsHash1"), counterGroupsHash2 = this.get("model.counterGroupsHash2"),
        counters1 = [], counters2 = [], counters3 = [],
        counterIndex = 0, countersMod = {};
    console.log(counterGroupsHash1);
    console.log(counterGroupsHash2);
    if(counterGroupsHash1) {
      MoreObject.forEach(counterGroupsHash1, function (groupName, countersHash) {
        if(countersHash) {
          MoreObject.forEach(countersHash, function (counterName, counterValue) {
            countersMod[groupName+"."+counterName] = Ember.Object.create({
              uid: groupName,
              counterName: counterName,
              counterValue1: counterValue,
              id:groupName+"."+counterName
            });
            counterIndex++;
          });
        }
      });
    }
    if(counterGroupsHash2) {
      MoreObject.forEach(counterGroupsHash2, function (groupName, countersHash) {
        if(countersHash) {
          MoreObject.forEach(countersHash, function (counterName, counterValue) {
            if(countersMod[groupName+"."+counterName]) {
              countersMod[groupName+"."+counterName]["counterValue2"] = counterValue;
            } else {
              countersMod[groupName+"."+counterName] = Ember.Object.create({
                uid: groupName,
                counterName: counterName,
                counterValue2: counterValue,
                id:groupName+"."+counterName
              });
            }
            counterIndex++;
          });
        }
      });
    }
    Ember.$.each(countersMod, (item, i) => {
      counters3.push(i);
    });
    this.set("countersCount", counterIndex);
    this.set("counters", counters3);
  })
});
