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

from dashboard.conf import HAS_SQL_ENABLED
from filebrowser.conf import SHOW_UPLOAD_BUTTON
from metadata.conf import OPTIMIZER
from metastore.conf import ENABLE_NEW_CREATE_TABLE
from notebook.conf import ENABLE_QUERY_BUILDER, ENABLE_QUERY_SCHEDULING

from desktop import appmanager
from desktop import conf
from desktop.conf import IS_EMBEDDED, USE_NEW_SIDE_PANELS, VCS
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko
%>

<%namespace name="sqlDocIndex" file="/sql_doc_index.mako" />

<%def name="assistPanel(is_s3_enabled=False)">
  <script type="text/html" id="assist-no-database-entries">
    <ul class="assist-tables">
      <li>
        <span class="assist-no-entries">${_('No entries found')}</span>
      </li>
    </ul>
  </script>

  <script type="text/html" id="assist-no-table-entries">
    <ul>
      <li>
        <span class="assist-no-entries">${_('The table has no columns')}</span>
      </li>
    </ul>
  </script>

  <script type="text/html" id="assist-database-actions">
    <div class="assist-actions database-actions" style="opacity: 0">
      <!-- ko if: sourceType === 'hive' || sourceType === 'impala' -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, click: function (data, event) { showContextPopover(data, event); }, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${_('Show details')}"></i></a>
      <!-- /ko -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.openItem, click: openItem"><i class="fa fa-long-arrow-right" title="${_('Open')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="collection-title-context-items">
    <li><a href="javascript:void(0);" data-bind="hueLink: '/indexer'"><i class="fa fa-fw fa-table"></i> ${ _('Open in Browser') }</a></li>
  </script>

  <script type="text/html" id="sql-context-items">
    <!-- ko if: typeof catalogEntry !== 'undefined' -->
      <li><a href="javascript:void(0);" data-bind="click: function (data) { showContextPopover(data, { target: $parentContext.$contextSourceElement }, { left: -15, top: 2 }); }"><i class="fa fa-fw fa-info"></i> ${ _('Show details') }</a></li>
      <!-- ko switch: sourceType -->
      <!-- ko case: 'solr' -->
        <!-- ko if: catalogEntry.isTableOrView() -->
        <li><a href="javascript:void(0);" data-bind="click: openInIndexer"><i class="fa fa-fw fa-table"></i> ${ _('Open in Browser') }</a></li>
        <li><a href="javascript: void(0);" data-bind="click: function() { explore(true); }"><!-- ko template: { name: 'app-icon-template', data: { icon: 'dashboard' } } --><!-- /ko --> ${ _('Open in Dashboard') }</a></li>
        <!-- /ko -->
      <!-- /ko -->
      <!-- ko case: $default -->
        <!-- ko if: !catalogEntry.isDatabase() && $currentApp() === 'editor' -->
        <li><a href="javascript:void(0);" data-bind="click: dblClick"><i class="fa fa-fw fa-paste"></i> ${ _('Insert at cursor') }</a></li>
        <!-- /ko -->
        % if not IS_EMBEDDED.get():
        <!-- ko if: catalogEntry.path.length <=2 -->
        <li><a href="javascript:void(0);" data-bind="click: openInMetastore"><i class="fa fa-fw fa-table"></i> ${ _('Open in Browser') }</a></li>
        <!-- /ko -->
        % endif
        <!-- ko if: catalogEntry.isTableOrView() -->
        <li><a href="javascript:void(0);" data-bind="click: function() { huePubSub.publish('query.and.watch', {'url': '/notebook/browse/' + databaseName + '/' + tableName + '/', sourceType: sourceType}); }"><i class="fa fa-fw fa-code"></i> ${ _('Open in Editor') }</a></li>
        % if HAS_SQL_ENABLED.get():
        <li><a href="javascript: void(0);" data-bind="click: function() { explore(false); }"><!-- ko template: { name: 'app-icon-template', data: { icon: 'dashboard' } } --><!-- /ko --> ${ _('Open in Dashboard') }</a></li>
        % endif
        <!-- /ko -->
        %if ENABLE_QUERY_BUILDER.get():
        <!-- ko if: catalogEntry.isColumn() && $currentApp() === 'editor' -->
        <li class="divider"></li>
        <!-- ko template: { name: 'query-builder-context-items' } --><!-- /ko -->
        <!-- /ko -->
        %endif
      <!-- /ko -->
      <!-- /ko -->
    <!-- /ko -->
  </script>

  <script type="text/html" id="query-builder-context-items">
    <li data-bind="contextSubMenu: '.hue-context-sub-menu'">
      <a href="javascript:void(0);"><i class="fa fa-fw fa-magic"></i> ${ _('Project') }<i class="sub-icon fa fa-fw fa-chevron-right"></i></a>
      <ul class="hue-context-menu hue-context-sub-menu">
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Select', 'Project', '{0}', false, false); }">${ _('Select') }</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Select distinct', 'Project', '{0}', false, false); }">${ _('Select distinct') }</a></li>
      </ul>
    </li>

    <li data-bind="contextSubMenu: '.hue-context-sub-menu'">
      <a href="javascript:void(0);"><i class="fa fa-fw fa-magic"></i> ${ _('Aggregate') }<i class="sub-icon fa fa-fw fa-chevron-right"></i></a>
      <ul class="hue-context-menu hue-context-sub-menu">
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Count', 'Aggregate', 'COUNT({0}.{1}) as count_{1}', false, false); }">${ _('Count') }</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Count distinct', 'Aggregate', 'COUNT(DISTINCT {0}.{1}) as distinct_count_{1}', false, false); }">${ _('Count distinct') }</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Sum', 'Aggregate', 'SUM({0}.{1}) as sum_{1}', false, false); }">${ _('Sum') }</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Minimum', 'Aggregate', 'MIN({0}.{1}) as min_{1}', false, false); }">${ _('Minimum') }</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Maximum', 'Aggregate', 'MAX({0}.{1}) as max_{1}', false, false); }">${ _('Maximum') }</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Average', 'Aggregate', 'AVG({0}.{1}) as avg_{1}', false, false); }">${ _('Average') }</a></li>
      </ul>
    </li>

    <li data-bind="contextSubMenu: '.hue-context-sub-menu'">
      <a href="javascript:void(0);"><i class="fa fa-fw fa-magic"></i> ${ _('Filter') }<i class="sub-icon fa fa-fw fa-chevron-right"></i></a>
      <ul class="hue-context-menu hue-context-sub-menu">
        <li><a href="javascript:void(0);" data-bind="click: function () { var isNotNullRule = QueryBuilder.getRule(databaseName, tableName, columnName, 'Is not null'); if (isNotNullRule.length) { isNotNullRule.attr('rule', 'Is null'); isNotNullRule.find('.rule').text('Is null'); } else { QueryBuilder.addRule(databaseName, tableName, columnName, 'Is null', 'Filter', '{0}.{1} = null', false, false); } }">${ _('Is null') }</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { var isNullRule = QueryBuilder.getRule(databaseName, tableName, columnName, 'Is null'); if (isNullRule.length) { isNullRule.attr('rule', 'Is not null'); isNullRule.find('.rule').text('Is not null'); } else { QueryBuilder.addRule(databaseName, tableName, columnName, 'Is not null', 'Filter', '{0}.{1} != null', false, false); } }">${ _('Is not null') }</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Equal to', 'Filter', '{0}.{1} = {2}', true, true); }">${ _('Equal to') }</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Not equal to', 'Filter', '{0}.{1} != {2}', true, true); }">${ _('Not equal to') }</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Greater than', 'Filter', '{0}.{1} > {2}', true, false) }">${ _('Greater than') }</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { QueryBuilder.addRule(databaseName, tableName, columnName, 'Less than', 'Filter', '{0}.{1} < {2}', true, false); }">${ _('Less than') }</a></li>
      </ul>
    </li>
    <li data-bind="contextSubMenu: '.hue-context-sub-menu'">
      <a href="javascript:void(0);"><i class="fa fa-fw fa-magic"></i> ${ _('Order') }<i class="sub-icon fa fa-fw fa-chevron-right"></i></a>
      <ul class="hue-context-menu hue-context-sub-menu">
        <li><a href="javascript:void(0);" data-bind="click: function () { var descendingRule = QueryBuilder.getRule(databaseName, tableName, columnName, 'Descending'); if (descendingRule.length) { descendingRule.attr('rule', 'Ascending'); descendingRule.find('.rule').text('Ascending'); } else { QueryBuilder.addRule(databaseName, tableName, columnName, 'Ascending', 'Order', '{0}.{1} ASC', false, false); } }">${ _('Ascending') }</a></li>
        <li><a href="javascript:void(0);" data-bind="click: function () { var ascendingRule = QueryBuilder.getRule(databaseName, tableName, columnName, 'Ascending'); if (ascendingRule.length) { ascendingRule.attr('rule', 'Descending'); ascendingRule.find('.rule').text('Descending'); } else { QueryBuilder.addRule(databaseName, tableName, columnName, 'Descending', 'Order', '{0}.{1} DESC', false, false); } }">${ _('Descending') }</a></li>
      </ul>
    </li>
  </script>

  <script type="text/html" id="hdfs-context-items">
    <li><a href="javascript:void(0);" data-bind="click: function (data) { showContextPopover(data, { target: $parentContext.$contextSourceElement }, { left: -15, top: 2 }); }"><i class="fa fa-fw fa-info"></i> ${ _('Show details') }</a></li>
    <li><a href="javascript:void(0);" data-bind="hueLink: definition.url"><i class="fa fa-fw" data-bind="css: {'fa-folder-open-o': definition.type === 'dir', 'fa-file-text-o': definition.type === 'file'}"></i> ${ _('Open in Browser') }</a></li>
    <!-- ko if: definition.type === 'file' -->
    <li><a href="javascript:void(0);" data-bind="click: openInImporter"><!-- ko template: { name: 'app-icon-template', data: { icon: 'importer' } } --><!-- /ko --> ${ _('Open in Importer') }</a></li>
    <!-- /ko -->
    <!-- ko if: $currentApp() === 'editor' -->
    <li><a href="javascript:void(0);" data-bind="click: dblClick"><i class="fa fa-fw fa-paste"></i> ${ _('Insert at cursor') }</a></li>
    <!-- /ko -->
  </script>

  <script type="text/html" id="document-context-items">
    <!-- ko if: definition().type === 'directory' -->
    <li><a href="javascript: void(0);" data-bind="click: open"><i class="fa fa-fw fa-folder-open-o"></i> ${ _('Open folder') }</a></li>
    <!-- /ko -->
    <!-- ko if: definition().type !== 'directory' -->
    <li><a href="javascript: void(0);" data-bind="click: function(data) { showContextPopover(data, { target: $parentContext.$contextSourceElement }, { left: -15, top: 2 }); }"><i class="fa fa-fw fa-info"></i> ${ _('Show details') }</a></li>
    <li><a href="javascript: void(0);" data-bind="click: open"><i class="fa fa-fw fa-edit"></i> ${ _('Open document') }</a></li>
    <li><a href="javascript: void(0);" data-bind="click: function() { huePubSub.publish('doc.show.delete.modal', $data); activeEntry().getSelectedDocsWithDependents(); activeEntry().showDeleteConfirmation(); }"><i class="fa fa-fw fa-trash-o"></i> ${ _('Delete document') }</a></li>
    <!-- /ko -->
  </script>

  <script type="text/html" id="hbase-context-items">
    <!-- ko if: definition.host -->
    <li><a href="javascript: void(0);" data-bind="click: open"><i class="fa fa-fw fa-folder-open-o"></i> ${ _('Open cluster') }</a></li>
    <!-- /ko -->
    <!-- ko ifnot: definition.host -->
    <li><a href="javascript: void(0);" data-bind="click: open"><!-- ko template: { name: 'app-icon-template', data: { icon: 'hbase' } } --><!-- /ko --> ${ _('Open in HBase') }</a></li>
    <!-- /ko -->
  </script>

  <script type="text/html" id="assist-database-entry">
    <li class="assist-table" data-bind="appAwareTemplateContextMenu: { template: 'sql-context-items', scrollContainer: '.assist-db-scrollable' }, visibleOnHover: { selector: '.database-actions' }">
      <!-- ko template: { name: 'assist-database-actions' } --><!-- /ko -->
      <a class="assist-table-link" href="javascript: void(0);" data-bind="click: function () { $parent.selectedDatabase($data); $parent.selectedDatabaseChanged(); }, attr: {'title': catalogEntry.getTitle(true) }, draggableText: { text: editorText,  meta: {'type': 'sql', 'database': databaseName} }"><i class="fa fa-fw fa-database muted valign-middle"></i> <span class="highlightable" data-bind="text: catalogEntry.name, css: { 'highlight': highlight() }"></span></a>
    </li>
  </script>

  <script type="text/html" id="assist-table-entry">
    <li class="assist-table" data-bind="appAwareTemplateContextMenu: { template: 'sql-context-items', scrollContainer: '.assist-db-scrollable' }, visibleOnHover: { override: statsVisible() || navigationSettings.rightAssist, selector: '.table-actions' }">
      <div class="assist-actions table-actions" data-bind="css: { 'assist-actions-left': navigationSettings.rightAssist }" style="opacity: 0">
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, click: showContextPopover, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${_('Show details')}"></i></a>
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.openItem, click: openItem"><i class="fa fa-long-arrow-right" title="${_('Open')}"></i></a>
      </div>
      <a class="assist-entry assist-table-link" href="javascript:void(0)" data-bind="click: toggleOpen, attr: {'title': catalogEntry.getTitle(true) }, draggableText: { text: editorText,  meta: {'type': 'sql', 'isView': catalogEntry.isView(), 'table': tableName, 'database': databaseName} }">
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
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, click: showContextPopover, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${_('Show details')}"></i></a>
      </div>
      <!-- ko if: expandable -->
      <a class="assist-entry assist-field-link" href="javascript:void(0)" data-bind="click: toggleOpen, attr: {'title': catalogEntry.getTitle(true) }, css: { 'assist-entry-left-action': navigationSettings.rightAssist }">
        <span class="highlightable" data-bind="css: { 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName }, text: catalogEntry.getDisplayName(), draggableText: { text: editorText, meta: {'type': 'sql', 'column': columnName, 'table': tableName, 'database': databaseName } }"></span><!-- ko if: catalogEntry.isPrimaryKey() --> <i class="fa fa-key"></i><!-- /ko -->
      </a>
      <!-- /ko -->
      <!-- ko ifnot: expandable -->
      <div class="assist-entry assist-field-link default-cursor" href="javascript:void(0)" data-bind="event: { dblclick: dblClick }, attr: {'title': catalogEntry.getTitle(true) }, css: { 'assist-entry-left-action': navigationSettings.rightAssist }">
        <span class="highlightable" data-bind="css: { 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName}, text: catalogEntry.getDisplayName(), draggableText: { text: editorText, meta: {'type': 'sql', 'column': columnName, 'table': tableName, 'database': databaseName} }"></span><!-- ko if: catalogEntry.isPrimaryKey()  --> <i class="fa fa-key"></i><!-- /ko -->
      </div>
      <!-- /ko -->
      <div class="center assist-spinner" data-bind="visible: loading"><i class="fa fa-spinner fa-spin"></i></div>
      <!-- ko template: { if: open, name: 'assist-db-entries'  } --><!-- /ko -->
    </li>
  </script>

  <script type="text/html" id="assist-column-entry-assistant">
    <li data-bind="appAwareTemplateContextMenu: { template: 'sql-context-items', scrollContainer: '.assist-db-scrollable' }, visible: ! hasErrors(), visibleOnHover: { childrenOnly: true, override: statsVisible, selector: catalogEntry.isView() ? '.table-actions' : '.column-actions' }, css: { 'assist-table': catalogEntry.isView(), 'assist-column': catalogEntry.isField() }">
      <div class="assist-actions column-actions assist-actions-left" style="opacity: 0">
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, click: showContextPopover, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${_('Show details')}"></i></a>
      </div>
      <!-- ko if: expandable -->
      <a class="assist-entry assist-field-link assist-field-link-dark assist-entry-left-action assist-ellipsis" href="javascript:void(0)" data-bind="click: toggleOpen, attr: {'title': catalogEntry.getTitle(true) }">
        <span data-bind="text: catalogEntry.getType()" class="muted pull-right margin-right-20"></span>
        <span class="highlightable" data-bind="css: { 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName }, text: catalogEntry.name, draggableText: { text: editorText, meta: {'type': 'sql', 'column': columnName, 'table': tableName, 'database': databaseName } }"></span><!-- ko if: catalogEntry.isPrimaryKey() --> <i class="fa fa-key"></i><!-- /ko -->
      </a>
      <!-- /ko -->
      <!-- ko ifnot: expandable -->
      <div class="assist-entry assist-field-link assist-field-link-dark default-cursor assist-ellipsis" href="javascript:void(0)" data-bind="event: { dblclick: dblClick }, attr: {'title': catalogEntry.getTitle(true) }, css: { 'assist-entry-left-action': navigationSettings.rightAssist }">
        <span data-bind="text: catalogEntry.getType()" class="muted pull-right margin-right-20"></span>
        <span class="highlightable" data-bind="css: { 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName}, text: catalogEntry.name, draggableText: { text: editorText, meta: {'type': 'sql', 'column': columnName, 'table': tableName, 'database': databaseName} }"></span><!-- ko if: catalogEntry.isPrimaryKey() --> <i class="fa fa-key"></i><!-- /ko -->
      </div>
      <!-- /ko -->
      <div class="center assist-spinner" data-bind="visible: loading"><i class="fa fa-spinner fa-spin"></i></div>
      <!-- ko template: { if: open, name: 'assist-db-entries'  } --><!-- /ko -->
    </li>
  </script>

  <script type="text/html" id="assist-db-entries">
    <!-- ko if: ! hasErrors() && hasEntries() && ! loading() && filteredEntries().length == 0 -->
    <ul class="assist-tables">
      <li class="assist-entry assist-no-entries"><!-- ko if: catalogEntry.isTableOrView() -->${_('No columns found')}<!--/ko--><!-- ko if: catalogEntry.isDatabase() -->${_('No tables found')}<!--/ko--><!-- ko if: catalogEntry.isField() -->${_('No results found')}<!--/ko--></li>
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
      <li class="assist-errors">${ _('Error loading columns.') }</li>
      <!-- /ko -->
      <!-- ko if: catalogEntry.isField() -->
      <li class="assist-errors">${ _('Error loading fields.') }</li>
      <!-- /ko -->
    </ul>
    <!-- /ko -->
  </script>

  <script type="text/html" id="assist-db-breadcrumb">
    <div class="assist-flex-header assist-breadcrumb">
      <!-- ko if: selectedSource() -->
      <!-- ko if: selectedSource().selectedNamespace() -->
      <!-- ko if: selectedSource().selectedNamespace().selectedDatabase() -->
      <a data-bind="click: back, appAwareTemplateContextMenu: { template: 'sql-context-items', viewModel: selectedSource().selectedNamespace().selectedDatabase() }">
        <i class="fa fa-chevron-left assist-breadcrumb-back" ></i>
        <i class="fa assist-breadcrumb-text" data-bind="css: { 'fa-server': nonSqlType, 'fa-database': !nonSqlType }"></i>
        <span class="assist-breadcrumb-text" data-bind="text: breadcrumb, attr: {'title': breadcrumb() +  (nonSqlType ? '' : ' (' + selectedSource().sourceType + ' ' + selectedSource().selectedNamespace().name + ')') }"></span>
      </a>
      <!-- /ko -->
      <!-- ko ifnot: selectedSource().selectedNamespace().selectedDatabase() -->
      <!-- ko if: window.HAS_MULTI_CLUSTER-->
      <a data-bind="click: back">
        <i class="fa fa-chevron-left assist-breadcrumb-back"></i>
        <i class="fa fa-snowflake-o assist-breadcrumb-text"></i>
        <span class="assist-breadcrumb-text" data-bind="text: breadcrumb, attr: {'title': breadcrumb() + ' (' + selectedSource().sourceType + ')' }"></span>
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

  <script type="text/html" id="assist-s3-header-actions">
    <div class="assist-db-header-actions">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.s3.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manual refresh')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-s3-inner-panel">
    <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
    <!-- ko with: selectedS3Entry -->
    <div class="assist-flex-header assist-breadcrumb" >
      <!-- ko if: parent !== null -->
      <a href="javascript: void(0);" data-bind="appAwareTemplateContextMenu: { template: 'hdfs-context-items', scrollContainer: '.assist-s3-scrollable' }, click: function () { huePubSub.publish('assist.selectS3Entry', parent); }">
        <i class="fa fa-fw fa-chevron-left"></i>
        <i class="fa fa-fw fa-folder-o"></i>
        <span data-bind="text: definition.name, tooltip: {'title': path, 'placement': 'top' }"></span>
      </a>
      <!-- /ko -->
      <!-- ko if: parent === null -->
      <div>
        <i class="fa fa-fw fa-folder-o"></i>
        <span data-bind="text: path"></span>
      </div>
      <!-- /ko -->
      <!-- ko template: 'assist-s3-header-actions' --><!-- /ko -->
    </div>
    <div class="assist-flex-search">
      <div class="assist-filter"><input class="clearable" type="text" placeholder="${ _('Filter...') }" data-bind="clearable: filter, value: filter, valueUpdate: 'afterkeydown'"/></div>
    </div>
    <div class="assist-flex-fill assist-s3-scrollable" data-bind="delayedOverflow">
      <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
        <!-- ko hueSpinner: { spin: loadingMore, overlay: true } --><!-- /ko -->
        <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 22, container: '.assist-s3-scrollable', fetchMore: $data.fetchMore.bind($data) }">
          <li class="assist-entry assist-table-link" style="position: relative;" data-bind="appAwareTemplateContextMenu: { template: 'hdfs-context-items', scrollContainer: '.assist-s3-scrollable' }, visibleOnHover: { override: contextPopoverVisible, 'selector': '.assist-actions' }">
            <div class="assist-actions table-actions" style="opacity: 0;" >
              <a style="padding: 0 3px;" class="inactive-action" href="javascript:void(0);" data-bind="click: showContextPopover, css: { 'blue': contextPopoverVisible }">
                <i class='fa fa-info' title="${ _('Details') }"></i>
              </a>
            </div>

            <a href="javascript:void(0)" class="assist-entry assist-table-link" data-bind="multiClick: { click: toggleOpen, dblClick: dblClick }, attr: {'title': definition.name }">
              <!-- ko if: definition.type === 'dir' -->
              <i class="fa fa-fw fa-folder-o muted valign-middle"></i>
              <!-- /ko -->
              <!-- ko if: definition.type === 'file' -->
              <i class="fa fa-fw fa-file-o muted valign-middle"></i>
              <!-- /ko -->
              <span draggable="true" data-bind="text: definition.name, draggableText: { text: '\'' + path + '\'', meta: {'type': 's3', 'definition': definition} }"></span>
            </a>
          </li>
        </ul>
        <!-- ko if: !loading() && entries().length === 0 -->
        <ul class="assist-tables">
          <li class="assist-entry"><span class="assist-no-entries"><!-- ko if: filter() -->${_('No results found')}<!-- /ko --><!-- ko ifnot: filter() -->${_('Empty directory')}<!-- /ko --></span></li>
        </ul>
        <!-- /ko -->
      </div>
      <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
      <div class="assist-errors" data-bind="visible: ! loading() && hasErrors()">
        <span>${ _('Error loading contents.') }</span>
      </div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="git-details-title">
    <span data-bind="text: definition.name"></span>
  </script>

  <script type="text/html" id="assist-git-header-actions">
    <div class="assist-db-header-actions">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.git.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manual refresh')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-git-inner-panel">
    <!-- ko with: selectedGitEntry -->
    <div class="assist-flex-header assist-breadcrumb" >
      <!-- ko if: parent !== null -->
      <a href="javascript: void(0);" data-bind="click: function () { huePubSub.publish('assist.selectGitEntry', parent); }">
        <i class="fa fa-fw fa-chevron-left"></i>
        <i class="fa fa-fw fa-folder-o"></i>
        <span data-bind="text: path, attr: {'title': path }"></span>
      </a>
      <!-- /ko -->
      <!-- ko if: parent === null -->
      <div>
        <i class="fa fa-fw fa-folder-o"></i>
        <span data-bind="text: path"></span>
      </div>
      <!-- /ko -->
      <!-- ko template: 'assist-git-header-actions' --><!-- /ko -->
    </div>
    <div class="assist-flex-fill assist-git-scrollable" data-bind="delayedOverflow">
      <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
        <!-- ko hueSpinner: { spin: loadingMore, overlay: true } --><!-- /ko -->
        <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 22, container: '.assist-git-scrollable' }">
          <li class="assist-entry assist-table-link" style="position: relative;" data-bind="visibleOnHover: { 'selector': '.assist-actions' }">

            <a href="javascript:void(0)" class="assist-entry assist-table-link" data-bind="multiClick: { click: toggleOpen, dblClick: dblClick }, attr: {'title': definition.name }">
              <!-- ko if: definition.type === 'dir' -->
              <i class="fa fa-fw fa-folder-o muted valign-middle"></i>
              <!-- /ko -->
              <!-- ko ifnot: definition.type === 'dir' -->
              <i class="fa fa-fw fa-file-o muted valign-middle"></i>
              <!-- /ko -->
              <span draggable="true" data-bind="text: definition.name, draggableText: { text: '\'' + path + '\'', meta: {'type': 'git', 'definition': definition} }"></span>
            </a>
          </li>
        </ul>
        <!-- ko if: !loading() && entries().length === 0 -->
        <ul class="assist-tables">
          <li class="assist-entry"><span class="assist-no-entries">${_('Empty directory')}</span></li>
        </ul>
        <!-- /ko -->
      </div>
      <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
      <div class="assist-errors" data-bind="visible: ! loading() && hasErrors()">
        <span>${ _('Error loading contents.') }</span>
      </div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="assist-hdfs-header-actions">
    <div class="assist-db-header-actions">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: goHome, attr: { title: I18n('Go to ' + window.USER_HOME_DIR) }"><i class="pointer fa fa-home"></i></a>
      % if hasattr(SHOW_UPLOAD_BUTTON, 'get') and SHOW_UPLOAD_BUTTON.get():
      <a class="inactive-action" data-bind="dropzone: {
            url: '/filebrowser/upload/file?dest=' + path,
            params: { dest: path },
            paramName: 'hdfs_file',
            onError: function(x, e){ $(document).trigger('error', e); },
            onComplete: function () { huePubSub.publish('assist.hdfs.refresh'); huePubSub.publish('fb.hdfs.refresh', path); } }" title="${_('Upload file')}" href="javascript:void(0)">
        <div class="dz-message inline" data-dz-message><i class="pointer fa fa-plus" title="${_('Upload file')}"></i></div>
      </a>
      % endif
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.hdfs.refresh'); }" title="${_('Manual refresh')}"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-adls-header-actions">
    <div class="assist-db-header-actions">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: goHome, attr: { title: I18n('Go to ' + window.USER_HOME_DIR) }"><i class="pointer fa fa-home"></i></a>
      % if hasattr(SHOW_UPLOAD_BUTTON, 'get') and SHOW_UPLOAD_BUTTON.get():
      <a class="inactive-action" data-bind="dropzone: {
            url: '/filebrowser/upload/file?dest=adl:' + path,
            params: { dest: path },
            paramName: 'hdfs_file',
            onError: function(x, e){ $(document).trigger('error', e); },
            onComplete: function () { huePubSub.publish('assist.adls.refresh'); } }" title="${_('Upload file')}" href="javascript:void(0)">
        <div class="dz-message inline" data-dz-message><i class="pointer fa fa-plus" title="${_('Upload file')}"></i></div>
      </a>
      % endif
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.adls.refresh'); }" title="${_('Manual refresh')}"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-hdfs-inner-panel">
    <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
    <!-- ko with: selectedHdfsEntry -->
    <div class="assist-flex-header assist-breadcrumb" >
      <!-- ko if: parent !== null -->
      <a href="javascript: void(0);" data-bind="appAwareTemplateContextMenu: { template: 'hdfs-context-items', scrollContainer: '.assist-hdfs-scrollable' }, click: function () { huePubSub.publish('assist.selectHdfsEntry', parent); }">
        <i class="fa fa-fw fa-chevron-left"></i>
        <i class="fa fa-fw fa-folder-o"></i>
        <span data-bind="text: definition.name, tooltip: {'title': path, 'placement': 'top' }"></span>
      </a>
      <!-- /ko -->
      <!-- ko if: parent === null -->
      <div>
        <i class="fa fa-fw fa-folder-o"></i>
        <span data-bind="text: path"></span>
      </div>
      <!-- /ko -->
      <!-- ko template: 'assist-hdfs-header-actions' --><!-- /ko -->
    </div>
    <div class="assist-flex-search">
      <div class="assist-filter"><input class="clearable" type="text" placeholder="${ _('Filter...') }" data-bind="clearable: filter, value: filter, valueUpdate: 'afterkeydown'"/></div>
    </div>
    <div class="assist-flex-fill assist-hdfs-scrollable" data-bind="delayedOverflow">
      <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
        <!-- ko hueSpinner: { spin: loadingMore, overlay: true } --><!-- /ko -->
        <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 22, container: '.assist-hdfs-scrollable', fetchMore: $data.fetchMore.bind($data) }">
          <li class="assist-entry assist-table-link" style="position: relative;" data-bind="appAwareTemplateContextMenu: { template: 'hdfs-context-items', scrollContainer: '.assist-hdfs-scrollable' }, visibleOnHover: { override: contextPopoverVisible, 'selector': '.assist-actions' }">
            <div class="assist-actions table-actions" style="opacity: 0;" >
              <a style="padding: 0 3px;" class="inactive-action" href="javascript:void(0);" data-bind="click: showContextPopover, css: { 'blue': contextPopoverVisible }">
                <i class='fa fa-info' title="${ _('Details') }"></i>
              </a>
            </div>

            <a href="javascript:void(0)" class="assist-entry assist-table-link" data-bind="multiClick: { click: toggleOpen, dblClick: dblClick }, attr: {'title': definition.name }">
              <!-- ko if: definition.type === 'dir' -->
              <i class="fa fa-fw fa-folder-o muted valign-middle"></i>
              <!-- /ko -->
              <!-- ko if: definition.type === 'file' -->
              <i class="fa fa-fw fa-file-o muted valign-middle"></i>
              <!-- /ko -->
              <span draggable="true" data-bind="text: definition.name, draggableText: { text: '\'' + path + '\'', meta: {'type': 'hdfs', 'definition': definition} }"></span>
            </a>
          </li>
        </ul>
        <!-- ko if: !loading() && entries().length === 0 -->
        <ul class="assist-tables">
          <li class="assist-entry"><span class="assist-no-entries"><!-- ko if: filter() -->${_('No results found')}<!-- /ko --><!-- ko ifnot: filter() -->${_('Empty directory')}<!-- /ko --></span></li>
        </ul>
        <!-- /ko -->
      </div>
      <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
      <div class="assist-errors" data-bind="visible: ! loading() && hasErrors()">
        <span>${ _('Error loading contents.') }</span>
      </div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="assist-adls-inner-panel">
    <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
    <!-- ko with: selectedAdlsEntry -->
    <div class="assist-flex-header assist-breadcrumb" >
      <!-- ko if: parent !== null -->
      <a href="javascript: void(0);" data-bind="appAwareTemplateContextMenu: { template: 'hdfs-context-items', scrollContainer: '.assist-adls-scrollable' }, click: function () { huePubSub.publish('assist.selectAdlsEntry', parent); }">
        <i class="fa fa-fw fa-chevron-left"></i>
        <i class="fa fa-fw fa-folder-o"></i>
        <span data-bind="text: definition.name, tooltip: {'title': path, 'placement': 'top' }"></span>
      </a>
      <!-- /ko -->
      <!-- ko if: parent === null -->
      <div>
        <i class="fa fa-fw fa-folder-o"></i>
        <span data-bind="text: path"></span>
      </div>
      <!-- /ko -->
      <!-- ko template: 'assist-adls-header-actions' --><!-- /ko -->
    </div>
    <div class="assist-flex-search">
      <div class="assist-filter"><input class="clearable" type="text" placeholder="${ _('Filter...') }" data-bind="clearable: filter, value: filter, valueUpdate: 'afterkeydown'"/></div>
    </div>
    <div class="assist-flex-fill assist-adls-scrollable" data-bind="delayedOverflow">
      <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
        <!-- ko hueSpinner: { spin: loadingMore, overlay: true } --><!-- /ko -->
        <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 22, container: '.assist-adls-scrollable', fetchMore: $data.fetchMore.bind($data) }">
          <li class="assist-entry assist-table-link" style="position: relative;" data-bind="appAwareTemplateContextMenu: { template: 'hdfs-context-items', scrollContainer: '.assist-adls-scrollable' }, visibleOnHover: { override: contextPopoverVisible, 'selector': '.assist-actions' }">
            <div class="assist-actions table-actions" style="opacity: 0;" >
              <a style="padding: 0 3px;" class="inactive-action" href="javascript:void(0);" data-bind="click: showContextPopover, css: { 'blue': contextPopoverVisible }">
                <i class='fa fa-info' title="${ _('Details') }"></i>
              </a>
            </div>

            <a href="javascript:void(0)" class="assist-entry assist-table-link" data-bind="multiClick: { click: toggleOpen, dblClick: dblClick }, attr: {'title': definition.name }">
              <!-- ko if: definition.type === 'dir' -->
              <i class="fa fa-fw fa-folder-o muted valign-middle"></i>
              <!-- /ko -->
              <!-- ko if: definition.type === 'file' -->
              <i class="fa fa-fw fa-file-o muted valign-middle"></i>
              <!-- /ko -->
              <span draggable="true" data-bind="text: definition.name, draggableText: { text: '\'' + path + '\'', meta: {'type': 'adls', 'definition': definition} }"></span>
            </a>
          </li>
        </ul>
        <!-- ko if: !loading() && entries().length === 0 -->
        <ul class="assist-tables">
          <li class="assist-entry"><span class="assist-no-entries"><!-- ko if: filter() -->${_('No results found')}<!-- /ko --><!-- ko ifnot: filter() -->${_('Empty directory')}<!-- /ko --></span></li>
        </ul>
        <!-- /ko -->
      </div>
      <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
      <div class="assist-errors" data-bind="visible: ! loading() && hasErrors()">
        <span>${ _('Error loading contents.') }</span>
      </div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="assist-document-header-actions">
    <div class="assist-db-header-actions">
      <!-- ko if: !loading() -->
      <div class="highlightable" data-bind="css: { 'highlight': $parent.highlightTypeFilter() }, component: { name: 'hue-drop-down', params: { fixedPosition: true, value: typeFilter, searchable: true, entries: DOCUMENT_TYPES, linkTitle: '${ _ko('Document type') }' } }" style="display: inline-block"></div>
      <!-- /ko -->
      <span class="dropdown new-document-drop-down">

        <a class="inactive-action dropdown-toggle" data-toggle="dropdown" data-bind="dropdown" href="javascript:void(0);">
          <i class="pointer fa fa-plus" title="${ _('New document') }"></i>
        </a>
        <ul class="dropdown-menu less-padding document-types" style="margin-top:3px; margin-left:-140px; width: 175px;position: absolute;" role="menu">
            % if 'beeswax' in apps:
              <li>
                <a title="${_('Hive Query')}"
                % if is_embeddable:
                  data-bind="click: function() { huePubSub.publish('open.editor.new.query', {type: 'hive', 'directoryUuid': $data.getDirectory()}); }" href="javascript:void(0);"
                % else:
                  data-bind="click: function() { $('.new-document-drop-down').removeClass('open');}, hueLink: $data.addDirectoryParamToUrl('${ url('notebook:editor') }?type=hive')"
                % endif
                >
                  <!-- ko template: { name: 'app-icon-template', data: { icon: 'hive' } } --><!-- /ko --> ${_('Hive Query')}
                </a>
              </li>
            % endif
            % if 'impala' in apps:
              <li>
                <a title="${_('Impala Query')}" class="dropdown-item"
                % if is_embeddable:
                  data-bind="click: function() { huePubSub.publish('open.editor.new.query', {type: 'impala', 'directoryUuid': $data.getDirectory()}); }" href="javascript:void(0);"
                % else:
                  data-bind="click: function() { $('.new-document-drop-down').removeClass('open');}, hueLink: $data.addDirectoryParamToUrl('${ url('notebook:editor') }?type=impala')"
                % endif
                >
                  <!-- ko template: { name: 'app-icon-template', data: { icon: 'impala' } } --><!-- /ko --> ${_('Impala Query')}
                </a>
            </li>
            % endif
            <%
            from notebook.conf import SHOW_NOTEBOOKS
            %>
            % if SHOW_NOTEBOOKS.get():
              <li>
                <a title="${_('Notebook')}" data-bind="click: function() { $('.new-document-drop-down').removeClass('open');}, hueLink: $data.addDirectoryParamToUrl('${ url('notebook:index') }')">
                  <!-- ko template: { name: 'app-icon-template', data: { icon: 'notebook' } } --><!-- /ko --> ${_('Notebook')}
                </a>
              </li>
            % endif
            % if 'pig' in apps:
              <li>
                <a title="${_('Pig Script')}" data-bind="click: function() { $('.new-document-drop-down').removeClass('open');}, hueLink: $data.addDirectoryParamToUrl('${ url('pig:index') }')">
                  <!-- ko template: { name: 'app-icon-template', data: { icon: 'pig' } } --><!-- /ko --> ${_('Pig Script')}
                </a>
              </li>
            % endif
            % if 'oozie' in apps:
              <li>
                <a title="${_('Oozie Workflow')}" data-bind="click: function() { $('.new-document-drop-down').removeClass('open');}, hueLink: $data.addDirectoryParamToUrl('${ url('oozie:new_workflow') }')">
                  <!-- ko template: { name: 'app-icon-template', data: { icon: 'oozie-workflow' } } --><!-- /ko --> ${_('Workflow') if is_embeddable else _('Oozie Workflow')}
                </a>
              </li>
              <li>
                <a title="${_('Oozie Schedule')}" data-bind="click: function() { $('.new-document-drop-down').removeClass('open');}, hueLink: $data.addDirectoryParamToUrl('${ url('oozie:new_coordinator') }')">
                  <!-- ko template: { name: 'app-icon-template', data: { icon: 'oozie-coordinator' } } --><!-- /ko --> ${_('Schedule') if is_embeddable else _('Oozie Coordinator')}
                </a>
              </li>
              <li>
                <a title="${_('Oozie Bundle')}" data-bind="click: function() { $('.new-document-drop-down').removeClass('open');}, hueLink: $data.addDirectoryParamToUrl('${ url('oozie:new_bundle') }')">
                  <!-- ko template: { name: 'app-icon-template', data: { icon: 'oozie-bundle' } } --><!-- /ko --> ${_('Bundle') if is_embeddable else _('Oozie Bundle')}
                </a>
              </li>
            % endif
            % if 'search' in apps:
              <li>
                <a title="${_('Solr Search')}" data-bind="click: function() { $('.new-document-drop-down').removeClass('open');}, hueLink: $data.addDirectoryParamToUrl('${ url('search:new_search') }')">
                  <!-- ko template: { name: 'app-icon-template', data: { icon: 'dashboard' } } --><!-- /ko --> ${_('Dashboard')}
                </a>
              </li>
            % endif
            <li class="divider"></li>
            <li data-bind="css: { 'disabled': $data.isTrash() || $data.isTrashed() || !$data.canModify() }">
              <a href="javascript:void(0);" data-bind="click: function () { $('.new-document-drop-down').removeClass('open'); huePubSub.publish('show.create.directory.modal', $data); $data.showNewDirectoryModal()}"><svg class="hi"><use xlink:href="#hi-folder"></use><use xlink:href="#hi-plus-addon"></use></svg> ${_('New folder')}</a>
            </li>
          </ul>
      </span>
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.document.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manual refresh')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-documents-inner-panel">
    <!-- ko with: activeEntry -->
    <div class="assist-flex-header assist-breadcrumb" style="overflow: visible">
      <!-- ko ifnot: isRoot -->
      <a href="javascript: void(0);" data-bind="click: function () { if (loaded()) { parent.makeActive(); } }">
        <i class="fa fa-fw fa-chevron-left"></i>
        <i class="fa fa-fw fa-folder-o"></i>
        <span data-bind="text: definition().name, attr: {'title': definition().name }"></span>
      </a>
      <!-- /ko -->
      <!-- ko if: isRoot -->
      <div>
        <i class="fa fa-fw fa-folder-o"></i>
        <span>/</span>
      </div>
      <!-- /ko -->
      <!-- ko template: 'assist-document-header-actions' --><!-- /ko -->
    </div>
    <div class="assist-flex-search">
      <div class="assist-filter"><input class="clearable" type="text" placeholder="${ _('Filter...') }" data-bind="clearable: filter, value: filter, valueUpdate: 'afterkeydown'"/></div>
    </div>
    <div class="assist-flex-fill assist-file-scrollable" data-bind="delayedOverflow">
      <div data-bind="visible: ! loading() && ! hasErrors() && entries().length > 0">
        <!-- ko if: filteredEntries().length == 0 -->
        <ul class="assist-tables">
          <li class="assist-entry"><span class="assist-no-entries">${_('No documents found')}</span></li>
        </ul>
        <!-- /ko -->
        <ul class="assist-tables" data-bind="foreachVisible: { data: filteredEntries, minHeight: 27, container: '.assist-file-scrollable' }">
          <li class="assist-entry assist-file-entry" data-bind="appAwareTemplateContextMenu: { template: 'document-context-items', scrollContainer: '.assist-file-scrollable', beforeOpen: beforeContextOpen }, assistFileDroppable, assistFileDraggable, visibleOnHover: { 'selector': '.assist-file-actions' }">
            <div class="assist-file-actions table-actions">
              <a class="inactive-action" href="javascript:void(0)" data-bind="click: showContextPopover, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${_('Show details')}"></i></a>
            </div>
            <a href="javascript:void(0)" class="assist-entry assist-document-link" data-bind="click: open, attr: {'title': name }">
              <!-- ko template: { name: 'document-icon-template', data: { document: $data, showShareAddon: false } } --><!-- /ko -->
              <span class="highlightable" data-bind="css: { 'highlight': highlight }, text: definition().name"></span>
            </a>
          </li>
        </ul>
      </div>
      <div data-bind="visible: !loading() && ! hasErrors() && entries().length === 0">
        <span class="assist-no-entries">${_('Empty directory')}</span>
      </div>
      <div class="center" data-bind="visible: loading() && ! hasErrors()">
        <i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i>
      </div>
      <div class="assist-errors" data-bind="visible: ! loading() && hasErrors()">
        <span>${ _('Error loading contents.') }</span>
      </div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="assist-hbase-header-actions">
    <div class="assist-db-header-actions">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.hbase.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manual refresh')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-hbase-inner-panel">
    <!-- ko with: selectedHBaseEntry -->
    <div class="assist-inner-header assist-breadcrumb" >
      <!-- ko if: definition.host !== '' -->
      <a href="javascript: void(0);" data-bind="click: function () { huePubSub.publish('assist.clickHBaseRootItem'); }">
        <i class="fa fa-fw fa-chevron-left"></i>
        <i class="fa fa-fw fa-th-large"></i>
        <span data-bind="text: definition.name"></span>
      </a>
      <!-- /ko -->
      <!-- ko if: definition.host === '' -->
      ${_('Clusters')}
      <!-- /ko -->

      <!-- ko template: 'assist-hbase-header-actions' --><!-- /ko -->
    </div>
    <div class="assist-flex-fill assist-hbase-scrollable" data-bind="delayedOverflow">
      <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
        <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 22, container: '.assist-hbase-scrollable' }">
          <li class="assist-entry assist-table-link" style="position: relative;" data-bind="appAwareTemplateContextMenu: { template: 'hbase-context-items', scrollContainer: '.assist-hbase-scrollable' }, visibleOnHover: { 'selector': '.assist-actions' }">
            <a href="javascript:void(0)" class="assist-entry assist-table-link" data-bind="multiClick: { click: click, dblClick: dblClick }, attr: {'title': definition.name }">
              <!-- ko if: definition.host -->
              <i class="fa fa-fw fa-th-large muted valign-middle"></i>
              <!-- /ko -->
              <!-- ko ifnot: definition.host -->
              <i class="fa fa-fw fa-th muted valign-middle"></i>
              <!-- /ko -->
              <span draggable="true" data-bind="text: definition.name, draggableText: { text: '\'' + definition.name + '\'', meta: {'type': 'collection', 'definition': definition} }"></span>
            </a>
          </li>
        </ul>
        <!-- ko if: !loading() && entries().length === 0 -->
        <ul class="assist-tables">
          <li class="assist-entry">
            <span class="assist-no-entries">
            <!-- ko if: definition.host === '' -->
            ${_('No clusters available.')}
            <!-- /ko -->
            <!-- ko if: definition.host !== '' -->
            ${_('No tables available.')}
            <!-- /ko -->
            </span>
          </li>
        </ul>
        <!-- /ko -->
      </div>
      <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
      <div class="assist-errors" data-bind="visible: ! loading() && hasErrors()">
        <span>${ _('Error loading contents.') }</span>
      </div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="ask-for-invalidate-title">
    &nbsp;<a class="pull-right pointer close-popover inactive-action">&times;</a>
  </script>

  <script type="text/html" id="ask-for-invalidate-content">
    <label class="radio">
      <input type="radio" name="refreshImpala" value="cache" data-bind="checked: invalidateOnRefresh" />
      ${ _('Clear cache') }
    </label>
    <label class="radio">
      <input type="radio" name="refreshImpala" value="invalidate" data-bind="checked: invalidateOnRefresh" />
      ${ _('Perform incremental metadata update.') }
    </label>
    <div class="assist-invalidate-description">${ _('This will sync missing tables.') }</div>
    <label class="radio">
      <input type="radio" name="refreshImpala" value="invalidateAndFlush" data-bind="checked: invalidateOnRefresh"  />
      ${ _('Invalidate all metadata and rebuild index.') }
    </label>
    <div class="assist-invalidate-description">${ _('WARNING: This can be both resource and time-intensive.') }</div>
    <div style="width: 100%; display: inline-block; margin-top: 5px;"><button class="pull-right btn btn-primary" data-bind="css: { 'btn-primary': invalidateOnRefresh() !== 'invalidateAndFlush', 'btn-danger': invalidateOnRefresh() === 'invalidateAndFlush' }, click: function (data, event) { huePubSub.publish('close.popover'); triggerRefresh(data, event); }, clickBubble: false">${ _('Refresh') }</button></div>
  </script>

  <script type="text/html" id="assist-namespace-header-actions">
    <div class="assist-db-header-actions">
      <!-- ko ifnot: loading -->
      <span class="assist-tables-counter">(<span data-bind="text: filteredNamespaces().length"></span>)</span>
      <!-- ko if: window.HAS_MULTI_CLUSTER -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: triggerRefresh"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Refresh')}"></i></a>
      <!-- /ko -->
      <!-- /ko -->
      <!-- ko if: loading -->
      <i class="fa fa-refresh fa-spin blue" title="${_('Refresh')}"></i>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="assist-db-header-actions">
    <div class="assist-db-header-actions">
      <!-- ko ifnot: loading -->
      <span class="assist-tables-counter">(<span data-bind="text: filteredEntries().length"></span>)</span>
      % if hasattr(ENABLE_NEW_CREATE_TABLE, 'get') and ENABLE_NEW_CREATE_TABLE.get() and not IS_EMBEDDED.get():
        <!-- ko if: sourceType === 'hive' || sourceType === 'impala' -->
        <!-- ko if: typeof databaseName !== 'undefined' -->
          <a class="inactive-action" data-bind="hueLink: '${ url('indexer:importer_prefill', source_type='all', target_type='table') }' + databaseName + '/?sourceType=' + sourceType + '&namespace=' + assistDbNamespace.namespace.id" title="${_('Create table')}" href="javascript:void(0)">
            <i class="pointer fa fa-plus" title="${_('Create table')}"></i>
          </a>
        <!-- /ko -->
        <!-- ko if: typeof databases !== 'undefined' -->
          <a class="inactive-action" data-bind="hueLink: '${ url('indexer:importer_prefill', source_type='manual', target_type='database') }' + '/?sourceType=' + sourceType + '&namespace=' + namespace.id" href="javascript:void(0)">
            <i class="pointer fa fa-plus" title="${ _('Create database') }"></i>
          </a>
        <!-- /ko -->
        <!-- /ko -->
      % endif
      <!-- ko if: sourceType === 'solr' -->
      <a class="inactive-action" data-bind="hueLink: '/indexer/importer/prefill/all/index/'" title="${_('Create index')}">
        <i class="pointer fa fa-plus" title="${_('Create index')}"></i>
      </a>
      <!-- /ko -->
      <!-- ko if: sourceType === 'impala' -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="templatePopover : { contentTemplate: 'ask-for-invalidate-content', titleTemplate: 'ask-for-invalidate-title', trigger: 'click', minWidth: '320px' }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Refresh')}"></i></a>
      <!-- /ko -->
      <!-- ko if: sourceType !== 'impala' -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: triggerRefresh"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Refresh')}"></i></a>
      <!-- /ko -->
      <!-- /ko -->
      <!-- ko if: loading -->
      <i class="fa fa-refresh fa-spin blue" title="${_('Refresh')}"></i>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="assist-sources-template">
    <div class="assist-flex-header">
      <div class="assist-inner-header">
        ${_('Sources')}
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
        ${_('Namespaces')}
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
        <li class="assist-entry no-entries">${_('No results found')}</li>
      </ul>
      <!-- /ko -->
      <ul class="assist-tables" data-bind="foreach: filteredNamespaces">
        <li class="assist-table">
          <!-- ko if: status() === 'STARTING' -->
          <span class="assist-table-link" title="${_('Starting')}" data-bind="tooltip: { placement: 'bottom' }"><i class="fa fa-fw fa-spinner fa-spin muted valign-middle"></i> <span data-bind="text: name"></span></span>
          <!-- /ko -->
          <!-- ko if: status() !== 'STARTING' -->
          <!-- ko if: namespace.computes.length -->
          <a class="assist-table-link" href="javascript: void(0);" data-bind="click: function () { $parent.selectedNamespace($data); }"><i class="fa fa-fw fa-snowflake-o muted valign-middle"></i> <span data-bind="text: name"></span></a>
          <!-- /ko -->
          <!-- ko ifnot: namespace.computes.length -->
          <span class="assist-table-link" title="${_('No related computes')}" data-bind="tooltip: { placement: 'bottom' }"><i class="fa fa-fw fa-warning muted valign-middle"></i> <span data-bind="text: name"></span></span>
          <!-- /ko -->
          <!-- /ko -->
        </li>
      </ul>
    </div>
    <div class="assist-flex-fill" data-bind="visible: loading">
      <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
    </div>
    <div class="assist-flex-fill" data-bind="visible: hasErrors() && !loading()">
      <span class="assist-errors">${ _('Error loading namespaces.') }</span>
    </div>
    <div class="assist-flex-fill" data-bind="visible: !hasErrors() && !loading() && !hasNamespaces()">
      <span class="assist-errors">${ _('No namespaces found.') }</span>
    </div>
  </script>

  <script type="text/html" id="assist-databases-template">
    <div class="assist-flex-header" data-bind="visibleOnHover: { selector: '.hover-actions', override: loading() }">
      <div class="assist-inner-header">
        <!-- ko ifnot: sourceType === 'solr' || sourceType === 'kafka' -->
        ${_('Databases')}
        <!-- ko template: 'assist-db-header-actions' --><!-- /ko -->
        <!-- /ko -->
        <!-- ko if: sourceType === 'solr' || sourceType === 'kafka'-->
        ${_('Sources')}
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
              placeHolder: sourceType === 'solr' || sourceType === 'kafka' ? '${_('Filter sources...')}' : '${_('Filter databases...')}',
              knownFacetValues: {},
              autocompleteFromEntries: autocompleteFromEntries
            }
          } --><!-- /ko -->
      </div>
    </div>
    <div class="assist-flex-fill assist-db-scrollable" data-bind="visible: ! hasErrors() && ! loading() && hasEntries(), delayedOverflow">
      <!-- ko if: ! loading() && filteredEntries().length == 0 -->
      <ul class="assist-tables">
        <li class="assist-entry no-entries">${_('No results found')}</li>
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
      <span class="assist-errors">${ _('Error loading databases.') }</span>
    </div>
    <div class="assist-flex-fill" data-bind="visible: ! hasErrors() && ! loading() && ! hasEntries()">
      <span class="assist-errors">${ _('No databases found.') }</span>
    </div>
  </script>

  <script type="text/html" id="assist-tables-template">
    <div class="assist-flex-header">
      <div class="assist-inner-header" data-bind="visible: !$parent.loading() && !$parent.hasErrors()">
        <!-- ko ifnot: sourceType === 'solr' || sourceType === 'kafka' -->
          ${_('Tables')}
        <!-- /ko -->
        <!-- ko if: sourceType === 'solr' -->
          <div data-bind="appAwareTemplateContextMenu: { template: 'collection-title-context-items', scrollContainer: '.assist-db-scrollable' }">${_('Indexes')}</div>
        <!-- /ko -->
        <!-- ko if: sourceType === 'kafka' -->
          ${_('Topics')}
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
      <span class="assist-errors">${ _('Error loading tables.') }</span>
    </div>
  </script>

  <script type="text/html" id="assist-panel-inner-header">
    <div class="assist-header assist-fixed-height" data-bind="visibleOnHover: { selector: '.assist-header-actions' }, css: { 'assist-resizer': $index() > 0 }" style="display:none;">
      <span data-bind="text: $parent.name"></span>
      <div class="assist-header-actions">
        <div class="inactive-action" data-bind="click: function () { $parent.visible(false) }"><i class="fa fa-times"></i></div>
      </div>
    </div>
  </script>

  <script type="text/html" id="assist-panel-template">
    <div class="assist-panel" data-bind="dropzone: { url: '/filebrowser/upload/file?dest=' + DROPZONE_HOME_DIR, params: {dest: DROPZONE_HOME_DIR}, clickable: false, paramName: 'hdfs_file', onComplete: function(path){ huePubSub.publish('assist.dropzone.complete', path); }, disabled: '${ not (hasattr(SHOW_UPLOAD_BUTTON, 'get') and SHOW_UPLOAD_BUTTON.get()) }' === 'True' }">
      <!-- ko if: availablePanels().length > 1 -->
      <div class="assist-panel-switches">
        <!-- ko foreach: availablePanels -->
        <div class="inactive-action assist-type-switch" data-bind="click: function () { $parent.visiblePanel($data); }, css: { 'blue': $parent.visiblePanel() === $data }, style: { 'float': rightAlignIcon ? 'right' : 'left' },  attr: { 'title': name }">
          <!-- ko if: iconSvg --><span style="font-size:22px;"><svg class="hi"><use data-bind="attr: {'xlink:href': iconSvg }" xlink:href=''></use></svg></span><!-- /ko -->
          <!-- ko if: !iconSvg --><i class="fa fa-fw valign-middle" data-bind="css: icon"></i><!-- /ko -->
        </div>
        <!-- /ko -->
      </div>
      <!-- /ko -->
      <!-- ko with: visiblePanel -->
      <div class="assist-panel-contents" data-bind="style: { 'padding-top': $parent.availablePanels().length > 1 ? '10px' : '5px' }">
        <div class="assist-inner-panel">
          <div class="assist-flex-panel">
            <!-- ko template: { name: templateName, data: panelData } --><!-- /ko -->
          </div>
        </div>
      </div>
      <!-- /ko -->
    </div>
  </script>

  <div class="assist-file-entry-drag">
    <span class="drag-text"></span>
  </div>

  <script type="text/javascript">

    var SQL_ASSIST_KNOWN_FACET_VALUES = {
      'type': {'array': -1, 'table': -1, 'view': -1, 'boolean': -1, 'bigint': -1, 'binary': -1, 'char': -1, 'date': -1, 'double': -1, 'decimal': -1, 'float': -1, 'int': -1, 'map': -1, 'real': -1, 'smallint': -1, 'string': -1, 'struct': -1, 'timestamp': -1, 'tinyint': -1, 'varchar': -1 }
    };

    var SOLR_ASSIST_KNOWN_FACET_VALUES = {
      'type': {'date': -1, 'tdate': -1, 'timestamp': -1, 'pdate': -1, 'int': -1, 'tint': -1, 'pint': -1, 'long': -1, 'tlong': -1, 'plong': -1, 'float': -1, 'tfloat': -1, 'pfloat': -1, 'double': -1, 'tdouble': -1, 'pdouble': -1, 'currency': -1, 'smallint': -1, 'bigint': -1, 'tinyint': -1, 'SpatialRecursivePrefixTreeFieldType': -1, 'string': -1, 'boolean': -1 }
    };


    (function () {

      var NAV_FACET_ICON = 'fa-tags';
      var NAV_TYPE_ICONS = {
        'DATABASE': 'fa-database',
        'TABLE': 'fa-table',
        'VIEW': 'fa-eye',
        'FIELD': 'fa-columns',
        'PARTITION': 'fa-th',
        'SOURCE': 'fa-server',
        'OPERATION': 'fa-cogs',
        'OPERATION_EXECUTION': 'fa-cog',
        'DIRECTORY': 'fa-folder-o',
        'FILE': 'fa-file-o',
        'S3BUCKET': 'fa-cubes',
        'SUB_OPERATION': 'fa-code-fork',
        'COLLECTION': 'fa-search',
        'HBASE': 'fa-th-large',
        'HUE': 'fa-file-o'
      };

      /**
       * @param {Object} params
       * @param {string} params.user
       * @param {boolean} params.onlySql - For the old query editors
       * @param {string[]} params.visibleAssistPanels - Panels that will initially be shown regardless of total storage
       * @param {Object} params.sql
       * @param {Object[]} params.sql.sourceTypes - All the available SQL source types
       * @param {string} params.sql.sourceTypes[].name - Example: Hive SQL
       * @param {string} params.sql.sourceTypes[].type - Example: hive
       * @param {string} [params.sql.activeSourceType] - Example: hive
       * @param {Object} params.sql.navigationSettings - enable/disable the links
       * @param {boolean} params.sql.navigationSettings.openItem - Example: true
       * @param {boolean} params.sql.navigationSettings.showStats - Example: true
       * @constructor
       */
      function AssistPanel (params) {
        var self = this;
        var i18n = {
          errorLoadingDatabases: "${ _('There was a problem loading the databases') }",
          errorLoadingTablePreview: "${ _('There was a problem loading the table preview') }"
        };
        var i18nCollections = {
          errorLoadingDatabases: "${ _('There was a problem loading the indexes') }",
          errorLoadingTablePreview: "${ _('There was a problem loading the index preview') }"
        };

        self.tabsEnabled = '${ USE_NEW_SIDE_PANELS.get() }' === 'True';

        self.availablePanels = ko.observableArray();
        self.visiblePanel = ko.observable();

        self.lastOpenPanelType = ko.observable();
        window.apiHelper.withTotalStorage('assist', 'last.open.panel', self.lastOpenPanelType);

        huePubSub.subscribeOnce('cluster.config.set.config', function (clusterConfig) {
          if (clusterConfig && clusterConfig['app_config']) {
            var panels = [];
            var appConfig = clusterConfig['app_config'];

            if (appConfig['editor']) {
              var sqlPanel = new AssistInnerPanel({
                panelData: new AssistDbPanel($.extend({
                  i18n: i18n
                }, params.sql)),
                name: '${ _("SQL") }',
                type: 'sql',
                icon: 'fa-database',
                minHeight: 75
              });
              panels.push(sqlPanel);

              huePubSub.subscribe('assist.show.sql', function () {
                if (self.visiblePanel() !== sqlPanel) {
                  self.visiblePanel(sqlPanel);
                }
              });
            }

            if (self.tabsEnabled) {

              if (appConfig['browser'] && appConfig['browser']['interpreter_names'].indexOf('hdfs') != -1) {
                panels.push(new AssistInnerPanel({
                  panelData: new AssistHdfsPanel({}),
                  name: '${ _("HDFS") }',
                  type: 'hdfs',
                  icon: 'fa-files-o',
                  minHeight: 50
                }));
              }

              if (appConfig['browser'] && appConfig['browser']['interpreter_names'].indexOf('s3') != -1) {
                panels.push(new AssistInnerPanel({
                  panelData: new AssistS3Panel({}),
                  name: '${ _("S3") }',
                  type: 's3',
                  icon: 'fa-cubes',
                  minHeight: 50
                }));
              }

              if (appConfig['browser'] && appConfig['browser']['interpreter_names'].indexOf('adls') != -1) {
                panels.push(new AssistInnerPanel({
                  panelData: new AssistAdlsPanel({}),
                  name: '${ _("ADLS") }',
                  type: 'adls',
                  icon: 'fa-windows',
                  iconSvg: '#hi-adls',
                  minHeight: 50
                }));
              }

              if (appConfig['browser'] && appConfig['browser']['interpreter_names'].indexOf('indexes') != -1) {
                var solrPanel = new AssistInnerPanel({
                  panelData: new AssistDbPanel($.extend({
                    i18n: i18nCollections,
                    isSolr: true
                  }, params.sql)),
                  name: '${ _("Indexes") }',
                  type: 'solr',
                  icon: 'fa-search-plus',
                  minHeight: 75
                });
                panels.push(solrPanel);
                huePubSub.subscribe('assist.show.solr', function () {
                  if (self.visiblePanel() !== solrPanel) {
                    self.visiblePanel(solrPanel);
                  }
                });
              }

              if (appConfig['browser'] && appConfig['browser']['interpreter_names'].indexOf('kafka') != -1) {
                var streamsPanel = new AssistInnerPanel({
                  panelData: new AssistDbPanel($.extend({
                    i18n: i18nCollections,
                    isStreams: true
                  }, params.sql)),
                  name: '${ _("Streams") }',
                  type: 'kafka',
                  icon: 'fa-sitemap',
                  minHeight: 75
                });
                panels.push(streamsPanel);
              }

              if (appConfig['browser'] && appConfig['browser']['interpreter_names'].indexOf('hbase') != -1) {
                panels.push(new AssistInnerPanel({
                  panelData: new AssistHBasePanel({}),
                  name: '${ _("HBase") }',
                  type: 'hbase',
                  icon: 'fa-th-large',
                  minHeight: 50
                }));
              }

              % if not IS_EMBEDDED.get():
              var documentsPanel = new AssistInnerPanel({
                panelData: new AssistDocumentsPanel({
                  user: params.user
                }),
                name: '${ _("Documents") }',
                type: 'documents',
                icon: 'fa-files-o',
                iconSvg: '#hi-documents',
                minHeight: 50,
                rightAlignIcon: true,
                visible: params.visibleAssistPanels && params.visibleAssistPanels.indexOf('documents') !== -1
              });

              panels.push(documentsPanel);

              huePubSub.subscribe('assist.show.documents', function (docType) {
                huePubSub.publish('left.assist.show');
                if (self.visiblePanel() !== documentsPanel) {
                  self.visiblePanel(documentsPanel);
                }
                if (docType) {
                  documentsPanel.panelData.setTypeFilter(docType);
                }
              });
              % endif

              var vcsKeysLength = ${ len(VCS.keys()) };
              if (vcsKeysLength > 0) {
                panels.push(new AssistInnerPanel({
                  panelData: new AssistGitPanel({}),
                  name: '${ _("Git") }',
                  type: 'git',
                  icon: 'fa-github',
                  minHeight: 50,
                  rightAlignIcon: true
                }));
              }

            }

            self.availablePanels(panels);
          } else {
            self.availablePanels([new AssistInnerPanel({
              panelData: new AssistDbPanel($.extend({
                i18n: i18n
              }, params.sql)),
              name: '${ _("SQL") }',
              type: 'sql',
              icon: 'fa-database',
              minHeight: 75
            })]);
          }

          if (!self.lastOpenPanelType()) {
            self.lastOpenPanelType(self.availablePanels()[0].type);
          }

          var lastFoundPanel = self.availablePanels().filter(function (panel) { return panel.type === self.lastOpenPanelType() });

          // always forces the db panel to load
          var dbPanel = self.availablePanels().filter(function (panel) { return panel.type === 'sql' });
          if (dbPanel.length > 0) {
            dbPanel[0].panelData.init();
          }

          self.visiblePanel.subscribe(function(newValue) {
            self.lastOpenPanelType(newValue.type);
            if (newValue.type !== 'sql' && !newValue.panelData.initialized) {
              newValue.panelData.init();
            }
          });

          self.visiblePanel(lastFoundPanel.length === 1 ? lastFoundPanel[0] : self.availablePanels()[0]);
        });

        window.setTimeout(function () {
          // Main initialization trigger in hue.mako, this is for Hue 3
          if (self.availablePanels().length === 0) {
            huePubSub.publish('cluster.config.get.config');
          }
        }, 0);
      }

      ko.components.register('assist-panel', {
        viewModel: AssistPanel,
        template: { element: 'assist-panel-template' }
      });
    })();
  </script>

  <script type="text/html" id="language-reference-topic-tree">
    <!-- ko if: $data.length -->
    <ul class="assist-docs-topic-tree " data-bind="foreach: $data">
      <li>
        <a class="black-link" href="javascript: void(0);" data-bind="click: function () { $component.selectedTopic($data); }, toggle: open">
          <i class="fa fa-fw" style="font-size: 12px;" data-bind="css: { 'fa-chevron-right': children.length && !open(), 'fa-chevron-down': children.length && open() }"></i>
          <span class="assist-field-link" href="javascript: void(0);" data-bind="css: { 'blue': $component.selectedTopic() === $data }, text: title"></span>
        </a>
        <!-- ko if: open -->
        <!-- ko template: { name: 'language-reference-topic-tree', data: children } --><!-- /ko -->
        <!-- /ko -->
      </li>
    </ul>
    <!-- /ko -->
  </script>

  <script type="text/html" id="language-reference-panel-template">
    <div class="assist-inner-panel">
      <div class="assist-flex-panel">
        <div class="assist-flex-header">
          <div class="assist-inner-header">
            <div class="function-dialect-dropdown" data-bind="component: { name: 'hue-drop-down', params: { fixedPosition: true, value: sourceType, entries: availableTypes, linkTitle: '${ _ko('Selected dialect') }' } }" style="display: inline-block"></div>
          </div>
        </div>
        <div class="assist-flex-search">
          <div class="assist-filter">
            <input class="clearable" type="text" placeholder="Filter..." data-bind="clearable: query, value: query, valueUpdate: 'afterkeydown'">
          </div>
        </div>
        <div class="assist-docs-topics" data-bind="css: { 'assist-flex-fill': !selectedTopic(), 'assist-flex-40': selectedTopic() }">
          <!-- ko ifnot: query -->
          <!-- ko template: { name: 'language-reference-topic-tree', data: topics } --><!-- /ko -->
          <!-- /ko -->
          <!-- ko if: query -->
          <!-- ko if: filteredTopics().length > 0 -->
          <ul class="assist-docs-topic-tree" data-bind="foreach: filteredTopics">
            <li>
              <a class="assist-field-link" href="javascript: void(0);" data-bind="css: { 'blue': $component.selectedTopic() === $data }, click: function () { $component.selectedTopic($data); }, html: titleMatch() || title"></a>
            </li>
          </ul>
          <!-- /ko -->
          <!-- ko if: filteredTopics().length === 0 -->
          <ul class="assist-docs-topic-tree">
            <li class="assist-no-entries">${ _('No matches found. ') }</li>
          </ul>
          <!-- /ko -->
          <!-- /ko -->
        </div>
        <!-- ko if: selectedTopic -->
        <div class="assist-flex-60 assist-docs-details" data-bind="with: selectedTopic">
          <div class="assist-panel-close"><button class="close" data-bind="click: function() { $component.selectedTopic(undefined); }">&times;</button></div>
          <div data-bind="html: bodyMatch() || body()"></div>
        </div>
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/html" id="functions-panel-template">
    <div class="assist-inner-panel">
      <div class="assist-flex-panel">
        <div class="assist-flex-header">
          <div class="assist-inner-header">
            <div class="function-dialect-dropdown" data-bind="component: { name: 'hue-drop-down', params: { fixedPosition: true, value: activeType, entries: availableTypes, linkTitle: '${ _ko('Selected dialect') }' } }" style="display: inline-block"></div>
          </div>
        </div>
        <div class="assist-flex-search">
          <div class="assist-filter">
            <input class="clearable" type="text" placeholder="Filter..." data-bind="clearable: query, value: query, valueUpdate: 'afterkeydown'">
          </div>
        </div>
        <div data-bind="css: { 'assist-flex-fill': !selectedFunction(), 'assist-flex-half': selectedFunction() }">
          <!-- ko ifnot: query -->
          <ul class="assist-function-categories" data-bind="foreach: activeCategories">
            <li>
              <a class="black-link" href="javascript: void(0);" data-bind="toggle: open"><i class="fa fa-fw" data-bind="css: { 'fa-chevron-right': !open(), 'fa-chevron-down': open }"></i> <span data-bind="text: name"></span></a>
              <ul class="assist-functions" data-bind="slideVisible: open, foreach: functions">
                <li data-bind="tooltip: { title: description, placement: 'left', delay: 1000 }">
                  <a class="assist-field-link" href="javascript: void(0);" data-bind="draggableText: { text: draggable, meta: { type: 'function' } }, css: { 'blue': $parents[1].selectedFunction() === $data }, multiClick: { click: function () { $parents[1].selectedFunction($data); }, dblClick: function () { huePubSub.publish('editor.insert.at.cursor', draggable); } }, text: signature"></a>
                </li>
              </ul>
            </li>
          </ul>
          <!-- /ko -->
          <!-- ko if: query -->
          <!-- ko if: filteredFunctions().length > 0 -->
          <ul class="assist-functions" data-bind="foreach: filteredFunctions">
            <li data-bind="tooltip: { title: description, placement: 'left', delay: 1000 }">
              <a class="assist-field-link" href="javascript: void(0);" data-bind="draggableText: { text: draggable, meta: { type: 'function' } }, css: { 'blue': $parent.selectedFunction() === $data }, multiClick: { click: function () { $parent.selectedFunction($data); }, dblClick: function () { huePubSub.publish('editor.insert.at.cursor', draggable); } }, html: signatureMatch"></a>
            </li>
          </ul>
          <!-- /ko -->
          <!-- ko if: filteredFunctions().length === 0 -->
          <ul class="assist-functions">
            <li class="assist-no-entries">${ _('No functions found. ') }</li>
          </ul>
          <!-- /ko -->
          <!-- /ko -->
        </div>
        <!-- ko if: selectedFunction -->
        <div class="assist-flex-half assist-function-details" data-bind="with: selectedFunction">
          <div class="assist-panel-close"><button class="close" data-bind="click: function() { $parent.selectedFunction(null); }">&times;</button></div>
          <div class="assist-function-signature blue" data-bind="draggableText: { text: draggable, meta: { type: 'function' } }, text: signature, event: { 'dblclick': function () { huePubSub.publish('editor.insert.at.cursor', draggable); } }"></div>
          <!-- ko if: description -->
          <div data-bind="html: descriptionMatch"></div>
          <!-- /ko -->
        </div>
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      ${ sqlDocIndex.sqlDocIndex() }
      ${ sqlDocIndex.sqlDocTopLevel() }

      var LanguageReferenceTopic = function (entry, index) {
        var self = this;
        self.ref = entry.ref;
        self.title = entry.title;
        self.index = index;
        self.weight = 1;
        self.children = [];
        entry.children.forEach(function (child) {
          self.children.push(new LanguageReferenceTopic(child, self.index));
        });
        self.loadDeferred = $.Deferred();
        self.loading = ko.observable(false);
        self.body = ko.observable();
        self.bodyMatch = ko.observable();
        self.open = ko.observable(false);
        self.titleMatch = ko.observable();
      };

      LanguageReferenceTopic.prototype.load = function () {
        var self = this;
        if (self.body() || self.loading()) {
          return self.loadDeferred.promise();
        }
        self.loading(true);
        window.apiHelper.simpleGet(self.index[self.ref]).done(function (doc) {
          self.body(doc.body);
        }).always(function () {
          self.loading(false);
          self.loadDeferred.resolve(self);
        });
        return self.loadDeferred.promise();
      };

      function LanguageReferencePanel (params, element) {
        var self = this;
        self.disposals = [];

        self.availableTypes = ['impala', 'hive'];

        self.sourceType = ko.observable('hive');

        self.allTopics = {
          impala: [],
          hive: []
        };
        window.IMPALA_DOC_TOP_LEVEL.forEach(function (topLevelItem) {
          self.allTopics.impala.push(new LanguageReferenceTopic(topLevelItem, window.IMPALA_DOC_INDEX));
        });
        window.HIVE_DOC_TOP_LEVEL.forEach(function (topLevelItem) {
          self.allTopics.hive.push(new LanguageReferenceTopic(topLevelItem, window.HIVE_DOC_INDEX));
        });

        var updateType = function (type) {
          if (self.availableTypes.indexOf(type) !== -1) {
            self.sourceType(type);
          }
        };

        var activeSnippetTypeSub = huePubSub.subscribe('active.snippet.type.changed', function (details) { updateType(details.type) });

        self.disposals.push(function () {
          activeSnippetTypeSub.remove();
        });

        huePubSub.subscribeOnce('set.active.snippet.type', updateType);
        huePubSub.publish('get.active.snippet.type');

        self.topics = ko.pureComputed(function () {
          return self.allTopics[self.sourceType()];
        });

        self.selectedTopic = ko.observable();

        var selectedSub = self.selectedTopic.subscribe(function (newTopic) {
          if (newTopic) {
            newTopic.load();
          }
        });

        self.disposals.push(function () {
          selectedSub.dispose();
        });
        self.query = ko.observable().extend({ throttle: 200 });
        self.filteredTopics = ko.observableArray();

        var sortFilteredTopics = function () {
          self.filteredTopics.sort(function (a, b) {
            if (a.weight !== b.weight) {
              return b.weight - a.weight;
            }
            return a.title.localeCompare(b.title);
          });
        };

        self.query.subscribe(function (newVal) {
          if (!newVal) {
            return;
          }
          var lowerCaseQuery = self.query().toLowerCase();
          var replaceRegexp = new RegExp('(' + lowerCaseQuery + ')', 'i');
          self.filteredTopics([]);
          var promises = [];

          var sortTimeout = -1;

          var findInside = function (topic) {
            promises.push(topic.load().done(function (loadedTopic) {
              var match = false;
              var titleIndex = loadedTopic.title.toLowerCase().indexOf(lowerCaseQuery);
              if (titleIndex !== -1) {
                loadedTopic.weight = titleIndex === 0 ? 2 : 1;
                loadedTopic.titleMatch(loadedTopic.title.replace(new RegExp('(' + lowerCaseQuery + ')', 'i'), '<b>$1</b>'));
                loadedTopic.bodyMatch(undefined);
                self.filteredTopics.push(loadedTopic);
                match = true;
              } else if (loadedTopic.body() && loadedTopic.body().toLowerCase().indexOf(lowerCaseQuery) !== -1) {
                loadedTopic.weight = 0;
                loadedTopic.titleMatch(undefined);
                loadedTopic.bodyMatch(loadedTopic.body().replace(replaceRegexp, '<b>$1</b>'));
                self.filteredTopics.push(loadedTopic);
                match = true;
              } else {
                loadedTopic.titleMatch(undefined);
                loadedTopic.bodyMatch(undefined);
              }
              if (match) {
                window.clearTimeout(sortTimeout);
                sortTimeout = window.setTimeout(sortFilteredTopics, 100);
              }
            }));

            topic.children.forEach(findInside);
          };

          self.topics.forEach(findInside);

          window.setTimeout(function () {
            // Initial sort deferred for promises to complete
            sortFilteredTopics();
          }, 0);

        });

        var selectedTopicSub = self.selectedTopic.subscribe(function () {
          $(element).find('.assist-docs-details').scrollTop(0);
        });

        var querySub = self.query.subscribe(function () {
          $(element).find('.assist-docs-topics').scrollTop(0);
        });

        var scrollToSelectedTopic = function () {
          var topics = $(element).find('.assist-docs-topics');
          if (topics.find('.blue').length) {
            topics.scrollTop(Math.min(topics.scrollTop() + topics.find('.blue').position().top - 20, topics.find('> ul').height() - topics.height()));
          }
        };

        var scrollToAnchor = function (anchorId) {
          if (!anchorId) {
            return;
          }
          var detailsPanel = $(element).find('.assist-docs-details');
          var found = detailsPanel.find('#' + anchorId.split('/').join(' #'));
          if (found.length) {
            detailsPanel.scrollTop(found.position().top - 10);
          }
        };

        huePubSub.subscribe('scroll.test', scrollToSelectedTopic);

        var showTopicSub = huePubSub.subscribe('assist.lang.ref.panel.show.topic', function (targetTopic) {
          var topicStack = [];
          var findTopic = function (topics) {
            topics.some(function (topic) {
              topicStack.push(topic);
              if (topic.ref === targetTopic.ref) {
                while (topicStack.length) {
                  topicStack.pop().open(true);
                }
                self.query('');
                self.selectedTopic(topic);
                window.setTimeout(function () {
                  scrollToAnchor(targetTopic.anchorId);
                  scrollToSelectedTopic();
                }, 0);
                return true;
              } else if (topic.children.length) {
                var inChild = findTopic(topic.children);
                if (inChild) {
                  return true;
                }
              }
              topicStack.pop();
            })
          };
          findTopic(self.topics());
        });

        $(element).on('click.langref', function (event) {
          if (event.target.className === 'hue-doc-internal-link') {
            huePubSub.publish('assist.lang.ref.panel.show.topic', {
              ref: $(event.target).data('doc-ref'),
              anchorId: $(event.target).data('doc-anchor-id')
            });
          }
        });

        self.disposals.push(function () {
          selectedTopicSub.dispose();
          querySub.dispose();
          showTopicSub.remove();
          $(element).off('click.langref');
        });
      }

      LanguageReferencePanel.prototype.dispose = function () {
        var self = this;
        while (self.disposals.length) {
          self.disposals.pop()();
        }
      };

      ko.components.register('language-reference-panel', {
        viewModel: {
          createViewModel: function(params, componentInfo) {
            return new LanguageReferencePanel(params, componentInfo.element)
          }
        },
        template: { element: 'language-reference-panel-template' }
      });

      function FunctionsPanel(params) {
        var self = this;
        self.categories = {};
        self.disposals = [];

        self.activeType = ko.observable();
        self.availableTypes = ko.observableArray(window.IS_EMBEDDED ? ['Impala'] : ['Hive', 'Impala', 'Pig']);
        self.query = ko.observable().extend({ rateLimit: 400 });
        self.selectedFunction = ko.observable();

        self.availableTypes().forEach(function (type) {
          self.initFunctions(type);
        });

        var selectedFunctionPerType = { 'Hive': null, 'Impala': null, 'Pig': null };
        self.selectedFunction.subscribe(function (newFunction) {
          if (newFunction) {
            selectedFunctionPerType[self.activeType()] = newFunction;
            if (!newFunction.category.open()) {
              newFunction.category.open(true);
            }
          }
        });

        self.activeCategories = ko.observableArray();

        self.filteredFunctions = ko.pureComputed(function () {
          var result = [];
          var lowerCaseQuery = self.query().toLowerCase();
          var replaceRegexp = new RegExp('(' + lowerCaseQuery + ')', 'i');
          self.activeCategories().forEach(function (category) {
            category.functions.forEach(function (fn) {
              if (fn.signature.toLowerCase().indexOf(lowerCaseQuery) === 0) {
                fn.weight = 2;
                fn.signatureMatch(fn.signature.replace(replaceRegexp, '<b>$1</b>'));
                fn.descriptionMatch(fn.description);
                result.push(fn);
              } else if (fn.signature.toLowerCase().indexOf(lowerCaseQuery) !== -1) {
                fn.weight = 1;
                fn.signatureMatch(fn.signature.replace(replaceRegexp, '<b>$1</b>'));
                fn.descriptionMatch(fn.description);
                result.push(fn);
              } else if ((fn.description && fn.description.toLowerCase().indexOf(lowerCaseQuery) !== -1)) {
                fn.signatureMatch(fn.signature);
                fn.descriptionMatch(fn.description.replace(replaceRegexp, '<b>$1</b>'));
                fn.weight = 0;
                result.push(fn);
              } else {
                if (fn.signatureMatch() !== fn.signature) {
                  fn.signatureMatch(fn.signature);
                }
                if (fn.descriptionMatch() !== fn.desciption) {
                  fn.descriptionMatch(fn.description);
                }
              }
            });
          });
          result.sort(function (a, b) {
            if (a.weight !== b.weight) {
              return b.weight - a.weight;
            }
            return a.signature.localeCompare(b.signature);
          });
          return result;
        });

        self.activeType.subscribe(function (newType) {
          self.selectedFunction(selectedFunctionPerType[newType]);
          self.activeCategories(self.categories[newType]);
          window.apiHelper.setInTotalStorage('assist', 'function.panel.active.type', newType);
        });

        var lastActiveType = window.apiHelper.getFromTotalStorage('assist', 'function.panel.active.type', self.availableTypes()[0]);
        self.activeType(lastActiveType);

        var updateType = function (type) {
          self.availableTypes().every(function (availableType) {
            if (availableType.toLowerCase() === type) {
              if (self.activeType() !== availableType) {
                self.activeType(availableType);
              }
              return false;
            }
            return true;
          });
        };

        var activeSnippetTypeSub = huePubSub.subscribe('active.snippet.type.changed', function (details) { updateType(details.type) });

        self.disposals.push(function () {
          activeSnippetTypeSub.remove();
        });

        huePubSub.subscribeOnce('set.active.snippet.type', updateType);
        huePubSub.publish('get.active.snippet.type');
      }

      FunctionsPanel.prototype.dispose = function () {
        var self = this;
        self.disposals.forEach(function (dispose) {
          dispose();
        })
      };

      FunctionsPanel.prototype.initFunctions = function (dialect) {
        var self = this;
        self.categories[dialect] = [];
        var functions = dialect === 'Pig' ? PigFunctions.CATEGORIZED_FUNCTIONS : SqlFunctions.CATEGORIZED_FUNCTIONS[dialect.toLowerCase()];

        functions.forEach(function (category) {
          var koCategory = {
            name: category.name,
            open: ko.observable(false),
            functions: $.map(category.functions, function(fn) {
              return {
                draggable: fn.draggable,
                signature: fn.signature,
                signatureMatch: ko.observable(fn.signature),
                description: fn.description,
                descriptionMatch: ko.observable(fn.description)
              }
            })
          };
          koCategory.functions.forEach(function (fn) {
            fn.category = koCategory;
          });
          self.categories[dialect].push(koCategory)
        });
      };

      ko.components.register('functions-panel', {
        viewModel: FunctionsPanel,
        template: { element: 'functions-panel-template' }
      });
    })();
  </script>

  <script type="text/html" id="editor-assistant-panel-template">
    <div class="assist-inner-panel assist-assistant-panel">
      <div class="assist-flex-panel">

        <div class="assist-flex-header">
          <div class="assist-inner-header">
            <!-- ko if: isSolr -->
            ${ _('Indexes') }
            <!-- /ko -->
            <!-- ko ifnot: isSolr -->
            ${ _('Tables') }
            <!-- ko if: statementCount() > 1 -->
            <div class="statement-count">${ _('Statement') } <span data-bind="text: activeStatementIndex() + '/' + statementCount()"></span></div>
            <!-- /ko -->
            <!-- /ko -->
          </div>
        </div>
        <div class="assist-flex-search" data-bind="visible: activeTables().length > 0">
          <div class="assist-filter">
            <!-- ko component: {
              name: 'inline-autocomplete',
              params: {
                querySpec: filter.querySpec,
                facets: ['type'],
                knownFacetValues: isSolr() ? SOLR_ASSIST_KNOWN_FACET_VALUES : SQL_ASSIST_KNOWN_FACET_VALUES,
                autocompleteFromEntries: $component.autocompleteFromEntries
              }
            } --><!-- /ko -->
          </div>
        </div>
        <div class="assist-flex-fill assist-db-scrollable" data-bind="delayedOverflow">
          <!-- ko if: filteredTables().length === 0 && (!filter.querySpec() || filter.querySpec().query === '') -->
          <div class="assist-no-entries">
            <!-- ko if: isSolr -->
            ${ _('No indexes selected.') }
            <!-- /ko -->
            <!-- ko ifnot: isSolr  -->
            ${ _('No tables identified.') }
            <!-- /ko -->
          </div>
          <!-- /ko -->
          <!-- ko if: filteredTables().length === 0 && filter.querySpec() && filter.querySpec().query !== '' && !someLoading() -->
          <div class="assist-no-entries">${ _('No entries found.') }</div>
          <!-- /ko -->
          <!-- ko if: filteredTables().length > 0 -->
          <ul class="database-tree assist-tables" data-bind="foreachVisible: { data: filteredTables, minHeight: 22, container: '.assist-db-scrollable', skipScrollEvent: true }">
            <!-- ko if: hasErrors -->
            <li class="assist-table hue-warning" data-bind="attr: { 'title': $parent.isSolr() ? '${ _ko('Error loading index details.') }' : '${ _ko('Error loading table details.') }'}">
              <span class="assist-entry">
                <i class="hue-warning fa fa-fw muted valign-middle fa-warning"></i>
                <!-- ko with: catalogEntry -->
                <!-- ko if: typeof reload !== 'undefined' -->
                <span data-bind="text: getDisplayName()"></span> <a class="inactive-action" href="javascript: void(0);" data-bind="click: reload"><i class="fa fa-refresh" data-bind="css: { 'fa-spin': reloading }"></i></a>
                <!-- /ko -->
                <!-- /ko -->
              </span>
            </li>
            <!-- /ko -->
            <!-- ko ifnot: hasErrors -->
            <!-- ko template: { if: catalogEntry.isTableOrView(), name: 'assist-table-entry' } --><!-- /ko -->
            <!-- ko template: { if: catalogEntry.isField(), name: 'assist-column-entry-assistant' } --><!-- /ko -->
            <!-- /ko -->
          </ul>
          <!-- /ko -->
          <!-- ko hueSpinner: { spin: filter.querySpec() && filter.querySpec().query !== '' && someLoading(), inline: true,  center: true} --><!-- /ko -->
        </div>

        <!-- ko if: showRisks -->
        <div class="assist-flex-header assist-divider"><div class="assist-inner-header">${ _('Query Analysis') }</div></div>
        <div class="assist-flex-third">
          <!-- ko if: ! activeRisks().hints -->
          <div class="assist-no-entries">${ _('Select a query or start typing to get optimization hints.') }</div>
          <!-- /ko -->
          <!-- ko if: activeRisks().hints && activeRisks().hints.length === 0 -->
          <div class="assist-no-entries">${ _('No optimizations identified.') }</div>
          <!-- /ko -->
          <!-- ko if: activeRisks().hints && activeRisks().hints.length > 0 -->
          <ul class="risk-list" data-bind="foreach: activeRisks().hints">
            <li>
              <div class="risk-list-title" data-bind="css: { 'risk-list-high' : risk === 'high', 'risk-list-normal':  risk !== 'high' }, tooltip: { title: risk + ' ' + riskTables }"><span data-bind="text: riskAnalysis"></span></div>
              <div class="risk-list-description" data-bind="text: riskRecommendation"></div>
              <div class="risk-quickfix" data-bind="visible: (riskId === 17 || riskId === 22) && $parent.activeEditor() && $parent.activeLocations()" style="display:none;">
                <a href="javascript:void(0);" data-bind="click: function () { $parent.addFilter(riskId); hueAnalytics.convert('optimizer', 'addFilter/' + riskId); }">${ _('Add filter') }</a>
              </div>
            </li>
          </ul>
          <!-- /ko -->
          <!-- ko if: hasMissingRisks() -->
          <div class="margin-top-20">
            <!-- ko hueSpinner: { spin: uploadingTableStats, inline: true} --><!-- /ko -->
            <!-- ko ifnot: uploadingTableStats -->
            <a href="javascript:void(0)" data-bind="visible: activeTables().length > 0, click: function() { uploadTableStats(true) }, attr: { 'title': ('${ _("Add table ") }'  + (isMissingDDL() ? 'DDL' : '') + (isMissingDDL() && isMissingStats() ? ' ${ _("and") } ' : '') + (isMissingStats() ? 'stats' : '')) }">
              <i class="fa fa-fw fa-plus-circle"></i> ${_('Improve Analysis')}
            </a>
            <!-- /ko -->
          </div>
          <!-- /ko -->
        </div>
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/javascript">
    var AssistantUtils = (function () {
      return {
        getFilteredTablesPureComputed: function (vm) {
          var openedByFilter = [];
          return ko.pureComputed(function () {
            if (vm.filter === null || !vm.filter.querySpec() || ((!vm.filter.querySpec().facets || Object.keys(vm.filter.querySpec().facets).length === 0) && (!vm.filter.querySpec().text || vm.filter.querySpec().text.length === 0))) {
              while (openedByFilter.length) {
                openedByFilter.pop().open(false);
              }
              return vm.activeTables();
            }

            var facets = vm.filter.querySpec().facets;

            var result = [];
            $.each(vm.activeTables(), function (index, entry) {
              var facetMatch = !facets || !facets['type'] || (!facets['type']['table'] && !facets['type']['view']);
              if (!facetMatch && facets['type']['table']) {
                facetMatch = entry.catalogEntry.isTable();
              }
              if (!facetMatch && facets['type']['view']) {
                facetMatch = entry.catalogEntry.isView();
              }

              var textMatch = !vm.filter.querySpec().text || vm.filter.querySpec().text.length === 0;
              if (!textMatch) {
                var nameLower = entry.catalogEntry.name.toLowerCase();
                textMatch = vm.filter.querySpec().text.every(function (text) {
                  return nameLower.indexOf(text.toLowerCase()) !== -1;
                });
              }
              entry.filterColumnNames(!textMatch);
              if ((facetMatch && textMatch) || entry.filteredEntries().length > 0) {
                if (!entry.open()) {
                  entry.open(true);
                  openedByFilter.push(entry);
                }
                result.push(entry);
              }
            });
            return result;
          });
        }
      }
    })();

    (function () {
      function EditorAssistantPanel(params) {
        var self = this;

        self.disposals = [];
        self.isSolr = ko.observable(false);
        self.activeTab = params.activeTab;

        self.sourceType = ko.observable(params.sourceType());

        self.showRisks = ko.pureComputed(function () {
          return window.HAS_OPTIMIZER && !self.isSolr() && (self.sourceType() === 'impala' || self.sourceType() === 'hive')
        });

        var typeSub = huePubSub.subscribe('active.snippet.type.changed', function (details) {
          self.sourceType(details.type);
        });

        self.disposals.push(function () {
          typeSub.remove();
        });

        self.uploadingTableStats = ko.observable(false);
        self.activeStatement = ko.observable();
        self.activeTables = ko.observableArray();
        self.activeRisks = ko.observable({});
        self.activeEditor = ko.observable();
        self.activeRisks.subscribe(function() {
          if (self.isMissingDDL()) {
            self.uploadTableStats(false);
          }
        });
        self.activeLocations = ko.observable();
        self.statementCount = ko.observable(0);
        self.activeStatementIndex = ko.observable(0);

        self.hasActiveRisks = ko.pureComputed(function () {
           return self.activeRisks().hints && self.activeRisks().hints.length > 0;
        });

        self.hasMissingRisks = ko.pureComputed(function () {
          return self.isMissingDDL() || self.isMissingStats();
        });

        self.isMissingDDL = ko.pureComputed(function () {
          return self.activeRisks().noDDL && self.activeRisks().noDDL.length > 0
        });

        self.isMissingStats = ko.pureComputed(function () {
          % if OPTIMIZER.AUTO_UPLOAD_STATS.get():
          return self.activeRisks().noStats && self.activeRisks().noStats.length > 0;
          % else:
          return false;
          % endif
        });

        self.someLoading = ko.pureComputed(function () {
          return self.activeTables().some(function (table) {
            return table.loading() || (!table.hasEntries() && !table.hasErrors());
          });
        });

        var createQualifiedIdentifier = function (identifierChain, defaultDatabase) {
          if (identifierChain.length === 1) {
            return defaultDatabase + '.' + identifierChain[0].name;
          }
          return $.map(identifierChain, function (identifier) {
            return identifier.name;
          }).join('.').toLowerCase();
        };

        self.filter = {
          querySpec: ko.observable({
            query: '',
            facets: {},
            text: []
          }).extend({ rateLimit: 300 })
        };

        self.filteredTables = AssistantUtils.getFilteredTablesPureComputed(self);

        var navigationSettings = {
          showStats: true,
          rightAssist: true
        };
        var i18n = {};

        var sources = {};

        var loadEntriesTimeout = -1;
        // This fetches the columns for each table synchronously with 2 second in between.
        var loadEntries = function (currentCount) {
          var count = currentCount || 0;
          count++;
          if (count > 10) {
            return;
          }
          window.clearTimeout(loadEntriesTimeout);
          if (self.activeTables().length === 1) {
            self.activeTables()[0].open(true);
          } else {
            loadEntriesTimeout = window.setTimeout(function () {
              self.activeTables().every(function (table) {
                if (!table.loaded && !table.hasErrors() && !table.loading()) {
                  table.loadEntries(function () {
                    loadEntries(count);
                  });
                  return false;
                }
                return !table.loading();
              })
            }, 2000);
          }
        };

        self.autocompleteFromEntries = function (nonPartial, partial) {
          var added = {};
          var result = [];
          var partialLower = partial.toLowerCase();
          self.filteredTables().forEach(function (table) {
            if (!added[table.catalogEntry.name] && table.catalogEntry.name.toLowerCase().indexOf(partialLower) === 0) {
              added[table.catalogEntry.name] = true;
              result.push(nonPartial + partial + table.catalogEntry.name.substring(partial.length))
            }
            table.entries().forEach(function (col) {
              if (!added[col.catalogEntry.name] && col.catalogEntry.name.toLowerCase().indexOf(partialLower) === 0) {
                added[col.catalogEntry.name] = true;
                result.push(nonPartial + partial + col.catalogEntry.name.substring(partial.length))
              }
            })
          });
          return result;
        };

        var activeTablesSub = self.activeTables.subscribe(loadEntries);
        self.disposals.push(function () {
          window.clearTimeout(loadEntriesTimeout);
          activeTablesSub.dispose();
        });

        var updateOnVisible = false;

        var runningPromises = [];

        var handleLocationUpdate = function (activeLocations) {
          while (runningPromises.length) {
            var promise = runningPromises.pop();
            if (promise.cancel) {
              promise.cancel();
            }
          }
          updateOnVisible = false;

          if (!sources[activeLocations.type]) {
            sources[activeLocations.type] = {
              assistDbSource: new AssistDbSource({
                i18n: i18n,
                initialNamespace: activeLocations.namespace,
                type: activeLocations.type,
                name: activeLocations.type,
                navigationSettings: navigationSettings
              }),
              databaseIndex: {},
              activeTableIndex: {}
            }
          }

          var assistDbSource = sources[activeLocations.type].assistDbSource;
          var databaseIndex = sources[activeLocations.type].databaseIndex;
          var activeTableIndex = sources[activeLocations.type].activeTableIndex;

          if (!activeLocations) {
            self.activeLocations(undefined);
            return;
          }
          self.activeLocations(activeLocations);
          self.statementCount(activeLocations.totalStatementCount);
          self.activeStatementIndex(activeLocations.activeStatementIndex);

          if (activeLocations.activeStatementLocations) {
            var updateTables = false;
            var tableQidIndex = {};
            var ctes = {};
            activeLocations.activeStatementLocations.forEach(function (location) {
              if (location.type === 'alias' && location.source === 'cte') {
                ctes[location.alias.toLowerCase()] = true;
              }
            });

            activeLocations.activeStatementLocations.forEach(function (location) {
              if (location.type === 'table' && (location.identifierChain.length !== 1 || !ctes[location.identifierChain[0].name.toLowerCase()])) {
                var tableDeferred = $.Deferred();
                var dbDeferred = $.Deferred();
                runningPromises.push(tableDeferred);
                runningPromises.push(dbDeferred);

                var qid = createQualifiedIdentifier(location.identifierChain, activeLocations.defaultDatabase);
                if (activeTableIndex[qid]) {
                  tableQidIndex[qid] = true;
                  tableDeferred.resolve(activeTableIndex[qid]);
                  dbDeferred.resolve(activeTableIndex[qid].parent);
                } else {
                  var database = location.identifierChain.length === 2 ? location.identifierChain[0].name : activeLocations.defaultDatabase;
                  database = database.toLowerCase();
                  if (databaseIndex[database]) {
                    dbDeferred.resolve(databaseIndex[database]);
                  } else {
                    dataCatalog.getEntry({
                      sourceType: activeLocations.type,
                      namespace: activeLocations.namespace,
                      compute: activeLocations.compute,
                      path: [ database ],
                      definition: { type: 'database' }
                    }).done(function (catalogEntry) {
                      databaseIndex[database] = new AssistDbEntry(catalogEntry, null, assistDbSource, self.filter, i18n,navigationSettings);
                      updateTables = true;
                      dbDeferred.resolve(databaseIndex[database])
                    }).fail(function () {
                      console.log('reject 1');
                      dbDeferred.reject();
                    });
                  }

                  dbDeferred.done(function (dbEntry) {
                    dbEntry.catalogEntry.getChildren({ silenceErrors: true }).done(function (tableEntries) {
                      var tableName = location.identifierChain[location.identifierChain.length - 1].name;
                      var found = tableEntries.some(function (tableEntry) {
                        if (tableEntry.name === tableName) {
                          var assistTableEntry = new AssistDbEntry(
                            tableEntry,
                            dbEntry,
                            assistDbSource,
                            self.filter,
                            i18n,
                            navigationSettings
                          );
                          activeTableIndex[createQualifiedIdentifier(location.identifierChain, activeLocations.defaultDatabase)] = assistTableEntry;
                          tableQidIndex[qid] = true;
                          updateTables = true;
                          tableDeferred.resolve(assistTableEntry);
                          return true;
                        }
                      });

                      if (!found) {
                        var missingEntry = new AssistDbEntry(
                          {
                            path: [dbEntry.catalogEntry.name, tableName],
                            name: tableName,
                            isTableOrView: function () { return true; },
                            getType: function () { return 'table' },
                            hasPossibleChildren: function () { return true; },
                            getSourceMeta: function () { return $.Deferred().resolve({ notFound: true }).promise() },
                            getDisplayName: function () { return dbEntry.catalogEntry.name + '.' + tableName },
                            reloading: ko.observable(false),
                            reload: function () {
                              var self = this;
                              if (self.reloading()) {
                                return;
                              }
                              self.reloading(true);
                              huePubSub.subscribeOnce('data.catalog.entry.refreshed', function (data) {
                                data.entry.getSourceMeta({ silenceErrors: true }).always(function () {
                                  self.reloading(false)
                                })
                              });
                              dataCatalog.getEntry({ sourceType: activeLocations.type, namespace: activeLocations.namespace, compute: activeLocations.compute, path: [] }).done(function (sourceEntry) {
                                sourceEntry.getChildren().done(function (dbEntries) {
                                  var clearPromise;
                                   // Clear the database first if it exists without cascade
                                  var hasDb = dbEntries.some(function (dbEntry) {
                                    if (dbEntry.name.toLowerCase() === self.path[0].toLowerCase()) {
                                      clearPromise = dbEntry.clearCache({ invalidate: 'invalidate', cascade: false });
                                      return true;
                                    }
                                  });
                                  if (!hasDb) {
                                    // If the database is missing clear the source without cascade
                                    clearPromise = sourceEntry.clearCache({ invalidate: 'invalidate', cascade: false });
                                  }
                                  clearPromise.fail(function () {
                                    self.reloading(false);
                                  });
                                }).fail(function () {
                                  self.reloading(false);
                                })
                              }).fail(function () {
                                self.reloading(false);
                              });
                            }
                          },
                          dbEntry,
                          assistDbSource,
                          self.filter,
                          i18n,
                          navigationSettings
                        );
                        activeTableIndex[createQualifiedIdentifier(location.identifierChain, activeLocations.defaultDatabase)] = missingEntry;
                        tableQidIndex[qid] = true;
                        updateTables = true;
                        missingEntry.hasErrors(true);
                        tableDeferred.resolve(missingEntry);
                      }
                    }).fail(tableDeferred.reject);
                  }).fail(tableDeferred.reject);
                }
              }
            });

            $.when.apply($, runningPromises).always(function () {
              runningPromises.length = 0;
              Object.keys(activeTableIndex).forEach(function (key) {
                if (!tableQidIndex[key]) {
                  delete activeTableIndex[key];
                  updateTables = true;
                }
              });

              if (updateTables) {
                var tables = [];
                Object.keys(activeTableIndex).forEach(function (key) {
                  tables.push(activeTableIndex[key]);
                });

                tables.sort(function (a, b) {
                  return a.catalogEntry.name.localeCompare(b.catalogEntry.name);
                });
                self.activeTables(tables);
              }
            });
          }
        };

        var entryRefreshedSub = huePubSub.subscribe('data.catalog.entry.refreshed', function (details) {
          var sourceType = details.entry.getSourceType();
          if (sources[sourceType]) {
            var completeRefresh = false;
            if (details.entry.isSource()) {
              sources[sourceType].databaseIndex = {};
              sources[sourceType].activeTableIndex = {};
              completeRefresh = true;
            } else if (details.entry.isDatabase() && sources[sourceType].databaseIndex[details.entry.name]) {
              var dbEntry = sources[sourceType].databaseIndex[details.entry.name];
              var activeTableIndex = sources[sourceType].activeTableIndex;
              Object.keys(activeTableIndex).forEach(function (tableKey) {
                var tableEntry = activeTableIndex[tableKey];
                if (tableEntry.parent === dbEntry) {
                  delete activeTableIndex[tableKey];
                  completeRefresh = true;
                }
              });
            } else if (details.entry.isTableOrView()) {
              var activeTableIndex = sources[sourceType].activeTableIndex;
              if (activeTableIndex[details.entry.getQualifiedPath()]) {
                delete activeTableIndex[details.entry.getQualifiedPath()];
                completeRefresh = true;
              }
            }
            if (completeRefresh) {
              handleLocationUpdate(self.activeLocations());
            }
          }
        });

        if (self.activeTab() === 'editorAssistant') {
          huePubSub.publish('get.active.editor.locations', handleLocationUpdate);
        } else {
          updateOnVisible = true;
        }

        var activeTabSub = self.activeTab.subscribe(function (activeTab) {
          if (activeTab === 'editorAssistant' && updateOnVisible) {
            huePubSub.publish('get.active.editor.locations', handleLocationUpdate);
          }
        });

        self.disposals.push(function () {
          entryRefreshedSub.remove();
          activeTabSub.dispose();
        });

        var activeLocationsSub = huePubSub.subscribe('editor.active.locations', function (activeLocations) {
          if (self.activeTab() === 'editorAssistant') {
            handleLocationUpdate(activeLocations);
          } else {
            updateOnVisible = true;
          }
        });

        var activeRisksSub = huePubSub.subscribe('editor.active.risks', function (details) {
          if (details.risks !== self.activeRisks()) {
            self.activeRisks(details.risks);
            self.activeEditor(details.editor);
          }
        });

        huePubSub.publish('editor.get.active.risks', function (details) {
          self.activeRisks(details.risks);
          self.activeEditor(details.editor);
        });

        self.disposals.push(function () {
          activeLocationsSub.remove();
          activeRisksSub.remove();
        });
      }

      EditorAssistantPanel.prototype.addFilter = function (riskId) {
        var self = this;
        if (self.activeLocations() && self.activeEditor()) {
          self.activeLocations().activeStatementLocations.every(function (location) {
            var isLowerCase = false;
            if (self.activeLocations().activeStatementLocations && self.activeLocations().activeStatementLocations.length > 0) {
              var firstToken = self.activeLocations().activeStatementLocations[0].firstToken;
              isLowerCase = firstToken === firstToken.toLowerCase();
            }

            if (location.type === 'whereClause' && !location.subquery && (location.missing || riskId === 22 )) {
              self.activeEditor().moveCursorToPosition({
                row: location.location.last_line - 1,
                column: location.location.last_column - 1
              });
              self.activeEditor().clearSelection();

              if (/\S$/.test(self.activeEditor().getTextBeforeCursor())) {
                self.activeEditor().session.insert(self.activeEditor().getCursorPosition(), ' ');
              }

              var operation = location.missing ? 'WHERE ' : 'AND ';
              self.activeEditor().session.insert(self.activeEditor().getCursorPosition(), isLowerCase ? operation.toLowerCase() : operation);
              self.activeEditor().focus();

              if (riskId === 22) {
                huePubSub.publish('editor.autocomplete.temporary.sort.override', { partitionColumnsFirst: true });
              }

              window.setTimeout(function () {
                self.activeEditor().execCommand("startAutocomplete");
              }, 1);

              return false;
            }
            return true;
          })
        }
      };

      EditorAssistantPanel.prototype.uploadTableStats = function (showProgress) {
        var self = this;
        if (self.uploadingTableStats()) {
          return;
        }
        self.uploadingTableStats(true);
        huePubSub.publish('editor.upload.table.stats', {
          activeTables: self.activeTables(),
          showProgress: showProgress,
          callback: function () {
            self.uploadingTableStats(false);
          }
        });
      };

      EditorAssistantPanel.prototype.dispose = function () {
        var self = this;
        self.disposals.forEach(function (dispose) {
          dispose();
        })
      };

      ko.components.register('editor-assistant-panel', {
        viewModel: EditorAssistantPanel,
        template: { element: 'editor-assistant-panel-template' }
      });
    })();
  </script>

  <script type="text/html" id="schedule-panel-template">
    <div class="assist-inner-panel">
      <div class="assist-flex-panel">
        <!-- ko if: selectedNotebook() && selectedNotebook().isBatchable() -->
        <!-- ko with: selectedNotebook() -->
        <div class="tab-pane" id="scheduleTab">
          <!-- ko ifnot: isSaved() && ! isHistory() -->
          ${ _('Query needs to be saved.') }
          <!-- /ko -->
          <!-- ko if: isSaved() && ! isHistory() -->
            <!-- ko if: schedulerViewModelIsLoaded() && schedulerViewModel.coordinator.isDirty() -->
            <a data-bind="click: saveScheduler" href="javascript: void(0);">${ _('Save changes') }</a>
            <!-- /ko -->
            <!-- ko if: schedulerViewModelIsLoaded() && ! schedulerViewModel.coordinator.isDirty() && (! viewSchedulerId() || isSchedulerJobRunning() == false )-->
            <a data-bind="click: showSubmitPopup" href="javascript: void(0);">${ _('Start') }</a>
            <!-- /ko -->
            <!-- ko if: schedulerViewModelIsLoaded() && viewSchedulerId()-->
            <a data-bind="click: function() { huePubSub.publish('show.jobs.panel', {id: viewSchedulerId(), interface: 'schedules'}) }, clickBubble: false" href="javascript: void(0);">
              ${ _('View') }
            </a>
            <!-- ko if: isSchedulerJobRunning() -->
              ${ _("Running")}
            <!-- /ko -->
            <!-- ko if: isSchedulerJobRunning() == false -->
              ${ _("Stopped")}
            <!-- /ko -->
          <!-- /ko -->
          <!-- /ko -->
          <br>
          <br>
          <div id="schedulerEditor"></div>
        </div>
        <!-- /ko -->
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {
      function SchedulePanel(params) {
        var self = this;
        self.disposals = [];
        self.selectedNotebook = ko.observable();

        // TODO: Move all the scheduler logic out of the notebook to here.

        var selectedNotebookSub = self.selectedNotebook.subscribe(function (notebook) { // Happening 4 times for each notebook loaded
          if (notebook && notebook.schedulerViewModel == null && notebook.isSaved() && ! notebook.isHistory()) {
            notebook.loadScheduler();
            if (notebook.viewSchedulerId()) {
              huePubSub.publish('check.schedules.browser');
            }
          }
        });
        self.disposals.push(selectedNotebookSub.dispose.bind(selectedNotebookSub));

        var setSelectedNotebookSub = huePubSub.subscribe('jobbrowser.schedule.data', function (jobs) {
          if (self.selectedNotebook() && self.selectedNotebook().viewSchedulerId()) {
            var _job = $.grep(jobs, function (job) {
              return self.selectedNotebook().viewSchedulerId() == job.id;
            });
            self.selectedNotebook().isSchedulerJobRunning(_job.length > 0 && _job[0].apiStatus == 'RUNNING');
          }
        });
        self.disposals.push(setSelectedNotebookSub.remove.bind(setSelectedNotebookSub));

        // Hue 3
        var setSelectedNotebookSub = huePubSub.subscribe('set.selected.notebook', self.selectedNotebook);
        self.disposals.push(setSelectedNotebookSub.remove.bind(setSelectedNotebookSub));
        var selectedNotebookChangedSub = huePubSub.subscribe('selected.notebook.changed', self.selectedNotebook);
        self.disposals.push(selectedNotebookChangedSub.remove.bind(selectedNotebookChangedSub));
        huePubSub.publish('get.selected.notebook');

        // Hue 4
        var currentAppSub = huePubSub.subscribe('set.current.app.view.model', function (viewModel) {
          if (viewModel.selectedNotebook) {
            if (viewModel.selectedNotebook()) {
              self.selectedNotebook(viewModel.selectedNotebook());
            } else {
              var subscription = viewModel.selectedNotebook.subscribe(function (notebook) {
                self.selectedNotebook(notebook);
                subscription.dispose();
              });
            }
          } else {
            self.selectedNotebook(null);
          }
        });
        self.disposals.push(currentAppSub.remove.bind(currentAppSub));
      }

      SchedulePanel.prototype.dispose = function () {
        var self = this;
        self.disposals.forEach(function (dispose) {
          dispose();
        })
      };

      ko.components.register('schedule-panel', {
        viewModel: SchedulePanel,
        template: { element: 'schedule-panel-template' }
      });
    })();
  </script>

  <script type="text/javascript">
    (function () {
      function DashboardAssistantPanel(params) {
        var self = this;

        self.disposals = [];
        self.isSolr = ko.observable(true);

        self.showRisks = ko.observable(false);

        self.filter = {
          querySpec: ko.observable({
            query: '',
            facets: {},
            text: []
          }).extend({ rateLimit: 300 })
        };

        self.sourceType = ko.observable('solr');

        self.activeTables = ko.observableArray();

        self.filteredTables = AssistantUtils.getFilteredTablesPureComputed(self);

        self.someLoading = ko.pureComputed(function () {
          return self.activeTables().some(function (table) {
            return table.loading() || (!table.hasEntries() && !table.hasErrors());
          });
        });

        var navigationSettings = {
          showStats: true,
          rightAssist: true
        };
        var i18n = {};

        var activeDashboardCollection = huePubSub.subscribe('set.active.dashboard.collection', function(collection) {
          var collectionName = collection.name();

          if (!collectionName) {
            return;
          }

          self.sourceType = ko.observable(collection.engine());

          var assistDbSource = new AssistDbSource({
            i18n : i18n,
            initialNamespace: collection.activeNamespace,
            initialCompute: collection.activeCompute,
            type: collection.engine(),
            name: collection.engine(),
            nonSqlType: true,
            navigationSettings: navigationSettings
          });

          var fakeParentName = collectionName.indexOf('.') > -1 ? collectionName.split('.')[0] : 'default';

          var sourceType = collection.source() === 'query' ? collection.engine() + '-query' : collection.engine();

          dataCatalog.getEntry({
            sourceType: sourceType,
            namespace: collection.activeNamespace,
            compute: collection.activeCompute,
            path: [ fakeParentName ],
            definition: { type: 'database' }
          }).done(function (fakeDbCatalogEntry) {
            var assistFakeDb = new AssistDbEntry(fakeDbCatalogEntry, null, assistDbSource, self.filter, i18n, navigationSettings);
            dataCatalog.getEntry({
              sourceType: sourceType,
              namespace: collection.activeNamespace,
              compute: collection.activeCompute,
              path: [fakeParentName, collectionName.indexOf('.') > -1 ? collectionName.split('.')[1] : collectionName],
              definition: { type: 'table' }
            }).done(function (collectionCatalogEntry) {
              var collectionEntry = new AssistDbEntry(collectionCatalogEntry, assistFakeDb, assistDbSource, self.filter, i18n, navigationSettings);
              self.activeTables([collectionEntry]);

              if (!collectionEntry.loaded && !collectionEntry.hasErrors() && !collectionEntry.loading()) {
                collectionEntry.loadEntries(function() { collectionEntry.toggleOpen(); });
              }
            });
          });

          self.autocompleteFromEntries = function (nonPartial, partial) {
            var added = {};
            var result = [];
            var partialLower = partial.toLowerCase();
            self.activeTables().forEach(function (table) {
              if (!added[table.catalogEntry.name] && table.catalogEntry.name.toLowerCase().indexOf(partialLower) === 0) {
                added[table.catalogEntry.name] = true;
                result.push(nonPartial + partial + table.catalogEntry.name.substring(partial.length))
              }
              table.entries().forEach(function (col) {
                if (!added[col.catalogEntry.name] && col.catalogEntry.name.toLowerCase().indexOf(partialLower) === 0) {
                  added[col.catalogEntry.name] = true;
                  result.push(nonPartial + partial + col.catalogEntry.name.substring(partial.length))
                }
              })
            });
            return result;
          };
        });

        self.disposals.push(function () {
          activeDashboardCollection.remove();
        });
      }

      DashboardAssistantPanel.prototype.dispose = function () {
        var self = this;
        self.disposals.forEach(function (dispose) {
          dispose();
        })
      };

      ko.components.register('dashboard-assistant-panel', {
        viewModel: DashboardAssistantPanel,
        template: { element: 'editor-assistant-panel-template' }
      });
    })();
  </script>

  <script type="text/html" id="right-assist-panel-template">
    <div class="right-assist-tabs" data-bind="splitFlexDraggable : {
        containerSelector: '.content-wrapper',
        sidePanelSelector: '.right-panel',
        sidePanelVisible: visible,
        orientation: 'right',
        onPosition: function() { huePubSub.publish('split.draggable.position') }
      }">
      <div class="right-assist-tab" data-bind="visible: editorAssistantTabAvailable" style="display:none;"><a class="inactive-action" href="javascript: void(0);" title="${ _('Assistant') }" data-bind="css: { 'blue' : activeTab() === 'editorAssistant' }, tooltip: { placement: 'left' }, click: editorAssistantTabClick"><i class="fa fa-fw fa-compass"></i></a></div>
      <div class="right-assist-tab" data-bind="visible: dashboardAssistantTabAvailable" style="display:none;"><a class="inactive-action" href="javascript: void(0);" title="${ _('Assistant') }" data-bind="css: { 'blue' : activeTab() === 'dashboardAssistant' }, tooltip: { placement: 'left' }, click: dashboardAssistantTabClick"><i class="fa fa-fw fa-compass"></i></a></div>
      <div class="right-assist-tab" data-bind="visible: functionsTabAvailable" style="display:none;"><a class="inactive-action" href="javascript: void(0);" title="${ _('Functions') }" data-bind="css: { 'blue' : activeTab() === 'functions' }, tooltip: { placement: 'left' }, click: functionsTabClick"><i class="fa fa-fw fa-superscript"></i></a></div>
      <div class="right-assist-tab" data-bind="visible: langRefTabAvailable" style="display:none;"><a class="inactive-action" href="javascript: void(0);" title="${ _('Language Reference') }" data-bind="css: { 'blue' : activeTab() === 'langRef' }, tooltip: { placement: 'left' }, click: langRefTabClick"><i class="fa fa-fw fa-book"></i></a></div>
      <div class="right-assist-tab" data-bind="visible: schedulesTabAvailable" style="display:none;"><a class="inactive-action" href="javascript: void(0);" title="${ _('Schedule') }" data-bind="css: { 'blue' : activeTab() === 'schedules' }, tooltip: { placement: 'left' }, click: schedulesTabClick"><i class="fa fa-fw fa-calendar"></i></a></div>
    </div>

    <!-- ko if: visible -->
    <div class="right-assist-contents">
      <!-- ko if: editorAssistantTabAvailable-->
      <div data-bind="component: { name: 'editor-assistant-panel', params: { activeTab: activeTab, sourceType: sourceType } }, visible: activeTab() === 'editorAssistant'"></div>
      <!-- /ko -->

      <!-- ko if: functionsTabAvailable -->
      <div data-bind="component: { name: 'functions-panel' }, visible: activeTab() === 'functions'"></div>
      <!-- /ko -->

      <!-- ko if: langRefTabAvailable -->
      <div data-bind="component: { name: 'language-reference-panel' }, visible: activeTab() === 'langRef'"></div>
      <!-- /ko -->

      <!-- ko if: dashboardAssistantTabAvailable -->
      <div data-bind="component: { name: 'dashboard-assistant-panel' }, visible: activeTab() === 'dashboardAssistant'"></div>
      <!-- /ko -->

      ## TODO: Switch to if: when loadSchedules from notebook.ko.js has been moved to the schedule-panel component
      <div data-bind="component: { name: 'schedule-panel' }, visible: activeTab() === 'schedules'" style="display:none;"></div>
    </div>
    <!-- /ko -->
  </script>


  <script type="text/javascript">
    (function () {

      var EDITOR_ASSISTANT_TAB = 'editorAssistant';
      var DASHBOARD_ASSISTANT_TAB = 'dashboardAssistant';
      var FUNCTIONS_TAB = 'functions';
      var SCHEDULES_TAB = 'schedules';
      var LANG_REF_TAB = 'langRef';

      function RightAssistPanel(params) {
        var self = this;
        self.disposals = [];

        self.activeTab = ko.observable();
        self.visible = params.visible;
        self.sourceType = ko.observable();

        self.editorAssistantTabAvailable = ko.observable(false);
        self.dashboardAssistantTabAvailable = ko.observable(false);
        self.functionsTabAvailable = ko.observable(false);
        self.langRefTabAvailable = ko.observable(false);
        self.schedulesTabAvailable = ko.observable(false);

        self.lastActiveTabEditor = window.apiHelper.withTotalStorage('assist', 'last.open.right.panel', ko.observable(), EDITOR_ASSISTANT_TAB);
        self.lastActiveTabDashboard = window.apiHelper.withTotalStorage('assist', 'last.open.right.panel.dashboard', ko.observable(), DASHBOARD_ASSISTANT_TAB);

        huePubSub.subscribe('assist.highlight.risk.suggestions', function () {
          if (self.editorAssistantTabAvailable() && self.activeTab() !== EDITOR_ASSISTANT_TAB) {
            self.activeTab(EDITOR_ASSISTANT_TAB);
          }
        });

        huePubSub.subscribe('assist.lang.ref.show.topic', function (targetTopic) {
          huePubSub.publish('right.assist.show');
          if (self.langRefTabAvailable() && self.activeTab() !== LANG_REF_TAB) {
            self.activeTab(LANG_REF_TAB);
          }
          huePubSub.publish('assist.lang.ref.panel.show.topic', targetTopic)
        });

        var updateTabs = function () {
          if (!self.visible()) {
            self.activeTab(undefined);
            return;
          }
          if (self.lastActiveTabEditor() === FUNCTIONS_TAB && self.functionsTabAvailable()) {
            self.activeTab(FUNCTIONS_TAB);
          } else if (self.lastActiveTabEditor() === SCHEDULES_TAB && self.schedulesTabAvailable()) {
            self.activeTab(SCHEDULES_TAB);
          } else if (self.lastActiveTabEditor() === LANG_REF_TAB && self.langRefTabAvailable()) {
            self.activeTab(LANG_REF_TAB);
          } else if (self.editorAssistantTabAvailable()) {
            self.activeTab(EDITOR_ASSISTANT_TAB);
          } else if (self.functionsTabAvailable()) {
            self.activeTab(FUNCTIONS_TAB);
          } else if (self.schedulesTabAvailable()) {
            self.activeTab(SCHEDULES_TAB);
          } else if (self.dashboardAssistantTabAvailable()) {
            self.activeTab(DASHBOARD_ASSISTANT_TAB);
          } else {
            self.activeTab(undefined);
          }
        };

        var updateContentsForType = function (type, isSqlDialect) {
          self.sourceType(type);

          // TODO: Get these dynamically from langref and functions modules when moved to webpack
          self.functionsTabAvailable(type === 'hive' || type === 'impala' || type === 'pig');
          self.langRefTabAvailable(type === 'hive' || type === 'impala');
          self.editorAssistantTabAvailable((!window.IS_EMBEDDED || window.EMBEDDED_ASSISTANT_ENABLED) && isSqlDialect);
          self.dashboardAssistantTabAvailable(type === 'dashboard');
          self.schedulesTabAvailable(false);
          if (type !== 'dashboard') {
            if ('${ ENABLE_QUERY_SCHEDULING.get() }' === 'True') {
              huePubSub.subscribeOnce('set.current.app.view.model', function (viewModel) {
                // Async
                self.schedulesTabAvailable(!!viewModel.selectedNotebook);
                updateTabs();
              });
              huePubSub.publish('get.current.app.view.model');
            } else {
              self.schedulesTabAvailable(false);
            }
          }
          updateTabs();
        };

        var snippetTypeSub = huePubSub.subscribe('active.snippet.type.changed', function (details) { updateContentsForType(details.type, details.isSqlDialect) });
        self.disposals.push(snippetTypeSub.remove.bind(snippetTypeSub));

        huePubSub.subscribe('set.current.app.name', function (appName) {
          if (appName === 'dashboard') {
            updateContentsForType(appName, false);
          }
        });
        huePubSub.publish('get.current.app.name');
        updateTabs();
      }

      RightAssistPanel.prototype.switchTab = function (tabName) {
        var self = this;
        if (self.activeTab() === tabName) {
          self.visible(false);
          self.activeTab(undefined);
        } else {
          self.activeTab(tabName);
          if (!self.visible()) {
            self.visible(true);
          }
        }
      };

      RightAssistPanel.prototype.editorAssistantTabClick = function () {
        var self = this;
        self.lastActiveTabEditor(EDITOR_ASSISTANT_TAB);
        self.switchTab(EDITOR_ASSISTANT_TAB);
      };

      RightAssistPanel.prototype.dashboardAssistantTabClick = function () {
        var self = this;
        self.lastActiveTabDashboard(DASHBOARD_ASSISTANT_TAB);
        self.switchTab(DASHBOARD_ASSISTANT_TAB);
      };

      RightAssistPanel.prototype.functionsTabClick = function () {
        var self = this;
        self.lastActiveTabEditor(FUNCTIONS_TAB);
        self.switchTab(FUNCTIONS_TAB);
      };

      RightAssistPanel.prototype.langRefTabClick = function () {
        var self = this;
        self.lastActiveTabEditor(LANG_REF_TAB);
        self.switchTab(LANG_REF_TAB);
      };

      RightAssistPanel.prototype.schedulesTabClick = function () {
        var self = this;
        self.lastActiveTabEditor(SCHEDULES_TAB);
        self.switchTab(SCHEDULES_TAB);
      };

      RightAssistPanel.prototype.dispose = function () {
        var self = this;
        self.disposals.forEach(function (dispose) {
          dispose();
        })
      };

      ko.components.register('right-assist-panel', {
        viewModel: RightAssistPanel,
        template: { element: 'right-assist-panel-template' }
      });
    })();
  </script>
</%def>
