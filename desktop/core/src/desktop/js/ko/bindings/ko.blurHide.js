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

ko.bindingHandlers.blurHide = {
  init: function(element, valueAccessor) {
    const $el = $(element);
    const prop = valueAccessor();
    $el.on('blur', () => {
      if ($.trim($el.val()) === '') {
        if (ko.isObservable(prop)) {
          prop(false);
        }
      }
    });
  },
  update: function(element, valueAccessor) {
    const $el = $(element);
    const prop = valueAccessor();
    if (ko.isObservable(prop) && prop()) {
      $el.focus();
    }
  }
};
