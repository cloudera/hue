// Copyright (c) 2016 Cloudera, Inc. All rights reserved.

/**
 * @module ko/components/commonModals
 * @description Provides three types of alerts: basic alert, error alert, and confirmation alert
 * The main use case is to show a message inside a modal.
 * If you need to, you can customize the message and use a template instead with knockout bindings.
 */

var componentUtils = require('cloudera-ui/ko/components/componentUtils');
var eventTypes = require('cloudera-ui/ko/components/eventTypes');
var modalLoader = require('cloudera-ui/ko/components/modalLoader');
var pagebus = require('cloudera-ui/utils/pagebus');
var i18n = require('cloudera-ui/utils/i18n');

var modalTemplate = `
<!-- ko ifnot: messageTemplate -->
<div data-bind="text: message"></div>
<!-- /ko -->
<!-- ko if: messageTemplate -->
<div data-bind="template: {name: messageTemplate, data: $data}"></div>
<!-- /ko -->

`;

/**
 * @alias module:ko/components/Alert
 * @description A generic knockout component that goes inside a modal via modalLoader.
 */
class Alert {
  /**
   * @param {object} params knockout params.
   * @param {string} [params.message] optional message, if you don't want to use a message string, you can use messageTemplate instead.
   * @param {string} [params.messageTemplate] optional template to use instead of message string.  Must be an html script tag id.  @see knockout template binding handler for more details.
   * @param {object} [params.$data] optional template data for knockout template binding handler.
   */
  constructor(params) {
    this.message = params.message || '';
    this.messageTemplate = params.messageTemplate;
    this.$data = params.$data || {};
  }
}

componentUtils.addComponent(Alert, 'cui-alert', modalTemplate);

var commonModals = {};

/**
 * @param {string} message The message you want to show in an alert.
 * @param {object} [options] Customizations to the cui-modal, or Alert.  Any option here will be passed to cui-modal params.  This includes ok handlers, titles, button css, etc.
 * @param {string} [options.messageTemplate] A template id you can pass to Alert.
 * @param {object} [options.$data] messageTemplate's bindings.
 */
commonModals.showAlert = function(message, options) {
  options = options || {};

  var baseTitle = i18n.t('ko.components.alert.title');
  options.title = options.title || baseTitle;

  pagebus.publish(eventTypes.SHOW_COMPONENT_MODAL, {
    componentName: Alert.COMPONENT_NAME,
    data: {
      $data: options.$data,
      message: message || '',
      messageTemplate: options.messageTemplate
    },
    modalParams: _.extend({}, {
      modalClass: 'modal-message'
    }, options)
  });
};

/**
 * Shows an alert with a default title of 'Error'
 * @see commonModals.show for parameters.
 */
commonModals.showError = function(message, options) {
  options = options || {};
  var baseTitle = i18n.t('ko.components.alert.errorTitle');

  options.title = options.title || baseTitle;
  commonModals.showAlert(message, options);
};

/**
 * Shows an alert with a default title of 'Confirm'.  Also shows the cancel button.
 * @see commonModals.show for parameters.
 */
commonModals.showConfirm = function(message, options) {
  options = options || {};
  options.cancelVisible = true;
  var baseTitle = i18n.t('ko.components.alert.confirmTitle');

  options.title = options.title || baseTitle;
  commonModals.showAlert(message, options);
};

module.exports = commonModals;
