/*
 * This file was originally copied from Apache Ambari and has been modified. The modifications are subject to the
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
import datatypes from '../configs/datatypes';

export default Ember.Component.extend({
  tagName: 'tr',
  advancedOption: false,
  datatypes: Ember.copy(datatypes),
  editMode: false,



  hasPrecision: Ember.computed.oneWay('column.type.hasPrecision'),
  hasScale: Ember.computed.oneWay('column.type.hasScale'),
  isComplexType: Ember.computed.bool('column.type.complexDatatype'),
  val: Ember.computed.alias('column.type.label'),
  columnMetaType: null,

  didInsertElement() {
    Ember.run.later( () => {
      this.$('input').focus();
    });
  },
  didReceiveAttrs() {
    if(this.get('column.isPartitioned')) {
      this.set('columnMetaType', 'partitioned');
    } else if(this.get('column.isPartitioned')) {
      this.set('columnMetaType', 'clustered');
    } else {
      this.set('columnMetaType');
    }
  },

  actions: {
    typeSelectionMade(datatype) {
      this.set('column.type', datatype);
    },
    complexTypeSelectionMade(datatype) {
      this.set('column.type', {label:datatype.target.value.toUpperCase()});
    },
    advanceOptionToggle() {
      this.toggleProperty('advancedOption');
    },

    edit() {
      this.set('column.editing', true);
      Ember.run.later(() => {
        this.$('input').focus();
      });
    },

    delete() {
      console.log('deleting column');
      this.sendAction('columnDeleted', this.get('column'));
    },

    sanitizeColumnName() {
      let sanitizedColumnName = DOMPurify.sanitize(this.get('column.name'));
      this.set('column.name', sanitizedColumnName);
    }

  }
});
