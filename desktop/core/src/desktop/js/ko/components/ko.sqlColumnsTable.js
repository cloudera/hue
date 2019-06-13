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

import componentUtils from './componentUtils';
import I18n from 'utils/i18n';

const TEMPLATE = `
    <div class="context-popover-flex">
      <div class="context-popover-flex-header">
        <div class="context-popover-header" style="display:inline-block;">${I18n(
          'Columns'
        )} (<span data-bind="text: filteredColumns().length"></span>)</div>
        <div class="context-popover-inline-autocomplete">
          <!-- ko component: {
            name: 'inline-autocomplete',
            params: {
              querySpec: querySpec,
              facets: Object.keys(SQL_COLUMNS_KNOWN_FACET_VALUES),
              knownFacetValues: SQL_COLUMNS_KNOWN_FACET_VALUES,
              autocompleteFromEntries: autocompleteFromEntries
            }
          } --><!-- /ko -->
        </div>
      </div>
      <div class="context-popover-flex-fill sql-columns-table" style="position:relative; height: 100%; overflow-y: auto;">
        <table id="sqlColumnsTable" style="width: 100%" class="table table-condensed table-nowrap">
          <!-- ko if: filteredColumns().length !== 0 -->
          <thead>
          <tr>
            <th width="6%">&nbsp;</th>
            <!-- ko if: typeof filteredColumns()[0].table === 'undefined' -->
            <th width="60%">${I18n('Name')}</th>
            <!-- /ko -->
            <!-- ko if: typeof filteredColumns()[0].table !== 'undefined' -->
            <th width="40%">${I18n('Name')}</th>
            <th width="20%">${I18n('Table')}</th>
            <!-- /ko -->
            <th width="34%">${I18n('Type')}</th>
            <th width="6%">&nbsp;</th>
          </tr>
          </thead>
          <!-- /ko -->
          <tbody data-bind="foreachVisible: { data: filteredColumns, minHeight: 29, container: '.sql-columns-table', pubSubDispose: 'context.popover.dispose' }">
          <tr>
            <!-- ko if: typeof selected === 'undefined' -->
            <td data-bind="text: $index()+$indexOffset()+1"></td>
            <!-- /ko -->
            <!-- ko if: typeof selected !== 'undefined' -->
            <td class="center" data-bind="multiCheckForeachVisible: { entries: $parent.filteredColumns, selectedAttr: 'selected' }" style="cursor: default;">
              <div class="hue-checkbox fa" data-bind="css: {'fa-check': selected }"></div>
            </td>

            <!-- /ko -->
            <td style="overflow: hidden;">
              <!-- ko if: $parent.scrollToColumns -->
              <a href="javascript:void(0)" class="column-selector" data-bind="click: function() { huePubSub.publish('context.popover.scroll.to.column', name); }" title="${I18n(
                'Show sample'
              )}"><span data-bind="text: name"></span> <i class="fa fa-key" data-bind="visible: typeof primary_key !== 'undefined' && primary_key === 'true'"></i></a>
              <!-- /ko -->
              <!-- ko ifnot: $parent.scrollToColumns -->
              <span data-bind="text: name"></span> <i class="fa fa-key" data-bind="visible: typeof primary_key !== 'undefined' && primary_key === 'true'"></i>
              <!-- /ko -->
            </td>
            <!-- ko if: typeof table !== 'undefined' -->
            <td><span data-bind="text: table"></span></td>
            <!-- /ko -->
            <td><span data-bind="text: type, attr: { 'title': extendedType }, tooltip: { placement: 'bottom' }"></span></td>
            <td><i class="snippet-icon fa fa-question-circle" data-bind="visible: comment, attr: { 'title': comment }, tooltip: { placement: 'bottom' }"></i></td>
          </tr>
          </tbody>
        </table>
        <div class="context-popover-empty-columns" data-bind="visible: filteredColumns().length === 0">${I18n(
          'No columns found'
        )}</div>
      </div>
    </div>
`;

class SqlColumnsTable {
  constructor(params) {
    const self = this;
    self.columns = params.columns;
    self.scrollToColumns =
      typeof params.scrollToColumns !== 'undefined' ? params.scrollToColumns : true;
    self.searchInput = ko.observable('');
    self.searchFocus = ko.observable(false);
    self.querySpec = ko.observable();

    self.filteredColumns = ko.pureComputed(() => {
      if (!self.querySpec() || self.querySpec().query === '') {
        return self.columns;
      }

      const facets = self.querySpec().facets;
      const isFacetMatch = !facets || Object.keys(facets).length === 0 || !facets['type']; // So far only type facet is used for SQL
      const isTextMatch = !self.querySpec().text || self.querySpec().text.length === 0;

      return self.columns.filter(column => {
        let match = true;

        if (!isFacetMatch) {
          match = !!facets['type'][column.type];
        }

        if (match && !isTextMatch) {
          match = self.querySpec().text.every(text => {
            return (
              column.name.toLowerCase().indexOf(text.toLowerCase()) !== -1 ||
              column.comment.toLowerCase().indexOf(text.toLowerCase()) !== -1
            );
          });
        }

        return match;
      });
    });

    self.autocompleteFromEntries = function(nonPartial, partial) {
      const result = [];
      const partialLower = partial.toLowerCase();
      self.columns.forEach(column => {
        if (column.name.toLowerCase().indexOf(partialLower) === 0) {
          result.push(nonPartial + partial + column.name.substring(partial.length));
        }
      });
      return result;
    };
  }
}

componentUtils.registerComponent('sql-columns-table', SqlColumnsTable, TEMPLATE);
