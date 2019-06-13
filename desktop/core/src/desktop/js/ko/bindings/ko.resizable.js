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

/**
 * Binding for jquery UI resizable
 *
 * @type {{init: ko.bindingHandlers.resizable.init}}
 */
ko.bindingHandlers.resizable = {
  init: function(element, valueAccessor) {
    const options = valueAccessor() || {};
    $(element).resizable(options);
    $(element)
      .children('.ui-resizable-handle')
      .css('z-index', 10000);
  }
};
