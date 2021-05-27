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

import { SqlAnalyzerMode } from 'catalog/analyzer/types';
import $ from 'jquery';
import * as ko from 'knockout';

import dataCatalog from 'catalog/dataCatalog';
import huePubSub from 'utils/huePubSub';

/**
 * Show the Context Popover for SQL or Solr entities when the bound element is clicked.
 *
 * Parameters:
 *
 * {string} sourceType - 'impala', 'hive' etc.
 * {ContextNamespace} namespace
 * {ContextCompute} compute
 * {string} path - the path, i.e. 'default.customers' or ['default', 'customers'
 * {string} [orientation] - 'top', 'right', 'bottom', 'left'. Default 'right'
 * {Object} [offset] - Optional offset from the element
 * {number} [offset.top] - Offset in pixels
 * {number} [offset.left] - Offset in pixels
 *
 * Examples:
 *
 * data-bind="sqlContextPopover: { sourceType: 'impala', namespace: { id: 'myNamespace' }, compute: { id: 'myCompute' }, path: 'default.customers' }"
 * data-bind="sqlContextPopover: { sourceType: 'hive', namespace: { id: 'myNamespace' }, compute: { id: 'myCompute' }, path: 'default', orientation: 'bottom', offset: { top: 5 } }"
 *
 * @type {{init: ko.bindingHandlers.sqlContextPopover.init}}
 */
ko.bindingHandlers.sqlContextPopover = {
  init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
    ko.bindingHandlers.click.init(
      element,
      () => {
        return function () {
          const options = valueAccessor();

          // TODO: Use connector for SQL context popover
          if (
            !options.connector &&
            (options.sourceType === 'hive' || options.sourceType === 'impala')
          ) {
            options.connector = {
              optimizer: SqlAnalyzerMode.api,
              id: options.sourceType,
              dialect: options.sourceType
            };
          }
          dataCatalog.getEntry(options).then(entry => {
            const $source = $(element);
            const offset = $source.offset();
            if (options.offset) {
              offset.top += options.offset.top || 0;
              offset.left += options.offset.left || 0;
            }

            huePubSub.publish('context.popover.show', {
              data: {
                type: 'catalogEntry',
                catalogEntry: entry
              },
              showInAssistEnabled: true,
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
