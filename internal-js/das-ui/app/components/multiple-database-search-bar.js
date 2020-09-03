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

  classNames: ['multiple-database-search', 'clearfix'],

  databases: [],

  //will make use of these in templates
  heading: 'database',
  subHeading: 'Select or search database/schema',


  selectedDatabase: Ember.computed('selectedMultiDb', function() {
    // return this.get('databases').findBy('selected', true) || {'name': "default"};
    //return  {'name': "default"};
    return  this.get('selectedMultiDb');
  }),

  filteredDatabases: Ember.computed('filterText', 'databases.[]', function() {
    return this.get('databases').filter((item) => {
        return item.get('name');
  });
  }),

  resetDatabaseSelection() {
    this.get('databases').forEach(x => {
      if (x.get('selected')) {
      x.set('selected', false);
    }
  });
  },

  allDbs: Ember.computed('selectedMultiDb','filteredDatabases', function() {
    let dblist =[];
    this.get('filteredDatabases').forEach(db => {
      dblist.push(db.get('name'));
  });

    return dblist;
  }),

  selectedDbs: Ember.computed('selectedMultiDb','filteredDatabases', function() {
    let selecteddblist =[];
    this.get('selectedMultiDb').forEach((item => {
        selecteddblist.push(item.name);
  }));
    return selecteddblist;
  }),

  focusComesFromOutside(e){
    let blurredEl = e.relatedTarget;
    return !blurredEl || !blurredEl.classList.contains('ember-power-select-search-input');
  },


  actions: {
    createOnEnter(select, e) {
      if (e.keyCode === 13 && select.isOpen &&
        !select.highlighted && !Ember.isBlank(select.searchText)) {

        let selected = this.get('selectedDbs');
        if (!selected.includes(select.searchText)) {
          this.get('options').pushObject(select.searchText);
          select.actions.choose(select.searchText);
        }
      }
    },

    handleFocus(select, e) {
      if (this.focusComesFromOutside(e)) {
        select.actions.open();
        this.$('.browse').addClass('open');
      }

    },

    handleBlur() {
      //console.log('handleBlur');
    },

    updateTables(){
      this.sendAction('changeDbHandler', this.get('selectedDbs'));
    },

    browse(){

      if(this.$('.browse').hasClass('open')){
        this.$('.browse').removeClass('open');
        this.$('.multiple-db-select input').focusout();
      } else {
        this.$('.browse').addClass('open');
        this.$('.multiple-db-select input').focus();
      }

    }
  }

});
