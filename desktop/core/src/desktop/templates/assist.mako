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


from metadata.conf import has_navigator, OPTIMIZER
from metastore.conf import ENABLE_NEW_CREATE_TABLE
from notebook.conf import ENABLE_QUERY_BUILDER, ENABLE_QUERY_SCHEDULING, get_ordered_interpreters

from dashboard.conf import HAS_SQL_ENABLED

from desktop import appmanager
from desktop import conf
from desktop.conf import USE_NEW_SIDE_PANELS, VCS
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko
%>

<%def name="assistJSModels()">
<script src="${ static('desktop/js/assist/assistDbEntry.js') }"></script>
<script src="${ static('desktop/js/assist/assistDbSource.js') }"></script>
<script src="${ static('desktop/js/assist/assistStorageEntry.js') }"></script>
<script src="${ static('desktop/js/assist/assistGitEntry.js') }"></script>
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

  <script type="text/html" id="collection-title-context-items">
    <li><a href="javascript:void(0);" data-bind="hueLink: '/indexer'"><i class="fa fa-fw fa-table"></i> ${ _('Open in Browser') }</a></li>
  </script>

  <script type="text/html" id="sql-context-items">
    <!-- ko if: typeof definition !== 'undefined' -->
      <!-- ko if: sourceType === 'solr' -->
        <li><a href="javascript:void(0);" data-bind="click: function (data) { showContextPopover(data, { target: $parentContext.$contextSourceElement }, { left: 4, top: 2 }); }"><i class="fa fa-fw fa-info"></i> ${ _('Show details') }</a></li>
        <!-- ko if: definition.isView || definition.isTable -->
        <li><a href="javascript:void(0);" data-bind="click: openInIndexer"><i class="fa fa-fw fa-table"></i> ${ _('Open in Browser') }</a></li>
        <li>
          <a href="javascript: void(0);" data-bind="click: function() { explore(true); }">
            <!-- ko template: { name: 'app-icon-template', data: { icon: 'dashboard' } } --><!-- /ko --> ${ _('Open in Dashboard') }
          </a>
        </li>
        <!-- /ko -->
      <!-- /ko -->
      <!-- ko ifnot: sourceType === 'solr' -->
        <li><a href="javascript:void(0);" data-bind="click: function (data) { showContextPopover(data, { target: $parentContext.$contextSourceElement }, { left: 4, top: 2 }); }"><i class="fa fa-fw fa-info"></i> ${ _('Show details') }</a></li>
        <!-- ko if: !definition.isDatabase && $currentApp() === 'editor' -->
        <li><a href="javascript:void(0);" data-bind="click: dblClick"><i class="fa fa-fw fa-paste"></i> ${ _('Insert at cursor') }</a></li>
        <!-- /ko -->
        <!-- ko if: definition.isView || definition.isTable || definition.isDatabase -->
        <li><a href="javascript:void(0);" data-bind="click: openInMetastore"><i class="fa fa-fw fa-table"></i> ${ _('Open in Browser') }</a></li>
        <!-- /ko -->
        <!-- ko if: definition.isView || definition.isTable -->
        <li>
          <a href="javascript:void(0);" data-bind="click: function() { huePubSub.publish('query.and.watch', {'url': '/notebook/browse/' + databaseName + '/' + tableName + '/', sourceType: sourceType}); }">
            <i class="fa fa-fw fa-code"></i> ${ _('Open in Editor') }
          </a>
        </li>
        % if HAS_SQL_ENABLED.get():
        <li>
          <a href="javascript: void(0);" data-bind="click: function() { explore(false); }">
            <!-- ko template: { name: 'app-icon-template', data: { icon: 'dashboard' } } --><!-- /ko --> ${ _('Open in Dashboard') }
          </a>
        </li>
        % endif
        <!-- /ko -->
        %if ENABLE_QUERY_BUILDER.get():
        <!-- ko if: definition.isColumn && $currentApp() === 'editor' -->
        <li class="divider"></li>
        <!-- ko template: { name: 'query-builder-context-items' } --><!-- /ko -->
        <!-- /ko -->
        %endif
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
    <li><a href="javascript:void(0);" data-bind="hueLink: definition.url"><i class="fa fa-fw" data-bind="css: {'fa-folder-open-o': definition.type === 'dir', 'fa-file-text-o': definition.type === 'file'}"></i> ${ _('Open in Browser') }</a></li>
    <!-- ko if: IS_HUE_4 && definition.type === 'file' -->
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
    <li><a href="javascript: void(0);" data-bind="click: function(data) { showContextPopover(data, { target: $parentContext.$contextSourceElement }, { left: 4, top: 2 }); }"><i class="fa fa-fw fa-info"></i> ${ _('Show details') }</a></li>
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

  <script type="text/html" id="assist-database-entry">
    <li class="assist-table" data-bind="appAwareTemplateContextMenu: { template: 'sql-context-items', scrollContainer: '.assist-db-scrollable' }, visibleOnHover: { selector: '.database-actions' }">
      <!-- ko template: { name: 'assist-database-actions' } --><!-- /ko -->
      <a class="assist-table-link" href="javascript: void(0);" data-bind="click: function () { $parent.selectedDatabase($data); $parent.selectedDatabaseChanged(); }, attr: {'title': definition.title }, draggableText: { text: editorText,  meta: {'type': 'sql', 'database': databaseName} }"><i class="fa fa-fw fa-database muted valign-middle"></i> <span class="highlightable" data-bind="text: definition.name, css: { 'highlight': highlight() }"></span></a>
    </li>
  </script>

  <script type="text/html" id="assist-table-entry">
    <li class="assist-table" data-bind="appAwareTemplateContextMenu: { template: 'sql-context-items', scrollContainer: '.assist-db-scrollable' }, visibleOnHover: { override: statsVisible() || navigationSettings.rightAssist, selector: '.table-actions' }">
      <div class="assist-actions table-actions" data-bind="css: { 'assist-actions-left': navigationSettings.rightAssist }" style="opacity: 0">
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, click: showContextPopover, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${_('Show details')}"></i></a>
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.openItem, click: openItem"><i class="fa fa-long-arrow-right" title="${_('Open')}"></i></a>
      </div>
      <a class="assist-entry assist-table-link" href="javascript:void(0)" data-bind="click: toggleOpen, attr: {'title': definition.title }, draggableText: { text: editorText,  meta: {'type': 'sql', 'isView': definition.isView, 'table': tableName, 'database': databaseName} }">
        <i class="fa fa-fw fa-table muted valign-middle" data-bind="css: { 'fa-eye': definition.isView && !navigationSettings.rightAssist, 'fa-table': definition.isTable && sourceType !== 'solr' && !navigationSettings.rightAssist, 'fa-search': sourceType === 'solr' }"></i>
        <span class="highlightable" data-bind="text: definition.displayName, css: { 'highlight': highlight }"></span> <!-- ko if: assistDbSource.activeSort() === 'popular' && popularity() > 0 --><i title="${ _('Popular') }" class="fa fa-star-o top-star"></i> <!-- /ko -->
      </a>
      <div class="center assist-spinner" data-bind="visible: loading() && open()"><i class="fa fa-spinner fa-spin"></i></div>
      <!-- ko template: { if: open, name: 'assist-db-entries'  } --><!-- /ko -->
    </li>
  </script>

  <script type="text/html" id="assist-column-entry">
    <li data-bind="appAwareTemplateContextMenu: { template: 'sql-context-items', scrollContainer: '.assist-db-scrollable' }, visible: ! hasErrors(), visibleOnHover: { childrenOnly: true, override: statsVisible, selector: definition.isView ? '.table-actions' : '.column-actions' }, css: { 'assist-table': definition.isView, 'assist-column': definition.isColumn || definition.isComplex }">
      <div class="assist-actions column-actions" data-bind="css: { 'assist-actions-left': navigationSettings.rightAssist }" style="opacity: 0">
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, click: showContextPopover, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${_('Show details')}"></i></a>
      </div>
      <!-- ko if: expandable -->
      <a class="assist-entry assist-field-link" href="javascript:void(0)" data-bind="click: toggleOpen, attr: {'title': definition.title }, css: { 'assist-entry-left-action': navigationSettings.rightAssist }">
        <span class="highlightable" data-bind="css: { 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName }, text: definition.displayName, draggableText: { text: editorText, meta: {'type': 'sql', 'column': columnName, 'table': tableName, 'database': databaseName } }"></span><!-- ko if: definition.primary_key === 'true' --> <i class="fa fa-key"></i><!-- /ko -->
      </a>
      <!-- /ko -->
      <!-- ko ifnot: expandable -->
      <div class="assist-entry assist-field-link default-cursor" href="javascript:void(0)" data-bind="event: { dblclick: dblClick }, attr: {'title': definition.title }, css: { 'assist-entry-left-action': navigationSettings.rightAssist }">
        <span class="highlightable" data-bind="css: { 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName}, text: definition.displayName, draggableText: { text: editorText, meta: {'type': 'sql', 'column': columnName, 'table': tableName, 'database': databaseName} }"></span><!-- ko if: definition.primary_key === 'true'  --> <i class="fa fa-key"></i><!-- /ko --><!-- ko if: assistDbSource.activeSort() === 'popular' && popularity() > 0 --> <i title="${ _('Popular') }" class="fa fa-star-o top-star"></i> <!-- /ko -->
      </div>
      <!-- /ko -->
      <div class="center assist-spinner" data-bind="visible: loading"><i class="fa fa-spinner fa-spin"></i></div>
      <!-- ko template: { if: open, name: 'assist-db-entries'  } --><!-- /ko -->
    </li>
  </script>

  <script type="text/html" id="assist-column-entry-assistant">
    <li data-bind="appAwareTemplateContextMenu: { template: 'sql-context-items', scrollContainer: '.assist-db-scrollable' }, visible: ! hasErrors(), visibleOnHover: { childrenOnly: true, override: statsVisible, selector: definition.isView ? '.table-actions' : '.column-actions' }, css: { 'assist-table': definition.isView, 'assist-column': definition.isColumn || definition.isComplex }">
      <div class="assist-actions column-actions assist-actions-left" style="opacity: 0">
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, click: showContextPopover, css: { 'blue': statsVisible }"><i class="fa fa-fw fa-info" title="${_('Show details')}"></i></a>
      </div>
      <!-- ko if: expandable -->
      <a class="assist-entry assist-field-link assist-field-link-dark assist-entry-left-action assist-ellipsis" href="javascript:void(0)" data-bind="click: toggleOpen, attr: {'title': definition.title }">
        <span data-bind="text: definition.type" class="muted pull-right margin-right-20"></span>
        <span class="highlightable" data-bind="css: { 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName }, text: definition.name, draggableText: { text: editorText, meta: {'type': 'sql', 'column': columnName, 'table': tableName, 'database': databaseName } }"></span><!-- ko if: definition.primary_key === 'true' --> <i class="fa fa-key"></i><!-- /ko -->
      </a>
      <!-- /ko -->
      <!-- ko ifnot: expandable -->
      <div class="assist-entry assist-field-link assist-field-link-dark default-cursor assist-ellipsis" href="javascript:void(0)" data-bind="event: { dblclick: dblClick }, attr: {'title': definition.title }, css: { 'assist-entry-left-action': navigationSettings.rightAssist }">
        <span data-bind="text: definition.type" class="muted pull-right margin-right-20"></span>
        <span class="highlightable" data-bind="css: { 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName}, text: definition.name, draggableText: { text: editorText, meta: {'type': 'sql', 'column': columnName, 'table': tableName, 'database': databaseName} }"></span><!-- ko if: definition.primary_key === 'true'  --> <i class="fa fa-key"></i><!-- /ko --><!-- ko if: assistDbSource.activeSort() === 'popular' && popularity() > 0 --> <i title="${ _('Popular') }" class="fa fa-star-o top-star"></i> <!-- /ko -->
      </div>
      <!-- /ko -->
      <div class="center assist-spinner" data-bind="visible: loading"><i class="fa fa-spinner fa-spin"></i></div>
      <!-- ko template: { if: open, name: 'assist-db-entries'  } --><!-- /ko -->
    </li>
  </script>

  <script type="text/html" id="assist-db-entries">
    <!-- ko if: ! hasErrors() && hasEntries() && ! loading() && filteredEntries().length == 0 -->
    <ul class="assist-tables">
      <li class="assist-entry assist-no-entries"><!-- ko if: definition.isTable -->${_('No columns found')}<!--/ko--><!-- ko if: definition.isDatabase -->${_('No tables found')}<!--/ko--><!-- ko if: !definition.isTable && !definition.isDatabase -->${_('No results found')}<!--/ko--></li>
    </ul>
    <!-- /ko -->
    <!-- ko if: ! hasErrors() && hasEntries() && ! loading() && filteredEntries().length > 0 -->
    <ul class="database-tree" data-bind="foreachVisible: { data: filteredEntries, minHeight: navigationSettings.rightAssist ? 22 : 23, container: '.assist-db-scrollable' }, css: { 'assist-tables': definition.isDatabase }">
      <!-- ko template: { if: definition.isTable || definition.isView, name: 'assist-table-entry' } --><!-- /ko -->
      <!-- ko if: navigationSettings.rightAssist -->
        <!-- ko template: { ifnot: definition.isTable || definition.isView, name: 'assist-column-entry-assistant' } --><!-- /ko -->
      <!-- /ko -->
      <!-- ko ifnot: navigationSettings.rightAssist -->
        <!-- ko template: { ifnot: definition.isTable || definition.isView, name: 'assist-column-entry' } --><!-- /ko -->
      <!-- /ko -->
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
      <a data-bind="click: back, appAwareTemplateContextMenu: { template: 'sql-context-items', viewModel: selectedSource().selectedDatabase() }">
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

  <script type="text/html" id="assist-solr-inner-panel">
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
    <div class="assist-flex-fill assist-s3-scrollable">
      <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
        <!-- ko hueSpinner: { spin: loadingMore, overlay: true } --><!-- /ko -->
        <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 22, container: '.assist-s3-scrollable', fetchMore: $data.fetchMore.bind($data) }">
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
    <div class="assist-flex-fill assist-git-scrollable">
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
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: goHome" title="Go to ${ home_dir }"><i class="pointer fa fa-home"></i></a>
      <a class="inactive-action" data-bind="dropzone: {
            url: '/filebrowser/upload/file?dest=' + path,
            params: { dest: path },
            paramName: 'hdfs_file',
            onError: function(x, e){ $(document).trigger('error', e); },
            onComplete: function () { huePubSub.publish('assist.hdfs.refresh'); huePubSub.publish('fb.hdfs.refresh', path); } }" title="${_('Upload file')}" href="javascript:void(0)">
        <div class="dz-message inline" data-dz-message><i class="pointer fa fa-plus" title="${_('Upload file')}"></i></div>
      </a>
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.hdfs.refresh'); }" title="${_('Manual refresh')}"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-adls-header-actions">
    <div class="assist-db-header-actions">
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: goHome" title="Go to ${ home_dir }"><i class="pointer fa fa-home"></i></a>
      <a class="inactive-action" data-bind="dropzone: {
            url: '/filebrowser/upload/file?dest=adl:' + path,
            params: { dest: path },
            paramName: 'hdfs_file',
            onError: function(x, e){ $(document).trigger('error', e); },
            onComplete: function () { huePubSub.publish('assist.adls.refresh'); } }" title="${_('Upload file')}" href="javascript:void(0)">
        <div class="dz-message inline" data-dz-message><i class="pointer fa fa-plus" title="${_('Upload file')}"></i></div>
      </a>
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
    <div class="assist-flex-fill assist-hdfs-scrollable">
      <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
        <!-- ko hueSpinner: { spin: loadingMore, overlay: true } --><!-- /ko -->
        <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 22, container: '.assist-hdfs-scrollable', fetchMore: $data.fetchMore.bind($data) }">
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
    <div class="assist-flex-fill assist-adls-scrollable">
      <div data-bind="visible: ! loading() && ! hasErrors()" style="position: relative;">
        <!-- ko hueSpinner: { spin: loadingMore, overlay: true } --><!-- /ko -->
        <ul class="assist-tables" data-bind="foreachVisible: { data: entries, minHeight: 22, container: '.assist-adls-scrollable', fetchMore: $data.fetchMore.bind($data) }">
          <li class="assist-entry assist-table-link" style="position: relative;" data-bind="appAwareTemplateContextMenu: { template: 'hdfs-context-items', scrollContainer: '.assist-adls-scrollable' }, visibleOnHover: { 'selector': '.assist-actions' }">
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
      <!-- ko if: !loading() && availableTypeFilters().length > 1 -->
      <div data-bind="component: { name: 'hue-drop-down', params: { fixedPosition: true, value: typeFilter, entries: availableTypeFilters, linkTitle: '${ _ko('Document type') }' } }" style="display: inline-block"></div>
      <!-- /ko -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.document.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manual refresh')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-documents-inner-panel">
    <!-- ko with: activeEntry -->
    <div class="assist-flex-header assist-breadcrumb">
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
    <div class="assist-flex-fill assist-file-scrollable">
      <div data-bind="visible: ! loading() && ! hasErrors() && entries().length > 0">
         <ul class="assist-tables" data-bind="foreachVisible: {data: filteredEntries, minHeight: 27, container: '.assist-file-scrollable' }">
           <li class="assist-entry assist-file-entry" data-bind="appAwareTemplateContextMenu: { template: 'document-context-items', scrollContainer: '.assist-file-scrollable' }, assistFileDroppable, assistFileDraggable, visibleOnHover: { 'selector': '.assist-file-actions' }">
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
      <!-- /ko -->
    </div>
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
      <!-- ko if: (typeof isSource === 'undefined' || !isSource) && sourceType !== 'solr' -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: toggleSearch, css: { 'blue' : isSearchVisible }"><i class="pointer fa fa-filter" title="${_('Filter')}"></i></a>
      <!-- /ko -->
      % if hasattr(ENABLE_NEW_CREATE_TABLE, 'get') and ENABLE_NEW_CREATE_TABLE.get():
        <!-- ko if: sourceType === 'hive' || sourceType === 'impala' -->
        <!-- ko if: typeof databaseName !== 'undefined' -->
          <a class="inactive-action" data-bind="hueLink: '${ url('indexer:importer_prefill', source_type='all', target_type='table') }' + databaseName + '/?sourceType=' + sourceType" title="${_('Create table')}" href="javascript:void(0)">
            <i class="pointer fa fa-plus" title="${_('Create table')}"></i>
          </a>
        <!-- /ko -->
        <!-- ko if: typeof databases !== 'undefined' -->
          <a class="inactive-action" data-bind="hueLink: '${ url('indexer:importer_prefill', source_type='manual', target_type='database') }' + '/?sourceType=' + sourceType" href="javascript:void(0)">
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

  <script type="text/html" id="assist-databases-template">
    <div class="assist-flex-header" data-bind="visibleOnHover: { selector: '.hover-actions', override: loading() }">
      <div class="assist-inner-header">
        <!-- ko ifnot: sourceType === 'solr' -->
        ${_('Databases')}
        <!-- ko template: 'assist-db-header-actions' --><!-- /ko -->
        <!-- /ko -->
        <!-- ko if: sourceType === 'solr' -->
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
              knownFacetValues: {},
              autocompleteFromEntries: autocompleteFromEntries
            }
          } --><!-- /ko -->
      </div>
    </div>
    <div class="assist-flex-fill assist-db-scrollable" data-bind="visible: ! hasErrors() && ! loading() && hasEntries()">
      <!-- ko if: ! loading() && filteredEntries().length == 0 -->
      <ul class="assist-tables">
        <li class="assist-entry no-entries">${_('No results found')}</li>
      </ul>
      <!-- /ko -->
      <ul class="assist-tables" data-bind="foreachVisible: {data: filteredEntries, minHeight: 23, container: '.assist-db-scrollable' }">
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
        <!-- ko ifnot: sourceType === 'solr' -->
        ${_('Tables')}
        <!-- /ko -->
        <!-- ko if: sourceType === 'solr' -->
        <div data-bind="appAwareTemplateContextMenu: { template: 'collection-title-context-items', scrollContainer: '.assist-db-scrollable' }">${_('Collections')}</div>
        <!-- /ko -->
        <!-- ko template: 'assist-db-header-actions' --><!-- /ko -->
      </div>
    </div>
    <div class="assist-flex-search" data-bind="visible: hasEntries() && isSearchVisible() && !$parent.loading() && !$parent.hasErrors()">
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
    <div class="assist-flex-search" data-bind="visible: hasEntries() && !$parent.loading() && !$parent.hasErrors()">
      <div class="assist-filter">
        <!-- ko component: {
          name: 'inline-autocomplete',
          params: {
            querySpec: filter.querySpec,
            facets: ['type'],
            knownFacetValues: sourceType === 'solr' ? SOLR_ASSIST_KNOWN_FACET_VALUES : SQL_ASSIST_KNOWN_FACET_VALUES,
            autocompleteFromEntries: autocompleteFromEntries
          }
        } --><!-- /ko -->
      </div>
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
      'type': {'date': -1, 'tdate': -1, 'timestamp': -1, 'pdate': -1, 'int': -1, 'tint': -1, 'pint': -1, 'long': -1, 'tlong': -1, 'plong': -1, 'float': -1, 'tfloat': -1, 'pfloat': -1, 'double': -1, 'tdouble': -1, 'pdouble': -1, 'currency': -1, 'smallint': -1, 'bigint': -1, 'tinyint': -1, 'SpatialRecursivePrefixTreeFieldType': -1 }
    };


    (function () {
      ko.bindingHandlers.assistFileDroppable = {
        init: function(element, valueAccessor, allBindings, boundEntry) {
          var dragData;
          var dragSub = huePubSub.subscribe('doc.browser.dragging', function (data) {
            dragData = data;
          });
          ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
            dragSub.remove();
          });

          var $element = $(element);
          if (boundEntry.isDirectory) {
            $element.droppable({
              drop: function () {
                if (dragData && !dragData.dragToSelect && boundEntry.isDirectory()) {
                  boundEntry.moveHere(dragData.selectedEntries);
                  dragData.originEntry.load();
                }
                $element.removeClass('assist-file-entry-drop');
              },
              over: function () {
                if (!$element.hasClass('assist-file-entry-drop') && dragData && !dragData.dragToSelect && boundEntry.isDirectory()) {
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

      ko.bindingHandlers.assistFileDraggable = {
        init: function(element, valueAccessor, allBindings, boundEntry, bindingContext) {
          var $element = $(element);

          var dragStartY = -1;
          var dragStartX = -1;
          $element.draggable({
            start: function (event, ui) {
              var $container = $('.doc-browser-drag-container');
              boundEntry.selected(true);
              huePubSub.publish('doc.browser.dragging', {
                selectedEntries: [ boundEntry ],
                originEntry: boundEntry,
                dragToSelect: false
              });
              huePubSub.publish('doc.drag.to.select', false);

              dragStartX = event.clientX;
              dragStartY = event.clientY;

              var $helper = $('.assist-file-entry-drag').clone().show();
              $helper.find('.drag-text').text(boundEntry.definition().name);
              $helper.find('i').removeClass().addClass($element.find('.doc-browser-primary-col i').attr('class'));

              $helper.appendTo($container);
            },
            drag: function (event) {
            },
            stop: function (event) {
              var elementAtStart = document.elementFromPoint(dragStartX, dragStartY);
              var elementAtStop = document.elementFromPoint(event.clientX, event.clientY);
              if (elementAtStart.nodeName === "A" && elementAtStop.nodeName === "A" && Math.sqrt((dragStartX-event.clientX)*(dragStartX-event.clientX) + (dragStartY-event.clientY)*(dragStartY-event.clientY)) < 8) {
                $(elementAtStop).trigger('click');
              }
              boundEntry.selected(false);
            },
            helper: function (event) {
              return $('<div>').addClass('doc-browser-drag-container');
            },
            appendTo: "body",
            cursorAt: {
              top: 0,
              left: 0
            }
          });
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
       * @param {(AssistDbPanel|AssistHdfsPanel|AssistGitPanel|AssistDocumentsPanel|AssistS3Panel)} panelData
       * @constructor
       */
      function AssistInnerPanel (options) {
        var self = this;
        self.minHeight = options.minHeight;
        self.icon = options.icon;
        self.type = options.type;
        self.name = options.name;
        self.panelData = options.panelData;
        self.rightAlignIcon = !!options.rightAlignIcon;
        self.iconSvg = options.iconSvg;

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
        self.initialized = false;

        if (typeof options.sourceTypes === 'undefined') {
          options.sourceTypes = [];

          if (options.isSolr) {
            options.sourceTypes = [{
              type: 'solr',
              name: 'solr'
            }];
          } else {
            % for interpreter in get_ordered_interpreters(request.user):
              % if interpreter["is_sql"]:
                options.sourceTypes.push({
                  type: '${ interpreter["type"] }',
                  name: '${ interpreter["name"] }'
                });
              % endif
            % endfor
          }
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

        huePubSub.subscribe('assist.collections.refresh', function() {
          huePubSub.publish('assist.db.refresh', { sourceTypes: ['solr'], allCacheTypes: false });
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

        huePubSub.subscribe('assist.db.highlight', function (location) {
          huePubSub.publish('left.assist.show');
          if (location.sourceType === 'solr') {
            huePubSub.publish('assist.show.solr');
          }
          else {
            huePubSub.publish('assist.show.sql');
          }
          huePubSub.publish('context.popover.hide');
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

        if (!options.isSolr) {
          huePubSub.subscribe('assist.set.database', function (databaseDef) {
            if (!databaseDef.source || !self.sourceIndex[databaseDef.source]) {
              return;
            }
            self.selectedSource(self.sourceIndex[databaseDef.source]);
            self.setDatabaseWhenLoaded(databaseDef.name);
          });

          huePubSub.subscribe('assist.get.database', function (source) {
            if (self.sourceIndex[source] && self.sourceIndex[source].selectedDatabase()) {
              huePubSub.publish('assist.database.set', {
                source: source,
                name: self.sourceIndex[source].selectedDatabase().databaseName
              });
            } else {
              huePubSub.publish('assist.database.set', {
                source: source,
                name: 'default'
              });
            }
          });

          huePubSub.subscribe('assist.get.database.callback',  function (options) {
            if (self.sourceIndex[options.source] && self.sourceIndex[options.source].selectedDatabase()) {
              options.callback({
                source: options.source,
                name: self.sourceIndex[options.source].selectedDatabase().databaseName
              });
            } else {
              options.callback({
                source: options.source,
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
        }

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
        if (self.initialized) {
          return;
        }
        if (self.options.isSolr) {
          self.selectedSource(self.sourceIndex['solr']);
          self.setDatabaseWhenLoaded();
        } else {
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
        }
        self.initialized = true;
      };

      /**
       * @param {Object} options
       * @param {ApiHelper} options.apiHelper
       * @param {string} options.user
       * @constructor
       **/
      function AssistDocumentsPanel (options) {
        var self = this;
        self.apiHelper = options.apiHelper;
        self.user = options.user;

        self.activeEntry = ko.observable();
        self.activeSort = ko.observable('defaultAsc');
        self.typeFilter = ko.observable({
          type: 'all',
          label: DocumentTypeGlobals['all']
        });

        var lastOpenedUuid = self.apiHelper.getFromTotalStorage('assist', 'last.opened.assist.doc.uuid');

        if (lastOpenedUuid) {
          self.activeEntry(new HueFileEntry({
            activeEntry: self.activeEntry,
            trashEntry: ko.observable(),
            apiHelper: self.apiHelper,
            app: 'documents',
            user: self.user,
            activeSort: self.activeSort,
            typeFilter: self.typeFilter,
            definition: {
              uuid: lastOpenedUuid,
              type: 'directory'
            }
          }))
        } else {
          self.fallbackToRoot();
        }

        self.activeEntry.subscribe(function (newEntry) {
          if (!newEntry.loaded()) {
            var loadedSub = newEntry.loaded.subscribe(function (loaded) {
              if (loaded && !newEntry.hasErrors() && newEntry.definition() && newEntry.definition().uuid) {
                self.apiHelper.setInTotalStorage('assist', 'last.opened.assist.doc.uuid', newEntry.definition().uuid);
              }
              loadedSub.dispose();
            })
          } else if (!newEntry.hasErrors() && newEntry.definition() && newEntry.definition().uuid) {
            self.apiHelper.setInTotalStorage('assist', 'last.opened.assist.doc.uuid', newEntry.definition().uuid);
          }
        });

        self.reload = function () {
          self.activeEntry().load(function () {}, function () {
            self.fallbackToRoot();
          });
        };

        huePubSub.subscribe('assist.document.refresh', function () {
          huePubSub.publish('assist.clear.document.cache');
          self.reload();
        });

        huePubSub.subscribe('assist.doc.highlight', function (details) {
          huePubSub.publish('left.assist.show');
          huePubSub.publish('assist.show.documents');
          huePubSub.publish('context.popover.hide');
          var whenLoaded = $.Deferred().done(function () {
            self.activeEntry().highlightInside(details.docUuid);
          });
          if (self.activeEntry() && self.activeEntry().definition() && self.activeEntry().definition().uuid === details.parentUuid) {
            if (self.activeEntry().loaded() && !self.activeEntry().hasErrors()) {
              whenLoaded.resolve();
            } else {
              var loadedSub = self.activeEntry().loaded.subscribe(function (newVal) {
                if (newVal) {
                  if (!self.activeEntry().hasErrors()) {
                    whenLoaded.resolve();
                  }
                  whenLoaded.reject();
                  loadedSub.remove();
                }
              })
            }
            self.activeEntry().highlight(details.docUuid);
          } else {
            self.activeEntry(new HueFileEntry({
              activeEntry: self.activeEntry,
              trashEntry: ko.observable(),
              apiHelper: self.apiHelper,
              app: 'documents',
              user: self.user,
              activeSort: self.activeSort,
              typeFilter: self.typeFilter,
              definition: {
                uuid: details.parentUuid,
                type: 'directory'
              }
            }));
            self.activeEntry().load(function() {
              whenLoaded.resolve();
            }, function () {
              whenLoaded.reject();
              self.fallbackToRoot();
            });
          }
        });
      }

      AssistDocumentsPanel.prototype.fallbackToRoot = function () {
        var self = this;
        if (!self.activeEntry() || self.activeEntry().definition() && (self.activeEntry().definition().path !== '/' || self.activeEntry().definition().uuid)) {
          self.apiHelper.setInTotalStorage('assist', 'last.opened.assist.doc.uuid', null);
          self.activeEntry(new HueFileEntry({
            activeEntry: self.activeEntry,
            trashEntry: ko.observable(),
            apiHelper: self.apiHelper,
            app: 'documents',
            user: self.user,
            activeSort: self.activeSort,
            typeFilter: self.typeFilter,
            definition: {
              name: '/',
              type: 'directory'
            }
          }));
          self.activeEntry().load();
        }
      };

      AssistDocumentsPanel.prototype.init = function () {
        var self = this;
        if (! self.activeEntry().loaded()) {
          self.activeEntry().load(function () {}, function () {
            self.fallbackToRoot();
          }, true);
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
        self.loading = ko.observable();
        self.initialized = false;

        var loadPath = function (path) {
          self.loading(true);
          var parts = path.split('/');
          parts.shift();

          var currentEntry = new AssistStorageEntry({
            type: 'hdfs',
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
            self.loading(false);
          });
        };

        self.reload = function () {
          loadPath(self.apiHelper.getFromTotalStorage('assist', 'currentHdfsPath', '${ home_dir }'));
        };

        huePubSub.subscribe('assist.hdfs.go.home', function () {
          loadPath('${ home_dir }');
          self.apiHelper.setInTotalStorage('assist', 'currentHdfsPath', '${ home_dir }');
        });

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
        var self = this;
        if (self.initialized) {
          return;
        }
        self.reload();
        self.initialized = true;
      };

      function AssistAdlsPanel (options) {
        var self = this;
        self.apiHelper = options.apiHelper;
        self.selectedAdlsEntry = ko.observable();
        self.loading = ko.observable();
        self.initialized = false;

        var loadPath = function (path) {
          self.loading(true);
          var parts = path.split('/');
          parts.shift();

          var currentEntry = new AssistStorageEntry({
            type: 'adls',
            definition: {
              name: '/',
              type: 'dir'
            },
            parent: null,
            apiHelper: self.apiHelper
          });

          currentEntry.loadDeep(parts, function (entry) {
            self.selectedAdlsEntry(entry);
            entry.open(true);
            self.loading(false);
          });
        };

        self.reload = function () {
          loadPath(self.apiHelper.getFromTotalStorage('assist', 'currentAdlsPath', '/'));
        };

        huePubSub.subscribe('assist.adls.go.home', function () {
          loadPath('${ home_dir }');
          self.apiHelper.setInTotalStorage('assist', 'currentAdlsPath', '${ home_dir }');
        });

        huePubSub.subscribe('assist.selectAdlsEntry', function (entry) {
          self.selectedAdlsEntry(entry);
          self.apiHelper.setInTotalStorage('assist', 'currentAdlsPath', entry.path);
        });

        huePubSub.subscribe('assist.adls.refresh', function () {
          huePubSub.publish('assist.clear.adls.cache');
          self.reload();
        });
      }

      AssistAdlsPanel.prototype.init = function () {
        var self = this;
        if (self.initialized) {
          return;
        }
        self.reload();
        self.initialized = true;
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
        self.loading = ko.observable();
        self.initialized = false;

        self.reload = function () {
          self.loading(true);
          var lastKnownPath = self.apiHelper.getFromTotalStorage('assist', 'currentS3Path', '/');
          var parts = lastKnownPath.split('/');
          parts.shift();

          var currentEntry = new AssistStorageEntry({
            type: 's3',
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
            self.loading(false);
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
        var self = this;
        if (self.initialized) {
          return;
        }
        self.reload();
        self.initialized = true;
      };

      /**
       * @param {Object} options
       * @param {ApiHelper} options.apiHelper
       * @constructor
       **/
      function AssistHBasePanel(options) {
        var self = this;
        self.apiHelper = options.apiHelper;
        self.initialized = false;

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
          root.loadEntries(function () {
            var lastOpenendPath = self.apiHelper.getFromTotalStorage('assist', 'last.opened.hbase.entry', null);
            if (lastOpenendPath) {
              root.entries().every(function (entry) {
                if (entry.path === lastOpenendPath) {
                  entry.open();
                  return false;
                }
                return true;
              })
            }
          });
        };

        self.selectedHBaseEntry.subscribe(function (newEntry) {
          if (newEntry !== root || (newEntry === root && newEntry.loaded)) {
            self.apiHelper.setInTotalStorage('assist', 'last.opened.hbase.entry', newEntry.path);
          }
        });

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

        var delayChangeHash = function (hash) {
          window.setTimeout(function () {
            window.location.hash = hash;
          }, 0);
        }

        self.lastClickeHBaseEntry = null;
        self.HBaseLoaded = false;

        huePubSub.subscribeOnce('hbase.app.loaded', function() {
          delayChangeHash(self.selectedHBaseEntry().definition.name + '/' + self.lastClickeHBaseEntry.definition.name);
          self.HBaseLoaded = true;
        });

        huePubSub.subscribe('assist.dblClickHBaseItem', function (entry) {
          var hash = self.selectedHBaseEntry().definition.name + '/' + entry.definition.name;
          if (IS_HUE_4) {
            if (window.location.pathname.startsWith('/hue/hbase')) {
              window.location.hash = hash;
            }
            else {
              self.lastClickeHBaseEntry = entry;
              huePubSub.subscribeOnce('app.gained.focus', function (app) {
                if (app === 'hbase' && self.HBaseLoaded) {
                  delayChangeHash(hash);
                }
              });
              huePubSub.publish('open.link', '/hbase');
            }
          }
          else {
            window.open('/hbase/#' + hash);
          }
        });

        huePubSub.subscribe('assist.hbase.refresh', function () {
          huePubSub.publish('assist.clear.hbase.cache');
          self.reload();
        });
      }

      AssistHBasePanel.prototype.init = function () {
        var self = this;
        if (self.initialized) {
          return;
        }
        self.reload();
        self.initialized = true;
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
          errorLoadingTablePreview: "${ _('There was a problem loading the table preview') }"
        };
        var i18nCollections = {
          errorLoadingDatabases: "${ _('There was a problem loading the collections') }",
          errorLoadingTablePreview: "${ _('There was a problem loading the collection preview') }"
        };

        self.apiHelper = ApiHelper.getInstance();

        self.tabsEnabled = '${ USE_NEW_SIDE_PANELS.get() }' === 'True';

        self.availablePanels = ko.observableArray();
        self.visiblePanel = ko.observable();

        self.lastOpenPanelType = ko.observable();
        self.apiHelper.withTotalStorage('assist', 'last.open.panel', self.lastOpenPanelType);

        huePubSub.subscribeOnce('cluster.config.set.config', function (clusterConfig) {
          if (clusterConfig && clusterConfig['app_config']) {
            var panels = [];
            var appConfig = clusterConfig['app_config'];

            if (appConfig['editor']) {
              var sqlPanel = new AssistInnerPanel({
                panelData: new AssistDbPanel($.extend({
                  apiHelper: self.apiHelper,
                  i18n: i18n
                }, params.sql)),
                apiHelper: self.apiHelper,
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
                  panelData: new AssistHdfsPanel({
                    apiHelper: self.apiHelper
                  }),
                  apiHelper: self.apiHelper,
                  name: '${ _("HDFS") }',
                  type: 'hdfs',
                  icon: 'fa-files-o',
                  minHeight: 50
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
                }));
              }

              if (appConfig['browser'] && appConfig['browser']['interpreter_names'].indexOf('adls') != -1) {
                panels.push(new AssistInnerPanel({
                  panelData: new AssistAdlsPanel({
                    apiHelper: self.apiHelper
                  }),
                  apiHelper: self.apiHelper,
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
                    apiHelper: self.apiHelper,
                    i18n: i18nCollections,
                    isSolr: true
                  }, params.sql)),
                  apiHelper: self.apiHelper,
                  name: '${ _("Collections") }',
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

              if (appConfig['browser'] && appConfig['browser']['interpreter_names'].indexOf('hbase') != -1) {
                panels.push(new AssistInnerPanel({
                  panelData: new AssistHBasePanel({
                    apiHelper: self.apiHelper
                  }),
                  apiHelper: self.apiHelper,
                  name: '${ _("HBase") }',
                  type: 'hbase',
                  iconSvg: '#hi-hbase',
                  minHeight: 50
                }));
              }

              var documentsPanel = new AssistInnerPanel({
                panelData: new AssistDocumentsPanel({
                  user: params.user,
                  apiHelper: self.apiHelper
                }),
                apiHelper: self.apiHelper,
                name: '${ _("Documents") }',
                type: 'documents',
                icon: 'fa-files-o',
                iconSvg: '#hi-documents',
                minHeight: 50,
                rightAlignIcon: true,
                visible: params.visibleAssistPanels && params.visibleAssistPanels.indexOf('documents') !== -1
              });

              panels.push(documentsPanel);

              huePubSub.subscribe('assist.show.documents', function () {
                if (self.visiblePanel() !== documentsPanel) {
                  self.visiblePanel(documentsPanel);
                }
              });

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

          // always forces the db panel to load if not the last open panel
          var dbPanel = self.availablePanels().filter(function (panel) { return panel.type === 'sql' });
          if (dbPanel.length > 0 && (lastFoundPanel.length === 0 || (lastFoundPanel[0] !== dbPanel[0]))) {
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
      function FunctionsPanel(params) {
        var self = this;
        self.categories = {};
        self.disposals = [];

        self.activeType = ko.observable();
        self.availableTypes = ko.observableArray(['Hive', 'Impala', 'Pig']);
        self.query = ko.observable();
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

        var apiHelper = ApiHelper.getInstance();

        self.activeType.subscribe(function (newType) {
          self.selectedFunction(selectedFunctionPerType[newType]);
          self.activeCategories(self.categories[newType]);
          apiHelper.setInTotalStorage('assist', 'function.panel.active.type', newType);
        });

        var lastActiveType = apiHelper.getFromTotalStorage('assist', 'function.panel.active.type', self.availableTypes()[0]);
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

        var activeSnippetTypeSub = huePubSub.subscribe('active.snippet.type.changed', updateType);

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
            <div data-bind="appAwareTemplateContextMenu: { template: 'collection-title-context-items', scrollContainer: '.assist-db-scrollable' }">${_('Collections')}</div>
            <!-- /ko -->
            <!-- ko ifnot: isSolr  -->
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
        <div class="assist-flex-half assist-db-scrollable">
          <!-- ko if: filteredTables().length === 0 && (!filter.querySpec() || filter.querySpec().query === '') -->
          <div class="assist-no-entries">
            <!-- ko if: isSolr -->
            ${ _('No collections selected.') }
            <!-- /ko -->
            <!-- ko ifnot: isSolr  -->
            ${ _('No tables identified.') }
            <!-- /ko -->
          </div>
          <!-- /ko -->
          <!-- ko if: filteredTables().length === 0 && filter.querySpec() && filter.querySpec().query !== '' -->
          <div class="assist-no-entries">${ _('No entries found.') }</div>
          <!-- /ko -->
          <!-- ko if: filteredTables().length > 0 -->
          <ul class="database-tree assist-tables" data-bind="foreachVisible: { data: filteredTables, minHeight: 22, container: '.assist-db-scrollable' }">
            <!-- ko if: hasErrors -->
            <li class="assist-table hue-warning" data-bind="attr: { 'title': $parent.isSolr() ? '${ _ko('Error loading collection details.') }' : '${ _ko('Error loading table details.') }'}">
              <span class="assist-entry">
                <i class="hue-warning fa fa-fw muted valign-middle fa-warning"></i>
                <span data-bind="text: definition.displayName"></span>
              </span>
            </li>
            <!-- /ko -->
            <!-- ko ifnot: hasErrors -->
            <!-- ko template: { if: definition.isTable || definition.isView, name: 'assist-table-entry' } --><!-- /ko -->
            <!-- ko template: { ifnot: definition.isTable || definition.isView, name: 'assist-column-entry-assistant' } --><!-- /ko -->
            <!-- /ko -->
          </ul>
          <!-- /ko -->
        </div>

        <!-- ko if: HAS_OPTIMIZER && !isSolr() -->
        <div class="assist-flex-header assist-divider"><div class="assist-inner-header">${ _('Suggestions') }</div></div>
        <div class="assist-flex-half">
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
                if (vm.filter == null || !vm.filter.querySpec() || ((!vm.filter.querySpec().facets || Object.keys(vm.filter.querySpec().facets).length === 0) && (!vm.filter.querySpec().text || vm.filter.querySpec().text.length === 0))) {
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
                    facetMatch = entry.definition.isTable;
                  }
                  if (!facetMatch && facets['type']['view']) {
                    facetMatch = entry.definition.isView;
                  }

                  var textMatch = !vm.filter.querySpec().text || vm.filter.querySpec().text.length === 0;
                  if (!textMatch) {
                    var nameLower = entry.definition.name.toLowerCase();
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

        var createQualifiedIdentifier = function (identifierChain, defaultDatabase) {
          if (identifierChain.length === 1) {
            return defaultDatabase + '.' + identifierChain[0].name;
          }
          return $.map(identifierChain, function (identifier) {
            return identifier.name;
          }).join('.').toLowerCase();
        };

        var databaseIndex = {};

        var activeTableIndex = {};

        self.filter = {
          querySpec: ko.observable({
            query: '',
            facets: {},
            text: []
          }),
          showViews: ko.observable(true),
          showTables: ko.observable(true)
        };

        self.filteredTables = AssistantUtils.getFilteredTablesPureComputed(self);

        var navigationSettings = {
          showStats: true,
          rightAssist: true
        };
        var i18n = {};

        var assistDbSource = new AssistDbSource({
          i18n : i18n,
          type: 'hive',
          name: 'hive',
          navigationSettings: navigationSettings
        });

        var loadEntriesTimeout = -1;
        // This fetches the columns for each table synchronously with 2 second in between.
        var loadEntries = function () {
          window.clearTimeout(loadEntriesTimeout);
          if (self.activeTables().length === 1) {
            self.activeTables()[0].open(true);
          }
          else {
            loadEntriesTimeout = window.setTimeout(function () {
              self.activeTables().every(function (table) {
                if (!table.loaded && !table.hasErrors() && !table.loading()) {
                  table.loadEntries(loadEntries, true);
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
          self.activeTables().forEach(function (table) {
            if (!added[table.definition.name] && table.definition.name.toLowerCase().indexOf(partialLower) === 0) {
              added[table.definition.name] = true;
              result.push(nonPartial + partial + table.definition.name.substring(partial.length))
            }
            table.entries().forEach(function (col) {
              if (!added[col.definition.name] && col.definition.name.toLowerCase().indexOf(partialLower) === 0) {
                added[col.definition.name] = true;
                result.push(nonPartial + partial + col.definition.name.substring(partial.length))
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

        var handleLocationUpdate = function (activeLocations) {
          assistDbSource.sourceType = activeLocations.type;
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
                var database = location.identifierChain.length === 2 ? location.identifierChain[0].name : activeLocations.defaultDatabase;
                database = database.toLowerCase();
                if (!databaseIndex[database]) {
                  databaseIndex[database] = new AssistDbEntry(
                    {
                      name: database,
                      type: 'database',
                      isDatabase: true
                    },
                    null,
                    assistDbSource,
                    self.filter,
                    i18n,
                    navigationSettings,
                    {}
                  );
                }
                var qid = createQualifiedIdentifier(location.identifierChain, activeLocations.defaultDatabase);
                tableQidIndex[qid] = true;
                if (!activeTableIndex[qid]) {
                  var tableName = location.identifierChain[location.identifierChain.length - 1].name;
                  var displayName = database + '.' + tableName;

                  activeTableIndex[createQualifiedIdentifier(location.identifierChain, activeLocations.defaultDatabase)] = new AssistDbEntry(
                    {
                      name: tableName,
                      type: 'table',
                      isTable: true,
                      displayName: displayName.toLowerCase(),
                      title: displayName
                    },
                    databaseIndex[database],
                    assistDbSource,
                    self.filter,
                    {},
                    navigationSettings,
                    {}
                  );
                  updateTables = true;
                }
              }
            });
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
                return a.definition.name.localeCompare(b.definition.name);
              });
              self.activeTables(tables);
            }
          }
        };

        huePubSub.subscribeOnce('set.active.editor.locations', handleLocationUpdate);
        huePubSub.publish('get.active.editor.locations');

        var activeLocationsSub = huePubSub.subscribe('editor.active.locations', handleLocationUpdate);

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

        self.filter = {
          querySpec: ko.observable({
            query: '',
            facets: {},
            text: []
          })
        };

        self.activeTables = ko.observableArray();

        self.filteredTables = AssistantUtils.getFilteredTablesPureComputed(self);

        var navigationSettings = {
          showStats: true,
          rightAssist: true
        };
        var i18n = {};

        var activeDashboardCollection = huePubSub.subscribe('set.active.dashboard.collection', function(collection) {
          var collectionName = collection.name();

          var assistDbSource = new AssistDbSource({
            i18n : i18n,
            type: collection.engine(),
            name: collection.engine(),
            navigationSettings: navigationSettings
          });

          var assistFakeDb = new AssistDbEntry(
              {
                name: collectionName.indexOf('.') > -1 ? collectionName.split('.')[0] : 'default',
                type: 'database',
                isDatabase: true
              },
              null,
              assistDbSource,
              self.filter,
              i18n,
              navigationSettings
          );

          var collectionEntry = new AssistDbEntry(
              {
                name: collectionName.indexOf('.') > -1 ? collectionName.split('.')[1] : collectionName,
                type: 'table',
                isTable: true,
                displayName: collectionName.toLowerCase()
              },
              assistFakeDb,
              assistDbSource,
              self.filter,
              i18n,
              navigationSettings
          );

          self.activeTables([collectionEntry]);

          self.autocompleteFromEntries = function (nonPartial, partial) {
            var added = {};
            var result = [];
            var partialLower = partial.toLowerCase();
            self.activeTables().forEach(function (table) {
              if (!added[table.definition.name] && table.definition.name.toLowerCase().indexOf(partialLower) === 0) {
                added[table.definition.name] = true;
                result.push(nonPartial + partial + table.definition.name.substring(partial.length))
              }
              table.entries().forEach(function (col) {
                if (!added[col.definition.name] && col.definition.name.toLowerCase().indexOf(partialLower) === 0) {
                  added[col.definition.name] = true;
                  result.push(nonPartial + partial + col.definition.name.substring(partial.length))
                }
              })
            });
            return result;
          };

          if (!collectionEntry.loaded && !collectionEntry.hasErrors() && !collectionEntry.loading()) {
            collectionEntry.loadEntries(function() { collectionEntry.toggleOpen(); });
          }
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
    <div style="height: 100%; width: 100%; position: relative;">
      <ul class="right-panel-tabs nav nav-pills">
        <li data-bind="css: { 'active' : activeTab() === 'editorAssistant' }, visible: editorAssistantTabAvailable" style="display:none;"><a href="javascript: void(0);" data-bind="click: function() { lastActiveTabEditor('editorAssistant'); activeTab('editorAssistant'); }">${ _('Assistant') }</a></li>
        <li data-bind="css: { 'active' : activeTab() === 'functions' }, visible: functionsTabAvailable" style="display:none;"><a href="javascript: void(0);" data-bind="click: function() { lastActiveTabEditor('functions'); activeTab('functions'); }">${ _('Functions') }</a></li>
        <li data-bind="css: { 'active' : activeTab() === 'schedules' }, visible: schedulesTabAvailable" style="display:none;"><a href="javascript: void(0);" data-bind="click: function() { lastActiveTabEditor('schedules'); activeTab('schedules'); }">${ _('Schedule') }</a></li>
        <li data-bind="css: { 'active' : activeTab() === 'dashboardAssistant' }, visible: dashboardAssistantTabAvailable" style="display:none;"><a href="javascript: void(0);" data-bind="click: function() { lastActiveTabDashboard('dashboardAssistant'); activeTab('dashboardAssistant'); }">${ _('Assistant') }</a></li>
      </ul>

      <div class="right-panel-tab-content tab-content">
        <!-- ko if: activeTab() === 'editorAssistant' && editorAssistantTabAvailable()-->
        <div data-bind="component: { name: 'editor-assistant-panel' }"></div>
        <!-- /ko -->

        <!-- ko if: activeTab() === 'functions' && functionsTabAvailable -->
        <div data-bind="component: { name: 'functions-panel' }"></div>
        <!-- /ko -->

        <!-- ko if: activeTab() === 'dashboardAssistant' && dashboardAssistantTabAvailable()-->
        <div data-bind="component: { name: 'dashboard-assistant-panel' }"></div>
        <!-- /ko -->

        ## TODO: Switch to if: when loadSchedules from notebook.ko.js has been moved to the schedule-panel component
        <div data-bind="component: { name: 'schedule-panel' }, visible: activeTab() === 'schedules'" style="display:none;"></div>
      </div>
    </div>
  </script>


  <script type="text/javascript">
    (function () {

      var EDITOR_ASSISTANT_TAB = 'editorAssistant';
      var DASHBOARD_ASSISTANT_TAB = 'dashboardAssistant';
      var FUNCTIONS_TAB = 'functions';
      var SCHEDULES_TAB = 'schedules';

      function RightAssistPanel(params) {
        var self = this;
        self.disposals = [];

        self.activeTab = ko.observable();

        self.editorAssistantTabAvailable = ko.observable(false);
        self.dashboardAssistantTabAvailable = ko.observable(false);
        self.functionsTabAvailable = ko.observable(false);
        self.schedulesTabAvailable = ko.observable(false);

        var apiHelper = ApiHelper.getInstance();
        self.lastActiveTabEditor = apiHelper.withTotalStorage('assist', 'last.open.right.panel', ko.observable(), EDITOR_ASSISTANT_TAB);
        self.lastActiveTabDashboard = apiHelper.withTotalStorage('assist', 'last.open.right.panel.dashboard', ko.observable(), DASHBOARD_ASSISTANT_TAB);

        var assistEnabledApp = false;

        huePubSub.subscribe('assist.highlight.risk.suggestions', function () {
          if (self.editorAssistantTabAvailable() && self.activeTab() !== EDITOR_ASSISTANT_TAB) {
            self.activeTab(EDITOR_ASSISTANT_TAB);
          }
        });

        var updateTabs = function () {
          if (!assistEnabledApp) {
            params.rightAssistAvailable(false);
            return;
          }
          var rightAssistAvailable = true;
          if (self.lastActiveTabEditor() === FUNCTIONS_TAB && self.functionsTabAvailable()) {
            self.activeTab(FUNCTIONS_TAB);
          } else if (self.lastActiveTabEditor() === SCHEDULES_TAB && self.schedulesTabAvailable()) {
            self.activeTab(SCHEDULES_TAB);
          } else if (self.editorAssistantTabAvailable()) {
            self.activeTab(EDITOR_ASSISTANT_TAB);
          } else if (self.functionsTabAvailable()) {
            self.activeTab(FUNCTIONS_TAB);
          } else if (self.schedulesTabAvailable()) {
            self.activeTab(SCHEDULES_TAB);
          } else if (self.dashboardAssistantTabAvailable()) {
            self.activeTab(DASHBOARD_ASSISTANT_TAB);
          } else {
            self.activeTab(null);
            rightAssistAvailable = false;
          }
          params.rightAssistAvailable(rightAssistAvailable);
        };

        var updateContentsForType = function (type) {
          self.functionsTabAvailable(type === 'hive' || type === 'impala' || type === 'pig');
          self.editorAssistantTabAvailable(type === 'hive' || type === 'impala');
          self.dashboardAssistantTabAvailable(type === 'dashboard');
          self.schedulesTabAvailable(false);
          if (type !== 'dashboard') {
            if ('${ ENABLE_QUERY_SCHEDULING.get() }' === 'True' && IS_HUE_4) {
              huePubSub.subscribeOnce('set.current.app.view.model', function (viewModel) {
                // Async
                self.schedulesTabAvailable(!!viewModel.selectedNotebook);
                updateTabs();
              });
              huePubSub.publish('get.current.app.view.model');
            } else {
              // Right assist is only available in the Hue 3 editor and notebook.
              self.schedulesTabAvailable('${ ENABLE_QUERY_SCHEDULING.get() }' === 'True');
            }
          }
          updateTabs();
        };

        var snippetTypeSub = huePubSub.subscribe('active.snippet.type.changed', updateContentsForType);
        self.disposals.push(snippetTypeSub.remove.bind(snippetTypeSub));

        if (IS_HUE_4) {
          huePubSub.subscribe('set.current.app.name', function (appName) {
            assistEnabledApp = appName === 'editor' || appName === 'notebook' || appName === 'dashboard';
            if (!assistEnabledApp) {
              params.rightAssistAvailable(false);
            }
            if (appName === 'dashboard') {
              updateContentsForType(appName);
            }
          });
          huePubSub.publish('get.current.app.name');
        } else {
          assistEnabledApp = true;
        }
        updateTabs();
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
