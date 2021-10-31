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

import {
  ASSIST_DB_HIGHLIGHT_EVENT,
  ASSIST_DB_PANEL_IS_READY_EVENT,
  ASSIST_GET_DATABASE_EVENT,
  ASSIST_GET_SOURCE_EVENT,
  ASSIST_IS_DB_PANEL_READY_EVENT,
  ASSIST_SET_DATABASE_EVENT,
  ASSIST_SET_SOURCE_EVENT,
  ASSIST_SHOW_SOLR_EVENT,
  ASSIST_SHOW_SQL_EVENT,
  SHOW_LEFT_ASSIST_EVENT
} from './events';
import { ASSIST_KEY_COMPONENT } from './ko.assistKey';
import dataCatalog from 'catalog/dataCatalog';
import { CONFIG_REFRESHED_TOPIC } from 'config/events';
import {
  filterEditorConnectors,
  findBrowserConnector,
  findDashboardConnector,
  findEditorConnector
} from 'config/hueConfig';
import AssistDbSource from 'ko/components/assist/assistDbSource';
import componentUtils from 'ko/components/componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';

const ASSIST_TABLE_TEMPLATES = `
  <script type="text/html" id="assist-no-database-entries">
    <ul class="assist-tables">
      <li>
        <span class="assist-no-entries">${I18n('No entries found')}</span>
      </li>
    </ul>
  </script>

  <script type="text/html" id="assist-no-table-entries">
    <ul>
      <li>
        <span class="assist-no-entries">${I18n('The table has no columns')}</span>
      </li>
    </ul>
  </script>

  <script type="text/html" id="sql-context-items">
    <!-- ko if: typeof catalogEntry !== 'undefined' -->
      <li><a href="javascript:void(0);" data-bind="click: function (data) { showContextPopover(data, { target: $parentContext.$contextSourceElement }, { left: -15, top: 2 }); }"><i class="fa fa-fw fa-info"></i> ${I18n(
        'Show details'
      )}</a></li>
      <!-- ko switch: sourceType -->
      <!-- ko case: 'solr' -->
        <!-- ko if: catalogEntry.isTableOrView() -->
        <li><a href="javascript:void(0);" data-bind="click: openInIndexer"><i class="fa fa-fw fa-table"></i> ${I18n(
          'Open in Browser'
        )}</a></li>
        <li><a href="javascript: void(0);" data-bind="click: function() { explore(true); }"><!-- ko template: { name: 'app-icon-template', data: { icon: 'dashboard' } } --><!-- /ko --> ${I18n(
          'Open in Dashboard'
        )}</a></li>
        <!-- /ko -->
      <!-- /ko -->
      <!-- ko case: $default -->
        <!-- ko if: !catalogEntry.isDatabase() && $currentApp() === 'editor' -->
        <li><a href="javascript:void(0);" data-bind="click: dblClick"><i class="fa fa-fw fa-paste"></i> ${I18n(
          'Insert at cursor'
        )}</a></li>
        <!-- /ko -->
        <!-- ko if: catalogEntry.path.length <=2 -->
        <li><a href="javascript:void(0);" data-bind="click: openInMetastore"><i class="fa fa-fw fa-table"></i> ${I18n(
          'Open in Browser'
        )}</a></li>
        <!-- /ko -->
        <!-- ko if: catalogEntry.isTableOrView() -->
        <li><a href="javascript:void(0);" data-bind="click: function() { huePubSub.publish('query.and.watch', {'url': '/notebook/browse/' + databaseName + '/' + tableName + '/', sourceType: sourceType}); }"><i class="fa fa-fw fa-code"></i> ${I18n(
          'Open in Editor'
        )}</a></li>
        <!-- ko if: window.HAS_SQL_DASHBOARD -->
        <li><a href="javascript: void(0);" data-bind="click: function() { explore(false); }"><!-- ko template: { name: 'app-icon-template', data: { icon: 'dashboard' } } --><!-- /ko --> ${I18n(
          'Open in Dashboard'
        )}</a></li>
        <!-- /ko -->
        <!-- /ko -->
        <!-- ko if: window.ENABLE_QUERY_BUILDER && catalogEntry.isColumn() && $currentApp() === 'editor' -->
        <li class="divider"></li>
        <!-- ko template: { name: 'query-builder-context-items' } --><!-- /ko -->
        <!-- /ko -->
      <!-- /ko -->
      <!-- /ko -->
    <!-- /ko -->
  </script>

  <script type="text/html" id="query-builder-context-items">
    <li data-bind="contextSubMenu: '.hue-context-sub-menu'">
      <a href="javascript:void(0);"><i class="fa fa-fw fa-magic"></i> ${I18n(
        'Project'
      )}<i class="sub-icon fa fa-fw fa-chevron-right"></i></a>
      <ul class="hue-context-menu hue-context-sub-menu">
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Select', 'Project', '{0}', false, false); }">Select</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Select distinct', 'Project', '{0}', false, false); }">Select distinct</a></li>
      </ul>
    </li>

    <li data-bind="contextSubMenu: '.hue-context-sub-menu'">
      <a href="javascript:void(0);"><i class="fa fa-fw fa-magic"></i> ${I18n(
        'Aggregate'
      )}<i class="sub-icon fa fa-fw fa-chevron-right"></i></a>
      <ul class="hue-context-menu hue-context-sub-menu">
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Count', 'Aggregate', 'COUNT({0}.{1}) as count_{1}', false, false); }">Count</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Count distinct', 'Aggregate', 'COUNT(DISTINCT {0}.{1}) as distinct_count_{1}', false, false); }">Count distinct</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Sum', 'Aggregate', 'SUM({0}.{1}) as sum_{1}', false, false); }">Sum</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Minimum', 'Aggregate', 'MIN({0}.{1}) as min_{1}', false, false); }">Minimum</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Maximum', 'Aggregate', 'MAX({0}.{1}) as max_{1}', false, false); }">Maximum</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Average', 'Aggregate', 'AVG({0}.{1}) as avg_{1}', false, false); }">Average</a></li>
      </ul>
    </li>

    <li data-bind="contextSubMenu: '.hue-context-sub-menu'">
      <a href="javascript:void(0);"><i class="fa fa-fw fa-magic"></i> ${I18n(
        'Filter'
      )}<i class="sub-icon fa fa-fw fa-chevron-right"></i></a>
      <ul class="hue-context-menu hue-context-sub-menu">
        <li><a href="javascript:void(0);" data-bind="click: function () { var isNotNullRule = QueryBuilder.getRule(databaseName, tableName, columnName, 'Is not null'); if (isNotNullRule.length) { isNotNullRule.attr('rule', 'Is null'); isNotNullRule.find('.rule').text('Is null'); } else { QueryBuilder.addRule(databaseName, tableName, columnName, 'Is null', 'Filter', '{0}.{1} = null', false, false); } }">Is null</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { var isNullRule = QueryBuilder.getRule(databaseName, tableName, columnName, 'Is null'); if (isNullRule.length) { isNullRule.attr('rule', 'Is not null'); isNullRule.find('.rule').text('Is not null'); } else { QueryBuilder.addRule(databaseName, tableName, columnName, 'Is not null', 'Filter', '{0}.{1} != null', false, false); } }">Is not null</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Equal to', 'Filter', '{0}.{1} = {2}', true, true); }">Equal to</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Not equal to', 'Filter', '{0}.{1} != {2}', true, true); }">Not equal to</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Greater than', 'Filter', '{0}.{1} > {2}', true, false) }">Greater than</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Less than', 'Filter', '{0}.{1} < {2}', true, false); }">Less than</a></li>
      </ul>
    </li>
    <li data-bind="contextSubMenu: '.hue-context-sub-menu'">
      <a href="javascript:void(0);"><i class="fa fa-fw fa-magic"></i> ${I18n(
        'Order'
      )}<i class="sub-icon fa fa-fw fa-chevron-right"></i></a>
      <ul class="hue-context-menu hue-context-sub-menu">
        <li><a href="javascript:void(0);" data-bind="click: function () { var descendingRule = QueryBuilder.getRule(databaseName, tableName, columnName, 'Descending'); if (descendingRule.length) { descendingRule.attr('rule', 'Ascending'); descendingRule.find('.rule').text('Ascending'); } else { QueryBuilder.addRule(databaseName, tableName, columnName, 'Ascending', 'Order', '{0}.{1} ASC', false, false); } }">Ascending</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { var ascendingRule = QueryBuilder.getRule(databaseName, tableName, columnName, 'Ascending'); if (ascendingRule.length) { ascendingRule.attr('rule', 'Descending'); ascendingRule.find('.rule').text('Descending'); } else { QueryBuilder.addRule(databaseName, tableName, columnName, 'Descending', 'Order', '{0}.{1} DESC', false, false); } }">Descending</a></li>
      </ul>
    </li>
  </script>

  <script type="text/html" id="assist-table-entry">
    <li class="assist-table" data-bind="appAwareTemplateContextMenu: { template: 'sql-context-items', scrollContainer: '.assist-db-scrollable' }, visibleOnHover: { override: statsVisible() || navigationSettings.rightAssist, selector: '.table-actions' }">
      <div class="assist-actions table-actions" data-bind="css: { 'assist-actions-left': navigationSettings.rightAssist }" style="opacity: 0">
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, popoverOnHover: showContextPopover, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${I18n(
          'Show details'
        )}"></i></a>
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.openItem, click: openItem"><i class="fa fa-long-arrow-right" title="${I18n(
          'Open'
        )}"></i></a>
      </div>
      <a class="assist-entry assist-table-link" href="javascript:void(0)" data-bind="click: toggleOpen, attr: {'title': catalogEntry.getTitle(true) }, draggableText: { text: editorText,  meta: { connector: catalogEntry.getConnector(), type: 'sql', isView: catalogEntry.isView(), table: tableName, database: databaseName } }">
        <i class="fa fa-fw muted valign-middle" data-bind="css: iconClass"></i>
        <span class="highlightable" data-bind="text: catalogEntry.getDisplayName(navigationSettings.rightAssist), css: { 'highlight': highlight }"></span>
      </a>
      <div class="center assist-spinner" data-bind="visible: loading() && open()"><i class="fa fa-spinner fa-spin"></i></div>
      <!-- ko template: { if: open, name: 'assist-db-entries'  } --><!-- /ko -->
    </li>
  </script>

  <script type="text/html" id="assist-column-entry">
    <li data-bind="appAwareTemplateContextMenu: { template: 'sql-context-items', scrollContainer: '.assist-db-scrollable' }, visible: ! hasErrors(), visibleOnHover: { childrenOnly: true, override: statsVisible, selector: catalogEntry.isView() ? '.table-actions' : '.column-actions' }, css: { 'assist-table': catalogEntry.isView(), 'assist-column': catalogEntry.isField() }">
      <div class="assist-actions column-actions" data-bind="css: { 'assist-actions-left': navigationSettings.rightAssist }" style="opacity: 0">
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, popoverOnHover: showContextPopover, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${I18n(
          'Show details'
        )}"></i></a>
      </div>
      <!-- ko if: expandable -->
      <a class="assist-entry assist-field-link" href="javascript:void(0)" data-bind="click: toggleOpen, attr: {'title': catalogEntry.getTitle(true) }, css: { 'assist-entry-left-action': navigationSettings.rightAssist }">
        <span class="highlightable" data-bind="css: { 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName }, text: catalogEntry.getDisplayName(), draggableText: { text: editorText, meta: { connector: catalogEntry.getConnector(), type: 'sql', column: columnName, table: tableName, database: databaseName } }"></span><!-- ko if: catalogEntry.isKey() --> <!-- ko component: { name: '${ASSIST_KEY_COMPONENT}', params: { entry: catalogEntry } } --><!-- /ko --><!-- /ko -->
      </a>
      <!-- /ko -->
      <!-- ko ifnot: expandable -->
      <div class="assist-entry assist-field-link default-cursor" href="javascript:void(0)" data-bind="event: { dblclick: dblClick }, attr: {'title': catalogEntry.getTitle(true) }, css: { 'assist-entry-left-action': navigationSettings.rightAssist }">
        <span class="highlightable" data-bind="css: { 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName}, text: catalogEntry.getDisplayName(), draggableText: { text: editorText, meta: { connector: catalogEntry.getConnector(), type: 'sql', column: columnName, table: tableName, database: databaseName } }"></span><!-- ko if: catalogEntry.isKey() --> <!-- ko component: { name: '${ASSIST_KEY_COMPONENT}', params: { entry: catalogEntry } } --><!-- /ko --><!-- /ko -->
      </div>
      <!-- /ko -->
      <div class="center assist-spinner" data-bind="visible: loading"><i class="fa fa-spinner fa-spin"></i></div>
      <!-- ko template: { if: open, name: 'assist-db-entries'  } --><!-- /ko -->
    </li>
  </script>

  <script type="text/html" id="assist-column-entry-assistant">
    <li data-bind="appAwareTemplateContextMenu: { template: 'sql-context-items', scrollContainer: '.assist-db-scrollable' }, visible: ! hasErrors(), visibleOnHover: { childrenOnly: true, override: statsVisible, selector: catalogEntry.isView() ? '.table-actions' : '.column-actions' }, css: { 'assist-table': catalogEntry.isView(), 'assist-column': catalogEntry.isField() }">
      <div class="assist-actions column-actions assist-actions-left" style="opacity: 0">
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, popoverOnHover: showContextPopover, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${I18n(
          'Show details'
        )}"></i></a>
      </div>
      <!-- ko if: expandable -->
      <a class="assist-entry assist-field-link assist-field-link-dark assist-entry-left-action assist-ellipsis" href="javascript:void(0)" data-bind="click: toggleOpen, attr: {'title': catalogEntry.getTitle(true) }">
        <span data-bind="text: catalogEntry.getType()" class="muted pull-right margin-right-20"></span>
        <span class="highlightable" data-bind="css: { 'highlight': highlight}, attr: { 'column': columnName, 'table': tableName, 'database': databaseName }, text: catalogEntry.name, draggableText: { text: editorText, meta: { connector: catalogEntry.getConnector(), type: 'sql', column: columnName, table: tableName, database: databaseName } }"></span><!-- ko if: catalogEntry.isKey() --> <!-- ko component: { name: '${ASSIST_KEY_COMPONENT}', params: { entry: catalogEntry } } --><!-- /ko --><!-- /ko -->
      </a>
      <!-- /ko -->
      <!-- ko ifnot: expandable -->
      <div class="assist-entry assist-field-link assist-field-link-dark default-cursor assist-ellipsis" href="javascript:void(0)" data-bind="event: { dblclick: dblClick }, attr: {'title': catalogEntry.getTitle(true) }, css: { 'assist-entry-left-action': navigationSettings.rightAssist }">
        <span data-bind="text: catalogEntry.getType()" class="muted pull-right margin-right-20"></span>
        <span class="highlightable" data-bind="css: { 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName}, text: catalogEntry.name, draggableText: { text: editorText, meta: { connector: catalogEntry.getConnector(), type: 'sql', column: columnName, table: tableName, database: databaseName } }"></span><!-- ko if: catalogEntry.isKey() --> <!-- ko component: { name: '${ASSIST_KEY_COMPONENT}', params: { entry: catalogEntry } } --><!-- /ko --><!-- /ko -->
      </div>
      <!-- /ko -->
      <div class="center assist-spinner" data-bind="visible: loading"><i class="fa fa-spinner fa-spin"></i></div>
      <!-- ko template: { if: open, name: 'assist-db-entries'  } --><!-- /ko -->
    </li>
  </script>

  <script type="text/html" id="assist-db-entries">
    <!-- ko if: ! hasErrors() && hasEntries() && ! loading() && filteredEntries().length == 0 -->
    <ul class="assist-tables">
      <li class="assist-entry assist-no-entries"><!-- ko if: catalogEntry.isTableOrView() -->${I18n(
        'No columns found'
      )}<!--/ko--><!-- ko if: catalogEntry.isDatabase() -->${I18n(
  'No tables found'
)}<!--/ko--><!-- ko if: catalogEntry.isField() -->${I18n('No results found')}<!--/ko--></li>
    </ul>
    <!-- /ko -->
    <!-- ko if: ! hasErrors() && hasEntries() && ! loading() && filteredEntries().length > 0 -->
    <ul class="database-tree" data-bind="foreachVisible: { data: filteredEntries, minHeight: navigationSettings.rightAssist ? 22 : 23, container: '.assist-db-scrollable', skipScrollEvent: navigationSettings.rightAssist, usePreloadBackground: true }, css: { 'assist-tables': catalogEntry.isDatabase() }">
      <!-- ko template: { if: catalogEntry.isTableOrView(), name: 'assist-table-entry' } --><!-- /ko -->
      <!-- ko if: navigationSettings.rightAssist -->
        <!-- ko template: { ifnot: catalogEntry.isTableOrView(), name: 'assist-column-entry-assistant' } --><!-- /ko -->
      <!-- /ko -->
      <!-- ko ifnot: navigationSettings.rightAssist -->
        <!-- ko template: { ifnot: catalogEntry.isTableOrView(), name: 'assist-column-entry' } --><!-- /ko -->
      <!-- /ko -->
    </ul>
    <!-- /ko -->
    <!-- ko template: { if: ! hasErrors() && ! hasEntries() && ! loading() && (catalogEntry.isTableOrView()), name: 'assist-no-table-entries' } --><!-- /ko -->
    <!-- ko template: { if: ! hasErrors() && ! hasEntries() && ! loading() && catalogEntry.isDatabase(), name: 'assist-no-database-entries' } --><!-- /ko -->
    <!-- ko if: hasErrors -->
    <ul class="assist-tables">
      <!-- ko if: catalogEntry.isTableOrView() -->
      <li class="assist-errors">${I18n('Error loading columns.')}</li>
      <!-- /ko -->
      <!-- ko if: catalogEntry.isField() -->
      <li class="assist-errors">${I18n('Error loading fields.')}</li>
      <!-- /ko -->
    </ul>
    <!-- /ko -->
  </script>
`;

