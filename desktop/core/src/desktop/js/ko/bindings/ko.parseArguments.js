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

ko.bindingHandlers.parseArguments = {
  init: function(element, valueAccessor) {
    const $el = $(element);

    function splitStrings(str) {
      const bits = [];
      let isInQuotes = false;
      let tempStr = '';
      str
        .replace(/<\/?arg>|<\/?command>/gi, ' ')
        .replace(/\r?\n|\r/g, '')
        .replace(/\s\s+/g, ' ')
        .split('')
        .forEach(char => {
          if (char === '"' || char === "'") {
            isInQuotes = !isInQuotes;
          } else if ((char === ' ' || char === '\n') && !isInQuotes && tempStr !== '') {
            bits.push(tempStr);
            tempStr = '';
          } else {
            tempStr += char;
          }
        });
      if (tempStr !== '') {
        bits.push(tempStr);
      }
      return bits;
    }

    $el.bind('paste', e => {
      const pasted = e.originalEvent.clipboardData.getData('text');
      const args = splitStrings(pasted);
      if (args.length > 1) {
        const newList = [];
        args.forEach(arg => {
          const obj = {};
          obj[valueAccessor().objectKey] = $.trim(arg);
          newList.push(obj);
        });
        valueAccessor().list(ko.mapping.fromJS(newList)());
        valueAccessor().callback();
      }
    });
  }
};
