// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/*!
 * gridster-knockout v0.0.1
 * (c) Justin Kohlhepp -
 * License: MIT (http://www.opensource.org/licenses/mit-license.php)
 */

// It's not maintained anymore so we modified it to get extra things in

ko.bindingHandlers.gridster = {
  init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
    var gridster = $(element).data('gridster');
    var model = ko.unwrap(valueAccessor)();
    var itemsArray = ko.unwrap(model.items);
    var template = ko.unwrap(model.template);
    var templateContents = $('#' + template).html();

    // Some of the items may already have widget IDs, so we have
    // to initialize the counter to be higher than that
    var idCounter = 1;
    for (var i = 0; i < itemsArray.length; i++) {
      var item = itemsArray[i];
      if (item.widgetId && item.widgetId() >= idCounter)
        idCounter = parseInt(item.widgetId()) + 1;
    }

    var addWidget = function (widget) {
      var col = (widget.col !== undefined) ? parseInt(ko.unwrap(widget.col)) : null;
      var row = (widget.row !== undefined) ? parseInt(ko.unwrap(widget.row)) : null;
      var sizex = parseInt(ko.unwrap(widget.size_x));
      var sizey = parseInt(ko.unwrap(widget.size_y));
      var addedWidget = gridster.add_widget(templateContents, sizex, sizey, col, row);

      // Update the col and row based on it being added
      if (widget.col === undefined)
        widget.col = ko.observable(parseInt(addedWidget.attr('data-col')));
      if (widget.row === undefined)
        widget.row = ko.observable(parseInt(addedWidget.attr('data-row')));

      // Keep an id for each widget so we can keep our sanity
      if (widget.widgetId === undefined) {
        widget.widgetId = ko.observable();
        widget.widgetId(idCounter++);
      }
      addedWidget.attr('data-widgetId', widget.widgetId());

      // Keep track of the element that was created with the widget
      widget.gridsterElement = addedWidget.get(0);

      // http://knockoutjs.com/documentation/custom-bindings-controlling-descendant-bindings.html
      var childBindingContext = bindingContext.createChildContext(
        widget,
        null, // Optionally, pass a string here as an alias for the data item in descendant contexts
        function (context) {
          ko.utils.extend(context, valueAccessor());
        });
      ko.applyBindingsToDescendants(childBindingContext, addedWidget.get(0));

      huePubSub.publish('gridster.added.widget', addedWidget);

      return addedWidget;
    };

    var getWidgetModelById = function (widgetId) {
      for (var i = 0; i < itemsArray.length; i++) {
        var item = itemsArray[i];
        if (item.widgetId() == widgetId)
          return item;
      }
      return null;
    };

    for (var i = 0; i < itemsArray.length; i++) {
      item = itemsArray[i];
      addWidget(item);
    }

    model.items.subscribe(function (changes) {
      changes.forEach(function (change) {
        switch (change.status) {
          case 'added':
            var addedWidget = addWidget(change.value);
            if (change.value.callback) {
              ko.unwrap(change.value.callback)(addedWidget);
            }
            syncPositionsToModel();
            break;
          case 'deleted':
            huePubSub.publish('gridster.deleted.widget', change.value.gridsterElement);
            gridster.remove_widget(change.value.gridsterElement, syncPositionsToModel);
            break;
          default:
            throw new Error('Unexpected change.status');
            break;
        }
      });
      itemsArray = ko.unwrap(model.items);
    }, null, "arrayChange");

    var syncPositionsToModel = function () {
      // Loop through all model items
      for (var i = 0; i < itemsArray.length; i++) {
        var item = itemsArray[i];
        var eleColValue = parseInt($(item.gridsterElement).attr('data-col'));
        var eleRowValue = parseInt($(item.gridsterElement).attr('data-row'));
        item.col(eleColValue);
        item.row(eleRowValue);
      }
    };

    var syncSub = huePubSub.subscribe('gridster.sync.model', syncPositionsToModel);

    ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
      syncSub.remove();
    });

    // Just in case the consumer set up their own resize handler, we need to chain the calls
    var oldOnResize = gridster.options.resize.stop;
    gridster.options.resize.stop = function (event, ui, $widget) {
      var widgetId = parseInt($widget.attr('data-widgetid'));
      var newSizeX = parseInt($widget.attr('data-sizex'));
      var newSizeY = parseInt($widget.attr('data-sizey'));

      var widgetModel = getWidgetModelById(widgetId);
      widgetModel.size_x(newSizeX);
      widgetModel.size_y(newSizeY);

      // Move a widget can change the positions of all other widgets
      syncPositionsToModel();

      if (oldOnResize !== undefined)
        oldOnResize(event, ui, $widget);
    };

    var oldOnMove = gridster.options.draggable.stop;
    gridster.options.draggable.stop = function (event, ui) {
      // Moving a widget can change the positions of all other widgets
      syncPositionsToModel();

      if (oldOnMove !== undefined)
        oldOnMove(event, ui);
    };

    // We are controlling sub-bindings, so don't have KO do it
    return {controlsDescendantBindings: true};
  },

  //update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
  //    alert('update called');
  //},
};