const TEMPLATE =
  ASSIST_TABLE_TEMPLATES +
  `
  <script type="text/html" id="assist-database-actions">
    <div class="assist-actions database-actions" style="opacity: 0">
      <!-- ko if: sourceType === 'hive' || sourceType === 'impala' -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, popoverOnHover: function (data, event) { showContextPopover(data, event); }, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${I18n(
        'Show details'
      )}"></i></a>
      <!-- /ko -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.openItem, click: openItem"><i class="fa fa-long-arrow-right" title="${I18n(
        'Open'
      )}"></i></a>
    </div>
  </script>

  <script type="text/html" id="collection-title-context-items">
    <li><a href="javascript:void(0);" data-bind="hueLink: '/indexer'"><i class="fa fa-fw fa-table"></i> ${I18n(
      'Open in Browser'
    )}</a></li>
  </script>

  <script type="text/html" id="assist-database-entry">
    <li class="assist-table" data-bind="appAwareTemplateContextMenu: { template: 'sql-context-items', scrollContainer: '.assist-db-scrollable' }, visibleOnHover: { selector: '.database-actions' }">
      <!-- ko template: { name: 'assist-database-actions' } --><!-- /ko -->
      <a class="assist-table-link" href="javascript: void(0);" data-bind="click: function () { $parent.selectedDatabase($data); $parent.selectedDatabaseChanged(); }, attr: {'title': catalogEntry.getTitle(true) }, draggableText: { text: editorText,  meta: { connector: catalogEntry.getConnector(), type: 'sql', database: databaseName } }"><i class="fa fa-fw fa-database muted valign-middle"></i> <span class="highlightable" data-bind="text: catalogEntry.name, css: { 'highlight': highlight() }"></span></a>
    </li>
  </script>

  <script type="text/html" id="assist-db-breadcrumb">
    <div class="assist-flex-header assist-breadcrumb">
      <!-- ko if: selectedSource() -->
      <!-- ko if: selectedSource().selectedNamespace() -->
      <!-- ko if: selectedSource().selectedNamespace().selectedDatabase() -->
      <a data-bind="click: back, appAwareTemplateContextMenu: { template: 'sql-context-items', viewModel: selectedSource().selectedNamespace().selectedDatabase() }">
        <i class="fa fa-chevron-left assist-breadcrumb-back" ></i>
        <i class="fa assist-breadcrumb-text" data-bind="css: { 'fa-server': nonSqlType, 'fa-database': !nonSqlType }"></i>
        <span class="assist-breadcrumb-text" data-bind="text: breadcrumb, attr: {'title': breadcrumbTitle }"></span>
      </a>
      <!-- /ko -->
      <!-- ko ifnot: selectedSource().selectedNamespace().selectedDatabase() -->
      <!-- ko if: window.HAS_MULTI_CLUSTER-->
      <a data-bind="click: back">
        <i class="fa fa-chevron-left assist-breadcrumb-back"></i>
        <i class="fa fa-snowflake-o assist-breadcrumb-text"></i>
        <span class="assist-breadcrumb-text" data-bind="text: breadcrumb, attr: {'title': breadcrumbTitle }"></span>
      </a>
      <!-- /ko -->
      <!-- ko ifnot: window.HAS_MULTI_CLUSTER -->
      <a data-bind="click: back">
        <i class="fa fa-chevron-left assist-breadcrumb-back"></i>
        <i class="fa fa-server assist-breadcrumb-text"></i>
        <span class="assist-breadcrumb-text" data-bind="text: breadcrumb"></span>
      </a>
      <!-- /ko -->
      <!-- /ko -->
      <!-- /ko -->
      <!-- ko ifnot: selectedSource().selectedNamespace() -->
      <a data-bind="click: back">
        <i class="fa fa-chevron-left assist-breadcrumb-back"></i>
        <i class="fa fa-server assist-breadcrumb-text"></i>
        <span class="assist-breadcrumb-text" data-bind="text: breadcrumb"></span>
      </a>
      <!-- /ko -->
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="assist-sql-inner-panel">
    <!-- ko template: { if: breadcrumb() !== null, name: 'assist-db-breadcrumb' } --><!-- /ko -->
    <!-- ko template: { ifnot: selectedSource, name: 'assist-sources-template' } --><!-- /ko -->
    <!-- ko with: selectedSource -->
      <!-- ko template: { ifnot: selectedNamespace, name: 'assist-namespaces-template' } --><!-- /ko -->
      <!-- ko with: selectedNamespace -->
        <!-- ko template: { ifnot: selectedDatabase, name: 'assist-databases-template' } --><!-- /ko -->
        <!-- ko with: selectedDatabase -->
          <!-- ko template: { name: 'assist-tables-template' } --><!-- /ko -->
        <!-- /ko -->
      <!-- /ko -->
    <!-- /ko -->
  </script>

  <script type="text/html" id="ask-for-invalidate-title">
    &nbsp;<a class="pull-right pointer close-popover inactive-action">&times;</a>
  </script>

  <script type="text/html" id="assist-namespace-header-actions">
    <div class="assist-db-header-actions">
      <!-- ko ifnot: loading -->
      <span class="assist-tables-counter">(<span data-bind="text: filteredNamespaces().length"></span>)</span>
      <!-- ko if: window.HAS_MULTI_CLUSTER -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: triggerRefresh"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${I18n(
        'Refresh'
      )}"></i></a>
      <!-- /ko -->
      <!-- /ko -->
      <!-- ko if: loading -->
      <i class="fa fa-refresh fa-spin blue" title="${I18n('Refresh')}"></i>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="assist-db-header-actions">
    <div class="assist-db-header-actions">
      <!-- ko ifnot: loading -->
      <span class="assist-tables-counter">(<span data-bind="text: filteredEntries().length"></span>)</span>
      <!-- ko if: sourceType !== 'solr' && $component.showImporter() -->
      <!-- ko if: typeof databaseName !== 'undefined' -->
        <a class="inactive-action" data-bind="hueLink: importer_url + databaseName + '/?sourceType=' + sourceType + '&namespace=' + assistDbNamespace.namespace.id" title="${I18n(
          'Create table'
        )}" href="javascript:void(0)">
          <i class="pointer fa fa-plus" title="${I18n('Create table')}"></i>
        </a>
      <!-- /ko -->
      <!-- ko if: typeof databases !== 'undefined' -->
        <a class="inactive-action" data-bind="hueLink: window.HUE_URLS.IMPORTER_CREATE_DATABASE + '/?sourceType=' + sourceType + '&namespace=' + namespace.id" href="javascript:void(0)">
          <i class="pointer fa fa-plus" title="${I18n('Create database')}"></i>
        </a>
      <!-- /ko -->
      <!-- /ko -->
      <!-- ko if: sourceType === 'solr' -->
      <a class="inactive-action" data-bind="hueLink: '/indexer/importer/prefill/all/index/'" title="${I18n(
        'Create index'
      )}">
        <i class="pointer fa fa-plus" title="${I18n('Create index')}"></i>
      </a>
      <!-- /ko -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: triggerRefresh"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${I18n(
        'Refresh'
      )}"></i></a>
      <!-- /ko -->
      <!-- ko if: loading -->
      <i class="fa fa-refresh fa-spin blue" title="${I18n('Refresh')}"></i>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="assist-sources-template">
    <div class="assist-flex-header">
      <div class="assist-inner-header">
        ${I18n('Sources')}
      </div>
    </div>
    <div class="assist-flex-fill">
      <ul class="assist-tables" data-bind="foreach: sources">
        <li class="assist-table">
          <a class="assist-table-link" href="javascript: void(0);" data-bind="click: function () { $parent.selectedSource($data); }"><i class="fa fa-fw fa-server muted valign-middle"></i> <span data-bind="text: name"></span></a>
        </li>
      </ul>
    </div>
  </script>

  <script type="text/html" id="assist-namespaces-template">
    <div class="assist-flex-header">
      <div class="assist-inner-header">
        ${I18n('Namespaces')}
        <!-- ko template: 'assist-namespace-header-actions' --><!-- /ko -->
      </div>
    </div>
    <div class="assist-flex-search" data-bind="visible: hasNamespaces() && !hasErrors()">
      <div class="assist-filter">
        <!-- ko component: {
            name: 'inline-autocomplete',
            params: {
              querySpec: filter.querySpec,
              facets: [],
              knownFacetValues: {},
              autocompleteFromEntries: autocompleteFromNamespaces
            }
          } --><!-- /ko -->
      </div>
    </div>
    <div class="assist-flex-fill assist-db-scrollable" data-bind="visible: !hasErrors() && !loading() && hasNamespaces(), delayedOverflow">
      <!-- ko if: !loading() && filteredNamespaces().length == 0 -->
      <ul class="assist-tables">
        <li class="assist-entry no-entries">${I18n('No results found')}</li>
      </ul>
      <!-- /ko -->
      <ul class="assist-tables" data-bind="foreach: filteredNamespaces">
        <li class="assist-table">
          <!-- ko if: status() === 'STARTING' -->
          <span class="assist-table-link" title="${I18n(
            'Starting'
          )}" data-bind="tooltip: { placement: 'bottom' }"><i class="fa fa-fw fa-spinner fa-spin muted valign-middle"></i> <span data-bind="text: name"></span></span>
          <!-- /ko -->
          <!-- ko if: status() !== 'STARTING' -->
          <!-- ko if: namespace.computes.length -->
          <a class="assist-table-link" href="javascript: void(0);" data-bind="click: function () { $parent.selectedNamespace($data); }"><i class="fa fa-fw fa-snowflake-o muted valign-middle"></i> <span data-bind="text: name"></span></a>
          <!-- /ko -->
          <!-- ko ifnot: namespace.computes.length -->
          <span class="assist-table-link" title="${I18n(
            'No related computes'
          )}" data-bind="tooltip: { placement: 'bottom' }"><i class="fa fa-fw fa-warning muted valign-middle"></i> <span data-bind="text: name"></span></span>
          <!-- /ko -->
          <!-- /ko -->
        </li>
      </ul>
    </div>
    <div class="assist-flex-fill" data-bind="visible: loading">
      <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
    </div>
    <div class="assist-flex-fill" data-bind="visible: hasErrors() && !loading()">
      <span class="assist-errors">${I18n('Error loading namespaces.')}</span>
    </div>
    <div class="assist-flex-fill" data-bind="visible: !hasErrors() && !loading() && !hasNamespaces()">
      <span class="assist-errors">${I18n('No namespaces found.')}</span>
    </div>
  </script>

  <script type="text/html" id="assist-databases-template">
    <div class="assist-flex-header" data-bind="visibleOnHover: { selector: '.hover-actions', override: loading() }">
      <div class="assist-inner-header">
        <!-- ko ifnot: sourceType === 'solr' || sourceType === 'kafka' -->
        ${I18n('Databases')}
        <!-- ko template: 'assist-db-header-actions' --><!-- /ko -->
        <!-- /ko -->
        <!-- ko if: sourceType === 'solr' || sourceType === 'kafka'-->
        ${I18n('Sources')}
        <!-- /ko -->
      </div>
    </div>
    <div class="assist-flex-search" data-bind="visible: hasEntries() && ! hasErrors()">
      <div class="assist-filter">
        <!-- ko component: {
            name: 'inline-autocomplete',
            params: {
              querySpec: filter.querySpec,
              facets: [],
              placeHolder: sourceType === 'solr' || sourceType === 'kafka' ? '${I18n(
                'Filter sources...'
              )}' : '${I18n('Filter databases...')}',
              knownFacetValues: {},
              autocompleteFromEntries: autocompleteFromEntries
            }
          } --><!-- /ko -->
      </div>
    </div>
    <div class="assist-flex-fill assist-db-scrollable" data-bind="visible: ! hasErrors() && ! loading() && hasEntries(), delayedOverflow">
      <!-- ko if: ! loading() && filteredEntries().length == 0 -->
      <ul class="assist-tables">
        <li class="assist-entry no-entries">${I18n('No results found')}</li>
      </ul>
      <!-- /ko -->
      <ul class="assist-tables" data-bind="foreachVisible: {data: filteredEntries, minHeight: 23, container: '.assist-db-scrollable', skipScrollEvent: navigationSettings.rightAssist }">
        <!-- ko template: { name: 'assist-database-entry' } --><!-- /ko -->
      </ul>
    </div>
    <div class="assist-flex-fill" data-bind="visible: loading">
      <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
    </div>
    <div class="assist-flex-fill" data-bind="visible: hasErrors() && ! loading()">
      <span class="assist-errors">${I18n('Error loading databases.')}</span>
    </div>
    <div class="assist-flex-fill" data-bind="visible: ! hasErrors() && ! loading() && ! hasEntries()">
      <span class="assist-errors">${I18n('No databases found.')}</span>
    </div>
  </script>

  <script type="text/html" id="assist-tables-template">
    <div class="assist-flex-header">
      <div class="assist-inner-header" data-bind="visible: !$parent.loading() && !$parent.hasErrors()">
        <!-- ko ifnot: sourceType === 'solr' || sourceType === 'kafka' -->
          ${I18n('Tables')}
        <!-- /ko -->
        <!-- ko if: sourceType === 'solr' -->
          <div data-bind="appAwareTemplateContextMenu: { template: 'collection-title-context-items', scrollContainer: '.assist-db-scrollable' }">${I18n(
            'Indexes'
          )}</div>
        <!-- /ko -->
        <!-- ko if: sourceType === 'kafka' -->
          ${I18n('Topics')}
        <!-- /ko -->
        <!-- ko template: 'assist-db-header-actions' --><!-- /ko -->
      </div>
    </div>
    <div class="assist-flex-search" data-bind="visible: hasEntries() && !$parent.loading() && !$parent.hasErrors()">
      <div class="assist-filter">
        <!-- ko component: {
          name: 'inline-autocomplete',
          params: {
            querySpec: filter.querySpec,
            facets: ['type'],
            knownFacetValues: knownFacetValues.bind($data),
            autocompleteFromEntries: autocompleteFromEntries
          }
        } --><!-- /ko -->
      </div>
    </div>
    <div class="assist-flex-fill assist-db-scrollable" data-bind="visible: ! hasErrors() && ! loading(), delayedOverflow">
      <!-- ko template: 'assist-db-entries' --><!-- /ko -->
    </div>
    <div class="assist-flex-fill" data-bind="visible: loading() || $parent.loading()">
      <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
    </div>
    <div class="assist-flex-fill" data-bind="visible: hasErrors() && ! loading()">
      <span class="assist-errors">${I18n('Error loading tables.')}</span>
    </div>
  </script>

  <!-- ko template: 'assist-sql-inner-panel' --><!-- /ko -->
`;

