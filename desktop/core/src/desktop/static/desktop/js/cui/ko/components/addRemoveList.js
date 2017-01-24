// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/addRemoveList
 * @description Provides a component that has +/- options to edit an observableArray
 * Example:
 *  <cui-add-remove-list params="list: observableArray, placeholder: 'foo', editable: myEditable">
 *  </cui-add-remove-list>
 */

var componentUtils = require('cloudera-ui/ko/components/componentUtils');
var $ = require('jquery');
var ko = require('knockout');
var _ = require('_');

/**
 * @constructor
 * @alias module:ko/components/addRemoveList
 */
class AddRemoveList {
  /**
   * @param {object} params.list observableArray of data to show
   *  The list must come from using komappingHelper.convertStringToListObservable or any convert*ToListObservable function.
   * @param {string} [params.placeholder] Placeholder text to show, if any. Defaults to ''.
   * @param {boolean} [params.editable] If the input is editable. Defaults to true.
   */
  constructor(params) {
    this.list = params.list;
    this.placeholder = params.placeholder || '';

    // By default the input fills 100% of the grid size
    // the buttons are size 2, and 12 grid columns - 2 ==> 10
    this.gridSize = params.gridSize || 10;

    this.inputGridClasses = _.map(['xs', 'sm','md','lg'], (size) => {
      return 'col-' + size + '-' + this.gridSize;
    }, this).join(' ');

    this.editable = ko.pureComputed(function() {
      var editable = ko.unwrap(params.editable);
      if (_.isUndefined(editable)) {
        return true;
      }

      return editable;
    });
  }

  /**
   * Add item to list.
   * @param {object} data knockout data.
   * @param {node} element knockout element.
   */
  addItem(data, element) {
    this.list.insertAfter(data, element);
  }

  /**
   * Remove item from list.
   * @param {object} data knockout data.
   * @param {node} element knockout element.
   */
  removeItem(data, element) {
    this.list.removeItem(data, element);
  }
}

var template = `
<ul class="list-unstyled cui-add-remove-list">
  <li class="row" data-bind="visible: list().length === 0 && editable()">
    <div class="col-md-4 col-sm-4 col-xs-4 add-remove-controls">
      <button type="button" class="btn btn-default cui-btn-circle cui-icon-plus" data-bind="click: function() { addItem({}, $element); }"></button>
    </div>
  </li>

  <!-- ko foreach: list -->
  <li class="row">
    <div data-bind="attr: {class: $component.inputGridClasses}">
      <input type="text" class="form-control"
             data-bind="event: {focus: function(){$element.select()}},
                        enable: $component.editable(),
                        textInput: value,
                        attr: _.defaults({
                         placeholder: $component.placeholder,
                         autocomplete: 'on'
                        }, _.isUndefined($parents[1].name) ? {} :
                         {name: $parents[1].name}
                        )" />
    </div>
    <div class="col-xs-2 col-md-2 col-sm-2 col-xs-2 add-remove-controls" data-bind="visible: $component.editable()">
      <button type="button" class="btn btn-default cui-btn-circle cui-icon-minus" data-bind="click: function() { $component.removeItem($data, $element); }"></button>
      <button type="button" class="btn btn-default cui-btn-circle cui-icon-plus" data-bind="click: function() { $component.addItem($data, $element); }"></button>
    </div>
  </li>
  <!-- /ko -->
</ul>
`;

componentUtils.addComponent(AddRemoveList, 'cui-add-remove-list', template);

module.exports = AddRemoveList;
