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

import componentUtils from 'ko/components/componentUtils';
import DisposableComponent from 'ko/components/DisposableComponent';
import I18n from 'utils/i18n';

export const NAME = 'result-grid';

// prettier-ignore
const TEMPLATE = `
<div>
  <div class="column-side" style="position: relative; white-space: nowrap;" data-bind="
      visible: isResultSettingsVisible,
      css: { 'span3 result-settings': isResultSettingsVisible, 'hidden': !isResultSettingsVisible() }">
    <div class="snippet-grid-settings" data-bind="delayedOverflow">
      <table class="table table-condensed margin-top-10 no-border">
        <thead>
        <tr>
          <th width="16">
            <input class="all-meta-checked no-margin-top" type="checkbox" data-bind="
                enable: !isMetaFilterVisible() && filteredMeta().length,
                event: {
                  change: function() { toggleAllResultColumns($element); clickFilteredMetaCheck() }
                },
                checked: filteredMetaChecked
              "/>
          </th>
          <th colspan="2" class="nav-header-like">
            <span class="meta-title pointer" data-bind="toggle: isMetaFilterVisible, attr: { title: filteredColumnCount }">${ I18n('columns')}</span>
            (<span class="meta-title pointer" data-bind="toggle: isMetaFilterVisible, text: filteredColumnCount"></span>)
            <span class="inactive-action" href="javascript:void(0)" data-bind="toggle: isMetaFilterVisible, css: { 'blue' : isMetaFilterVisible }"><i class="pointer fa fa-search" title="${ I18n('Search') }"></i></span>
          </th>
        </tr>
        <tr data-bind="visible: isMetaFilterVisible">
          <td colspan="3">
            <div class="context-popover-inline-autocomplete" style="display: block;">
              <!-- ko component: {
                name: 'inline-autocomplete',
                params: {
                  placeHolder: '${ I18n('Filter columns...') }',
                  querySpec: metaFilter,
                  facets: Object.keys(SQL_COLUMNS_KNOWN_FACET_VALUES),
                  knownFacetValues: SQL_COLUMNS_KNOWN_FACET_VALUES,
                  autocompleteFromEntries: autocompleteFromEntries
                }
              } --><!-- /ko -->
            </div>
          </td>
        </tr>
        </thead>
        <tbody class="unstyled filtered-meta" data-bind="foreach: filteredMeta">
        <tr data-bind="visible: name !== ''">
          <td><input class="no-margin-top" type="checkbox" data-bind="
              event: {
                change: function() { $parent.toggleResultColumn($element, originalIndex);}
              },
              checked: checked
            "/></td>
          <td><a class="pointer" data-bind="
              click: function() { $parent.scrollToResultColumn($element); },
              attr: { title: name + ' - ' + type }
            "><span data-bind="text: name"></span></a></td>
          <td><span data-bind="text: type" class="muted margin-left-20"></span></td>
        </tr>
        </tbody>
        <tfoot>
        <tr>
          <td colspan="3">
            <div class="margin-top-10 muted meta-noresults" data-bind="visible: !filteredMeta().length">
              ${ I18n('No results found') }
            </div>
          </td>
        </tr>
        </tfoot>
      </table>
    </div>
    <div class="resize-bar" style="top: 0; right: -10px; cursor: col-resize;"></div>
  </div>
  <div class="grid-side" data-bind="css: { 'span9': isResultSettingsVisible, 'span12 nomargin': !isResultSettingsVisible() }">
    <div data-bind="delayedOverflow: 'slow', css: resultsKlass">
      <table class="table table-condensed resultTable">
        <thead>
        <tr data-bind="foreach: meta">
          <th class="sorting" data-bind="
              text: ($index() == 0 ? '&nbsp;' : $data.name),
              css: typeof cssClass != 'undefined' ? cssClass : 'sort-string',
              attr: { title: $data.type },
              style: { 
                'width': $index() == 0 ? '1%' : '',
                'height': $index() == 0 ? '32px' : ''
              },
              click: function(obj, e) { $(e.target).parents('table').trigger('sort', obj); }
            "></th>
        </tr>
        </thead>
        <tbody>
        </tbody>
      </table>
      <div style="display:none;" data-bind="
          visible: status() == 'expired' && data() && data().length > 99,
          css: resultsKlass
        ">
        <pre class="margin-top-10"><i class="fa fa-check muted"></i> ${ I18n("Results have expired, rerun the query if needed.") }</pre>
      </div>
    </div>
  </div>
</div>
`;

class ResultGrid extends DisposableComponent {
  constructor(params) {
    super();
    this.status = params.status;
    this.isResultSettingsVisible = params.isResultSettingsVisible;
    this.isMetaFilterVisible = params.isMetaFilterVisible; // result
    this.filteredMeta = params.filteredMeta; // result
    this.filteredMetaChecked = params.filteredMetaChecked; // result
    this.clickFilteredMetaCheck = params.clickFilteredMetaCheck; // result
    this.filteredColumnCount = params.filteredColumnCount; // result
    this.metaFilter = params.metaFilter; // result
    this.autocompleteFromEntries = params.autocompleteFromEntries; // result
    this.toggleResultColumn = params.toggleResultColumn;
    this.scrollToResultColumn = params.scrollToResultColumn;
    this.resultsKlass = params.resultsKlass;
    this.meta = params.meta; // result
    this.data = params.data; // result
  }
}

componentUtils.registerComponent(NAME, ResultGrid, TEMPLATE);
