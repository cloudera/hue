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

import TableController from '../table';
import ColumnDefinition from 'em-table/utils/column-definition';
import TableDefinition from 'em-table/utils/table-definition';

var MoreObject = more.Object;

export default TableController.extend({
  searchText: "tez",

  countersCount: 20,

  breadcrumbs: [{
    text: "Configurations",
    routeName: "app.configs",
  }],

  definition: Ember.computed(function () {
    return TableDefinition.create({
      rowCount: 25
    });
  }),

  columns: ColumnDefinition.make([{
    id: 'configName',
    headerTitle: 'Configuration Name',
    contentPath: 'configName',
  }, {
    id: 'configValue1',
    headerTitle: 'Configuration Value - A',
    contentPath: 'configValue1',
  }, {
    id: 'configValue2',
    headerTitle: 'Configuration Value - B',
    contentPath: 'configValue2',
  }]),


  configs: Ember.computed("configsmodel", "isShowDuplicate", function () {
    var configs1 = this.get("configsmodel.query1.details.configuration"), configs2 = this.get("configsmodel.query2.details.configuration"),
        configRows = [];

    if(configs1 || configs2) {
      MoreObject.forEach(configs1, (key, value)=> {
        if(!this.get("isShowDuplicate")) {
          configRows.push(Ember.Object.create({
            configName: key,
            configValue1: value,
            configValue2: configs2[key]
          }));
        } else {
          if(value !== configs2[key]) {
            configRows.push(Ember.Object.create({
              configName: key,
              configValue1: value,
              configValue2: configs2[key]
            }));
          }
        }
      });
    }

    return Ember.A(configRows);
  }),
  isShowDuplicate: true
});
