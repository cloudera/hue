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

from desktop import appmanager
from desktop import conf
from desktop.conf import USE_NEW_SIDE_PANELS, VCS
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko

from metadata.conf import has_navigator, has_navigator_file_search
from metastore.conf import ENABLE_NEW_CREATE_TABLE
from notebook.conf import ENABLE_QUERY_BUILDER, ENABLE_QUERY_SCHEDULING
from notebook.conf import get_ordered_interpreters
%>

<%def name="assistJSModels()">
<script src="${ static('desktop/js/assist/assistDbEntry.js') }"></script>
<script src="${ static('desktop/js/assist/assistDbSource.js') }"></script>
<script src="${ static('desktop/js/assist/assistHdfsEntry.js') }"></script>
<script src="${ static('desktop/js/assist/assistGitEntry.js') }"></script>
<script src="${ static('desktop/js/assist/assistS3Entry.js') }"></script>
<script src="${ static('desktop/js/assist/assistCollectionEntry.js') }"></script>
<script src="${ static('desktop/js/assist/assistHBaseEntry.js') }"></script>
<script src="${ static('desktop/js/document/hueDocument.js') }"></script>
<script src="${ static('desktop/js/document/hueFileEntry.js') }"></script>
</%def>

<%def name="assistPanel(is_s3_enabled=False)">
  <%
    # TODO remove
    try:
      home_dir = user.get_home_directory()
      if not request.fs.isdir(home_dir):
        home_dir = '/'
    except:
      home_dir = '/'
  %>

  <%namespace name="assistSearch" file="assist_search.mako" />
  <%namespace name="sqlContextPopover" file="/sql_context_popover.mako" />
  <%namespace name="nav_components" file="/nav_components.mako" />

  ${ assistSearch.assistSearch() }
  ${ sqlContextPopover.sqlContextPopover() }
  ${ nav_components.nav_tags(readOnly=not user.has_hue_permission(action="write", app="metadata")) }

  <script type="text/html" id="assist-no-database-entries">
    <ul class="assist-tables">
      <li>
        <span class="assist-no-entries">${_('The database has no tables')}</span>
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
      %if has_navigator(user):
      <!-- ko if: sourceType === 'hive' || sourceType === 'impala' -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, click: function (data, event) { showContextPopover(data, event); }, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${_('Show details')}"></i></a>
      <!-- /ko -->
      %endif
      <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.openItem, click: openItem"><i class="fa fa-long-arrow-right" title="${_('Open')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="sql-context-items">
    <!-- ko if: typeof definition !== 'undefined' -->
    <li><a href="javascript:void(0);" data-bind="click: function (data) { showContextPopover(data, { target: $parentContext.$contextSourceElement }, { left: 4, top: 2 }); }"><i class="fa fa-fw fa-info"></i> ${ _('Show details') }</a></li>
    <!-- ko if: !definition.isDatabase && $currentApp() === 'editor' -->
    <li><a href="javascript:void(0);" data-bind="click: dblClick"><i class="fa fa-fw fa-paste"></i> ${ _('Insert at cursor') }</a></li>
    <!-- /ko -->
    <!-- ko if: definition.isView || definition.isTable || definition.isDatabase -->
    <li><a href="javascript:void(0);" data-bind="click: openInMetastore"><i class="fa fa-fw fa-table"></i> ${ _('Open in Metastore') }</a></li>
    <!-- /ko -->
    %if ENABLE_QUERY_BUILDER.get():
    <!-- ko if: definition.isColumn && $currentApp() === 'editor' -->
    <li class="divider"></li>
    <!-- ko template: { name: 'query-builder-context-items' } --><!-- /ko -->
    <!-- /ko -->
    %endif
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
    <li><a href="javascript:void(0);" data-bind="hueLink: definition.url"><i class="fa fa-fw" data-bind="css: {'fa-folder-open-o': definition.type === 'dir', 'fa-file-text-o': definition.type === 'file'}"></i> ${ _('Open in File Browser') }</a></li>
    <!-- ko if: $currentApp() === 'editor' -->
    <li><a href="javascript:void(0);" data-bind="click: dblClick"><i class="fa fa-fw fa-paste"></i> ${ _('Insert at cursor') }</a></li>
    <!-- /ko -->
  </script>

  <script type="text/html" id="document-context-items">
    <!-- ko if: definition().type === 'directory' -->
    <li><a href="javascript: void(0);" data-bind="click: open"><i class="fa fa-fw fa-folder-open-o"></i> ${ _('Open folder') }</a></li>
    <!-- /ko -->
    <!-- ko if: definition().type !== 'directory' -->
    <li><a href="javascript: void(0);" data-bind="click: open"><i class="fa fa-fw fa-edit"></i> ${ _('Open document') }</a></li>
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

  <script type="text/html" id="collections-context-items">
    <li><a href="javascript: void(0);" data-bind="click: open"><!-- ko template: { name: 'app-icon-template', data: { icon: 'indexes' } } --><!-- /ko --> ${ _('Open in Indexer') }</a></li>
  </script>

  <script type="text/html" id="assist-database-entry">
    <li class="assist-table" data-bind="appAwareTemplateContextMenu: { template: 'sql-context-items', scrollContainer: '.assist-db-scrollable' }, visibleOnHover: { selector: '.database-actions' }">
      <!-- ko template: { name: 'assist-database-actions' } --><!-- /ko -->
      <a class="assist-table-link" href="javascript: void(0);" data-bind="click: function () { $parent.selectedDatabase($data); $parent.selectedDatabaseChanged(); }, attr: {'title': definition.title }, draggableText: { text: editorText,  meta: {'type': 'sql', 'database': databaseName} }"><i class="fa fa-fw fa-database muted valign-middle"></i> <span class="highlightable" data-bind="text: definition.name, css: { 'highlight': highlight() }"></span></a>
    </li>
  </script>

  <script type="text/html" id="assist-table-entry">
    <li class="assist-table" data-bind="appAwareTemplateContextMenu: { template: 'sql-context-items', scrollContainer: '.assist-db-scrollable' }, visibleOnHover: { override: statsVisible, selector: '.table-actions' }">
      <div class="assist-actions table-actions" style="opacity: 0">
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, click: showContextPopover, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${_('Show details')}"></i></a>
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.openItem, click: openItem"><i class="fa fa-long-arrow-right" title="${_('Open')}"></i></a>
      </div>
      <a class="assist-entry assist-table-link" href="javascript:void(0)" data-bind="click: toggleOpen, attr: {'title': definition.title }, draggableText: { text: editorText,  meta: {'type': 'sql', 'table': tableName, 'database': databaseName} }">
        <i class="fa fa-fw fa-table muted valign-middle" data-bind="css: { 'fa-eye': definition.isView, 'fa-table': definition.isTable }"></i>
        <span class="highlightable" data-bind="text: definition.displayName, css: { 'highlight': highlight }"></span> <!-- ko if: assistDbSource.activeSort() === 'popular' && popularity() > 0 --><i title="${ _('Popular') }" class="fa fa-star-o top-star"></i> <!-- /ko -->
      </a>
      <div class="center" data-bind="visible: loading"><i class="fa fa-spinner fa-spin assist-spinner"></i></div>
      <!-- ko template: { if: open, name: 'assist-db-entries'  } --><!-- /ko -->
    </li>
  </script>

  <script type="text/html" id="assist-column-entry">
    <li data-bind="appAwareTemplateContextMenu: { template: 'sql-context-items', scrollContainer: '.assist-db-scrollable' }, visible: ! hasErrors(), visibleOnHover: { childrenOnly: true, override: statsVisible, selector: definition.isView ? '.table-actions' : '.column-actions' }, css: { 'assist-table': definition.isView, 'assist-column': definition.isColumn || definition.isComplex }">
      <div class="assist-actions column-actions" style="opacity: 0">
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, click: showContextPopover, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${_('Show details')}"></i></a>
      </div>
      <!-- ko if: expandable -->
      <a class="assist-entry assist-field-link" href="javascript:void(0)" data-bind="click: toggleOpen, attr: {'title': definition.title }">
        <span class="highlightable" data-bind="css: { 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName }, text: definition.displayName, draggableText: { text: editorText, meta: {'type': 'sql', 'column': columnName, 'table': tableName, 'database': databaseName } }"></span><!-- ko if: definition.primary_key === 'true' --> <i class="fa fa-key"></i><!-- /ko -->
      </a>
      <!-- /ko -->
      <!-- ko ifnot: expandable -->
      <div class="assist-entry assist-field-link default-cursor" href="javascript:void(0)" data-bind="event: { dblclick: dblClick }, attr: {'title': definition.title }">
        <span class="highlightable" data-bind="css: { 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName}, text: definition.displayName, draggableText: { text: editorText, meta: {'type': 'sql', 'column': columnName, 'table': tableName, 'database': databaseName} }"></span><!-- ko if: definition.primary_key === 'true'  --> <i class="fa fa-key"></i><!-- /ko --><!-- ko if: assistDbSource.activeSort() === 'popular' && popularity() > 0 --> <i title="${ _('Popular') }" class="fa fa-star-o top-star"></i> <!-- /ko -->
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
      <span class="assist-breadcrumb-text" data-bind="text: breadcrumb, attr: {'title': breadcrumb }"></span>
      <!-- /ko -->
      <!-- ko if: selectedSource()  && ! selectedSource().selectedDatabase() && sources().length > 1 -->
      <a data-bind="click: back">
        <i class="fa fa-chevron-left assist-breadcrumb-back"></i>
        <i class="fa fa-server assist-breadcrumb-text"></i>
        <span class="assist-breadcrumb-text" data-bind="text: breadcrumb, attr: {'title': breadcrumb }"></span>
      </a>
      <!-- /ko -->
      <!-- ko if: selectedSource()  && selectedSource().selectedDatabase() -->
      <a data-bind="click: back">
        <i class="fa fa-chevron-left assist-breadcrumb-back" ></i>
        <i class="fa fa-database assist-breadcrumb-text"></i>
        <span class="assist-breadcrumb-text" data-bind="text: breadcrumb, attr: {'title': breadcrumb }"></span>
      </a>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="assist-sql-inner-panel">
    <!-- ko template: { if: breadcrumb() !== null, name: 'assist-db-breadcrumb' } --><!-- /ko -->
    <!-- ko template: { ifnot: selectedSource, name: 'assist-sources-template' } --><!-- /ko -->
    <!-- ko with: selectedSource -->
    <!-- ko template: { ifnot: selectedDatabase, name: 'assist-databases-template' }--><!-- /ko -->
    <!-- ko with: selectedDatabase -->
    <!-- ko template: { name: 'assist-tables-template' } --><!-- /ko -->
    <!-- /ko -->
    <!-- /ko -->
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
    <div class="assist-db-header-actions">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.s3.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manual refresh')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-s3-inner-panel">
    <!-- ko with: selectedS3Entry -->
    <div class="assist-flex-header assist-breadcrumb" >
      <!-- ko if: parent !== null -->
      <a href="javascript: void(0);" data-bind="click: function () { huePubSub.publish('assist.selectS3Entry', parent); }">
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
      <!-- ko template: 'assist-s3-header-actions' --><!-- /ko -->
    </div>
    <div class="assist-flex-fill assist-s3-scrollable">
      <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
        <!-- ko hueSpinner: { spin: loadingMore, overlay: true } --><!-- /ko -->
        <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 20, container: '.assist-s3-scrollable', fetchMore: $data.fetchMore.bind($data) }">
          <li class="assist-entry assist-table-link" style="position: relative;" data-bind="appAwareTemplateContextMenu: { template: 'hdfs-context-items', scrollContainer: '.assist-s3-scrollable' }, visibleOnHover: { 'selector': '.assist-actions' }">
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
    <div class="assist-flex-fill assist-git-scrollable">
      <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
        <!-- ko hueSpinner: { spin: loadingMore, overlay: true } --><!-- /ko -->
        <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 20, container: '.assist-git-scrollable' }">
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
    <div class="assist-db-header-actions">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.hdfs.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manual refresh')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-hdfs-inner-panel">
    <!-- ko with: selectedHdfsEntry -->
    <div class="assist-flex-header assist-breadcrumb" >
      <!-- ko if: parent !== null -->
      <a href="javascript: void(0);" data-bind="click: function () { huePubSub.publish('assist.selectHdfsEntry', parent); }">
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
      <!-- ko template: 'assist-hdfs-header-actions' --><!-- /ko -->
    </div>
    <div class="assist-flex-fill assist-hdfs-scrollable">
      <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
        <!-- ko hueSpinner: { spin: loadingMore, overlay: true } --><!-- /ko -->
        <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 20, container: '.assist-hdfs-scrollable', fetchMore: $data.fetchMore.bind($data) }">
          <li class="assist-entry assist-table-link" style="position: relative;" data-bind="appAwareTemplateContextMenu: { template: 'hdfs-context-items', scrollContainer: '.assist-hdfs-scrollable' }, visibleOnHover: { 'selector': '.assist-actions' }">
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
    <div class="assist-header-actions">
      <a class="inactive-action" href="javascript:void(0)"><i class="pointer fa fa-filter" title="${_('Filter')}"></i></a>
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.file.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manual refresh')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-documents-inner-panel">
    <!-- ko with: activeEntry -->
    <div class="assist-flex-header assist-document-breadcrumb assist-breadcrumb">
      <!-- ko ifnot: isRoot -->
      <a href="javascript: void(0);" data-bind="click: function () { parent.makeActive(); }">
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
    <div class="assist-flex-fill assist-file-scrollable">
      <div data-bind="visible: ! loading() && ! hasErrors() && entries().length > 0">
         <ul class="assist-tables" data-bind="foreachVisible: {data: entries, minHeight: 20, container: '.assist-file-scrollable' }">
           <li class="assist-entry assist-file-entry" style="position: relative;" data-bind="appAwareTemplateContextMenu: { template: 'document-context-items', scrollContainer: '.assist-db-scrollable' }, assistFileDroppable, visibleOnHover: { 'selector': '.assist-file-actions' }">
             <div class="assist-file-actions table-actions" style="opacity: 0;" >
               <a style="padding: 0 3px;" class="inactive-action" href="javascript:void(0);" data-bind="templatePopover : { contentTemplate: 'file-details-content', titleTemplate: 'file-details-title', minWidth: '350px' }">
                 <i class='fa fa-info' title="${ _('Details') }"></i>
               </a>
             </div>
             <a href="javascript:void(0)" class="assist-entry assist-document-link" data-bind="click: open, attr: {'title': name }">
               <!-- ko template: { name: 'document-icon-template', data: { document: $data, showShareAddon: false } } --><!-- /ko -->
               <span data-bind="draggableText: { text: definition().name, meta: {'type': 'document', 'definition': definition()} }, text: definition().name"></span>
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
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="assist-collections-header-actions">
    <div class="assist-db-header-actions">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: $parent.toggleSearch, css: { 'blue' : $parent.isSearchVisible }"><i class="pointer fa fa-filter" title="${_('Filter')}"></i></a>
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.collections.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manual refresh')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-collections-inner-panel">
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
          <li class="assist-entry assist-table-link" style="position: relative;" data-bind="appAwareTemplateContextMenu: { template: 'collections-context-items', scrollContainer: '.assist-collections-scrollable' }, visibleOnHover: { 'selector': '.assist-actions' }">
            <a href="javascript:void(0)" class="assist-entry assist-table-link" data-bind="multiClick: { click: click, dblClick: dblClick }, attr: {'title': definition.name }">
              <i class="fa fa-fw fa-search muted valign-middle"></i>
              <span draggable="true" data-bind="text: definition.name, draggableText: { text: '\'' + path + '\'', meta: {'type': 'collection', 'definition': definition} }"></span>
            </a>
          </li>
        </ul>
        <!-- ko if: !loading() && entries().length === 0 -->
        <ul class="assist-tables">
          <li class="assist-entry"><span class="assist-no-entries">${_('No collections available.')}</span></li>
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
    <div class="assist-flex-fill assist-hbase-scrollable">
      <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
        <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 20, container: '.assist-hbase-scrollable' }">
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
    &nbsp;<a class="pull-right pointer close-popover inactive-action">&times;</a>
  </script>

  <script type="text/html" id="ask-for-invalidate-content">
    <label class="radio">
      <input type="radio" name="refreshImpala" value="cache" data-bind="checked: invalidateOnRefresh" />
      ${ _('Clear cache') }
    </label>
    <label class="radio">
      <input type="radio" name="refreshImpala" value="invalidate" data-bind="checked: invalidateOnRefresh" />
      ${ _('Perform incremental metadata update') }
    </label>
    <div class="assist-invalidate-description">${ _('This will sync missing tables in Hive.') }</div>
    <label class="radio">
      <input type="radio" name="refreshImpala" value="invalidateAndFlush" data-bind="checked: invalidateOnRefresh"  />
      ${ _('Invalidate all metadata and rebuild index') }
    </label>
    <div class="assist-invalidate-description">${ _('WARNING: This can be both resource and time-intensive.') }</div>
    <div style="width: 100%; display: inline-block; margin-top: 5px;"><button class="pull-right btn btn-primary" data-bind="css: { 'btn-primary': invalidateOnRefresh() !== 'invalidateAndFlush', 'btn-danger': invalidateOnRefresh() === 'invalidateAndFlush' }, click: function (data, event) { huePubSub.publish('close.popover'); triggerRefresh(data, event); }, clickBubble: false">${ _('Refresh') }</button></div>
  </script>

  <script type="text/html" id="assist-db-header-actions">
    <div class="assist-db-header-actions">
      <!-- ko ifnot: loading -->
      <span class="assist-tables-counter">(<span data-bind="text: filteredEntries().length"></span>)</span>
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: toggleSearch, css: { 'blue' : isSearchVisible }"><i class="pointer fa fa-filter" title="${_('Filter')}"></i></a>
      % if ENABLE_NEW_CREATE_TABLE.get():
        <!-- ko if: sourceType === 'hive' || sourceType === 'impala' -->
        <!-- ko if: typeof databaseName !== 'undefined' -->
          <!-- ko if: IS_HUE_4 -->
            <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('open.link', '${ url('indexer:importer_prefill', source_type='all', target_type='table') }' + databaseName ); }" title="${_('Create table')}" href="javascript:void(0)">
              <i class="pointer fa fa-plus" title="${_('Create table')}"></i>
            </a>
          <!-- /ko -->
          <!-- ko if: ! IS_HUE_4 -->
            <a class="inactive-action" href="javascript:void(0)" data-bind="attr: { 'href': '${ url('indexer:importer_prefill', source_type='all', target_type='table') }' + databaseName }"><i class="pointer fa fa-plus" title="${_('Create table')}"></i></a>
          <!-- /ko -->
        <!-- /ko -->
        <!-- ko if: typeof databases !== 'undefined' -->
          <!-- ko if: IS_HUE_4 -->
            <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('open.link', '${ url('indexer:importer_prefill', source_type='manual', target_type='database') }'); }" href="javascript:void(0)"><i class="pointer fa fa-plus" title="${_('Create database')}"></i></a>
          <!-- /ko -->
          <!-- ko if: ! IS_HUE_4 -->
            <a class="inactive-action" href="javascript:void(0)" data-bind="attr: { 'href': '${ url('indexer:importer_prefill', source_type='manual', target_type='database') }' }"><i class="pointer fa fa-plus" title="${_('Create database')}"></i></a>
          <!-- /ko -->
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
      <div class="assist-filter"><input id="searchInput" class="clearable" type="text" placeholder="${ _('Database name...') }" data-bind="hasFocus: editingSearch, clearable: filter.query, value: filter.query, valueUpdate: 'afterkeydown'"/></div>
    </div>
    <div class="assist-flex-fill assist-db-scrollable" data-bind="visible: ! hasErrors() && ! loading() && hasEntries()">
      <!-- ko if: ! loading() && filteredEntries().length == 0 -->
      <ul class="assist-tables">
        <li class="assist-entry no-entries">${_('No results found')}</li>
      </ul>
      <!-- /ko -->
      <ul class="assist-tables" data-bind="foreachVisible: {data: filteredEntries, minHeight: 20, container: '.assist-db-scrollable' }">
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
        ${_('Tables')}
        <!-- ko template: 'assist-db-header-actions' --><!-- /ko -->
      </div>
    </div>
    <div class="assist-flex-table-search" data-bind="visible: hasEntries() && isSearchVisible() && !$parent.loading() && !$parent.hasErrors()">
      <div>
        <label class="checkbox inline-block margin-left-5"><input type="checkbox" data-bind="checked: filter.showTables" />${_('Tables')}</label>
        <label class="checkbox inline-block margin-left-5"><input type="checkbox" data-bind="checked: filter.showViews" />${_('Views')}</label>
        <!-- ko if: $parent.activeSort -->
        <a class="assist-sort inactive-action inactive-action-dark" style="position: absolute;" data-toggle="dropdown" href="javascript:void(0)">
          <!-- ko if: $parent.activeSort() === 'creation' -->
          <i class="pointer fa fa-sort" title="${_('Sort')}"></i>
          <!-- /ko -->
          <!-- ko if: $parent.activeSort() === 'popular' -->
          <i class="pointer fa fa-star-o" title="${_('Sort')}"></i>
          <!-- /ko -->
          <!-- ko if: $parent.activeSort() === 'alpha' -->
          <i class="pointer fa fa-sort-alpha-asc" title="${_('Sort')}"></i>
          <!-- /ko -->
          ${_('Sort')}
        </a>
        <ul class="dropdown-menu" style="top: initial; left: inherit; position: fixed; z-index:10000;">
          <li>
            <a href="javascript:void(0)" data-bind="click: function () { $parent.activeSort('creation'); }">
              <i class="fa fa-fw" data-bind="css: { 'fa-check': $parent.activeSort() === 'creation' }"></i> ${ _('Default') }
            </a>
          </li>
          <li>
            <a href="javascript:void(0)" data-bind="click: function () { $parent.activeSort('alpha'); }">
              <i class="fa fa-fw" data-bind="css: { 'fa-check': $parent.activeSort() === 'alpha' }"></i> ${ _('Alphabetical') }
            </a>
          </li>
          <!-- ko if: HAS_OPTIMIZER -->
          <li>
            <a href="javascript:void(0)" data-bind="click: function () { $parent.activeSort('popular'); }">
              <i class="fa fa-fw" data-bind="css: { 'fa-check': $parent.activeSort() === 'popular' }"></i> ${ _('Popularity') }
            </a>
          </li>
          <!-- /ko -->
        </ul>
        <!-- /ko -->
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

  <script type="text/html" id="assist-panel-inner-header">
    <div class="assist-header assist-fixed-height" data-bind="visibleOnHover: { selector: '.assist-header-actions' }, css: { 'assist-resizer': $index() > 0 }" style="display:none;">
      <span data-bind="text: $parent.name"></span>
      <div class="assist-header-actions">
        <div class="inactive-action" data-bind="click: function () { $parent.visible(false) }"><i class="fa fa-times"></i></div>
      </div>
    </div>
  </script>

  <script type="text/html" id="assist-panel-template">
    <div class="assist-panel">
      <!-- ko if: availablePanels().length > 1 -->
      <div class="assist-panel-switches">
        <!-- ko foreach: availablePanels -->
        <div class="inactive-action assist-type-switch" data-bind="click: function () { $parent.visiblePanel($data); }, css: { 'blue': $parent.visiblePanel() === $data }, style: { 'float': rightAlignIcon ? 'right' : 'left' },  attr: { 'title': name }">
          <i class="fa fa-fw valign-middle" data-bind="css: icon"></i>
        </div>
        <!-- /ko -->
      </div>
      <!-- /ko -->
      <!-- ko with: visiblePanel -->
      <!-- ko template: { if: showNavSearch && $parent.navigatorSearch.navigatorEnabled(), name: 'assist-panel-navigator-search', data: $parent }--><!-- /ko -->
      <div class="assist-panel-contents" data-bind="style: { 'padding-top': $parent.availablePanels().length > 1 ? '10px' : '5px' }">
        <div class="assist-inner-panel">
          <div class="assist-flex-panel">
            <!-- ko template: { name: templateName, data: panelData } --><!-- /ko -->
          </div>
          <!-- ko with: $parent.navigatorSearch -->
          <!-- ko template: { if: searchActive() && searchInput() !== '' && navigatorEnabled(), name: 'nav-search-result' } --><!-- /ko -->
          <!-- /ko -->
        </div>
      </div>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/javascript">
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
       * @param {(AssistDbPanel|AssistHdfsPanel|AssistGitPanel|AssistDocumentsPanel|AssistS3Panel|AssistCollectionsPanel)} panelData
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

        if (typeof options.sourceTypes === 'undefined') {
          options.sourceTypes = [];
          % for interpreter in get_ordered_interpreters(request.user):
            % if interpreter["interface"] in ["hiveserver2", "rdbms", "jdbc", "solr"]:
              options.sourceTypes.push({
                type: '${ interpreter["type"] }',
                name: '${ interpreter["name"] }'
              });
            % endif
          % endfor
        }

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
          huePubSub.publish('sql.context.popover.hide');
          huePubSub.publish('assist.hide.search');
          window.setTimeout(function () {
            var foundSource;
            $.each(self.sources(), function (idx, source) {
              if (source.sourceType === location.sourceType) {
                foundSource = source;
                return false;
              }
            });
            if (foundSource) {
              var whenLoaded = function () {
                if (self.selectedSource() !== foundSource) {
                  self.selectedSource(foundSource);
                }
                foundSource.highlightInside(location.path);
              };
              if (foundSource.hasEntries()) {
                whenLoaded();
              } else {
                foundSource.initDatabases(whenLoaded);
              }
            }
          }, 0);
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
              name: 'default'
            });
          }
        });

        huePubSub.subscribe('assist.get.source', function () {
          huePubSub.publish('assist.source.set', self.selectedSource() ? self.selectedSource().sourceType : undefined);
        });

        huePubSub.subscribe('assist.set.source', function (source) {
          if (self.sourceIndex[source]) {
            self.selectedSource(self.sourceIndex[source]);
          }
        });

        huePubSub.publish('assist.db.panel.ready');

        huePubSub.subscribe('assist.is.db.panel.ready', function () {
          huePubSub.publish('assist.db.panel.ready');
        });

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
      function AssistGitPanel (options) {
        var self = this;
        self.apiHelper = ApiHelper.getInstance();

        self.selectedGitEntry = ko.observable();
        self.reload = function () {
          var lastKnownPath = self.apiHelper.getFromTotalStorage('assist', 'currentGitPath', '${ home_dir }');
          var parts = lastKnownPath.split('/');
          parts.shift();

          var currentEntry = new AssistGitEntry({
            definition: {
              name: '/',
              type: 'dir'
            },
            parent: null,
            apiHelper: self.apiHelper
          });

          currentEntry.loadDeep(parts, function (entry) {
            self.selectedGitEntry(entry);
            entry.open(true);
          });
        };

        huePubSub.subscribe('assist.selectGitEntry', function (entry) {
          self.selectedGitEntry(entry);
          self.apiHelper.setInTotalStorage('assist', 'currentGitPath', entry.path);
        });

        huePubSub.subscribe('assist.git.refresh', function () {
          huePubSub.publish('assist.clear.git.cache');
          self.reload();
        });
      }

      AssistGitPanel.prototype.init = function () {
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
          var link = '/indexer/#edit/' + entry.definition.name;
          if (IS_HUE_4){
            huePubSub.publish('open.link', link);
          }
          else {
            window.open(link);
          }
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
          else {
            huePubSub.publish('assist.dblClickHBaseItem', entry);
          }
        });

        huePubSub.subscribe('assist.clickHBaseRootItem', function (entry) {
          self.reload();
        });

        huePubSub.subscribe('assist.dblClickHBaseItem', function (entry) {
          var link = '/hbase/#' + self.selectedHBaseEntry().definition.name + '/' + entry.definition.name;
          if (IS_HUE_4){
            huePubSub.publish('open.link', link);
          }
          else {
            window.open(link);
          }
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

        self.apiHelper = ApiHelper.getInstance();

        self.tabsEnabled = '${ USE_NEW_SIDE_PANELS.get() }' === 'True';

        self.availablePanels = ko.observableArray();
        self.visiblePanel = ko.observable();

        // TODO handle panel reloading
        self.lastOpenPanelType = ko.observable();
        self.apiHelper.withTotalStorage('assist', 'last.open.panel', self.lastOpenPanelType);

        self.visiblePanel.subscribe(function(newValue) {
          newValue.panelData.init();
        });

        huePubSub.subscribe('cluster.config.set.config', function (clusterConfig) {
          if (clusterConfig && clusterConfig['app_config']) {
            var panels = [];
            var appConfig = clusterConfig['app_config'];

            if (appConfig['editor']) {
              panels.push(
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
              );
            }

            if (self.tabsEnabled) {

              if (appConfig['browser'] && appConfig['browser']['interpreter_names'].indexOf('hdfs') != -1) {
                panels.push(new AssistInnerPanel({
                  panelData: new AssistHdfsPanel({
                    apiHelper: self.apiHelper
                  }),
                  apiHelper: self.apiHelper,
                  name: '${ _("HDFS") }',
                  type: 'hdfs',
                  icon: 'fa-folder-o',
                  minHeight: 50
                  % if not has_navigator_file_search(user):
                    , showNavSearch: false
                  % endif
                }));
              }

              if (appConfig['browser'] && appConfig['browser']['interpreter_names'].indexOf('s3') != -1) {
                panels.push(new AssistInnerPanel({
                  panelData: new AssistS3Panel({
                    apiHelper: self.apiHelper
                  }),
                  apiHelper: self.apiHelper,
                  name: '${ _("S3") }',
                  type: 's3',
                  icon: 'fa-cubes',
                  minHeight: 50
                  % if not has_navigator_file_search(user):
                    , showNavSearch: false
                  % endif
                }));
              }

              if (appConfig['browser'] && appConfig['browser']['interpreter_names'].indexOf('indexes') != -1) {
                panels.push(new AssistInnerPanel({
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
              }

              if (appConfig['browser'] && appConfig['browser']['interpreter_names'].indexOf('hbase') != -1) {
                panels.push(new AssistInnerPanel({
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
              }

              panels.push(new AssistInnerPanel({
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

              var vcsKeysLength = ${ len(VCS.keys()) };
              if (vcsKeysLength > 0) {
                panels.push(new AssistInnerPanel({
                  panelData: new AssistGitPanel({
                    apiHelper: self.apiHelper
                  }),
                  apiHelper: self.apiHelper,
                  name: '${ _("Git") }',
                  type: 'git',
                  icon: 'fa-github',
                  minHeight: 50,
                  showNavSearch: false,
                  rightAlignIcon: true
                }));
              }

            }

            self.availablePanels(panels);
          } else {
            self.availablePanels([new AssistInnerPanel({
              panelData: new AssistDbPanel($.extend({
                apiHelper: self.apiHelper,
                i18n: i18n
              }, params.sql)),
              apiHelper: self.apiHelper,
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
          var dbPanel = self.availablePanels().filter(function (panel) { return panel.type === 'sql' });
          if (lastFoundPanel.length === 1) {
            dbPanel[0].panelData.init(); // always forces the db panel to load
          }

          self.visiblePanel(lastFoundPanel.length === 1 ? lastFoundPanel[0] : self.availablePanels()[0]);
        });

        window.setTimeout(function () {
          // Main initialization trigger in hue.mako, this is for Hue 3
          if (self.availablePanels().length === 0) {
            huePubSub.publish('cluster.config.get.config');
          }
        }, 0);

        self.navigatorSearch = new NavigatorSearch(self, params.sql.navigationSettings);
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

  <script type="text/javascript">
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
                  return fn.signature.toLowerCase().indexOf(self.query().toLowerCase()) !== -1 || (fn.description && fn.description.toLowerCase().indexOf(self.query().toLowerCase()) !== -1);
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
    <div class="assist-inner-panel assist-assistant-panel">
      <div class="assist-flex-panel">
        <!-- ko if: statementCount() > 1 -->
        <div class="assist-flex-header">${ _('Statement') } <span data-bind="text: activeStatementIndex() + '/' + statementCount()"></span></div>
        <!-- /ko -->

        <div class="assist-flex-header"><div class="assist-inner-header">${ _('Tables') }</div></div>
        <div class="assist-flex-half">
          <!-- ko if: activeTables().length === 0 -->
          <div class="assist-no-entries">${ _('No tables identified.') }</div>
          <!-- /ko -->
          <!-- ko if: activeTables().length > 0 -->
          <ul data-bind="foreach: activeTables">
            <li>
              <span data-bind="text: name"></span>
              <div class="pull-right margin-right-10">
                <a class="inactive-action" href="javascript:void(0)" data-bind="click: function (data, event) { showContextPopover(data, event, 'left') }"><i class="fa fa-info"></i></a>
                <i class="fa fa-fw fa-clock-o muted" title="02/01/2017 10:15 PM"></i>
              </div>
            </li>
          </ul>
          <!-- /ko -->
        </div>

        <!-- ko if: HAS_OPTIMIZER -->
        <div class="assist-flex-header assist-divider"><div class="assist-inner-header">${ _('Suggestions') }</div></div>
        <div class="assist-flex-half">
          <!-- ko if: ! activeRisks().hints -->
          <div class="assist-no-entries">...</div>
          <!-- /ko -->
          <!-- ko if: activeRisks().hints && activeRisks().hints.length === 0 -->
          <div class="assist-no-entries">${ _('No optimizations identified.') }</div>
          <!-- /ko -->
          <!-- ko if: activeRisks().hints && activeRisks().hints.length > 0 -->
          <ul class="risk-list" data-bind="foreach: activeRisks().hints">
            <li>
              <div class="risk-list-title" data-bind="css: { 'risk-list-high' : risk === 'high', 'risk-list-normal':  risk !== 'high' }, tooltip: { title: risk + ' ' + riskTables }"><span data-bind="text: riskAnalysis"></span></div>
              <div class="risk-list-description" data-bind="text: riskRecommendation"></div>
            </li>
          </ul>
          <!-- /ko -->
        </div>

        <!-- ko if: hasMissingRisks() -->
        <div class="assist-flex-fill">
          <br>
          <a href="javascript:void(0)" data-bind="visible: activeTables().length > 0, click: function() { huePubSub.publish('editor.table.stats.upload', activeTables()); }, attr: { 'title': ('${ _("Add missing table and columns ") }'  + (isMissingDDL() ? 'DDL' : '') + (isMissingDDL() && isMissingStats() ? ' ${ _("and") } ' : '') + (isMissingStats() ? 'stats' : '')) }">
            <i class="fa fa-fw fa-plus-circle"></i> ${_('Improve Analysis')}
          </a>
        </div>
        <!-- /ko -->
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/javascript">
    (function () {
      function AssistantPanel(params) {
        var self = this;

        self.disposals = [];

        self.activeCursorLocation = ko.observable();
        self.activeStatementLocation = ko.observable();
        self.locationIndex = ko.observable({});

        self.activeSourceType = ko.observable();
        self.activeTables = ko.observableArray();
        self.activeColumns = ko.observableArray();
        self.activeRisks = ko.observable({});
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
          return self.activeRisks().noStats && self.activeRisks().noStats.length > 0;
        });
        self.statementCount = ko.observable(0);
        self.activeStatementIndex = ko.observable(0);

        var isPointInside = function (location, row, col) {
          return (location.first_line < row && row < location.last_line) ||
              (location.first_line === row && row === location.last_line && location.first_column <= col && col <= location.last_column) ||
              (location.first_line === row && row < location.last_line && col >= location.first_column) ||
              (location.first_line < row && row === location.last_line && col <= location.last_column);
        };

        var createQualifiedIdentifier = function (identifierChain) {
          return $.map(identifierChain, function (identifier) {
            return identifier.name;
          }).join('.');
        };

        var AceRange = ace.require('ace/range').Range;
        var lastMarkedGutterLines = [];
        var findStatementTextAtCursor = function () {
          if (!self.activeStatementLocation() || !self.activeCursorLocation()) {
            return; // undefined when unknown
          }
          var statementLoc = self.activeStatementLocation();

          var editor = self.activeCursorLocation().editor;
          var statementAtCursor = editor.session.getTextRange(new AceRange(statementLoc.first_line - 1, statementLoc.first_column - 1, statementLoc.last_line - 1, statementLoc.last_column - 1));

          var leadingEmptyLineCount = 0;
          var leadingWhiteSpace = statementAtCursor.match(/^\s+/);
          if (leadingWhiteSpace) {
            var lineBreakMatch = leadingWhiteSpace[0].match(/^(\r\n)|(\n)|(\r)/g);
            if (lineBreakMatch) {
              leadingEmptyLineCount = lineBreakMatch.length;
            }
          }

          while(lastMarkedGutterLines.length) {
            editor.session.removeGutterDecoration(lastMarkedGutterLines.shift(), 'ace-active-gutter-decoration');
          }
          for (var line = statementLoc.first_line - 1 + leadingEmptyLineCount; line < statementLoc.last_line; line ++) {
            lastMarkedGutterLines.push(line);
            editor.session.addGutterDecoration(line, 'ace-active-gutter-decoration');
          }

          return editor.session.getTextRange(new AceRange(statementLoc.first_line - 1, statementLoc.first_column - 1, statementLoc.last_line - 1, statementLoc.last_column - 1));
        };

        var activeStatementSub = huePubSub.subscribe('get.active.editor.statement', function () {
          huePubSub.publish('set.active.editor.statement', findStatementTextAtCursor());
        });

        self.disposals.push(activeStatementSub.remove.bind(activeStatementSub));

        var initActive = function () {
          if (!self.activeCursorLocation()) {
            huePubSub.publish('get.active.editor.cursor.location');
          }
          if (typeof self.activeCursorLocation() !== 'undefined' && typeof self.locationIndex()[self.activeCursorLocation().id] !== 'undefined') {
            var locations = self.locationIndex()[self.activeCursorLocation().id].locations;
            self.activeSourceType(self.locationIndex()[self.activeCursorLocation().id].type);

            var statements = [];

            // Statement always comes first
            var currentStatement = [];
            locations.forEach(function (location) {
              if (location.type === 'statement') {
                if (currentStatement.length > 0) {
                  statements.push(currentStatement);
                  currentStatement = [];
                }
              }
              currentStatement.push(location);
            });
            if (currentStatement.length > 0) {
              statements.push(currentStatement);
            }
            self.statementCount(statements.length);

            var activeLocations = [];
            if (statements.length > 0) {
              // Pick the last statement by default (only one or cursor after last ';')
              var statementIndex = statements.length;
              activeLocations = statements[statementIndex - 1];
              if (statements.length > 1) {
                var cursorPos = self.activeCursorLocation().position;
                var index = 1;
                statements.every(function (statement) {
                  // First is the actual statement
                  if (isPointInside(statement[0].location, cursorPos.row+1, cursorPos.column+1)) {
                    activeLocations = statement;
                    statementIndex = index;
                    return false;
                  }
                  index++;
                  return true;
                })
              }
              self.activeStatementIndex(statementIndex);
            }

            var tableIndex = {};
            var columnIndex = {};

            activeLocations.forEach(function (location) {
              if (location.type === 'statement' && self.activeStatementLocation() !== location.location) {
                self.activeStatementLocation(location.location);
                huePubSub.publish('active.editor.statement.changed', findStatementTextAtCursor());
              } else if (location.type === 'table' && location.identifierChain.length <= 2) {
                // tableIndex is used to make sure we only add each table once
                tableIndex[createQualifiedIdentifier(location.identifierChain)] = { name: location.identifierChain[location.identifierChain.length - 1].name, identifierChain: location.identifierChain }
              } else if (location.type === 'column') {
                columnIndex[createQualifiedIdentifier(location.identifierChain)] = { name: location.identifierChain[location.identifierChain.length - 1].name, identifierChain: location.identifierChain }
              }
            });

            self.activeTables($.map(tableIndex, function (value) {
              return new MetastoreTable({
                database: {
                  name: value.identifierChain.length === 2 ? value.identifierChain[0].name : self.locationIndex()[self.activeCursorLocation().id].defaultDatabase
                },
                type: 'table',
                name: value.name
              });
            }));
            self.activeColumns($.map(columnIndex, function (value) {
              return value;
            }));
          }
        };

        huePubSub.subscribeOnce('set.active.snippet.type', self.activeSourceType);
        huePubSub.publish('get.active.snippet.type');

        var snippetTypeChangedSub = huePubSub.subscribe('active.snippet.type.changed', self.activeSourceType);
        self.disposals.push(snippetTypeChangedSub.remove.bind(snippetTypeChangedSub));

        var cursorLocationSub = huePubSub.subscribe('editor.active.cursor.location', function (location) {
          self.activeCursorLocation(location);
          initActive();
        });
        self.disposals.push(cursorLocationSub.remove.bind(cursorLocationSub));

        var activeLocationsSub = huePubSub.subscribe('editor.active.locations', function (activeLocations) {
          var index = self.locationIndex();
          index[activeLocations.id] = activeLocations;
          self.locationIndex(index);
          initActive();
        });
        self.disposals.push(activeLocationsSub.remove.bind(activeLocationsSub));

        var activeRisksSub = huePubSub.subscribe('editor.active.risks', function (activeRisks) {
          self.activeRisks(activeRisks);
        });
        self.disposals.push(activeRisksSub.remove.bind(activeRisksSub));

        huePubSub.publish('get.active.editor.locations');
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

  <script type="text/html" id="schedule-panel-template">
    <div class="assist-inner-panel">
      <div class="assist-flex-panel">
        <div class="assist-flex-header"><div class="assist-inner-header">${ _('Schedule') }</div></div>
        <!-- ko if: selectedNotebook() && selectedNotebook().isBatchable() -->
        <!-- ko with: selectedNotebook() -->
        <div class="tab-pane" id="scheduleTab">
          <!-- ko if: isSaved() && ! isHistory() -->
          <!-- ko if: schedulerViewModelIsLoaded() && schedulerViewModel.coordinator.isDirty() -->
          <a data-bind="click: save" href="javascript: void(0);">${ _('Save changes') }</a>
          <!-- /ko -->
          <!-- ko if: schedulerViewModelIsLoaded() && ! schedulerViewModel.coordinator.isDirty() && ! viewSchedulerId()-->
          <a data-bind="click: showSubmitPopup" href="javascript: void(0);">${ _('Start') }</a>
          <!-- /ko -->
          <!-- ko if: schedulerViewModelIsLoaded() && viewSchedulerId()-->
          <a data-bind="click: function() { huePubSub.publish('show.jobs.panel'); huePubSub.publish('mini.jb.navigate', 'schedules') }" href="javascript: void(0);">${ _('View') }</a>
          <!-- /ko -->
          <br>
          <br>
          <div id="schedulerEditor"></div>
          <!-- /ko -->

          <!-- ko ifnot: isSaved() && ! isHistory() -->
          ${ _('Query needs to be saved first.') }
          <!-- /ko -->
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

        var selectedNotebookSub = self.selectedNotebook.subscribe(function (notebook) {
          if (notebook && notebook.schedulerViewModel == null && notebook.isSaved() && ! notebook.isHistory()) {
            notebook.loadScheduler();
          }
        });
        self.disposals.push(selectedNotebookSub.dispose.bind(selectedNotebookSub));

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
            self.selectedNotebook(undefined);
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

  <script type="text/html" id="right-assist-panel-template">
    <div style="height: 100%; width: 100%; position: relative;">
      <ul class="right-panel-tabs nav nav-pills">
        <li data-bind="css: { 'active' : activeTab() === 'assistant' }, visible: assistantAvailable"><a href="javascript: void(0);" data-bind="click: function() { activeTab('assistant'); }">${ _('Assistant') }</a></li>
        <li data-bind="css: { 'active' : activeTab() === 'functions' }"><a href="javascript: void(0);" data-bind="click: function() { activeTab('functions'); }">${ _('Functions') }</a></li>
        <li data-bind="css: { 'active' : activeTab() === 'schedules' }, visible: schedulesAvailable"><a href="javascript: void(0);" data-bind="click: function() { activeTab('schedules'); }">${ _('Schedule') }</a></li>
      </ul>

      <div class="right-panel-tab-content tab-content">
        <!-- ko if: activeTab() === 'assistant' -->
        <div data-bind="component: { name: 'assistant-panel' }"></div>
        <!-- /ko -->

        <!-- ko if: activeTab() === 'functions' -->
        <div data-bind="component: { name: 'functions-panel' }"></div>
        <!-- /ko -->

        ## TODO: Switch to if: when loadSchedules from notebook.ko.js has been moved to the schedule-panel component
        <div data-bind="component: { name: 'schedule-panel' }, visible: activeTab() === 'schedules'" style="display:none;"></div>
      </div>
    </div>
  </script>


  <script type="text/javascript">
    (function () {
      function RightAssistPanel(params) {
        var self = this;
        self.disposals = [];

        self.activeTab = ko.observable();
        self.assistantAvailable = ko.observable(false);

        self.schedulesAvailable = ko.observable(false);

        if ('${ ENABLE_QUERY_SCHEDULING.get() }' === 'True' && IS_HUE_4) {
          var currentAppSub = huePubSub.subscribe('set.current.app.view.model', function (viewModel) {
            self.schedulesAvailable(!!viewModel.selectedNotebook);
          });
          self.disposals.push(currentAppSub.remove.bind(currentAppSub));
          huePubSub.publish('get.current.app.view.model');
        } else {
          // Right assist is only available in the Hue 3 editor and notebook.
          self.schedulesAvailable('${ ENABLE_QUERY_SCHEDULING.get() }' === 'True');
        }

        var snippetTypeSub = huePubSub.subscribe('active.snippet.type.changed', function (type) {
          if (type === 'hive' || type === 'impala') {
            if (!self.assistantAvailable() && self.activeTab() !== 'assistant') {
              self.activeTab('assistant');
            }
            self.assistantAvailable(true);
          } else {
            if (self.activeTab() === 'assistant') {
              self.activeTab('functions');
            }
            self.assistantAvailable(false);
          }
        });
        self.disposals.push(snippetTypeSub.remove.bind(snippetTypeSub));

        if (!self.activeTab()) {
          self.activeTab('functions');
        }

        if (self.assistantAvailable()) {
          self.activeTab('assistant');
        }
      }

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
