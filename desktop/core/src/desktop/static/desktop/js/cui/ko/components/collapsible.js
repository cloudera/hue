// (c) Copyright 2016 Cloudera, Inc. All Rights reserved
/**
 * @module ko/components/collapsible
 * @description Defines cui-collapsible which shows/hides the inner element.
 * Example: <cui-collapsible params="title: 'myLabel', collapsed: false">
 *           <div>Hi</div>
 *          </cui-collapsible>
 * cui-collapsible is basically a wrapper for the bootstrap collapse module, but provides a basic html template.
 * Any inner nodes will be wrapped with a knockout collapsible template.
 * The inner nodes' context will be the outer context of cui-collapsible.
 * We do not pollute the inner nodes with the component context.
 * If the component context is needed, you can access $component.
 *
 * @see node_modules/bootstrap/js/collapse.js
 */

var collapse = require('bootstrap/collapse');
var componentUtils = require('cloudera-ui/ko/components/componentUtils');
var guid = require('cloudera-ui/utils/guid');
var $ = require('jquery');
var ko = require('knockout');
var _ = require('_');

var collapsibleTemplate = `
<div class="collapsible-section-header" role="button"
   data-toggle="collapse"
   data-bind="attr: {
               'aria-controls': id,
               'data-target': href,
               'aria-expanded': (!collapsed()).toString(),
               }">

  <i class="cui-chevron" data-bind="css: { 'cui-chevron-down': !collapsed() }"></i>
  <!-- ko if: _.isEmpty($component.childNodeTemplates['cui-collapsible-title']) -->
    <span data-bind="text: title"></span>
  <!-- /ko -->
  <!-- ko injectChildTemplate: 'cui-collapsible-title' -->
  <!-- /ko -->
</div>
<!-- ko componentContextEscaper -->
<div data-bind="template: {nodes: $component.children, data: $data},
                attr: {id: $component.id}"
                class="fade collapse collapsible-section-body">
</div>
<!-- /ko -->`;

/**
 * @constructor
 * @alias module:ko/components/collapsible
 * @param {object} params incoming component params.
 * @param {string} params.title The collapsible title.  If you need a custom title, you can specify <cui-collapsible-title></cui-collapsible-title> which will be used instead of params.title.
 * @param {boolean} [params.collapsed] If we should should start out collapsed. (default true)
 * @param {object} componentInfo incoming node and childNode data.
 * @param {node[]} componentInfo.templateNodes Array of child nodes. We only allow one child node.
 */
var CollapsibleComponent = function(params, componentInfo) {
  this.$collapsePanelElement = $(componentInfo.element).find('> .collapse');
  this.title = params.title;

  componentUtils.captureChildTemplate(this, componentInfo.templateNodes, 'cui-collapsible-title');

  var paramCollapsed = ko.unwrap(params.collapsed);
  /**
   * Read-write observable
   * This is an internal collapsed that only controls the state of the > cheveron icon.
   * @type {boolean}
   */
  this.collapsed = ko.observable(paramCollapsed === undefined ? true : paramCollapsed);

  /**
   * If the incomming params.collapsed is an observable, then we need to subscribe to it
   *  so that we can trigger collapse events and update the collapse cheveron.
   */
  if (ko.isObservable(params.collapsed)) {
    params.collapsed.subscribe(function(collapsed) {
      this.$collapsePanelElement.collapse(collapsed ? 'hide' : 'show');
    }, this);
  }

  // setup the initial state of collapse.  Toggle only effects the first call.
  this.$collapsePanelElement
    .collapse({
      toggle: !this.collapsed()
    })
    .on('shown.bs.collapse', _.bind(function() {
      this.collapsed(false);
      if (ko.isObservable(params.collapsed)) {
        params.collapsed(false);
      }
    }, this))
    .on('hidden.bs.collapse', _.bind(function() {
      this.collapsed(true);
      if (ko.isObservable(params.collapsed)) {
        params.collapsed(true);
      }
    }, this));

  this.children = componentInfo.templateNodes;

  // to use bootstrap collapse, you need an id for aria-controls
  this.id = guid.generate();
  this.href = '#' + this.id;
};

componentUtils.addComponent(CollapsibleComponent, 'cui-collapsible', collapsibleTemplate);

module.exports = CollapsibleComponent;
