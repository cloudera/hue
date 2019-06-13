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

/**
 * This binding can be used to toggle a boolean value on click
 *
 * Example:
 *
 * <div databind="toggle: value">...</div>
 *
 * @type {{init: ko.bindingHandlers.toggle.init}}
 */
ko.bindingHandlers.toggle = {
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    const value = valueAccessor();
    ko.bindingHandlers.click.init(
      element,
      () => {
        return function() {
          value(!value());
        };
      },
      allBindings,
      viewModel,
      bindingContext
    );
  }
};