class AssistDbPanel {
  /**
   * @param {Object} options
   * @param {Object} options.i18n
   * @param {Object} options.navigationSettings - enable/disable the links
   * @param {boolean} options.navigationSettings.openItem
   * @param {boolean} options.navigationSettings.showStats
   * @param {boolean} options.navigationSettings.pinEnabled
   * @param {boolean} [options.isSolr] - Default false;
   * @param {boolean} [options.isStreams] - Default false;
   * @constructor
   **/
  constructor(options) {
    this.options = options;
    this.i18n = options.i18n;

    this.isStreams = options.isStreams;
    this.isSolr = options.isSolr;
    this.nonSqlType = this.isSolr || this.isStreams;
    this.showImporter = ko.observable(false);

    this.sources = ko.observableArray();
    this.sourceIndex = {};
    this.selectedSource = ko.observable(null);

    this.breadcrumbTitle = ko.pureComputed(
      () => `${this.breadcrumb()} (${this.selectedSource().connector.displayName})`
    );

    this.breadcrumb = ko.pureComputed(() => {
      if (this.isStreams && this.selectedSource()) {
        return this.selectedSource().connector.displayName;
      }
      if (!this.isSolr && this.selectedSource()) {
        if (this.selectedSource().selectedNamespace()) {
          if (this.selectedSource().selectedNamespace().selectedDatabase()) {
            return this.selectedSource().selectedNamespace().selectedDatabase().catalogEntry.name;
          }
          if (window.HAS_MULTI_CLUSTER) {
            return this.selectedSource().selectedNamespace().name;
          }
        }
        return this.selectedSource().connector.displayName;
      }
      return null;
    });

    huePubSub.subscribe(ASSIST_DB_HIGHLIGHT_EVENT, catalogEntry => {
      huePubSub.publish(SHOW_LEFT_ASSIST_EVENT);
      if (catalogEntry.getDialect() === 'solr') {
        huePubSub.publish(ASSIST_SHOW_SOLR_EVENT);
      } else {
        huePubSub.publish(ASSIST_SHOW_SQL_EVENT);
      }
      huePubSub.publish('context.popover.hide');
      window.setTimeout(() => {
        let foundSource;
        this.sources().some(source => {
          if (source.sourceType === catalogEntry.getConnector().id) {
            foundSource = source;
            return true;
          }
        });
        if (foundSource) {
          if (this.selectedSource() !== foundSource) {
            this.selectedSource(foundSource);
          }
          foundSource.highlightInside(catalogEntry);
        }
      }, 0);
    });

    if (this.isSolr) {
      huePubSub.subscribe('assist.collections.refresh', () => {
        const solrSource = this.sourceIndex['solr'];
        const doRefresh = () => {
          if (solrSource.selectedNamespace()) {
            const assistDbNamespace = solrSource.selectedNamespace();
            dataCatalog
              .getEntry({
                namespace: assistDbNamespace.namespace,
                compute: assistDbNamespace.compute(),
                connector: { id: 'solr' },
                path: []
              })
              .then(entry => {
                entry.clearCache({ cascade: true });
              });
          }
        };
        if (!solrSource.hasNamespaces()) {
          solrSource.loadNamespaces(true).done(doRefresh);
        } else {
          doRefresh();
        }
      });
    } else if (!this.isSolr && !this.isStreams) {
      huePubSub.subscribe(ASSIST_SET_DATABASE_EVENT, databaseDef => {
        if (!databaseDef.connector || !this.sourceIndex[databaseDef.connector.id]) {
          return;
        }
        this.selectedSource(this.sourceIndex[databaseDef.connector.id]);
        this.setDatabaseWhenLoaded(databaseDef.namespace, databaseDef.name);
      });

      const getSelectedDatabase = connector => {
        const deferred = $.Deferred();
        const assistDbSource = this.sourceIndex[connector.id];
        if (assistDbSource) {
          assistDbSource.loadedDeferred.done(() => {
            if (assistDbSource.selectedNamespace()) {
              assistDbSource.selectedNamespace().loadedDeferred.done(() => {
                if (assistDbSource.selectedNamespace().selectedDatabase()) {
                  deferred.resolve(
                    assistDbSource.selectedNamespace().selectedDatabase().catalogEntry
                  );
                } else {
                  let lastSelectedDb = getFromLocalStorage(
                    'assist_' +
                      connector.id +
                      '_' +
                      assistDbSource.selectedNamespace().namespace.id +
                      '.lastSelectedDb'
                  );
                  if (!lastSelectedDb && lastSelectedDb !== '') {
                    lastSelectedDb = 'default';
                  }
                  dataCatalog
                    .getEntry({
                      connector: connector,
                      namespace: assistDbSource.selectedNamespace().namespace,
                      compute: assistDbSource.selectedNamespace().compute,
                      path: [lastSelectedDb]
                    })
                    .then(deferred.resolve);
                }
              });
            } else {
              dataCatalog
                .getEntry({
                  connector: connector,
                  namespace: { id: 'default' },
                  compute: { id: 'default' },
                  path: ['default']
                })
                .then(deferred.resolve);
            }
          });
        } else {
          deferred.reject();
        }

        return deferred;
      };

      huePubSub.subscribe(ASSIST_GET_DATABASE_EVENT, options => {
        getSelectedDatabase(options.connector).done(options.callback);
      });

      huePubSub.subscribe(ASSIST_GET_SOURCE_EVENT, callback => {
        callback(this.selectedSource() ? this.selectedSource().sourceType : undefined);
      });

      huePubSub.subscribe(ASSIST_SET_SOURCE_EVENT, source => {
        if (this.sourceIndex[source]) {
          this.selectedSource(this.sourceIndex[source]);
        }
      });

      this.selectedSource.subscribe(newSource => {
        if (newSource) {
          if (newSource.namespaces().length === 0) {
            newSource.loadNamespaces();
          }
          setInLocalStorage('assist.lastSelectedSource', newSource.sourceType);
        } else {
          setInLocalStorage('assist.lastSelectedSource', null);
        }
      });
    }

    this.init(options.navigationSettings);
    huePubSub.publish(ASSIST_DB_PANEL_IS_READY_EVENT);

    huePubSub.subscribe(ASSIST_IS_DB_PANEL_READY_EVENT, () => {
      huePubSub.publish(ASSIST_DB_PANEL_IS_READY_EVENT);
    });
  }

