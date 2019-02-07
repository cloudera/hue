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

import hueUtils from 'utils/hueUtils';

// we override the default html binding to prevent XSS/JS injection
const originalHtmlBinding = ko.bindingHandlers.html;

ko.bindingHandlers.html = {
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    const newValueAccessor = function() {
      return hueUtils.deXSS(ko.unwrap(valueAccessor()));
    };
    originalHtmlBinding.init(element, newValueAccessor, allBindings, viewModel, bindingContext);
  },
  update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    const newValueAccessor = function() {
      return hueUtils.deXSS(ko.unwrap(valueAccessor()));
    };
    originalHtmlBinding.update(element, newValueAccessor, allBindings, viewModel, bindingContext);
  }
};

ko.bindingHandlers.htmlUnsecure = {
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    originalHtmlBinding.init(element, valueAccessor, allBindings, viewModel, bindingContext);
  },
  update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    originalHtmlBinding.update(element, valueAccessor, allBindings, viewModel, bindingContext);
  }
};
