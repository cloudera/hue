// (c) Copyright 2015 Cloudera, Inc. All rights reserved.
/**
 * @module ko/bindings/scrollableTable
 * @description bindinghandler which fixes an html table header and scrolls a table.
 */
var $ = require('jquery');
var ko = require('knockout');
var _ = require('_');

ko.bindingHandlers.scrollableTable = {
  /**
   * @param {Node} element The <table> node to add scrollable behavior to.
   * @param {Object} valueAccessor Extra details for scrollable tables.
   * @param {string} valueAccessor.height Mandatory: specifies the max-height for the table.
   * @param {observable} [valueAccessor.observable] Optional: knockout object to subscribe to and recalculate column widths.
   * @param {Object} allBindings the node bindings.
   * @param {Object} viewModel the current viewModel.
   * @param {Object} bindingContext The current context.
   */
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    var $element = $(element),
        $colgroup = $element.find('colgroup'),
        $head = $element.find('thead'),
        options = valueAccessor();

    // apply bindings first, then we can manipulte the $element table.
    ko.applyBindingsToDescendants(bindingContext, element);

    // clone the table, move the $head and $colgroup to the cloned table.
    var $headerTable = $element.clone();
    $headerTable.html('');
    $headerTable.append($colgroup);
    $headerTable.append($head);
    $headerTable.insertBefore($element);
    $headerTable.addClass('cui-table-scrollable-header');

    // add scrollable css to the parent table
    $element.addClass('cui-table-scrollable');
    $element.find('tbody').css({ 'max-height': options.height });

    /**
     * Makes the first row of the parent table have the same column widths as the header table.
     */
    function recalculateColumns() {
      $head.find('th,td').each(function(i, node) {
        var $node = $(node);
        var width = $node.width();

        $element.find('tr:first td:eq(' + i + ')').width(width);
      });
    }

    recalculateColumns();

    // if our table is bound to an observable, we subscribe to when its observable changes
    if (ko.isObservable(options.observable)) {
      options.observable.subscribe(recalculateColumns);
    }

    // when a table is inside a bootstrap modal, we need to wait until the modal-dialog is visible
    var $modal = $element.parents('.modal');
    if ($modal.length > 0) {
      $element.parents('.modal-dialog').on('bsTransitionEnd', function() {
        // we need a delay so that modal bindings can be applied first, then we can recalculate the columns
        _.delay(function() {
          recalculateColumns();
        }, 100);
      });
    }

    return { controlsDescendantBindings: true };
  }
};

