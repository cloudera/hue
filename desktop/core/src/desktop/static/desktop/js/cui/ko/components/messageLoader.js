// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/messageLoader
 * @description A dialog that loads components.
 */
import componentUtils  from 'cloudera-ui/ko/components/componentUtils';
import singletonLoader from 'cloudera-ui/ko/components/singletonLoader';
import eventTypes     from 'cloudera-ui/ko/components/eventTypes';
import pagebus        from 'cloudera-ui/utils/pagebus';
import safeHTML       from 'cloudera-ui/ko/bindings/safeHTML';

import $              from 'jquery';
import ko             from 'knockout';
import _              from '_';

var messageLoaderTemplate = `
<div class="cui-messages" data-bind="template: { foreach: messageParamsArray, beforeRemove: hideMessage, afterAdd: showMessage }">
  <div class="cui-message" data-bind="css: css">
    <button type="button" class="close" data-bind="click: remove">
      <span aria-hidden="true">&times;</span>
      <span class="sr-only">Close</span>
      </button>
    <div data-bind="safeHTML: message"></div>
  </div>
</div>`;

/**
 * Correspond to a single message object.
 */
class Message {
  constructor(params) {
    this.css = params.css;
    this.message = params.message;
    this.autoHideDuration = params.autoHideDuration || 10000;

    if (params.autoHide) {
      _.delay(this.remove.bind(this), this.autoHideDuration);
    }
  }

  remove() {
    pagebus.publish(eventTypes.REMOVE_COMPONENT_MESSAGE, this);
  }
}

/**
 * @constructor
 * @alias module:ko/components/messageLoader
 * @param {number} [params.maxCount]
 */
var messageLoader = function(params, componentInfo) {
  // This is the parent container of all the messages.
  this.element = componentInfo.element;

  this.maxCount = ko.unwrap(params.maxCount) || 5;

  this.messageParamsArray = ko.observableArray();

  pagebus.subscribe(eventTypes.SHOW_COMPONENT_MESSAGE, this.onShow.bind(this));
  pagebus.subscribe(eventTypes.REMOVE_COMPONENT_MESSAGE, this.onRemove.bind(this));
  this.hideMessage = function(elem) {
    $(elem).fadeOut(function() { $(elem).remove(); });
  };

  this.showMessage = function(elem) {
    $(elem).hide().fadeIn();
  };
};

messageLoader.prototype.onRemove = function(item) {
  this.messageParamsArray.remove(item);
};

/**
 * Creates a new cui-message.
 * @param {object} showOptions Dynamic metadata to configure the new message.
 * @param {string} showOptions.message The param data for cui-message.
 * @param {boolean} showOptions.type
 */
messageLoader.prototype.onShow = function(showOptions) {
  var css = {};
  var autoHide = true;
  if (showOptions.autoHide !== undefined) {
    autoHide = showOptions.autoHide;
  }

  var type = showOptions.type;
  if (_.contains(['warning', 'danger', 'success', 'info'], type)) {
    css['cui-message-' + type] = true;
  }

  while (this.messageParamsArray().length >= this.maxCount) {
    this.messageParamsArray.pop();
  }

  this.messageParamsArray.unshift(new Message({
    css: css,
    message: showOptions.message,
    autoHide: autoHide
  }));
};

/**
 * The component name.
 * @type {string}
 */
messageLoader.COMPONENT_NAME = 'cui-message-loader';

componentUtils.addComponent(
  messageLoader,
  messageLoader.COMPONENT_NAME,
  messageLoaderTemplate
);

$('<' + messageLoader.COMPONENT_NAME + '>').appendTo(singletonLoader.getContainer());

module.exports = messageLoader;
