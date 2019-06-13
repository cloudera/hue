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

ko.extenders.numeric = function(target, config) {
  const precision = typeof config.precision === 'undefined' ? config : config.precision;
  const roundingMultiplier = Math.pow(10, precision);

  const result = ko
    .computed({
      read: target,
      write: function(newValue) {
        const current = target();
        const newValueAsNum = isNaN(newValue) ? 0 : parseFloat(+newValue);
        let valueToWrite = Math.round(newValueAsNum * roundingMultiplier) / roundingMultiplier;

        if (newValue === '' && config.allowEmpty) {
          valueToWrite = newValue;
        }
        if (valueToWrite !== current) {
          target(valueToWrite);
        } else if (newValue !== current) {
          target.notifySubscribers(valueToWrite);
        }
      }
    })
    .extend({ notify: 'always' });
  result(target());
  return result;
};
