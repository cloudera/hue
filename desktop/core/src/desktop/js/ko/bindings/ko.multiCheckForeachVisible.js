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

ko.bindingHandlers.multiCheckForeachVisible = {
  init: function(element, valueAccessor, allBindings, clickedEntry, bindingContext) {
    const $element = $(element);
    const parentContext = bindingContext.$parentContext;

    const selectedAttr = valueAccessor().selectedAttr;
    const entries = valueAccessor().entries;

    $element
      .attr('unselectable', 'on')
      .css('user-select', 'none')
      .on('selectstart', false);

    $element.on('click', e => {
      if (e.shiftKey && parentContext.$multiCheckLastEntry) {
        const lastEntry = parentContext.$multiCheckLastEntry;
        let inside = false;
        entries().every(otherEntry => {
          if (otherEntry === lastEntry || otherEntry === clickedEntry) {
            if (inside) {
              return false;
            }
            inside = true;
            return true;
          }
          if (inside && otherEntry[selectedAttr]() !== lastEntry[selectedAttr]()) {
            otherEntry[selectedAttr](lastEntry[selectedAttr]());
          }
          return true;
        });
        if (clickedEntry[selectedAttr]() !== lastEntry[selectedAttr]()) {
          clickedEntry[selectedAttr](lastEntry[selectedAttr]());
        }
      } else {
        clickedEntry[selectedAttr](!clickedEntry[selectedAttr]());
      }

      parentContext.$multiCheckLastEntry = clickedEntry;
      parentContext.$multiCheckLastChecked = clickedEntry[selectedAttr]();
    });

    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
      $element.off('click');
    });
  },
  update: function() {}
};
