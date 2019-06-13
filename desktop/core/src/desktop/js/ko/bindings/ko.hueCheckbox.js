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

import $ from 'jquery';
import ko from 'knockout';

ko.bindingHandlers.hueCheckbox = {
  after: ['value', 'attr'],
  init: function(element, valueAccessor) {
    const value = valueAccessor();
    $(element).addClass('hue-checkbox fa');

    const updateCheckedState = function() {
      ko.utils.toggleDomNodeCssClass(element, 'fa-check', value());
    };

    ko.utils.registerEventHandler(element, 'click', () => {
      value(!value());
    });

    value.subscribe(updateCheckedState);
    updateCheckedState();
  }
};
