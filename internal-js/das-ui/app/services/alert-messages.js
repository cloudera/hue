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


/**
  Shows alert flash and also creates `alert` objects in store. If creation of
  `alert` objects in store pass `options.flashOnly` as `true`. The options
  required for creating the `alert` objects are:
  ```
    options.message: message field returned by the API server.
    options.status : Status XHR request if the message is a response to XHR request. Defaults to -1.
    options.error: Detailed error to be displayed.
  ```
  Options required for ember-cli-flash can also be passed in the alertOptions to override the
  default behaviour.
*/
export default Ember.Service.extend({
  flashMessages: Ember.inject.service('flash-messages'),
  store: Ember.inject.service('store'),
  alertsChanged: false,

  currentUnreadMessages: function() {
   return this.get('store').peekAll('alert').filter((entry) => {
     return entry.get('read') === false;
   });
  },

  setUnreadMessagesToRead: function() {
    this.currentUnreadMessages().forEach((entry) => {
      entry.set('read', true);
    });
    this.toggleProperty('alertsChanged');
  },

  currentMessagesCount: Ember.computed('alertsChanged', function() {
    return this.currentUnreadMessages().get('length');
  }),

  success: function(message, options = {}, alertOptions = {}) {
    return this._processMessage('success', message, options, alertOptions);
  },

  warn: function(message, options = {}, alertOptions = {}) {
    return this._processMessage('warn', message, options, alertOptions);
  },

  info: function(message, options = {}, alertOptions = {}) {
    return this._processMessage('info', message, options, alertOptions);
  },

  danger: function(message, options = {}, alertOptions = {}) {
    return this._processMessage('danger', message, options, alertOptions);
  },

  error: function() {
    return this.danger(...arguments);
  },

  clearMessages: function() {
    this.get('flashMessages').clearMessages();
  },

  _processMessage: function(type, message, options, alertOptions) {
    this._clearMessagesIfRequired(alertOptions);
    let alertRecord = this._createAlert(message, type, options, alertOptions);
    if(alertRecord) {
      this.toggleProperty('alertsChanged');
      message = this._addDetailsToMessage(message, alertRecord);
    }
    switch (type) {
      case 'success':
        this.get('flashMessages').success(message, this._getOptions(Ember.merge(alertOptions, {sticky: false})));
        break;
      case 'warn':
        this.get('flashMessages').warning(message, this._getOptions(Ember.merge(alertOptions, {sticky: false})));
        break;
      case 'info':
        this.get('flashMessages').info(message, this._getOptions(Ember.merge(alertOptions, {sticky: false})));
        break;
      case 'danger':
        this.get('flashMessages').danger(message, this._getOptions(alertOptions));
    }

    return alertRecord;
  },

  _addDetailsToMessage: function(message, record) {
    /* TODOs:: Use below code at the time of implementing notification */
    //let id = record.get('id');
    //let suffix = `<a href="#/messages/${id}">(details)</a>`;
    //return message + "  " + suffix;
    return message;
  },

  _createAlert: function(message, type, options, alertOptions) {
    var data = {};
    data.message = message;
    data.responseMessage = options.message || '';
    data.id = this._getNextAlertId();
    data.type = type;
    data.status = options.status || -1;
    if(options.trace){
      data.trace = this._getDetailedError(options.trace);
    }
    else{
      data.trace = this._getDetailedError(options.stack);
    }
    delete options.status;
    delete options.error;

    if(alertOptions.flashOnly === true) {
      return;
    }
    return this.get('store').createRecord('alert', data);
  },

  _getDetailedError: function(error) {
    return error || '';
  },

  _getOptions: function(options = {}) {
    var defaultOptions = {
      priority: 100,
      showProgress: true,
      timeout: 6*1000,
      sticky: true
    };
    return Ember.merge(defaultOptions, options);
  },

  _getNextAlertId: function() {
    return this.get('store').peekAll('alert').get('length') + 1;
  },

  _clearMessagesIfRequired: function(options = {}) {
    var stackMessages = options.stackMessages || false;
    if(stackMessages !== true) {
      this.clearMessages();
    }
  }
});
