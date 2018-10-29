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

// This is meant to fix the .droppable binding we inherit from knockout-sortable.min.js
// by calling the original 'drop' event coming from droppable options instead of just overriding it
(function () {
  ko.bindingHandlers.droppable = {
    init: function (element, valueAccessor, allBindingsAccessor, data, context) {
      var ITEMKEY = "ko_sortItem",
        DRAGKEY = "ko_dragItem",
        unwrap = ko.utils.unwrapObservable,
        dataGet = ko.utils.domData.get;

      var value = ko.utils.unwrapObservable(valueAccessor()) || {},
        options = value.options || {},
        droppableOptions = ko.utils.extend({}, ko.bindingHandlers.droppable.options),
        isEnabled = value.isEnabled !== undefined ? value.isEnabled : ko.bindingHandlers.droppable.isEnabled;

      //override global options with override options passed in
      ko.utils.extend(droppableOptions, options);

      //get reference to drop method
      value = "data" in value ? value.data : valueAccessor();

      var originalDropOption = droppableOptions.drop;
      //set drop method
      droppableOptions.drop = function (event, ui) {
        var droppedItem = ko.utils.domData.get(ui.draggable[0], DRAGKEY) || dataGet(ui.draggable[0], ITEMKEY);
        value(droppedItem);
        if (originalDropOption) {
          originalDropOption(event, ui);
        }
      };

      //initialize droppable
      $(element).droppable(droppableOptions);

      //handle enabling/disabling droppable
      if (isEnabled !== undefined) {
        ko.computed({
          read: function () {
            $(element).droppable(ko.utils.unwrapObservable(isEnabled) ? "enable" : "disable");
          },
          disposeWhenNodeIsRemoved: element
        });
      }

      //handle disposal
      ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
        $(element).droppable("destroy");
      });
    },
    options: {
      accept: "*"
    }
  };

})();
