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

export default Ember.Component.extend({
  tagName: 'tr',
  selectedValue: '',
  selectedParam: null,

  isValueDisabled: Ember.computed('selectedParam', function(){
    if(this.get('selectedParam')){
      return false;
    } else{
      return true;
    }
  }),

  didReceiveAttrs() {
    this._super(...arguments);
    let selectedParameter = this.get('hiveParameters').filterBy('name', this.get('setting.key'));
    if (selectedParameter.get('length') === 1) {
      this.set('selectedParam', selectedParameter[0]);
      this.set('selectedValue', this.get('setting.value'));
    }
  },
  setUserSettingsAddOption: function (list, term) {
    let filteredList = list.filter(x => x.get('name').toLowerCase().indexOf('Add') !== -1);
    if (filteredList.get('length') > 0) {
      list.removeObject(filteredList.objectAt(0));
    }

    list.unshiftObject(Ember.Object.create({name: `Add '${term}' to list`, actualValue: term}));
    return list;
  },

  validate() {
    let value = this.get('selectedValue');
    let setting = this.get('selectedParam');
    let error = "";
    if (Ember.isEmpty(value)) {
      return {valid: false, error: "Value cannot be empty"};
    }

    if (!this.get('selectedParam')) {
      return {valid: false, error: "Please select a key for the value."};
    }

    if (Ember.isEmpty(setting.get('values')) && Ember.isEmpty(setting.get('validate'))) {
      return {valid: true};
    }

    if (setting.get('values') && setting.get('values').mapBy('value').contains(value.toLowerCase())) {
      return {valid: true};
    } else if (setting.get('values')) {
      error = `Value should be in (${setting.get('values').mapBy('value').join(', ')})`;
    }

    if (setting.get('validate') && setting.get('validate').test(value)) {
      return {valid: true};
    } else if (setting.get('validate')) {
      error = `Value should be matching regex ${setting.get('validate')}`;
    }

    return {valid: false, error: error};
  },

  actions: {
    searchAction(term) {
      this.set('currentSearchField', term);
      // Check for partial Matches
      let filteredList = this.get('hiveParameters').filter(x => x.get('name').toLowerCase().indexOf(term.toLowerCase()) !== -1);
      //check for exact matches
      if ((filteredList.get('length') !== 1) || (filteredList[0].get('name') !== term)) {
        filteredList = this.setUserSettingsAddOption(filteredList, term);
      }
      return filteredList;
    },
    selectionMade(selection, list) {
      this.get('hiveParameters').setEach('disable', false);
      if (selection.get('name').startsWith('Add')) {
        let actualValue = selection.get('actualValue');
        let newParam = Ember.Object.create({name: actualValue, disabled: true});
        this.set('selectedParam', newParam);
        this.get('hiveParameters').unshiftObject(newParam);
      } else {
        selection.set('disabled', true);
        this.set('selectedParam', selection);
      }
    },
    cancel() {
      this.set('setting.editMode', false);
      this.sendAction('cancelAction', this.get('setting'));
    },
    update() {
      let validationResult = this.validate();
      if(validationResult.valid) {
        let selected = this.get('selectedParam');
        this.set('setting.key', selected.get('name'));
        this.set('setting.value', this.get('selectedValue') || '');
        this.sendAction('updateAction', this.get('setting'));
      } else {
        this.set('invalid', true);
        this.set('currentError', validationResult.error);
      }

    }
  }
});
