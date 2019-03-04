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
import sprintf from 'sprintf-js';

ko.bindingHandlers.duration = (function() {
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
      const formatted = that.humanTime(ko.unwrap(value));
      $(element).text(formatted);
    },
    humanTime: function(value) {
      value = value * 1;
      if (value < Math.pow(10, 3)) {
        return sprintf.sprintf('%i ns', value);
      } else if (value - Math.pow(10, 6) < -Math.pow(10, 3) / 2) {
        // Make sure rounding doesn't cause numbers to have more than 4 significant digits.
        value = (value * 1.0) / Math.pow(10, 3);
        const sprint = value > 100 ? '%i us' : '%.1f us';
        return sprintf.sprintf(sprint, value);
      } else if (value - Math.pow(10, 9) < -Math.pow(10, 6) / 2) {
        value = (value * 1.0) / Math.pow(10, 6);
        const sprint = value > 100 ? '%i ms' : '%.1f ms';
        return sprintf.sprintf(sprint, value);
      } else {
        // get the ms value
        const SECOND = 1;
        const MINUTE = SECOND * 60;
        const HOUR = MINUTE * 60;
        value = (value * 1) / Math.pow(10, 9);
        let buffer = '';

        if (value > HOUR) {
          buffer += sprintf.sprintf('%i h', value / HOUR);
          value = value % HOUR;
        }

        if (buffer.length < 4 && value > MINUTE) {
          const sprint = buffer.length ? ' %i m' : '%i m';
          buffer += sprintf.sprintf(sprint, value / MINUTE);
          value = value % MINUTE;
        }

        if (buffer.length < 4 && value > SECOND) {
          const sprint = buffer.length ? ' %i s' : '%.1f s';
          buffer += sprintf.sprintf(sprint, (value * 1.0) / SECOND);
        }
        return buffer;
      }
    }
  });
})();
