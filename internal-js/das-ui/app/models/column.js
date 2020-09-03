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
import Helper from '../configs/helpers';
let Column = Ember.Object.extend(Ember.Copyable,{
  name: '',
  type: datatypes[0],
  precision: null,
  scale: null,
  isPartitioned: false,
  isClustered: false,
  comment: '',


  hasError: Ember.computed('errors.[]', function() { return this.get('errors.length') !== 0; }),
  errors: [],

  nameError: Ember.computed('errors.[]', function() {
    return this.get('errors').findBy('type', 'name');
  }),

  typeError: Ember.computed('errors.[]', function() {
    return this.get('errors').findBy('type', 'type');
  }),


  precisionError: Ember.computed('errors.[]', function() {
    return this.get('errors').findBy('type', 'precision');
  }),

  scaleError: Ember.computed('errors.[]', function() {
    return this.get('errors').findBy('type', 'scale');
  }),

  partitionObserver: Ember.observer('isPartitioned', function() {
    if(this.get('isPartitioned')) {
      this.set('isClustered', false);
    }
  }),

  clusteredObserver: Ember.observer('isClustered', function() {
    if(this.get('isClustered')) {
      this.set('isPartitioned', false);
    }
  }),


  // Control the UI
  editing: false,

  clearError() {
    this.set('errors', []);
  },


  validate() {
    this.clearError();
    if (Ember.isEmpty(this.get('name'))) {
      this.get('errors').pushObject({type: 'name', error: "name cannot be empty"});
    }

    if(Ember.isEmpty(this.get('type'))) {
      this.get('errors').pushObject({type: 'type', error: "Type cannot be empty"});
    }

    if(this.get('type.hasPrecision')) {
      if(Ember.isEmpty(this.get('precision'))) {
        this.get('errors').pushObject({type: 'precision', error: "Precision cannot be empty"});
      } else if(!Helper.isInteger(this.get('precision'))) {
        this.get('errors').pushObject({type: 'precision', error: "Precision can only be a number"});
      } else if(parseInt(this.get('precision')) <= 0) {
        this.get('errors').pushObject({type: 'precision', error: "Precision can only be greater than zero"});
      } else if(this.get('type.hasScale') && this.get('scale') && parseInt(this.get('precision')) < parseInt(this.get('scale'))) {
        this.get('errors').pushObject({type: 'precision', error: "Precision can only be greater than scale"});
      }
    }else{
      delete this.precision;
    }


    if(this.get('type.hasScale')) {
      if(Ember.isEmpty(this.get('scale'))) {
        this.get('errors').pushObject({type: 'scale', error: "Scale cannot be empty"});
      } else if(!Helper.isInteger(this.get('scale'))) {
        this.get('errors').pushObject({type: 'scale', error: "Scale can only be a number"});
      } else if(this.get('scale') <= 0) {
        this.get('errors').pushObject({type: 'scale', error: "Scale can only be greater than zero"});
      }
    }else{
      delete this.scale;
    }

    return this.get('errors.length') === 0;
  },

  copy: function(){
    let col = Column.create({
      name: this.get("name"),
      type: datatypes.findBy("label", this.get("type.label")),
      precision: this.get("precision"),
      scale: this.get("scale"),
      isPartitioned: this.get("isPartitioned"),
      isClustered: this.get("isClustered"),
      comment: this.get("comment"),

      errors: this.get("errors").copy(),
      editing: this.get("editing"),
    });
    return col;
  }

});

export default Column;
