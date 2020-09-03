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

export default Ember.Component.extend({
  title: null,
  label: null,
  okText: 'OK',
  okIcon: 'check',
  titleIcon: null,
  labelIcon: null,
  isConnEditable: false,
  okClass: 'success',
  titleClass: 'primary',
  newJdbcConnectionUrl:"",
  closable: true,
  isUpdationSucess: false,
  isUpdationFailure: false,
  jdbcUrl: Ember.computed('contextInfo.jdbcConnection', 'newJdbcConnectionUrl', function(){
    return this.get('newJdbcConnectionUrl') || this.get('contextInfo.jdbcConnection');
  }),
  resetErrorMessage: function() {
    this.set('isUpdationFailure', false);
  },
  resetUrl: function(url) {
    this.set('jdbcUrl', url);
  },
  actions: {
    ok: function() {
      this.sendAction('ok');
    },
    toggleIsConnEditable: function(currentConnection) {
      this.toggleProperty('isConnEditable');
      this.set("newJdbcConnectionUrl", currentConnection);
      this.resetErrorMessage();
    },
    saveConnection: function() {
      this.set('isLoading', true);
      this.resetErrorMessage();
      this.get('saveConnection')(this.get("jdbcUrl")).then((data) => {
        this.toggleProperty("isConnEditable");
        this.set('isUpdationSucess', true)
        this.set('isLoading', false);
      }).catch((error) => {
        this.resetUrl(this.get("newJdbcConnectionUrl"));
        this.set('isUpdationFailure', true)
        this.set('isLoading', false);
      });
    },
    cancel: function() {
      this.resetErrorMessage();
      this.toggleProperty("isConnEditable");
      this.set('jdbcUrl', this.get("newJdbcConnectionUrl"));

    },
    resetConnection: function() {
      this.set('isLoading', true);
      this.resetErrorMessage();
      this.set('newJdbcConnectionUrl', '');
      this.get('resetConnection')().then((data) => {
        this.toggleProperty("isConnEditable");
        this.set('jdbcUrl', data.jdbcConnection);
        this.set('isUpdationSucess', true)
        this.set('isLoading', false);
      }).catch((data) => {
        this.resetUrl(this.get("newJdbcConnectionUrl"));
        this.set('isUpdationFailure', true)
        this.set('isLoading', false);
      });
    }
  }
});

