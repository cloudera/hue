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

import ko from 'knockout';

ko.bindingHandlers.hueCheckAll = {
  init: function(element, valueAccessor) {
    const allValues = ko.utils.unwrapObservable(valueAccessor()).allValues;
    const selectedValues = ko.utils.unwrapObservable(valueAccessor()).selectedValues;

    const updateCheckedState = function() {
      ko.utils.toggleDomNodeCssClass(
        element,
        'fa-check',
        allValues().length > 0 && selectedValues().length === allValues().length
      );
      ko.utils.toggleDomNodeCssClass(
        element,
        'fa-minus hue-uncheck',
        selectedValues().length > 0 && selectedValues().length !== allValues().length
      );
    };

    ko.utils.registerEventHandler(element, 'click', () => {
      if (selectedValues().length === 0) {
        selectedValues(allValues().slice(0));
      } else {
        selectedValues([]);
      }
    });

    selectedValues.subscribe(updateCheckedState);
    allValues.subscribe(updateCheckedState);
    updateCheckedState();
  }
};
