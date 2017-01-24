// Copyright (c) 2017 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/commonMessages
 * @description Provides four types of messages: TBD.
 */
import componentUtils from 'cloudera-ui/ko/components/componentUtils';
import messageLoader  from 'cloudera-ui/ko/components/messageLoader';
import eventTypes     from 'cloudera-ui/ko/components/eventTypes';
import pagebus        from 'cloudera-ui/utils/pagebus';
import i18n           from 'cloudera-ui/utils/i18n';

var commonMessages = {};

commonMessages.show = function(message, type) {
  pagebus.publish(eventTypes.SHOW_COMPONENT_MESSAGE, {
    message: message,
    type: type
  });
};

commonMessages.showWarning = function(message) {
  commonMessages.show(message, 'warning');
};

commonMessages.showError = function(message) {
  commonMessages.show(message, 'danger');
};

commonMessages.showSuccess = function(message) {
  commonMessages.show(message, 'success');
};

commonMessages.showInfo = function(message) {
  commonMessages.show(message, 'info');
};

module.exports = commonMessages;