  setDatabaseWhenLoaded(namespace, databaseName) {
    this.selectedSource().whenLoaded(() => {
      if (
        this.selectedSource().selectedNamespace() &&
        this.selectedSource().selectedNamespace().namespace.id !== namespace.id
      ) {
        this.selectedSource()
          .namespaces()
          .some(otherNamespace => {
            if (otherNamespace.namespace.id === namespace.id) {
              this.selectedSource().selectedNamespace(otherNamespace);
              return true;
            }
          });
      }

      if (this.selectedSource().selectedNamespace()) {
        this.selectedSource()
          .selectedNamespace()
          .whenLoaded(() => {
            this.selectedSource().selectedNamespace().setDatabase(databaseName);
          });
      }
    });
  }

  back() {
    if (this.isStreams) {
      this.selectedSource(null);
      return;
    }
    if (this.selectedSource()) {
      if (this.selectedSource() && this.selectedSource().selectedNamespace()) {
        if (this.selectedSource().selectedNamespace().selectedDatabase()) {
          this.selectedSource().selectedNamespace().selectedDatabase(null);
          this.selectedSource().selectedNamespace().selectedDatabaseChanged();
        } else if (window.HAS_MULTI_CLUSTER) {
          this.selectedSource().selectedNamespace(null);
        } else {
          this.selectedSource(null);
        }
      } else {
        this.selectedSource(null);
      }
    }
  }

