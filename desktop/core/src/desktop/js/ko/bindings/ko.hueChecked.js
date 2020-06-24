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

import * as ko from 'knockout';

ko.bindingHandlers.hueChecked = {
  after: ['value', 'attr'],
  init: function (element, valueAccessor, allBindings, viewModel) {
    const selectedValues = valueAccessor();

    if (allBindings().checkedValue) {
      viewModel = ko.unwrap(allBindings().checkedValue);
    }

    const updateCheckedState = function () {
      ko.utils.toggleDomNodeCssClass(element, 'fa-check', selectedValues.indexOf(viewModel) > -1);
    };

    ko.utils.registerEventHandler(element, 'click', () => {
      const currentIndex = selectedValues.indexOf(viewModel);
      if (currentIndex === -1) {
        selectedValues.push(viewModel);
      } else if (currentIndex > -1) {
        selectedValues.splice(currentIndex, 1);
      }
    });

    selectedValues.subscribe(updateCheckedState);
    updateCheckedState();
  }
};
