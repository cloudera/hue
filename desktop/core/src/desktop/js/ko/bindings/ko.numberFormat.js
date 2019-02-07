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

ko.bindingHandlers.numberFormat = (function() {
  let that;
  return (that = {
    init: function(element, valueAccessor) {
      that.format(element, valueAccessor);
    },
    update: function(element, valueAccessor) {
      that.format(element, valueAccessor);
    },
    format: function(element, valueAccessor) {
      const value = valueAccessor();
      const unwrapped = ko.unwrap(value);
      $(element).text(that.human(unwrapped.value, unwrapped.unit));
    },
    human: function(value, unit) {
      let fn;
      if (unit === 1) {
        fn = function(value) {
          return ko.bindingHandlers.simplesize.humanSize(value) + '/s';
        };
      } else if (unit === 3) {
        fn = ko.bindingHandlers.bytesize.humanSize;
      } else if (unit === 4) {
        fn = function(value) {
          return ko.bindingHandlers.bytesize.humanSize(value) + '/s';
        };
      } else if (unit === 5) {
        fn = ko.bindingHandlers.duration.humanTime;
      } else if (unit === 8) {
        fn = function(value) {
          return ko.bindingHandlers.duration.humanTime(value * 1000000);
        };
      } else if (unit === 9) {
        fn = function(value) {
          return ko.bindingHandlers.duration.humanTime(value * 1000000000);
        };
      } else {
        fn = ko.bindingHandlers.simplesize.humanSize;
      }
      return fn(value);
    }
  });
})();