  setSingleSource(connector, navigationSettings, nonSqlType) {
    this.sourceIndex = {};
    const source = new AssistDbSource({
      i18n: this.i18n,
      type: connector.id,
      name: connector.displayName,
      connector: connector,
      nonSqlType: nonSqlType,
      navigationSettings: navigationSettings
    });
    this.sourceIndex[connector.id] = source;
    this.sources([source]);
    this.selectedSource(source);

    source.loadNamespaces().then(() => {
      const namespace = this.selectedSource().selectedNamespace();
      if (namespace) {
        namespace.initDatabases();
        namespace.whenLoaded(() => {
          namespace.setDatabase('default');
        });
      }
    });
  }

  init(navigationSettings) {
    if (this.isSolr) {
      const connector = findDashboardConnector(connector => connector.id === 'solr');
      this.setSingleSource(connector, navigationSettings, true);
      return;
    }

    if (this.isStreams) {
      const connector = findEditorConnector(connector => connector.dialect === 'ksql');
      this.setSingleSource(connector, navigationSettings, true);
      return;
    }

    const updateFromConfig = () => {
      const sources = [];
      this.showImporter(!!findBrowserConnector(connector => connector.type === 'importer'));
      const connectors = filterEditorConnectors(connector => connector.is_sql);
      connectors.forEach(connector => {
        const source =
          this.sourceIndex[connector.id] ||
          new AssistDbSource({
            i18n: this.i18n,
            type: connector.id, // TODO: Remove redundant
            name: connector.displayName, // TODO: Remove redundant
            connector: connector,
            nonSqlType: false,
            navigationSettings: navigationSettings
          });
        sources.push(source);
      });
      this.sourceIndex = {};
      sources.forEach(source => {
        this.sourceIndex[source.sourceType] = source;
      });

      if (sources.indexOf(this.selectedSource()) === -1) {
        if (sources.length) {
          const storageSourceType = getFromLocalStorage('assist.lastSelectedSource');
          this.selectedSource(
            (storageSourceType && this.sourceIndex[storageSourceType]) || sources[0]
          );
        } else {
          this.selectedSource(undefined);
        }
      }
      this.sources(sources);
    };

    huePubSub.subscribe(CONFIG_REFRESHED_TOPIC, updateFromConfig);
    updateFromConfig();
  }
}

const instances = {};

const viewModelFactory = {
  createViewModel: params => {
    const name = params.isStreams ? 'streams' : params.isSolr ? 'solr' : 'sql';
    if (!instances[name]) {
      instances[name] = new AssistDbPanel(params);
    }
    return instances[name];
  }
};

componentUtils.registerComponent('hue-assist-db-panel', viewModelFactory, TEMPLATE);

export default ASSIST_TABLE_TEMPLATES;
