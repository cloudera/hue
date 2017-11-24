## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%!
from django.utils.translation import ugettext as _
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko
%>

<%def name="sqlColumnsTable()">

  <script type="text/html" id="sql-columns-table-template">
    <div class="context-popover-flex">
      <div class="context-popover-flex-header">
        <div class="context-popover-header" style="display:inline-block;">${_('Columns')} (<span data-bind="text: filteredColumns().length"></span>)</div>
        <a href="#" data-bind="toggle: searchVisible"><i class="snippet-icon fa fa-search inactive-action margin-left-10" data-bind="css: { 'blue': searchVisible }"></i></a>
        <div class="context-popover-inline-autocomplete" data-bind="visible: searchVisible">
          <!-- ko component: {
            name: 'inline-autocomplete',
            params: {
              querySpec: querySpec,
              facets: Object.keys(SQL_COLUMNS_KNOWN_FACET_VALUES),
              knownFacetValues: SQL_COLUMNS_KNOWN_FACET_VALUES
            }
          } --><!-- /ko -->
        </div>
##         <input class="input-large context-popover-inline-search" style="padding: 3px 6px;" type="text" data-bind="visible: searchVisible, hasFocus: searchFocus, clearable: searchInput, valueUpdate:'afterkeydown'" placeholder="${ _('Filter columns...') }">
      </div>
      <div class="context-popover-flex-fill sql-columns-table" style="position:relative; height: 100%; overflow-y: auto;">
        <table id="sqlColumnsTable" style="width: 100%" class="table table-condensed table-nowrap">
          <!-- ko if: filteredColumns().length !== 0 -->
          <thead>
          <tr>
            <th width="6%">&nbsp;</th>
            <!-- ko if: typeof filteredColumns()[0].table === 'undefined' -->
            <th width="60%">${_('Name')}</th>
            <!-- /ko -->
            <!-- ko if: typeof filteredColumns()[0].table !== 'undefined' -->
            <th width="40%">${_('Name')}</th>
            <th width="20%">${_('Table')}</th>
            <!-- /ko -->
            <th width="34%">${_('Type')}</th>
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
            <td data-bind="toggle: selected" class="center" style="cursor: default;">
              <div class="hueCheckbox fa" data-bind="multiCheck: '#sqlColumnsTable', css: {'fa-check': selected }"></div>
            </td>

            <!-- /ko -->
            <td style="overflow: hidden;">
              <!-- ko if: $parent.scrollToColumns -->
              <a href="javascript:void(0)" class="column-selector" data-bind="click: function() { huePubSub.publish('context.popover.scroll.to.column', name); }" title="${ _("Show sample") }"><span data-bind="text: name"></span> <i class="fa fa-key" data-bind="visible: typeof primary_key !== 'undefined' && primary_key === 'true'"></i></a>
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
        <div class="context-popover-empty-columns" data-bind="visible: filteredColumns().length === 0">${_('No columns found')}</div>
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      window.SQL_COLUMNS_KNOWN_FACET_VALUES = {
        'type': {'array': -1, 'boolean': -1, 'bigint': -1, 'binary': -1, 'char': -1, 'date': -1, 'double': -1, 'decimal': -1, 'float': -1, 'int': -1, 'map': -1, 'real': -1, 'smallint': -1, 'string': -1, 'struct': -1, 'timestamp': -1, 'tinyint': -1, 'varchar': -1 }
      };

      function SqlColumnsTable(params) {
        var self = this;
        var columns = params.columns;
        self.scrollToColumns = typeof params.scrollToColumns !== 'undefined' ?  params.scrollToColumns : true;
        self.searchInput = ko.observable('');
        self.searchVisible = ko.observable(true);
        self.searchFocus = ko.observable(false);
        self.querySpec = ko.observable();

        self.searchVisible.subscribe(function (newValue) {
          if (newValue) {
            self.searchFocus(true);
          }
        });

        self.filteredColumns = ko.pureComputed(function () {
          if (!self.querySpec() || self.querySpec().query === '') {
            return columns;
          }

          var facets = self.querySpec().facets;
          var isFacetMatch = !facets || Object.keys(facets).length === 0 || !facets['type']; // So far only type facet is used for SQL
          var isTextMatch = !self.querySpec().text || self.querySpec().text.length === 0;

          return columns.filter(function (column) {
            var match = true;

            if (!isFacetMatch) {
              match = !!facets['type'][column.type];
            }

            if (match && !isTextMatch) {
              match = self.querySpec().text.every(function (text) {
                return column.name.toLowerCase().indexOf(text.toLowerCase()) !== -1 || column.comment.toLowerCase().indexOf(text.toLowerCase()) != -1
              });
            }

            return match;
          })
        });
      }

      ko.components.register('sql-columns-table', {
        viewModel: SqlColumnsTable,
        template: { element: 'sql-columns-table-template' }
      });
    })();
  </script>
</%def>
