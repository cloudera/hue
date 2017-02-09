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

from desktop import conf
from desktop.conf import USE_NEW_SIDE_PANELS
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko

from metadata.conf import has_navigator
from metastore.conf import ENABLE_NEW_CREATE_TABLE
from notebook.conf import ENABLE_QUERY_BUILDER
%>

<%def name="assistJSModels()">
<script src="${ static('desktop/js/assist/assistDbEntry.js') }"></script>
<script src="${ static('desktop/js/assist/assistDbSource.js') }"></script>
<script src="${ static('desktop/js/assist/assistHdfsEntry.js') }"></script>
<script src="${ static('desktop/js/assist/assistS3Entry.js') }"></script>
<script src="${ static('desktop/js/assist/assistCollectionEntry.js') }"></script>
<script src="${ static('desktop/js/assist/assistHBaseEntry.js') }"></script>
<script src="${ static('desktop/js/document/hueDocument.js') }"></script>
<script src="${ static('desktop/js/document/hueFileEntry.js') }"></script>
</%def>

<%def name="assistPanel(is_s3_enabled=False)">
  <%
    home_dir = user.get_home_directory()
    if not request.fs.isdir(home_dir):
      home_dir = '/'
  %>

  <%namespace name="sqlContextPopover" file="/sql_context_popover.mako" />
  <%namespace name="nav_components" file="/nav_components.mako" />

  ${ sqlContextPopover.sqlContextPopover() }
  ${ nav_components.nav_tags(readOnly=not user.has_hue_permission(action="write", app="metadata")) }

  <script type="text/html" id="assist-no-database-entries">
    <ul class="assist-tables">
      <li>
        <span style="font-style: italic">${_('The database has no tables')}</span>
      </li>
    </ul>
  </script>

  <script type="text/html" id="assist-no-table-entries">
    <ul>
      <li>
        <span style="font-style: italic" class="assist-entry assist-field-link">${_('The table has no columns')}</span>
      </li>
    </ul>
  </script>

  <script type="text/html" id="assist-entry-actions">
    <div class="assist-actions" data-bind="css: { 'table-actions' : definition.isTable || definition.isView, 'column-actions': definition.isColumn, 'database-actions' : definition.isDatabase } " style="opacity: 0">
      <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, click: function (data, event) { showContextPopover(data, event); }, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${_('Show details')}"></i></a>
      <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.openItem || (navigationSettings.openDatabase && definition.isDatabase), click: openItem"><i class="fa fa-long-arrow-right" title="${_('Open')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="sql-context-items">
    <li><a href="javascript:void(0);" data-bind="click: function (data) { showContextPopover(data, { target: $parentContext.$contextSourceElement }, { left: 4, top: 2 }); }"><i class="fa fa-fw fa-info"></i> ${ _('Show details') }</a></li>
    <li><a href="javascript:void(0);" data-bind="click: dblClick"><i class="fa fa-fw fa-paste"></i> ${ _('Insert at cursor') }</a></li>
    %if ENABLE_QUERY_BUILDER.get():
    <!-- ko if: definition.isColumn -->
    <li class="divider"></li>
    <!-- ko template: { name: 'query-builder-context-items' } --><!-- /ko -->
    <!-- /ko -->
    %endif
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

  <script type="text/html" id="assist-table-entry">
    <li class="assist-table" data-bind="templateContextMenu: { template: 'sql-context-items', scrollContainer: '.assist-db-scrollable' }, visibleOnHover: { override: statsVisible, selector: '.table-actions' }">
      <div class="assist-actions table-actions" style="opacity: 0">
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, click: showContextPopover, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${_('Show details')}"></i></a>
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.openItem, click: openItem"><i class="fa fa-long-arrow-right" title="${_('Open')}"></i></a>
      </div>
      <a class="assist-entry assist-table-link" href="javascript:void(0)" data-bind="click: toggleOpen, attr: {'title': definition.title }, draggableText: { text: editorText,  meta: {'type': 'sql', 'table': tableName, 'database': databaseName} }">
        <i class="fa fa-fw fa-table muted valign-middle" data-bind="css: { 'fa-eye': definition.isView, 'fa-table': definition.isTable }"></i>
        <span data-bind="text: definition.displayName, css: { 'highlight': highlight }"></span> <!-- ko if: assistDbSource.activeSort() === 'popular' && popularity() > 0 --><i title="${ _('Popular') }" class="fa fa-star-o top-star"></i> <!-- /ko -->
      </a>
      <div class="center" data-bind="visible: loading"><i class="fa fa-spinner fa-spin assist-spinner"></i></div>
      <!-- ko template: { if: open, name: 'assist-db-entries'  } --><!-- /ko -->
    </li>
  </script>

  <script type="text/html" id="assist-column-entry">
    <li data-bind="templateContextMenu: { template: 'sql-context-items', scrollContainer: '.assist-db-scrollable' }, visible: ! hasErrors(), visibleOnHover: { childrenOnly: true, override: statsVisible, selector: definition.isView ? '.table-actions' : '.column-actions' }, css: { 'assist-table': definition.isView, 'assist-column': definition.isColumn || definition.isComplex }">
      <div class="assist-actions column-actions" style="opacity: 0">
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, click: showContextPopover, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${_('Show details')}"></i></a>
      </div>
      <!-- ko if: expandable -->
      <a class="assist-entry assist-field-link" href="javascript:void(0)" data-bind="click: toggleOpen, attr: {'title': definition.title }">
        <span class="highlightable" data-bind="css: { 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName }, text: definition.displayName, draggableText: { text: editorText, meta: {'type': 'sql', 'column': columnName, 'table': tableName, 'database': databaseName } }"></span><!-- ko if: definition.primary_key --> <i class="fa fa-key"></i><!-- /ko -->
      </a>
      <!-- /ko -->
      <!-- ko ifnot: expandable -->
      <div style="cursor: default;" class="assist-entry assist-field-link" href="javascript:void(0)" data-bind="event: { dblClick: dblClick }, attr: {'title': definition.title }">
        <span class="highlightable" data-bind="css: { 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName}, text: definition.displayName, draggableText: { text: editorText, meta: {'type': 'sql', 'column': columnName, 'table': tableName, 'database': databaseName} }"></span><!-- ko if: definition.primary_key --> <i class="fa fa-key"></i><!-- /ko --><!-- ko if: assistDbSource.activeSort() === 'popular' && popularity() > 0 --> <i title="${ _('Popular') }" class="fa fa-star-o top-star"></i> <!-- /ko -->
      </div>
      <!-- /ko -->
      <div class="center" data-bind="visible: loading"><i class="fa fa-spinner fa-spin assist-spinner"></i></div>
      <!-- ko template: { if: open, name: 'assist-db-entries'  } --><!-- /ko -->
    </li>
  </script>

  <script type="text/html" id="assist-db-entries">
    <!-- ko if: ! hasErrors() && hasEntries() && ! loading() && filteredEntries().length == 0 -->
    <ul class="assist-tables">
      <li class="assist-entry no-entries">${_('No results found')}</li>
    </ul>
    <!-- /ko -->
    <!-- ko if: ! hasErrors() && hasEntries() && ! loading() && filteredEntries().length > 0 -->
    <ul class="database-tree" data-bind="foreachVisible: { data: filteredEntries, minHeight: (definition.isTable || definition.isView ? 20 : 25), container: '.assist-db-scrollable' }, css: { 'assist-tables': definition.isDatabase }">
      <!-- ko template: { if: definition.isTable || definition.isView, name: 'assist-table-entry' } --><!-- /ko -->
      <!-- ko template: { ifnot: definition.isTable || definition.isView, name: 'assist-column-entry' } --><!-- /ko -->
    </ul>
    <!-- /ko -->
    <!-- ko template: { if: ! hasErrors() && ! hasEntries() && ! loading() && (definition.isTable || definition.isView), name: 'assist-no-table-entries' } --><!-- /ko -->
    <!-- ko template: { if: ! hasErrors() && ! hasEntries() && ! loading() && definition.isDatabase, name: 'assist-no-database-entries' } --><!-- /ko -->
    <!-- ko if: hasErrors -->
    <ul class="assist-tables">
      <!-- ko if: definition.isTable -->
      <li class="assist-errors">${ _('Error loading columns.') }</li>
      <!-- /ko -->
      <!-- ko ifnot: definition.isTable -->
      <li class="assist-errors">${ _('Error loading fields.') }</li>
      <!-- /ko -->
    </ul>
    <!-- /ko -->
  </script>

  <script type="text/html" id="assist-db-breadcrumb">
    <div class="assist-flex-header assist-breadcrumb">
      <!-- ko if: selectedSource()  && ! selectedSource().selectedDatabase() && sources().length === 1 -->
      <i class="fa fa-server assist-breadcrumb-text"></i>
      <span class="assist-breadcrumb-text" data-bind="text: breadcrumb"></span>
      <!-- /ko -->
      <!-- ko if: selectedSource()  && ! selectedSource().selectedDatabase() && sources().length > 1 -->
      <a data-bind="click: back">
        <i class="fa fa-chevron-left assist-breadcrumb-back"></i>
        <i class="fa fa-server assist-breadcrumb-text"></i>
        <span class="assist-breadcrumb-text" data-bind="text: breadcrumb"></span>
      </a>
      <!-- /ko -->
      <!-- ko if: selectedSource()  && selectedSource().selectedDatabase() -->
      <a data-bind="click: back">
        <i class="fa fa-chevron-left assist-breadcrumb-back" ></i>
        <i class="fa fa-database assist-breadcrumb-text"></i>
        <span class="assist-breadcrumb-text" data-bind="text: breadcrumb"></span>
      </a>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="assist-sql-inner-panel">
    <div class="assist-inner-panel">
      <div class="assist-flex-panel">
        <!-- ko template: { if: breadcrumb() !== null, name: 'assist-db-breadcrumb' } --><!-- /ko -->
        <!-- ko template: { ifnot: selectedSource, name: 'assist-sources-template' } --><!-- /ko -->
        <!-- ko with: selectedSource -->
        <!-- ko template: { ifnot: selectedDatabase, name: 'assist-databases-template' }--><!-- /ko -->
        <!-- ko with: selectedDatabase -->
        <!-- ko template: { name: 'assist-tables-template' } --><!-- /ko -->
        <!-- /ko -->
        <!-- /ko -->
      </div>
      <!-- ko with: $parents[1] -->
      <!-- ko template: { if: searchActive() && searchInput() !== '' && navigatorEnabled(), name: 'nav-search-result' } --><!-- /ko -->
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="s3-details-content">
    <!-- ko with: definition -->
    <div class="assist-details-wrap">
      <div><div class="assist-details-header">${ _('Size') }</div><div class="assist-details-value" data-bind="text: humansize"></div></div>
      <div><div class="assist-details-header">${ _('Permissions') }</div><div class="assist-details-value" data-bind="text: rwx"></div></div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="s3-details-title">
    <span data-bind="text: definition.name"></span>
  </script>

  <script type="text/html" id="assist-s3-header-actions">
    <div class="assist-db-header-actions" style="margin-top: -1px;">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.s3.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manual refresh')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-s3-inner-panel">
    <div class="assist-inner-panel">
      <div class="assist-flex-panel">
        <!-- ko with: selectedS3Entry -->
        <div class="assist-flex-header assist-breadcrumb" >
          <!-- ko if: parent !== null -->
          <a href="javascript: void(0);" data-bind="click: function () { huePubSub.publish('assist.selectS3Entry', parent); }">
            <i class="fa fa-chevron-left" style="font-size: 15px;margin-right:8px;"></i>
            <i class="fa fa-folder-o" style="font-size: 14px; line-height: 16px; vertical-align: top; margin-right:4px;"></i>
            <span style="font-size: 14px;line-height: 16px;vertical-align: top;" data-bind="text: path"></span>
          </a>
          <!-- /ko -->
          <!-- ko if: parent === null -->
          <div>
            <i class="fa fa-folder-o" style="font-size: 14px; line-height: 16px;vertical-align: top; margin-right:4px;"></i>
            <span style="font-size: 14px;line-height: 16px;vertical-align: top;" data-bind="text: path"></span>
          </div>
          <!-- /ko -->
          <!-- ko template: 'assist-s3-header-actions' --><!-- /ko -->
        </div>
        <div class="assist-flex-fill assist-s3-scrollable">
          <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
            <!-- ko hueSpinner: { spin: loadingMore, overlay: true } --><!-- /ko -->
            <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 20, container: '.assist-s3-scrollable', fetchMore: $data.fetchMore.bind($data) }">
              <li class="assist-entry assist-table-link" style="position: relative;" data-bind="visibleOnHover: { 'selector': '.assist-actions' }">
                <div class="assist-actions table-actions" style="opacity: 0;" >
                  <a style="padding: 0 3px;" class="inactive-action" href="javascript:void(0);" data-bind="templatePopover : { contentTemplate: 's3-details-content', titleTemplate: 's3-details-title', minWidth: '320px' }">
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
              <li class="assist-entry" style="font-style: italic;">${_('Empty directory')}</li>
            </ul>
            <!-- /ko -->
          </div>
          <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
          <div class="assist-errors" data-bind="visible: ! loading() && hasErrors()">
            <span>${ _('Error loading contents.') }</span>
          </div>
        </div>
        <!-- /ko -->
      </div>
      <!-- ko with: $parents[1] -->
      <!-- ko template: { if: searchActive() && searchInput() !== '' && navigatorEnabled(), name: 'nav-search-result' } --><!-- /ko -->
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="hdfs-details-content">
    <!-- ko with: definition -->
    <div class="assist-details-wrap">
      <div><div class="assist-details-header">${ _('Size') }</div><div class="assist-details-value" data-bind="text: humansize"></div></div>
      <!-- ko with: stats -->
      <div><div class="assist-details-header">${ _('User') }</div><div class="assist-details-value" data-bind="text: user"></div></div>
      <div><div class="assist-details-header">${ _('Group') }</div><div class="assist-details-value" data-bind="text: group"></div></div>
      <!-- /ko -->
      <div><div class="assist-details-header">${ _('Permissions') }</div><div class="assist-details-value" data-bind="text: rwx"></div></div>
      <div><div class="assist-details-header">${ _('Date') }</div><div class="assist-details-value" data-bind="text: mtime"></div></div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="hdfs-details-title">
    <span data-bind="text: definition.name"></span>
  </script>

  <script type="text/html" id="assist-hdfs-header-actions">
    <div class="assist-db-header-actions" style="margin-top: -1px;">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.hdfs.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manual refresh')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-hdfs-inner-panel">
    <div class="assist-inner-panel">
      <div class="assist-flex-panel">
        <!-- ko with: selectedHdfsEntry -->
        <div class="assist-flex-header assist-breadcrumb" >
          <!-- ko if: parent !== null -->
          <a href="javascript: void(0);" data-bind="click: function () { huePubSub.publish('assist.selectHdfsEntry', parent); }">
            <i class="fa fa-chevron-left" style="font-size: 15px;margin-right:8px;"></i>
            <i class="fa fa-folder-o" style="font-size: 14px; line-height: 16px; vertical-align: top; margin-right:4px;"></i>
            <span style="font-size: 14px;line-height: 16px;vertical-align: top;" data-bind="text: path"></span>
          </a>
          <!-- /ko -->
          <!-- ko if: parent === null -->
          <div style="padding-left: 5px;">
            <i class="fa fa-folder-o" style="font-size: 14px; line-height: 16px;vertical-align: top; margin-right:4px;"></i>
            <span style="font-size: 14px;line-height: 16px;vertical-align: top;" data-bind="text: path"></span>
          </div>
          <!-- /ko -->
          <!-- ko template: 'assist-hdfs-header-actions' --><!-- /ko -->
        </div>
        <div class="assist-flex-fill assist-hdfs-scrollable">
          <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
            <!-- ko hueSpinner: { spin: loadingMore, overlay: true } --><!-- /ko -->
            <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 20, container: '.assist-hdfs-scrollable', fetchMore: $data.fetchMore.bind($data) }">
              <li class="assist-entry assist-table-link" style="position: relative;" data-bind="visibleOnHover: { 'selector': '.assist-actions' }">
                <div class="assist-actions table-actions" style="opacity: 0;" >
                  <a style="padding: 0 3px;" class="inactive-action" href="javascript:void(0);" data-bind="templatePopover : { contentTemplate: 'hdfs-details-content', titleTemplate: 'hdfs-details-title', minWidth: '320px' }">
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
              <li class="assist-entry" style="font-style: italic;">${_('Empty directory')}</li>
            </ul>
            <!-- /ko -->
          </div>
          <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
          <div class="assist-errors" data-bind="visible: ! loading() && hasErrors()">
            <span>${ _('Error loading contents.') }</span>
          </div>
        </div>
        <!-- /ko -->
      </div>
      <!-- ko with: $parents[1] -->
      <!-- ko template: { if: searchActive() && searchInput() !== '' && navigatorEnabled(), name: 'nav-search-result' } --><!-- /ko -->
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="file-details-content">
    <!-- ko with: definition -->
    <div class="assist-details-wrap">
      <div><div class="assist-details-header">${ _('Description') }</div><div class="assist-details-value" data-bind="text: description"></div></div>
      <div><div class="assist-details-header">${ _('Modified') }</div><div class="assist-details-value" data-bind="text: localeFormat(last_modified)"></div></div>
      <div><div class="assist-details-header">${ _('Owner') }</div><div class="assist-details-value" data-bind="text: owner"></div></div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="file-details-title">
    <span data-bind="text: definition().name"></span>
  </script>

  <script type="text/html" id="assist-document-header-actions">
    <div class="assist-header-actions" style="margin-top: -1px;">
      <a class="inactive-action" href="javascript:void(0)"><i class="pointer fa fa-filter" title="${_('Filter')}"></i></a>
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.file.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manual refresh')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-documents-inner-panel">
    <div class="assist-inner-panel">
      <div class="assist-flex-panel">
        <!-- ko with: activeEntry -->
        <div class="assist-flex-header assist-breadcrumb">
          <!-- ko ifnot: isRoot -->
          <a href="javascript: void(0);" data-bind="click: function () { parent.makeActive(); }">
            <i class="fa fa-chevron-left" style="font-size: 15px;margin-right:8px;"></i>
            <i class="fa fa-folder-o" style="font-size: 14px; line-height: 16px; vertical-align: top; margin-right:4px;"></i>
            <span style="font-size: 14px;line-height: 16px;vertical-align: top;" data-bind="text: definition().name"></span>
          </a>
          <!-- /ko -->
          <!-- ko if: isRoot -->
          <div style="padding-left: 5px;">
            <i class="fa fa-folder-o" style="font-size: 14px; line-height: 16px;vertical-align: top;margin-right:4px;"></i>
            <span style="font-size: 14px;line-height: 16px;vertical-align: top;">/</span>
          </div>
          <!-- /ko -->
          <!-- ko template: 'assist-document-header-actions' --><!-- /ko -->
        </div>
        <div class="assist-flex-fill assist-file-scrollable">
          <div data-bind="visible: ! loading() && ! hasErrors() && entries().length > 0">
             <ul class="assist-tables" data-bind="foreachVisible: {data: entries, minHeight: 20, container: '.assist-file-scrollable' }">
               <li class="assist-entry assist-file-entry" style="position: relative;" data-bind="assistFileDroppable, visibleOnHover: { 'selector': '.assist-file-actions' }">
                 <div class="assist-file-actions table-actions" style="opacity: 0;" >
                   <a style="padding: 0 3px;" class="inactive-action" href="javascript:void(0);" data-bind="templatePopover : { contentTemplate: 'file-details-content', titleTemplate: 'file-details-title', minWidth: '350px' }">
                     <i class='fa fa-info' title="${ _('Details') }"></i>
                   </a>
                 </div>
                 <a href="javascript:void(0)" class="assist-entry assist-table-link" data-bind="click: open, attr: {'title': name }">
                   <!-- ko if: isDirectory -->
                   <i class="fa fa-fw fa-folder-o muted valign-middle"></i>
                   <!-- /ko -->
                   <!-- ko ifnot: isDirectory -->
                   <i class="fa fa-fw fa-file-o muted valign-middle"></i>
                   <!-- /ko -->
                   <span data-bind="draggableText: { text: definition().name, meta: {'type': 'document', 'definition': definition()} }, text: definition().name"></span>
                 </a>
               </li>
             </ul>
          </div>
          <div data-bind="visible: !loading() && ! hasErrors() && entries().length === 0">
            <span style="font-style: italic;">${_('Empty directory')}</span>
          </div>
          <div class="center" data-bind="visible: loading() && ! hasErrors()">
            <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i><!--<![endif]-->
            <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
          </div>
          <div class="assist-errors" data-bind="visible: ! loading() && hasErrors()">
            <span>${ _('Error loading contents.') }</span>
          </div>
          <!-- /ko -->
          <!-- ko with: $parents[1] -->
          <!-- ko template: { if: searchActive() && searchInput() !== '' && navigatorEnabled(), name: 'nav-search-result' } --><!-- /ko -->
        </div>
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/html" id="assist-collections-header-actions">
    <div class="assist-db-header-actions" style="margin-top: -1px;">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: $parent.toggleSearch, css: { 'blue' : $parent.isSearchVisible }"><i class="pointer fa fa-filter" title="${_('Filter')}"></i></a>
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.collections.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manual refresh')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-collections-inner-panel">
    <div class="assist-inner-panel">
      <div class="assist-flex-panel">
        <!-- ko with: selectedCollectionEntry -->
        <div class="assist-inner-header assist-breadcrumb">
          ${_('Collections')}
          <!-- ko template: 'assist-collections-header-actions' --><!-- /ko -->
        </div>
        <div class="assist-flex-table-search" data-bind="visible: $parent.isSearchVisible() && !loading() && !hasErrors() && entries().length > 0">
          <div>
            <label class="checkbox inline-block margin-left-5"><input type="checkbox" data-bind="checked: $parent.showCores" />${_('Show cores')}</label>
          </div>
          <div class="assist-filter"><input id="searchInput" class="clearable" type="text" placeholder="${ _('Collection name...') }" data-bind="hasFocus: $parent.editingSearch, clearable: $parent.filter, value: $parent.filter, valueUpdate: 'afterkeydown'"/></div>
        </div>
        <div class="assist-flex-fill assist-collections-scrollable">
          <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
            <ul class="assist-tables" data-bind="foreachVisible: { data: filteredEntries, minHeight: 20, container: '.assist-collections-scrollable' }">
              <li class="assist-entry assist-table-link" style="position: relative;" data-bind="visibleOnHover: { 'selector': '.assist-actions' }">
                <a href="javascript:void(0)" class="assist-entry assist-table-link" data-bind="multiClick: { click: click, dblClick: dblClick }, attr: {'title': definition.name }">
                  <i class="fa fa-fw fa-search muted valign-middle"></i>
                  <span draggable="true" data-bind="text: definition.name, draggableText: { text: '\'' + path + '\'', meta: {'type': 'collection', 'definition': definition} }"></span>
                </a>
              </li>
            </ul>
            <!-- ko if: !loading() && entries().length === 0 -->
            <ul class="assist-tables">
              <li class="assist-entry" style="font-style: italic;">${_('No collections available.')}</li>
            </ul>
            <!-- /ko -->
          </div>
          <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
          <div class="assist-errors" data-bind="visible: ! loading() && hasErrors()">
            <span>${ _('Error loading contents.') }</span>
          </div>
        </div>
        <!-- /ko -->
      </div>
      <!-- ko with: $parents[1] -->
      <!-- ko template: { if: searchActive() && searchInput() !== '' && navigatorEnabled(), name: 'nav-search-result' } --><!-- /ko -->
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="assist-hbase-header-actions">
    <div class="assist-db-header-actions" style="margin-top: -1px;">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.hbase.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manual refresh')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-hbase-inner-panel">
    <div class="assist-inner-panel">
      <div class="assist-flex-panel">
        <!-- ko with: selectedHBaseEntry -->
        <div class="assist-inner-header assist-breadcrumb" >
          <!-- ko if: definition.host !== '' -->
          <a href="javascript: void(0);" data-bind="click: function () { huePubSub.publish('assist.clickHBaseRootItem'); }">
            <i class="fa fa-chevron-left" style="font-size: 15px;margin-right:8px;"></i>
            <i class="fa fa-th-large" style="font-size: 14px; line-height: 16px; vertical-align: top; margin-right:4px;"></i>
            <span style="font-size: 14px;line-height: 16px;vertical-align: top;" data-bind="text: definition.name"></span>
          </a>
          <!-- /ko -->
          <!-- ko if: definition.host === '' -->
          ${_('Clusters')}
          <!-- /ko -->

          <!-- ko template: 'assist-hbase-header-actions' --><!-- /ko -->
        </div>
        <div class="assist-flex-fill assist-hbase-scrollable">
          <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
            <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 20, container: '.assist-hbase-scrollable' }">
              <li class="assist-entry assist-table-link" style="position: relative;" data-bind="visibleOnHover: { 'selector': '.assist-actions' }">
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
              <li class="assist-entry" style="font-style: italic;">
                <!-- ko if: definition.host === '' -->
                ${_('No clusters available.')}
                <!-- /ko -->
                <!-- ko if: definition.host !== '' -->
                ${_('No tables available.')}
                <!-- /ko -->
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
      </div>
      <!-- ko with: $parents[1] -->
      <!-- ko template: { if: searchActive() && searchInput() !== '' && navigatorEnabled(), name: 'nav-search-result' } --><!-- /ko -->
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

  <script type="text/html" id="ask-for-invalidate-title">
    <a class="pull-right pointer close-popover inactive-action"><i class="fa fa-times"></i></a>
  </script>

  <script type="text/html" id="ask-for-invalidate-content">
    <label class="radio" style="margin-bottom: 2px;">
      <input type="radio" name="refreshImpala" value="cache" data-bind="checked: invalidateOnRefresh" />
      ${ _('Clear cache') }
    </label>
    <label class="radio" style="margin-bottom: 2px;">
      <input type="radio" name="refreshImpala" value="invalidate" data-bind="checked: invalidateOnRefresh" />
      ${ _('Perform incremental metadata update') }
    </label>
    <div style="display: inline-block; margin-left: 20px; font-style: italic; color: #999;">${ _('This will sync missing tables in Hive.') }</div>
    <label class="radio" style="margin-bottom: 2px;">
      <input type="radio" name="refreshImpala" value="invalidateAndFlush" data-bind="checked: invalidateOnRefresh"  />
      ${ _('Invalidate all metadata and rebuild index') }
    </label>
    <div style="display: inline-block; margin-left: 20px; font-style: italic; color: #999;">${ _('WARNING: This can be both resource and time-intensive.') }</div>
    <div style="width: 100%; display: inline-block; margin-top: 5px;"><button class="pull-right btn btn-primary" data-bind="css: { 'btn-primary': invalidateOnRefresh() !== 'invalidateAndFlush', 'btn-danger': invalidateOnRefresh() === 'invalidateAndFlush' }, click: function (data, event) { huePubSub.publish('close.popover'); triggerRefresh(data, event); }, clickBubble: false">${ _('Refresh') }</button></div>
  </script>

  <script type="text/html" id="assist-db-header-actions">
    <div class="assist-db-header-actions">
      <span class="assist-tables-counter">(<span data-bind="text: filteredEntries().length"></span>)</span>
      <!-- ko ifnot: loading -->
      <!-- ko if: $parent.activeSort && isSearchVisible() -->
      <a class="inactive-action" data-toggle="dropdown" href="javascript:void(0)"><i class="pointer fa fa-sort" title="${_('Sort')}"></i></a>
      <ul class="dropdown-menu hue-inner-drop-down" style="top: initial; left: inherit; position: fixed; z-index:10000;">
        <li><a href="javascript:void(0)" data-bind="click: function () { $parent.activeSort('creation'); }"><i class="fa fa-fw" data-bind="css: { 'fa-check': $parent.activeSort() === 'creation' }"></i> ${ _('Default') }</a></li>
        <li><a href="javascript:void(0)" data-bind="click: function () { $parent.activeSort('alpha'); }"><i class="fa fa-fw" data-bind="css: { 'fa-check': $parent.activeSort() === 'alpha' }"></i> ${ _('Alphabetical') }</a></li>
        <!-- ko if: HAS_OPTIMIZER -->
        <li><a href="javascript:void(0)" data-bind="click: function () { $parent.activeSort('popular'); }"><i class="fa fa-fw" data-bind="css: { 'fa-check': $parent.activeSort() === 'popular' }"></i> ${ _('Popularity') }</a></li>
        <!-- /ko -->
      </ul>
      <!-- /ko -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: toggleSearch, css: { 'blue' : isSearchVisible }"><i class="pointer fa fa-filter" title="${_('Filter')}"></i></a>
      % if ENABLE_NEW_CREATE_TABLE.get():
        <!-- ko if: sourceType === 'hive' || sourceType === 'impala' -->
        <!-- ko if: typeof databaseName !== 'undefined' -->
        <a class="inactive-action" href="javascript:void(0)" data-bind="attr: { 'href': '${ url('indexer:importer_prefill', source_type='all', target_type='table') }' + databaseName }"><i class="pointer fa fa-plus" title="${_('Create table')}"></i></a>
        <!-- /ko -->
        <!-- ko if: typeof databases !== 'undefined' -->
        <a class="inactive-action" href="javascript:void(0)" data-bind="attr: { 'href': '${ url('indexer:importer_prefill', source_type='manual', target_type='database') }' }"><i class="pointer fa fa-plus" title="${_('Create database')}"></i></a>
        <!-- /ko -->
        <!-- /ko -->
      % endif
      <!-- ko if: sourceType === 'impala' -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="templatePopover : { contentTemplate: 'ask-for-invalidate-content', titleTemplate: 'ask-for-invalidate-title', trigger: 'click', minWidth: '320px' }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manually refresh the table list')}"></i></a>
      <!-- /ko -->
      <!-- ko if: sourceType !== 'impala' -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: triggerRefresh"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manually refresh the table list')}"></i></a>
      <!-- /ko -->
      <!-- /ko -->
      <!-- ko if: loading -->
      <span style="color: #aaa;"><i class="fa fa-filter" title="${_('Filter tables')}"></i></span>
      <i class="fa fa-refresh fa-spin blue" title="${_('Manually refresh the table list')}"></i>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="assist-databases-template">
    <div class="assist-flex-header" data-bind="visibleOnHover: { selector: '.hover-actions', override: loading() || isSearchVisible() }">
      <div class="assist-inner-header">
        ${_('Databases')}
        <!-- ko template: 'assist-db-header-actions' --><!-- /ko -->
      </div>
    </div>
    <div class="assist-flex-search" data-bind="visible: hasEntries() && isSearchVisible() && ! hasErrors()">
      <div class="assist-filter"><input id="searchInput" class="clearable" type="text" placeholder="${ _('Database name...') }" style="margin-top:3px;" data-bind="hasFocus: editingSearch, clearable: filter.query, value: filter.query, valueUpdate: 'afterkeydown'"/></div>
    </div>
    <div class="assist-flex-fill assist-db-scrollable" data-bind="visible: ! hasErrors() && ! loading() && hasEntries()">
      <!-- ko if: ! loading() && filteredEntries().length == 0 -->
      <ul class="assist-tables">
        <li class="assist-entry no-entries">${_('No results found')}</li>
      </ul>
      <!-- /ko -->
      <ul class="assist-tables" data-bind="foreachVisible: {data: filteredEntries, minHeight: 20, container: '.assist-db-scrollable' }">
        <li class="assist-table" data-bind="visibleOnHover: { selector: '.database-actions' }">
          <!-- ko template: { name: 'assist-entry-actions' } --><!-- /ko -->
          <a class="assist-table-link" href="javascript: void(0);" data-bind="click: function () { $parent.selectedDatabase($data); $parent.selectedDatabaseChanged(); }"><i class="fa fa-fw fa-database muted valign-middle"></i> <span class="highlightable" data-bind="text: definition.name, css: { 'highlight': highlight() }"></span></a>
        </li>
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
        ${_('Tables')}
        <!-- ko template: 'assist-db-header-actions' --><!-- /ko -->
      </div>
    </div>
    <div class="assist-flex-table-search" data-bind="visible: hasEntries() && isSearchVisible() && !$parent.loading() && !$parent.hasErrors()">
      <div>
        <label class="checkbox inline-block margin-left-5"><input type="checkbox" data-bind="checked: filter.showTables" />${_('Tables')}</label>
        <label class="checkbox inline-block margin-left-10"><input type="checkbox" data-bind="checked: filter.showViews" />${_('Views')}</label>
        <!-- ko if: filter.enableActiveFilter --><label class="checkbox inline-block margin-left-10"><input type="checkbox" data-bind="checked: filter.showActive" />${_('Active')}</label><!-- /ko -->
      </div>
      <div class="assist-filter"><input id="searchInput" class="clearable" type="text" placeholder="${ _('Table name...') }" data-bind="hasFocus: editingSearch, clearable: filter.query, value: filter.query, valueUpdate: 'afterkeydown'"/></div>
    </div>
    <div class="assist-flex-fill assist-db-scrollable" data-bind="visible: ! hasErrors() && ! loading()">
      <!-- ko template: 'assist-db-entries' --><!-- /ko -->
    </div>
    <div class="assist-flex-fill" data-bind="visible: loading() || $parent.loading()">
      <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
    </div>
    <div class="assist-flex-fill" data-bind="visible: hasErrors() && ! loading()">
      <span class="assist-errors">${ _('Error loading tables.') }</span>
    </div>
  </script>

  <style>
    .nav-autocomplete-item .ui-state-focus {
      border: 1px solid #DBE8F1;
      background-color: #DBE8F1 !important;
    }

    .nav-autocomplete-item-link {
      height: 44px;
      overflow:hidden;
    }

    .nav-autocomplete-item-link i {
      font-size: 18px;
      color: #338bb8;
    }

    .nav-autocomplete-item-link em, .result-entry em {
      font-style: normal;
      font-weight: bold;
    }

    .nav-autocomplete-item-link > div {
      vertical-align: top;
      display:inline-block;
    }

    .nav-autocomplete-divider {
      height: 2px;
      border-top: 1px solid #dddddd;
    }
  </style>

  <script type="text/html" id="nav-search-autocomp-item">
    <a>
      <div class="nav-autocomplete-item-link">
        <div style="padding: 12px 8px 0 8px;"><i class="fa fa-fw" data-bind="css: icon"></i></div>
        <div>
          <div style="font-size: 14px; color: #338bb8" data-bind="html: label, style: { 'padding-top': description ? 0 : '10px' }"></div>
          <!-- ko if: description -->
          <div style="display:inline-block; width: 250px; overflow: hidden; white-space: nowrap; text-overflow:ellipsis; font-size: 12px;" data-bind="html: description"></div>
          <!-- /ko -->
        </div>
      </div>
    </a>
  </script>

  <script type="text/html" id="nav-search-autocomp-no-match">
    <div class="nav-autocomplete-item-link" style="height: 30px;">
      <div style="font-size: 12px; margin: 6px 8px; color: #737373; font-style: italic;">${ _('No recent match found') }</div>
    </div>
  </script>

  <script type="text/html" id="assist-panel-navigator-search">
    <!-- ko if: navigatorEnabled -->
      <div class="search-container" data-bind="style: { 'padding-right': tabsEnabled ? null : '20px' }">
        <input placeholder="${ _('Search...') }" type="text" data-bind="autocomplete: {
          source: navAutocompleteSource,
          itemTemplate: 'nav-search-autocomp-item',
          noMatchTemplate: 'nav-search-autocomp-no-match',
          classPrefix: 'nav-',
          showOnFocus: true,
          onEnter: performSearch,
          valueObservable: searchInput,
          onSelect: performSearch,
          reopenPattern: /.*:$/
        },
        hasFocus: searchHasFocus,
        clearable: { value: searchInput, onClear: function () { searchActive(false); huePubSub.publish('autocomplete.close'); } },
        textInput: searchInput,
        valueUpdate: 'afterkeydown',
        attr: { placeholder: '${ _('Search ') }' + $parent.name.replace(/s$/g, '') + ($parent.type == 'sql' ? '${ _(' tables') }' : '${ _(' files') }' ) + '...' }">
        <a class="inactive-action" data-bind="click: performSearch"><i class="fa fa-search" data-bind="css: { 'blue': searchHasFocus() || searchActive() }"></i></a>
      </div>
    <!-- /ko -->
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
    <div style="display: -ms-flexbox; display: flex; -ms-flex-direction: column; flex-direction: column; position:relative; height: 100%; overflow: hidden;">
      <!-- ko if: availablePanels.length > 1 -->
      <div style="position: relative; flex: 0 0 40px; line-height: 40px;" class="assist-panel-switches">
        <!-- ko foreach: availablePanels -->
        <div class="inactive-action assist-type-switch" data-bind="click: function () { $parent.visiblePanel($data); }, css: { 'blue': $parent.visiblePanel() === $data }, style: { 'float': rightAlignIcon ? 'right' : 'left' },  attr: { 'title': name }">
          <i class="fa fa-fw valign-middle" data-bind="css: icon"></i>
        </div>
        <!-- /ko -->
      </div>
      <!-- /ko -->
      <!-- ko with: visiblePanel -->
      <!-- ko template: { if: showNavSearch && $parent.navigatorEnabled, name: 'assist-panel-navigator-search', data: $parent }--><!-- /ko -->
      <div style="position: relative; -ms-flex: 1 1 100%; flex: 1 1 100%; overflow: hidden; padding-top: 10px;" data-bind="style: { 'padding-top': $parent.availablePanels.length > 1 ? '10px' : '5px' }">
        <!-- ko template: { name: templateName, data: panelData } --><!-- /ko -->
      </div>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="nav-search-result">
    <div style="position:absolute; left:0; right: 0; top: 0; bottom: 0; overflow: hidden; background-color: #FFF;" data-bind="niceScroll">
      <div class="assist-inner-header" style="width: inherit;">${ _('Search result') }
        <div class="assist-db-header-actions">
          <span class="assist-tables-counter" data-bind="visible: searchResult().length > 0">(<span data-bind="text: searchResultCount">0</span>)</span>
          <a class="inactive-action" href="javascript:void(0)" data-bind="click: function() { searchActive(false); }"><i class="pointer fa fa-times" title="${ _('Close') }"></i></a>
        </div>
      </div>
      <!-- ko hueSpinner: { spin: searching, center: true, size: 'large' } --><!-- /ko -->
      <!-- ko if: !searching() -->
      <!-- ko if: searchResult().length == 0 -->
        <div class="result-entry">${ _('No result found.') }</div>
      <!-- /ko -->
      <div data-bind="foreach: searchResult" style="overflow-x:hidden">
        <div class="result-entry" data-bind="visibleOnHover: { override: statsVisible, selector: '.table-actions' }, event: { mouseover: showNavContextPopoverDelayed, mouseout: clearNavContextPopoverDelay }">
          <div class="icon-col">
            <i class="fa fa-fw valign-middle" data-bind="css: icon"></i>
          </div>
          <div class="doc-col" data-bind="css: { 'doc-col-no-desc' : !hasDescription }">
            <!-- ko if: typeof click !== 'undefined' -->
            <a class="pointer" data-bind="click: click, html: hue_name" target="_blank" ></a>
            <!-- /ko -->
            <!-- ko if: typeof click === 'undefined' && typeof link !== 'undefined'-->
            <a class="pointer" data-bind="attr: { 'href': link }, text: originalName" target="_blank" ></a>
            <!-- /ko -->
            <div class="doc-desc" data-bind="html: hue_description"></div>
          </div>
        </div>
      </div>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/javascript" charset="utf-8">
    (function () {
      ko.bindingHandlers.assistFileDroppable = {
        init: function(element, valueAccessor, allBindings, boundEntry) {
          var dragData;
          huePubSub.subscribe('doc.browser.dragging', function (data) {
            dragData = data;
          });
          var $element = $(element);
          if (boundEntry.isDirectory) {
            $element.droppable({
              drop: function () {
                if (dragData && !dragData.dragToSelect) {
                  boundEntry.moveHere(dragData.selectedEntries);
                  dragData.originEntry.load();
                }
              },
              over: function () {
                if (dragData && !dragData.dragToSelect) {
                  $element.addClass('assist-file-entry-drop');
                }
              },
              out: function () {
                $element.removeClass('assist-file-entry-drop');
              }
            })
          }
        }
      };

      /**
       * @param {Object} options
       * @param {ApiHelper} options.apiHelper
       * @param {string} options.type
       * @param {number} options.minHeight
       * @param {string} options.icon
       * @param {boolean} [options.rightAlignIcon] - Default false
       * @param {boolean} options.visible
       * @param {boolean} [options.showNavSearch] - Default true
       * @param {(AssistDbPanel|AssistHdfsPanel|AssistDocumentsPanel|AssistS3Panel|AssistCollectionsPanel)} panelData
       * @constructor
       */
      function AssistInnerPanel (options) {
        var self = this;
        self.minHeight = options.minHeight;
        self.icon = options.icon;
        self.type = options.type;
        self.name = options.name;
        self.panelData = options.panelData;
        self.showNavSearch = typeof options.showNavSearch !== 'undefined' ? options.showNavSearch : true;
        self.rightAlignIcon = !!options.rightAlignIcon;

        self.visible = ko.observable(options.visible || true);
        options.apiHelper.withTotalStorage('assist', 'showingPanel_' + self.type, self.visible, false, options.visible);
        self.templateName = 'assist-' + self.type + '-inner-panel';

        var loadWhenVisible = function () {
          if (! self.visible()) {
            return;
          }
          if (self.type === 'documents' && !self.panelData.activeEntry().loaded()) {
            self.panelData.activeEntry().load();
          }
        };

        self.visible.subscribe(loadWhenVisible);
        loadWhenVisible();
      }

      /**
       * @param {Object} options
       * @param {ApiHelper} options.apiHelper
       * @param {Object} options.i18n
       * @param {Object[]} options.sourceTypes - All the available SQL source types
       * @param {string} options.sourceTypes[].name - Example: Hive SQL
       * @param {string} options.sourceTypes[].type - Example: hive
       * @param {string} [options.activeSourceType] - Example: hive
       * @param {Object} options.navigationSettings - enable/disable the links
       * @param {boolean} options.navigationSettings.openItem
       * @param {boolean} options.navigationSettings.showStats
       * @param {boolean} options.navigationSettings.pinEnabled
       * @constructor
       **/
      function AssistDbPanel(options) {
        var self = this;
        self.options = options;
        self.apiHelper = options.apiHelper;
        self.i18n = options.i18n;

        self.sources = ko.observableArray();
        self.sourceIndex = {};
        $.each(options.sourceTypes, function (idx, sourceType) {
          self.sourceIndex[sourceType.type] = new AssistDbSource({
            apiHelper: self.apiHelper,
            i18n: self.i18n,
            type: sourceType.type,
            name: sourceType.name,
            navigationSettings: options.navigationSettings
          });
          self.sources.push(self.sourceIndex[sourceType.type]);
        });

        huePubSub.subscribe('assist.db.highlight', function (location) {
          huePubSub.publish('assist.hide.search');
          var foundSource;
          $.each(self.sources(), function (idx, source) {
            if (source.sourceType === location.sourceType) {
              foundSource = source;
              return false;
            }
          });
          if (foundSource) {
            if (foundSource.hasEntries()) {
              self.selectedSource(foundSource);
              foundSource.highlightInside(location.path);
            } else {
              foundSource.initDatabases(function () {
                self.selectedSource(foundSource);
                foundSource.highlightInside(location.path);
              });
            }
          }
        });

        self.selectedSource = ko.observable(null);

        self.setDatabaseWhenLoaded = function (databaseName) {
          if (self.selectedSource().loaded()) {
            self.selectedSource().setDatabase(databaseName);
          } else {
            var subscription = self.selectedSource().loaded.subscribe(function (newValue) {
              if (newValue) {
                self.selectedSource().setDatabase(databaseName);
                subscription.dispose();
              }
            });
            if (!self.selectedSource().loaded() && !self.selectedSource().loading()) {
              self.selectedSource().initDatabases();
            }
          }
        };

        huePubSub.subscribe("assist.set.database", function (databaseDef) {
          if (!databaseDef.source || !self.sourceIndex[databaseDef.source]) {
            return;
          }
          self.selectedSource(self.sourceIndex[databaseDef.source]);
          self.setDatabaseWhenLoaded(databaseDef.name);
        });

        huePubSub.subscribe("assist.get.database", function (source) {
          if (self.sourceIndex[source] && self.sourceIndex[source].selectedDatabase()) {
            huePubSub.publish("assist.database.set", {
              source: source,
              name: self.sourceIndex[source].selectedDatabase().databaseName
            });
          } else {
            huePubSub.publish("assist.database.set", {
              source: source,
              name: null
            });
          }
        });

        huePubSub.publish("assist.db.panel.ready");

        self.selectedSource.subscribe(function (newSource) {
          if (newSource) {
            if (newSource.databases().length === 0) {
              newSource.initDatabases();
            }
            self.apiHelper.setInTotalStorage('assist', 'lastSelectedSource', newSource.sourceType);
          } else {
            self.apiHelper.setInTotalStorage('assist', 'lastSelectedSource');
          }
        });

        self.breadcrumb = ko.computed(function () {
          if (self.selectedSource()) {
            if (self.selectedSource().selectedDatabase()) {
              return self.selectedSource().selectedDatabase().definition.name;
            }
            return self.selectedSource().name;
          }
          return null;
        });
      }

      AssistDbPanel.prototype.back = function () {
        var self = this;
        if (self.selectedSource() && self.selectedSource().selectedDatabase()) {
          self.selectedSource().selectedDatabase(null)
        } else if (self.selectedSource()) {
          self.selectedSource(null);
        }
      };

      AssistDbPanel.prototype.init = function () {
        var self = this;
        var storageSourceType = self.apiHelper.getFromTotalStorage('assist', 'lastSelectedSource');

        if (!self.selectedSource()) {
          if (self.options.activeSourceType) {
            self.selectedSource(self.sourceIndex[self.options.activeSourceType]);
            self.setDatabaseWhenLoaded();
          } else if (storageSourceType && self.sourceIndex[storageSourceType]) {
            self.selectedSource(self.sourceIndex[storageSourceType]);
            self.setDatabaseWhenLoaded();
          }
        }
      };

      /**
       * @param {Object} options
       * @param {ApiHelper} options.apiHelper
       * @param {string} options.user
       * @param {Object} options.i18n
       * @constructor
       **/
      function AssistDocumentsPanel (options) {
        var self = this;

        self.activeEntry = ko.observable();
        self.activeEntry(new HueFileEntry({
          activeEntry: self.activeEntry,
          trashEntry: ko.observable,
          apiHelper: options.apiHelper,
          app: 'documents',
          user: options.user,
          activeSort: ko.observable('name'),
          definition: {
            name: '/',
            type: 'directory'
          }
        }));

        huePubSub.subscribe('assist.document.refresh', function () {
          huePubSub.publish('assist.clear.document.cache');
          self.reload();
        });
      }

      AssistDocumentsPanel.prototype.init = function () {
        var self = this;
        if (! self.activeEntry().loaded()) {
          self.activeEntry().load();
        }
      };

      /**
       * @param {Object} options
       * @param {ApiHelper} options.apiHelper
       * @constructor
       **/
      function AssistHdfsPanel (options) {
        var self = this;
        self.apiHelper = options.apiHelper;

        self.selectedHdfsEntry = ko.observable();
        self.reload = function () {
          var lastKnownPath = self.apiHelper.getFromTotalStorage('assist', 'currentHdfsPath', '${ home_dir }');
          var parts = lastKnownPath.split('/');
          parts.shift();

          var currentEntry = new AssistHdfsEntry({
            definition: {
              name: '/',
              type: 'dir'
            },
            parent: null,
            apiHelper: self.apiHelper
          });

          currentEntry.loadDeep(parts, function (entry) {
            self.selectedHdfsEntry(entry);
            entry.open(true);
          });
        };

        huePubSub.subscribe('assist.selectHdfsEntry', function (entry) {
          self.selectedHdfsEntry(entry);
          self.apiHelper.setInTotalStorage('assist', 'currentHdfsPath', entry.path);
        });

        huePubSub.subscribe('assist.hdfs.refresh', function () {
          huePubSub.publish('assist.clear.hdfs.cache');
          self.reload();
        });
      }

      AssistHdfsPanel.prototype.init = function () {
        this.reload();
      };


      /**
       * @param {Object} options
       * @param {ApiHelper} options.apiHelper
       * @constructor
       **/
      function AssistS3Panel (options) {
        var self = this;
        self.apiHelper = options.apiHelper;

        self.selectedS3Entry = ko.observable();
        self.reload = function () {
          var lastKnownPath = self.apiHelper.getFromTotalStorage('assist', 'currentS3Path', '/');
          var parts = lastKnownPath.split('/');
          parts.shift();

          var currentEntry = new AssistS3Entry({
            definition: {
              name: '/',
              type: 'dir'
            },
            parent: null,
            apiHelper: self.apiHelper
          });

          currentEntry.loadDeep(parts, function (entry) {
            self.selectedS3Entry(entry);
            entry.open(true);
          });
        };

        huePubSub.subscribe('assist.selectS3Entry', function (entry) {
          self.selectedS3Entry(entry);
          self.apiHelper.setInTotalStorage('assist', 'currentS3Path', entry.path);
        });

        huePubSub.subscribe('assist.s3.refresh', function () {
          huePubSub.publish('assist.clear.s3.cache');
          self.reload();
        });
      }

      AssistS3Panel.prototype.init = function () {
        this.reload();
      };

      /**
       * @param {Object} options
       * @param {ApiHelper} options.apiHelper
       * @constructor
       **/
      function AssistCollectionsPanel (options) {
        var self = this;
        self.apiHelper = options.apiHelper;

        self.isSearchVisible = ko.observable(false);
        self.editingSearch = ko.observable(false);

        self.toggleSearch = function () {
          self.isSearchVisible(!self.isSearchVisible());
          self.editingSearch(self.isSearchVisible());
        };

        self.showCores = ko.observable(false);
        self.selectedCollectionEntry = ko.observable();
        self.filter = ko.observable('');
        self.reload = function () {
          var currentEntry = new AssistCollectionEntry({
            definition: {
              name: '/',
              type: 'collection'
            },
            apiHelper: self.apiHelper
          }, self.filter, self.showCores);
          self.selectedCollectionEntry(currentEntry);
          currentEntry.loadEntries();
          currentEntry.hasOnlyCores.subscribe(function (onlyCores) {
            self.showCores(onlyCores);
          });
          self.showCores(currentEntry.hasOnlyCores());
        };

        huePubSub.subscribe('assist.clickCollectionItem', function (entry) {

        });

        huePubSub.subscribe('assist.dblClickCollectionItem', function (entry) {
          window.open('/indexer/#edit/' + entry.definition.name);
        });

        huePubSub.subscribe('assist.collections.refresh', function () {
          huePubSub.publish('assist.clear.collections.cache');
          self.reload();
        });
      }

      AssistCollectionsPanel.prototype.init = function () {
        this.reload();
      };

      /**
       * @param {Object} options
       * @param {ApiHelper} options.apiHelper
       * @constructor
       **/
      function AssistHBasePanel(options) {
        var self = this;
        self.apiHelper = options.apiHelper;

        var root = new AssistHBaseEntry({
          definition: {
            host: '',
            name: '',
            port: 0
          },
          apiHelper: self.apiHelper
        });

        self.selectedHBaseEntry = ko.observable();
        self.reload = function () {
          self.selectedHBaseEntry(root);
          root.loadEntries();
        };

        huePubSub.subscribe('assist.clickHBaseItem', function (entry) {
          if (entry.definition.host) {
            entry.loadEntries();
            self.selectedHBaseEntry(entry);
          }
        });

        huePubSub.subscribe('assist.clickHBaseRootItem', function (entry) {
          self.reload();
        });

        huePubSub.subscribe('assist.dblClickHBaseItem', function (entry) {
          window.open('/hbase/#' + self.selectedHBaseEntry().definition.name + '/' + entry.definition.name);
        });

        huePubSub.subscribe('assist.hbase.refresh', function () {
          huePubSub.publish('assist.clear.hbase.cache');
          self.reload();
        });
      }

      AssistHBasePanel.prototype.init = function () {
        this.reload();
      };

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
          errorLoadingTablePreview: "${ _('There was a problem loading the table preview.') }",
          documentTypes: {
            'query-hive': "${ _('Hive Query') }",
            'query': "${ _('Query') }",
            'notebook': "${ _('Notebook') }"
          }
        };
        self.apiHelper = ApiHelper.getInstance({
          i18n: i18n,
          user: params.user
        });

        self.navigatorEnabled = ko.observable('${ has_navigator(user) }' === 'True');
        self.tabsEnabled = '${ USE_NEW_SIDE_PANELS.get() }' === 'True';

        self.searchInput = ko.observable('').extend({rateLimit: 500});
        self.searchResult = ko.observableArray();
        self.searchResultCount = ko.observable();

        self.searchHasFocus = ko.observable(false);
        self.searching = ko.observable(false);
        self.searchActive = ko.observable(false);

        huePubSub.subscribe('assist.hide.search', function () {
          self.searchActive(false);
        });

        var lastQuery = -1;

        self.availablePanels = [
          new AssistInnerPanel({
            panelData: new AssistDbPanel($.extend({
              apiHelper: self.apiHelper,
              i18n: i18n
            }, params.sql)),
            apiHelper: self.apiHelper,
            name: '${ _("SQL") }',
            type: 'sql',
            icon: 'fa-database',
            minHeight: 75
          })
        ];

        if (self.tabsEnabled) {
          self.availablePanels.push(new AssistInnerPanel({
            panelData: new AssistHdfsPanel({
              apiHelper: self.apiHelper
            }),
            apiHelper: self.apiHelper,
            name: '${ _("HDFS") }',
            type: 'hdfs',
            icon: 'fa-folder-o',
            minHeight: 50
          }));

          if (window.IS_S3_ENABLED) { // coming from common_header.mako
            self.availablePanels.push(new AssistInnerPanel({
              panelData: new AssistS3Panel({
                apiHelper: self.apiHelper
              }),
              apiHelper: self.apiHelper,
              name: '${ _("S3") }',
              type: 's3',
              icon: 'fa-cubes',
              minHeight: 50
            }));
          }

          self.availablePanels.push(new AssistInnerPanel({
            panelData: new AssistCollectionsPanel({
              apiHelper: self.apiHelper
            }),
            apiHelper: self.apiHelper,
            name: '${ _("Collections") }',
            type: 'collections',
            icon: 'fa-search-plus',
            minHeight: 50,
            showNavSearch: false
          }));

          self.availablePanels.push(new AssistInnerPanel({
            panelData: new AssistHBasePanel({
              apiHelper: self.apiHelper
            }),
            apiHelper: self.apiHelper,
            name: '${ _("HBase") }',
            type: 'hbase',
            icon: 'fa-th-large',
            minHeight: 50,
            showNavSearch: false
          }));

          self.availablePanels.push(new AssistInnerPanel({
            panelData: new AssistDocumentsPanel({
              user: params.user,
              apiHelper: self.apiHelper,
              i18n: i18n
            }),
            apiHelper: self.apiHelper,
            name: '${ _("Documents") }',
            type: 'documents',
            icon: 'fa-files-o',
            minHeight: 50,
            rightAlignIcon: true,
            visible: params.visibleAssistPanels && params.visibleAssistPanels.indexOf('documents') !== -1
          }));
        }

        self.performSearch = function () {
          huePubSub.publish('autocomplete.close');
          if (self.searchInput() === '') {
            self.searchActive(false);
            return;
          }
          if (!self.searchActive()) {
            self.searchActive(true);
          } else if (self.searchInput() === lastQuery) {
            return;
          }
          if (self.searching()) {
            window.setTimeout(function() {
              self.performSearch();
            }, 100);
            return;
          }
          lastQuery = self.searchInput();
          self.searching(true);

          var showInAssist = function (entry) {
            self.searchInput('');
            self.searchHasFocus(false);
            var path = entry.parentPath.split('/').concat([entry.originalName]).splice(1);
            window.setTimeout(function () {
              huePubSub.publish('assist.db.highlight', { sourceType: entry.sourceType.toLowerCase(), path: path });
            }, 200); // For animation effect
          };

          var showNavContextPopover = function (entry, event) {
            if (entry.type && entry.type !== 'TABLE' && entry.type !== 'VIEW' && entry.type !== 'DATABASE' && entry.type !== 'FIELD') {
              return;
            }
            var $source = $(event.target).closest('.result-entry');
            var offset = $source.offset();
            entry.statsVisible(true);
            huePubSub.publish('sql.context.popover.show', {
              data: {
                type: entry.type === 'FIELD' ? 'column' : (entry.type === 'DATABASE' ? 'database' : 'table'),
                identifierChain: $.map(entry.parentPath.substring(1).split('/'), function (part) { return { name: part } }).concat({ name: entry.originalName })
              },
              delayedHide: '.result-entry',
              orientation: 'right',
              sourceType: entry.sourceType.toLowerCase(),
              defaultDatabase: entry.parentPath.substring(1),
              pinEnabled: params.sql.navigationSettings.pinEnabled,
              source: {
                element: event.target,
                left: offset.left,
                top: offset.top - 3,
                right: offset.left + $source.width() + 3,
                bottom: offset.top + $source.height() - 3
              }
            });
            huePubSub.subscribeOnce('sql.context.popover.hidden', function () {
              entry.statsVisible(false);
            });
          };

          var navContextPopoverTimeout = -1;

          var showNavContextPopoverDelayed = function (entry, event) {
            window.clearTimeout(navContextPopoverTimeout);
            navContextPopoverTimeout = window.setTimeout(function () {
              showNavContextPopover(entry, event);
            }, 500);
          };

          var clearNavContextPopoverDelay = function () {
            window.clearTimeout(navContextPopoverTimeout);
          };

          $.post('/desktop/api/search/entities', {
            query_s: ko.mapping.toJSON(self.searchInput()),
            limit: 25,
            sources: ko.mapping.toJSON([self.visiblePanel().type])
          }, function (data) {
            data.entities.forEach(function (entity) {
              entity.statsVisible = ko.observable(false);
              entity.showNavContextPopoverDelayed = showNavContextPopoverDelayed;
              entity.clearNavContextPopoverDelay = clearNavContextPopoverDelay;
              entity.icon = NAV_TYPE_ICONS[entity.type];
              switch (entity.type) {
                case 'DATABASE': { }
                case 'TABLE': { }
                case 'VIEW': { }
                case 'FIELD': {
                  entity.click = function () {
                    showInAssist(entity);
                  };
                  break;
                }
                case 'SOURCE': {
                  entity.originalDescription = '${ _("Cluster") }: ' + entity.clusterName;
                  entity.link = entity.sourceUrl;
                  break;
                }
                case 'OPERATION_EXECUTION': {
                  entity.link = '/jobbrowser/jobs/' + entity.jobID;
                  break;
                }
                case 'DIRECTORY': {
                  entity.originalDescription = entity.parentPath;
                  if (entity.sourceType == 'S3') {
                    entity.link = '/filebrowser/view=S3A://#s3a://' + entity.bucketName + '/' + entity.fileSystemPath;
                  } else {
                    entity.link = '/filebrowser/#' + entity.fileSystemPath;
                  }
                  break;
                }
                case 'FILE': {
                  entity.originalDescription = entity.parentPath;
                  if (entity.sourceType == 'S3') {
                    entity.link = '/filebrowser/view=S3A://#s3a://' + entity.bucketName + '/' + entity.fileSystemPath;
                  } else {
                    entity.link = '/filebrowser/#' + entity.fileSystemPath;
                  }
                  break;
                }
                case 'S3BUCKET': {
                  entity.originalDescription = '${ _("Region") }: ' + entity.region;
                  entity.link = '/filebrowser/view=S3A://#s3a://' + entity.originalName;
                  break;
                }
                case 'SUB_OPERATION': {
                  entity.originalDescription = entity.metaClassName;
                  break;
                }
                case 'PARTITION': {}
                case 'OPERATION': {}
              }
              entity.hasDescription = typeof entity.originalDescription !== 'undefined' && entity.originalDescription !== null && entity.originalDescription.length > 0;
            });
            self.searchResult(data.entities);
            self.searchResultCount(data.count);
            self.searching(false);
          }).fail(function (xhr, textStatus, errorThrown) {
            $(document).trigger("error", xhr.responseText);
            self.searching(false);
          });
        };

        var lastOpenPanelType = self.apiHelper.getFromTotalStorage('assist', 'last.open.panel', self.availablePanels[0].type);

        var lastFoundPanel = self.availablePanels.filter(function (panel) { return panel.type === lastOpenPanelType });
        var dbPanel = self.availablePanels.filter(function (panel) { return panel.type === 'sql' });
        if (lastFoundPanel.length === 1) {
          dbPanel[0].panelData.init(); // always forces the db panel to load
        }
        self.visiblePanel = ko.observable(lastFoundPanel.length === 1 ? lastFoundPanel[0] : self.availablePanels[0]);

        self.visiblePanel().panelData.init();

        self.visiblePanel.subscribe(function(newValue) {
          self.apiHelper.setInTotalStorage('assist', 'last.open.panel', newValue.type);
          if (self.navigatorEnabled() && self.searchActive()) {
            lastQuery = 'refresh';
            self.performSearch();
          }
          newValue.panelData.init();
        });

        self.navAutocompleteSource = function (request, callback) {
          var facetMatch = request.term.match(/([a-z]+):\s*(\S+)?$/i);
          var isFacet = facetMatch !== null;
          var partialMatch = isFacet ? null : request.term.match(/\S+$/);
          var partial = isFacet && facetMatch[2] ? facetMatch[2] : (partialMatch ? partialMatch[0] : '');
          var beforePartial = request.term.substring(0, request.term.length - partial.length);

          self.apiHelper.navSearchAutocomplete({
            source: self.visiblePanel().type === 'sql' ?
                (self.visiblePanel().panelData.selectedSource() ? self.visiblePanel().panelData.selectedSource().sourceType : 'hive') : self.visiblePanel().type,
            query:  request.term,
            successCallback: function (data) {
              var values = [];
              var facetPartialRe = new RegExp(partial.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&"), 'i'); // Protect for 'tags:*axe'
              if (isFacet && typeof data.facets !== 'undefined') { // Is typed facet, e.g. type: type:bla
                var facetInQuery = facetMatch[1];
                if (typeof data.facets[facetInQuery] !== 'undefined') {
                  $.map(data.facets[facetInQuery], function (count, value) {
                    if (facetPartialRe.test(value)) {
                      values.push({ data: { label: facetInQuery + ':' + value, icon: NAV_FACET_ICON, description: count }, value: beforePartial + value})
                    }
                  });
                }
              } else {
                if (typeof data.facets !== 'undefined') {
                  Object.keys(data.facets).forEach(function (facet) {
                    if (facetPartialRe.test(facet)) {
                      if (Object.keys(data.facets[facet]).length > 0) {
                        values.push({ data: { label: facet + ':', icon: NAV_FACET_ICON, description: $.map(data.facets[facet], function (key, value) { return value + ' (' + key + ')'; }).join(', ') }, value: beforePartial + facet + ':'});
                      } else { // Potential facet from the list
                        values.push({ data: { label: facet + ':', icon: NAV_FACET_ICON, description: '' }, value: beforePartial + facet + ':'});
                      }
                    } else if (partial.length > 0) {
                      Object.keys(data.facets[facet]).forEach(function (facetValue) {
                        if (facetValue.indexOf(partial) !== -1) {
                          values.push({ data: { label: facet + ':' + facetValue, icon: NAV_FACET_ICON, description: facetValue }, value: beforePartial + facet + ':' + facetValue });
                        }
                      });
                    }
                  });
                }
              }

              if (values.length > 0) {
                values.push({ divider: true });
              }
              if (typeof data.results !== 'undefined') {
                data.results.forEach(function (result) {
                  values.push({ data: { label: result.hue_name, icon: NAV_TYPE_ICONS[result.type],  description: result.hue_description }, value: beforePartial + result.originalName });
                });
              }

              if (values.length > 0 && values[values.length - 1].divider) {
                values.pop();
              }
              if (values.length === 0) {
                values.push({ noMatch: true });
              }
              callback(values);
            },
            silenceErrors: true,
            errorCallback: function () {
              callback([]);
            }
          });
        };
      }

      ko.components.register('assist-panel', {
        viewModel: AssistPanel,
        template: { element: 'assist-panel-template' }
      });
    })();
  </script>

  <script type="text/html" id="functions-panel-template">
    <div class="assist-inner-panel">
      <div class="assist-flex-panel">
        <div class="assist-flex-header">
          <div class="assist-inner-header">
            <div class="function-dialect-dropdown" data-bind="component: { name: 'hue-drop-down', params: { value: activeType, entries: availableTypes, linkTitle: '${ _ko('Selected dialect') }' } }" style="display: inline-block"></div>
            <div class="assist-db-header-actions" style="margin-right:10px;">
              <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { searchVisible(!searchVisible()); query(''); }, css: { 'blue' : searchVisible }"><i class="pointer fa fa-filter" title="${ _('Filter') }"></i></a>
            </div>
          </div>
        </div>
        <div class="assist-flex-function-search" data-bind="visible: searchVisible">
          <div class="assist-filter">
            <input class="clearable" type="text" placeholder="Search..." data-bind="clearable: query, value: query, valueUpdate: 'afterkeydown'">
          </div>
        </div>
        <div data-bind="css: { 'assist-flex-fill': !selectedFunction(), 'assist-flex-half': selectedFunction() }">
          <ul class="assist-function-categories" data-bind="foreach: filteredCategories">
            <li>
              <a class="black-link" href="javascript: void(0);" data-bind="toggle: open"><i class="fa fa-fw" data-bind="css: { 'fa-chevron-right': !open(), 'fa-chevron-down': open }"></i> <span data-bind="text: name"></span></a>
              <ul class="assist-functions" data-bind="slideVisible: open, foreach: filteredFunctions">
                <li data-bind="tooltip: { title: description, placement: 'left', delay: 1000 }">
                  <a class="assist-field-link" href="javascript: void(0);" data-bind="css: { 'blue': $parents[1].selectedFunction() === $data }, click: function () { $parents[1].selectedFunction($data); }, text: signature"></a>
                </li>
              </ul>
            </li>
          </ul>
        </div>
        <!-- ko if: selectedFunction -->
        <div class="assist-flex-half assist-function-details" data-bind="with: selectedFunction">
          <div class="assist-function-signature blue" data-bind="text: signature"></div>
          <!-- ko if: description -->
          <div data-bind="text: description"></div>
          <!-- /ko -->
        </div>
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/javascript" charset="utf-8">
    (function () {
      function FunctionsPanel(params) {
        var self = this;
        self.categories = {};
        self.disposals = [];

        self.activeType = ko.observable();
        self.availableTypes = ko.observableArray(['Hive', 'Impala', 'Pig']);
        self.query = ko.observable();
        self.searchVisible = ko.observable(true);
        self.selectedFunction = ko.observable();

        self.availableTypes().forEach(function (type) {
          self.initFunctions(type);
        });

        var selectedFunctionPerType = { 'Hive': null, 'Impala': null, 'Pig': null };
        self.selectedFunction.subscribe(function (newFunction) {
          if (newFunction) {
            selectedFunctionPerType[self.activeType()] = newFunction;
          }
        });

        self.activeCategories = ko.observable();

        self.filteredCategories = ko.pureComputed(function () {
          if (! self.activeCategories()) {
            return [];
          }
          return self.activeCategories().filter(function (category) {
            return category.filteredFunctions().length > 0;
          })
        });

        self.activeType.subscribe(function (newType) {
          self.selectedFunction(selectedFunctionPerType[newType]);
          self.activeCategories(self.categories[newType]);
        });

        self.activeType(self.availableTypes()[0]);

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

        self.disposals.push(huePubSub.subscribe('active.snippet.type.changed', updateType).remove);

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
                signature: fn.signature,
                description: fn.description
              }
            }),
            filteredFunctions: ko.pureComputed(function () {
              if (self.query()) {
                return koCategory.functions.filter(function (fn) {
                  return fn.signature.toLowerCase().indexOf(self.query().toLowerCase()) !== -1 || fn.description.toLowerCase().indexOf(self.query().toLowerCase()) !== -1;
                });
              } else {
                return koCategory.functions;
              }
            })
          };
          self.categories[dialect].push(koCategory)
        });
      };

      ko.components.register('functions-panel', {
        viewModel: FunctionsPanel,
        template: { element: 'functions-panel-template' }
      });
    })();
  </script>

  <script type="text/html" id="assistant-panel-template">
    ${ _('Tables') }
    <!-- ko if: HAS_OPTIMIZER -->
      <a href="javascript:void(0)" data-bind="visible: activeTables().length > 0, click: function() { huePubSub.publish('editor.table.stats.upload', activeTables()); }" title="${ _('Load table and columns stats in order to improve recommendations') }">
        <i class="fa fa-fw fa-cloud-upload"></i>
      </a>
    <!-- /ko -->
    <br/>
    <ul data-bind="foreach: activeTables">
      <li>
        <span data-bind="text: $data"></span> <i class="fa fa-info"></i> <i class="fa fa-fw fa-clock-o muted" title="02/01/2017 10:15 PM"></i>
      </i>
    </ul>

    <form class="form-horizontal">
      <fieldset>
        ${ _('Fields') }<br/>
        <ul>
          <li>'country-code' is a popular field <a href="javascript:void(0)">add</a></li>
          <li>'gender' would be a good dimension with low cardinality (2) <a href="javascript:void(0)">add</a></li>
          <li>'ts_s=17Q1' is the latest partition <a href="javascript:void(0)">add</a></li>
          <li>'f1'</li>
          <li>'f2'</li>
          <li>'f3'</li>
          <li>'f4'</li>
          <li>'f5'</li>
        </ul>
      </fieldset>
    </form>

    <form class="form-horizontal">
      <fieldset>
        ${ _('Suggestions') }<br/>
        <ul>
          <li>Popular fields for the tables are: [code, salary, amount]</li>
          <li>The query would run 2x faster by adding a WHERE date_f > '2017-01-01'</li>
          <li>Parameterize the query?</li>
          <li>Could be automated with integrated scheduler</li>
          <li>Data has not been refreshed since last run 3 days ago  <i class="fa fa-warning"></i> <i class="fa fa-refresh"></i></li></li>
          <li>A schema change happened last week, a new column 'salary_med' was added</li>
          <li>Data statistics are not accurate, click to refresh them</li>
          <li>Query ran 17 times last week</li>
          <li>The datasets are sometimes joined with table [Population]</li>
          <li>Query would be a good candidate to run interactively with Impala</li>
        </ul>
      </fieldset>
    </form>

    <!-- ko if: HAS_OPTIMIZER -->
      <a href="javascript:void(0)" data-bind="click: function() { huePubSub.publish('editor.workload.upload'); }" title="${ _('Load past query history in order to improve recommendations') }">
        <i class="fa fa-fw fa-cloud-upload"></i> ${_('Upload workload')}
      </a>
    <!-- /ko -->
  </script>

  <script type="text/javascript" charset="utf-8">
    (function () {
      function AssistantPanel(params) {
        var self = this;

        self.disposals = [];

        self.activeType = ko.observable();

        self.lastLocationsPerType = ko.observable({});

        self.activeLocations = ko.pureComputed(function () {
          return self.lastLocationsPerType()[self.activeType()] ? self.lastLocationsPerType()[self.activeType()] : [];
        });
        self.activeTables = ko.pureComputed(function () {
          var allTables = $.grep(self.activeLocations(), function(item) { return item.type == 'table'; });
          var tables = [];
          $.each(allTables, function(i, item) {
            var tableName = item.identifierChain[item.identifierChain.length - 1].name;
            if (tables.indexOf(tableName) == -1) {
              tables.push(tableName);
            }
          });
          return tables;
        });

        self.disposals.push(huePubSub.subscribe('active.snippet.type.changed', self.activeType).remove);

        huePubSub.subscribeOnce('set.active.snippet.type', self.activeType);
        huePubSub.publish('get.active.snippet.type');

        self.disposals.push(huePubSub.subscribe('editor.active.locations', function (activeLocations) {
          var locationsIndex = self.lastLocationsPerType();
          locationsIndex[activeLocations.type] = activeLocations.locations;
          self.lastLocationsPerType(locationsIndex);
        }).remove);
      }

      AssistantPanel.prototype.dispose = function () {
        var self = this;
        self.disposals.forEach(function (dispose) {
          dispose();
        })
      };

      ko.components.register('assistant-panel', {
        viewModel: AssistantPanel,
        template: { element: 'assistant-panel-template' }
      });
    })();
  </script>
</%def>
