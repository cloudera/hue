// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/modalLoader
 * @description A dialog that loads components.
 */
var componentUtils = require('cloudera-ui/ko/components/componentUtils');
var singletonLoader = require('cloudera-ui/ko/components/singletonLoader');
var eventTypes = require('cloudera-ui/ko/components/eventTypes');
var modal = require('cloudera-ui/ko/components/modal');
var i18n = require('cloudera-ui/utils/i18n');
var pagebus = require('cloudera-ui/utils/pagebus');
var $ = require('jquery');
var ko = require('knockout');
var _ = require('_');

var modalLoaderTemplate = `
<!-- (c) Copyright 2016 Cloudera, Inc. All rights reserved. -->

<!-- ko if: !_.isEmpty(componentName()) -->
  <div data-bind="component: { name: 'cui-modal', params: modalParams }">
    <div class="cui-modal-loader-component" data-bind="component: { name: componentName, params: data }"></div>
  </div>
<!-- /ko -->`;

/**
 * @constructor
 * @alias module:ko/components/modalLoader
 */
var modalLoader = function(params, componentInfo) {
  this.element = componentInfo.element;

  /**
   * Read-write observable
   * Stores the current component that is injected inside modalLoader.
   * @type {string}
   */
  this.componentName = ko.observable();

  /**
   * Read-write observable
   * Stores the current data that is passed into the current element.
   * @type {*}
   */
  this.data = ko.observable();

  /**
   * Read-write observable
   * Stores the modal options that the <cui-modal> component will use.
   */
  this.modalParams = ko.observable();

  pagebus.subscribe(eventTypes.SHOW_COMPONENT_MODAL, this.onShow.bind(this));
};

/**
 * Returns the current component instance for modalLoader.
 * @return {object}
 */
modalLoader.prototype.modalComponent = function() {
  var $componentNode = $(this.element).find('.cui-modal-loader-component');
  if ($componentNode.length)  {
    var component = componentUtils.componentFor($componentNode[0]);
    return component;
  }

  return undefined;
};

/**
 * Creates a new cui-modal.
 * Configures the modal according to showOptions.modalParams.
 * @param {object} showOptions Dynamic metadata to configure the new modal.
 * @param {object} showOptions.modalParams The param data for cui-modal.
 * @param {string} showOptions.componentName The component we want to inject into modalLoader.
 * @param {*} showOptions.data The param data for your inner component.
 */
modalLoader.prototype.onShow = function(showOptions) {
  if (showOptions.componentName) {
    ko.components.defaultLoader.getConfig(showOptions.componentName, function(config) {
      this.loadComponent(showOptions, config.componentConstructor);
    }.bind(this));
  } else if (showOptions.componentPath) {
    this.requireComponent(showOptions);
  } else {
    throw 'Could not handle show event: ' + eventTypes.SHOW_COMPONENT_MODAL;
  }
};

/**
 * Calls a requirejs function to async fetch a component on demand.
 * Overridden in test.
 */
modalLoader.prototype.requireComponent = function(showOptions) {
  window.require([showOptions.componentPath], function(Component) {
    this.loadComponent(showOptions, Component);
  }.bind(this));
};

/**
 *
 */
modalLoader.prototype.loadOptions = function(modalParams, data) {
  this.data(data);

  this.modalParams(modalParams);

  var subscription = modalParams.showDialog.subscribe(function(show) {
    if (!show) {
      this.unloadModal();

      // only subscribe on this once, the inner modal goes away on close.
      subscription.dispose();
    }
  }, this);
};

/**
 *
 */
modalLoader.prototype.loadComponent = function(showOptions, Component) {
  var options = _.extend(showOptions.modalParams || {}, Component.modalParams || {});
  options.showDialog = ko.observable(false);

  this.componentName(Component.COMPONENT_NAME);

  this.loadOptions(options, showOptions.data || {});

  options.showDialog(true);
};

/**
 * Remove any data for the current component.
 *    setting componentName to undefined signals to the modalLoader template
 *    to remove the existing cui-modal.
 * Removing the existing cui-modal makes it so we don't have to edit the inner
 *    workings of cui-modal to make all the attributes observable.
 */
modalLoader.prototype.unloadModal = function() {
  this.modalParams(undefined);
  this.data(undefined);
  this.componentName(undefined);
};

/**
 * The component name.
 * @type {string}
 */
modalLoader.COMPONENT_NAME = 'cui-modal-loader';

componentUtils.addComponent(
  modalLoader,
  modalLoader.COMPONENT_NAME,
  modalLoaderTemplate
);

$('<' + modalLoader.COMPONENT_NAME + '>').appendTo(singletonLoader.getContainer());
module.exports = modalLoader;
