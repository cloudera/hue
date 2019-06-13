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

import AssistStorageEntry from 'assist/assistStorageEntry';
import huePubSub from 'utils/huePubSub';

/**
 * Show the Context Popover for files (HDFS, S3, ADLS, ...) when the bound element is clicked.
 *
 * Parameters:
 *
 * {string} path - the path (can include type, i.e. 'hdfs://tmp'
 * {string} [type] - Optional type, 'hdfs', 's3' etc. Default 'hdfs'.
 * {string} [orientation] - 'top', 'right', 'bottom', 'left'. Default 'right';
 * {Object} [offset] - Optional offset from the element
 * {number} [offset.top] - Offset in pixels
 * {number} [offset.left] - Offset in pixels
 *
 * Examples:
 *
 * data-bind="storageContextPopover: { path: '/tmp/banana.csv' }"
 * data-bind="storageContextPopover: { path: 's3:/tmp/banana.csv', orientation: 'bottom', offset: { top: 5 } }"
 *
 * @type {{init: ko.bindingHandlers.storageContextPopover.init}}
 */
ko.bindingHandlers.storageContextPopover = {
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    ko.bindingHandlers.click.init(
      element,
      () => {
        return function() {
          const options = valueAccessor();
          AssistStorageEntry.getEntry(options.path, options.type).done(entry => {
            const $source = $(element);
            const offset = $source.offset();

            if (options.offset) {
              offset.top += options.offset.top || 0;
              offset.left += options.offset.left || 0;
            }

            entry.open(true);
            huePubSub.publish('context.popover.show', {
              data: {
                type: 'storageEntry',
                storageEntry: entry
              },
              orientation: options.orientation || 'right',
              source: {
                element: element,
                left: offset.left,
                top: offset.top,
                right: offset.left + $source.width(),
                bottom: offset.top + $source.height()
              }
            });
          });
        };
      },
      allBindings,
      viewModel,
      bindingContext
    );
  }
};
