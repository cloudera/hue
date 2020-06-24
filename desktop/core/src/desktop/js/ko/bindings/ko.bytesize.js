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
import * as ko from 'knockout';
import sprintf from 'sprintf-js';

ko.bindingHandlers.bytesize = (function () {
  let that;
  return (that = {
    units: ['B', 'KB', 'MB', 'GB', 'TB', 'PB'],
    init: function (element, valueAccessor) {
      that.format(element, valueAccessor);
    },
    update: function (element, valueAccessor) {
      that.format(element, valueAccessor);
    },
    format: function (element, valueAccessor) {
      const value = valueAccessor();
      const formatted = that.humanSize(ko.unwrap(value));
      $(element).text(formatted);
    },
    getBaseLog: function (x, y) {
      return Math.log(x) / Math.log(y);
    },
    humanSize: function (bytes) {
      const isNumber = !isNaN(parseFloat(bytes)) && isFinite(bytes);
      if (!isNumber) {
        return '';
      }

      // Special case small numbers (including 0), because they're exact.
      if (bytes < 1024) {
        return sprintf.sprintf('%d B', bytes);
      }

      let index = Math.floor(that.getBaseLog(bytes, 1024));
      index = Math.min(that.units.length - 1, index);
      return sprintf.sprintf('%.1f %s', bytes / Math.pow(1024, index), that.units[index]);
    }
  });
})();
