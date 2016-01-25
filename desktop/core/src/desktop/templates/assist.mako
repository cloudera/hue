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
from desktop import conf
from desktop.lib.i18n import smart_unicode
from django.utils.translation import ugettext as _
from desktop.views import _ko
%>

<%def name="assistPanel(scrollable='.assist-stretchable-list')">
  <style>

    .assist-icon {
      width: 16px;
      height: 16px;
      -webkit-filter: grayscale(1);
      filter: grayscale(1);
      opacity: .8;
    }

    .assist {
      position: relative;
      height: 100%;
    }

    .assist-resizer {
      cursor: row-resize;
    }

    .assist-spinner {
      font-size: 20px;
      color: #BBB;
    }

    .assist-header {
      color: #338bb8;
      background-color: #f9f9f9;
      border-top: 1px solid #f1f1f1;
      border-bottom: 1px solid #f1f1f1;
      font-weight: bold;
      letter-spacing: 0.035em;
      font-size: 0.975em;
      line-height: 25px;
      padding-left: 10px;
      height: 24px;
      margin-bottom: 8px;
    }

    .assist-inner-panel {
      display: none;
      position: relative;
      padding: 0 0 0 10px;
      overflow: hidden;
    }

    .assist-inner-header {
      position:relative;
      width: 100%;
      color: #737373;
      margin-left:3px;
      margin-bottom:2px;
      font-weight: bold;
      margin-top: 0
    }
    
    .nav.nav-no-margin {
      margin-bottom: 0;
    }

    .assist-stretchable-list {
      position:relative;
      overflow-y: auto;
      overflow-x: hidden;
      width: 100%;
      border: none;
      padding: 0;
      margin-bottom: 1px;
      margin-top:3px;
    }

    .assist-header-actions {
      float: right;
      margin-right: 3px;
      opacity: 0;
    }

    .assist-header-actions > div {
      cursor: pointer;
    }

    .assist-panel-switches {
      padding-left: 12px;
      height: 29px;
      border-bottom: 1px solid #f1f1f1;
    }

    .assist-type-switch {
      display: inline-block;
      font-size: 16px;
      margin-right: 2px;
      cursor: pointer;
    }

    .assist-column {
      position: relative;
    }

    .assist-entry,a {
      white-space: nowrap;
    }

    .assist-tables {
      margin-left: 3px;
    }

    .assist-tables a {
      text-decoration: none;
    }

    .assist-tables li {
      list-style: none;
    }

    .assist-breadcrumb > a:hover {
      color: #338bb8;
    }

    .assist-errors {
      padding: 4px 5px;
      font-style: italic;
    }

    .assist-tables > li {
      position: relative;
      padding-top: 2px;
      padding-bottom: 2px;
      padding-left: 4px;
    }

    .assist-tables > li.selected {
      background-color: #EEE;
    }

    .assist-breadcrumb {
      position:relative;
      left: 0;
      top: 0;
      right: 0;
      height:25px;
      padding-top: 0px;
      padding-left: 0px;
    }

    .assist-breadcrumb a  {
      cursor: pointer;
      text-decoration: none;
      color: #737373;
      -webkit-transition: color 0.2s ease;
      -moz-transition: color 0.2s ease;
      -ms-transition: color 0.2s ease;
      transition: color 0.2s ease;
    }

    .assist-tables-counter {
      color: #d1d1d1;
      font-weight: normal;
    }

    .assist-table-link {
      font-size: 13px;
    }

    .assist-field-link {
      font-size: 12px;
    }

    .assist-table-link,
    .assist-table-link:focus {
      color: #444;
    }

    .assist-field-link,
    .assist-field-link:focus {
      white-space: nowrap;
      color: #737373;
    }

    .assist-db-header-actions,
    .assist-actions  {
      position:absolute;
      top: 0;
      right: 0;
      padding-right: 17px;
      padding-left:4px;
      background-color: #FFF;
    }

    .table-actions {
      padding-top:2px;
    }

    .assist-tables > li.selected .assist-actions {
      background-color: #EEE;
    }

    .assist-details-wrap {
      display: table;
      width: 100%;
      table-layout: fixed;
    }

    .assist-details-wrap > div {
      display: table-row;
    }

    .assist-details-header {
      display: table-cell;
      width: 95px;
      font-weight: bold;
    }

    .assist-details-value {
      display: table-cell;
    }

    .assist-show-more {
      padding-left: 2px;
      padding-bottom: 5px;
      font-style: italic;
    }

    .no-entries {
      font-style: italic;
    }
  </style>

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
      <a class="inactive-action" href="javascript:void(0)" data-bind="visible: (definition.isTable || definition.isView) && navigationSettings.showPreview, click: showPreview"><i class="fa fa-list" title="${_('Preview Sample data')}"></i></a>
      <span data-bind="visible: navigationSettings.showStats, component: { name: 'table-stats', params: {
          statsVisible: statsVisible,
          sourceType: assistDbSource.type,
          snippet: assistDbSource.snippet,
          databaseName: databaseName,
          tableName: tableName,
          columnName: columnName,
          fieldType: definition.type,
          assistHelper: assistDbSource.assistHelper
        } }"></span>
      <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.openItem || (navigationSettings.openDatabase && definition.isDatabase), click: openItem"><i class="fa fa-long-arrow-right" title="${_('Open')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-table-entry">
    <li class="assist-table" data-bind="visibleOnHover: { override: statsVisible, selector: '.table-actions' }">
      <div class="assist-actions table-actions" style="opacity: 0">
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showPreview, click: showPreview"><i class="fa fa-list" title="${_('Preview Sample data')}"></i></a>
        <span data-bind="visible: navigationSettings.showStats, component: { name: 'table-stats', params: { statsVisible: statsVisible, sourceType: assistDbSource.type, snippet: assistDbSource.snippet, databaseName: databaseName, tableName: tableName, columnName: columnName, fieldType: definition.type, assistHelper: assistDbSource.assistHelper }}"></span>
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.openItem, click: openItem"><i class="fa fa-long-arrow-right" title="${_('Open')}"></i></a>
      </div>
      <a class="assist-entry assist-table-link" href="javascript:void(0)" data-bind="multiClick: { click: toggleOpen, dblClick: dblClick }, attr: {'title': definition.title }"><i class="fa fa-fw fa-table muted valign-middle"></i><span draggable="true" data-bind="text: definition.displayName, draggableText: { text: editorText }"></span></a>
      <div class="center" data-bind="visible: loading" style="display:none;"><i class="fa fa-spinner fa-spin assist-spinner"></i></div>
      <!-- ko template: { if: open, name: 'assist-entries'  } --><!-- /ko -->
    </li>
  </script>

  <script type="text/html" id="assist-entries">
    <!-- ko if: hasEntries() && ! loading() && filteredEntries().length == 0 -->
    <ul class="assist-tables">
      <li class="assist-entry no-entries">${_('No results found')}</li>
    </ul>
    <!-- /ko -->
    <ul data-bind="hueach: {data: filteredEntries, itemHeight: (definition.isTable || definition.isView ? 20 : 25), scrollable: '${scrollable}', considerStretching: true}, css: { 'assist-tables': definition.isDatabase }">
      <!-- ko template: { if: definition.isTable, name: 'assist-table-entry' } --><!-- /ko -->
      <!-- ko ifnot: definition.isTable -->
      <li data-bind="visible: ! hasErrors(), visibleOnHover: { override: statsVisible, selector: definition.isView ? '.table-actions' : '.column-actions' }, css: { 'assist-table': definition.isView, 'assist-column': definition.isColumn }">
        <!-- ko template: { if: definition.isView || definition.isColumn, name: 'assist-entry-actions' } --><!-- /ko -->
        <a class="assist-entry" href="javascript:void(0)" data-bind="multiClick: { click: toggleOpen, dblClick: dblClick }, attr: {'title': definition.title }, css: { 'assist-field-link': !definition.isView, 'assist-table-link': definition.isView }">
          <!-- ko if: definition.isView -->
            <i class="fa fa-fw fa-eye muted valign-middle"></i>
          <!-- /ko -->
          <span draggable="true" data-bind="text: definition.displayName, draggableText: { text: editorText }"></span>
        </a>
        <div class="center" data-bind="visible: loading" style="display:none;"><i class="fa fa-spinner fa-spin assist-spinner"></i></div>
        <!-- ko template: { if: open, name: 'assist-entries'  } --><!-- /ko -->
      </li>
      <li class="assist-errors" data-bind="visible: hasErrors() && definition.isTable">
        <span >${ _('Error loading columns.') }</span>
      </li>

      <!-- /ko -->
    </ul>
    <!-- ko template: { if: ! hasEntries() && ! loading() && (definition.isTable || definition.isView), name: 'assist-no-table-entries' } --><!-- /ko -->
    <!-- ko template: { if: ! hasEntries() && ! loading() && definition.isDatabase, name: 'assist-no-database-entries' } --><!-- /ko -->
  </script>

  <script type="text/html" id="assist-db-breadcrumb">
    <div class="assist-breadcrumb">
      <a data-bind="click: back">
        <i class="fa fa-chevron-left" style="font-size: 15px;margin-right:8px;"></i>
        <i data-bind="visible: selectedSource() && ! selectedSource().selectedDatabase()" style="display:none;font-size: 14px;line-height: 16px;vertical-align: top;" class="fa fa-server"></i>
        <i data-bind="visible: selectedSource() && selectedSource().selectedDatabase()" style="display:none;font-size: 14px;line-height: 16px;vertical-align: top;" class="fa fa-database"></i>
        <span style="font-size: 14px;line-height: 16px;vertical-align: top;" data-bind="text: breadcrumb"></span></a>
    </div>
  </script>

  <script type="text/html" id="assist-db-inner-panel">
    <div class="assist-inner-panel" data-bind="event: { 'scroll': function (data, event) { if (selectedSource()) { selectedSource().repositionActions(data, event); } } }">
      <!-- ko template: { if: breadcrumb() !== null, name: 'assist-db-breadcrumb' } --><!-- /ko -->
        <!-- ko template: { ifnot: selectedSource, name: 'assist-sources-template' } --><!-- /ko -->
        <!-- ko with: selectedSource -->
        <!-- ko template: { ifnot: selectedDatabase, name: 'assist-databases-template' }--><!-- /ko -->
        <!-- ko with: selectedDatabase -->
        <!-- ko template: { name: "assist-tables-template" } --><!-- /ko -->
        <!-- /ko -->
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

  <script type="text/html" id="assist-hdfs-inner-panel">
    <div class="assist-inner-panel">
      <!-- ko with: selectedHdfsEntry -->
      <div class="assist-breadcrumb">
        <!-- ko if: parent !== null -->
        <a href="javascript: void(0);" data-bind="click: function () { huePubSub.publish('assist.selectHdfsEntry', parent); }">
          <i class="fa fa-chevron-left" style="font-size: 15px;margin-right:8px;"></i>
          <i class="fa fa-folder" style="font-size: 14px; line-height: 16px; vertical-align: top;"></i>
          <span style="font-size: 14px;line-height: 16px;vertical-align: top;" data-bind="text: path"></span>
        </a>
        <!-- /ko -->
        <!-- ko if: parent === null -->
        <div>
          <i class="fa fa-folder" style="font-size: 14px; line-height: 16px;vertical-align: top;"></i>
          <span style="font-size: 14px;line-height: 16px;vertical-align: top;" data-bind="text: path"></span>
        </div>
        <!-- /ko -->
      </div>
      <ul class="nav assist-stretchable-list" data-bind="stretchDown">
        <li class="center" data-bind="visible: loading">
          <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i><!--<![endif]-->
          <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
        </li>

        <li data-bind="visible: ! hasErrors()">
          <ul class="assist-tables" data-bind="hueach: {data: entries, itemHeight: 20, scrollable: '.assist-stretchable-list', considerStretching: true}">
            <li class="assist-entry assist-table-link" style="position: relative;" data-bind="visibleOnHover: { 'selector': '.assist-actions' }">
              <div class="assist-actions table-actions" style="opacity: 0;" >
                <a style="padding: 0 3px;" class="inactive-action" href="javascript:void(0);" data-bind="templatePopover : { contentTemplate: 'hdfs-details-content', titleTemplate: 'hdfs-details-title', minWidth: '320px' }">
                  <i class='fa fa-info' title="${ _('Details') }"></i>
                </a>
              </div>

              <a href="javascript:void(0)" class="assist-entry assist-table-link" data-bind="multiClick: { click: toggleOpen, dblClick: dblClick }, attr: {'title': definition.name }">
                <!-- ko if: definition.type === 'dir' -->
                <i class="fa fa-fw fa-folder muted valign-middle"></i>
                <!-- /ko -->
                <!-- ko if: definition.type === 'file' -->
                <i class="fa fa-fw fa-file-o muted valign-middle"></i>
                <!-- /ko -->
                <span draggable="true" data-bind="text: definition.name, draggableText: { text: '\'' + path + '\'' }"></span>
              </a>
            </li>
          </ul>
          <!-- ko if: !loading() && entries().length === 0 -->
          <ul class="assist-tables">
            <li class="assist-entry" style="font-style: italic;">${_('Empty directory')}</li>
          </ul>
          <!-- /ko -->
        </li>
        <li class="assist-errors" data-bind="visible: hasErrors">
          <span>${ _('Error loading contents.') }</span>
        </li>
      </ul>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="document-details-content">
    <!-- ko with: definition -->
    <div class="assist-details-wrap">
      <div><div class="assist-details-header">${ _('Description') }</div><div class="assist-details-value" data-bind="text: description"></div></div>
      <div><div class="assist-details-header">${ _('Modified') }</div><div class="assist-details-value" data-bind="text: last_modified"></div></div>
      <div><div class="assist-details-header">${ _('Owner') }</div><div class="assist-details-value" data-bind="text: owner"></div></div>
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="document-details-title">
    <span data-bind="text: definition.name"></span>
  </script>

  <script type="text/html" id="assist-documents-inner-panel">
    <div class="assist-inner-panel">
      <!-- ko with: documents -->
      <ul class="nav assist-tables assist-stretchable-list" data-bind="visible: ! hasErrors(), stretchDown, foreach: availableTypes">
        <li class="assist-table">
          <a class="assist-entry assist-table-link" href="javascript: void(0);" data-bind="click: function () { open(! open()) }">
            <!-- ko if: type == 'query-hive' || type == 'query' -->
            <img src="${ static('beeswax/art/icon_beeswax_48.png') }" class="assist-icon"/>
            <!-- /ko -->
            <!-- ko if: type == 'query-impala' -->
            <img src="${ static('impala/art/icon_impala_48.png') }" class="assist-icon"/>
            <!-- /ko -->
            <!-- ko if: type == 'notebook' -->
            <i class="fa fa-fw fa-tags muted valign-middle"></i>
            <!-- /ko -->
            <!-- ko if: type == 'oozie-workflow2' -->
            <img src="${ static('oozie/art/icon_oozie_workflow_48.png') }" class="assist-icon"/>
            <!-- /ko -->
            <!-- ko if: type == 'oozie-coordinator2' -->
            <img src="${ static('oozie/art/icon_oozie_coordinator_48.png') }" class="assist-icon"/>
            <!-- /ko -->
            <!-- ko if: type == 'oozie-bundle2' -->
            <img src="${ static('oozie/art/icon_oozie_bundle_48.png') }" class="assist-icon"/>
            <!-- /ko -->
            <!-- ko if: type == 'search-dashboard' -->
            <i class="fa fa-fw fa-search muted valign-middle"></i>
            <!-- /ko -->

            <span data-bind="text: name"></span>
          </a>
          <ul data-bind="slideVisible: open, foreach: documents">
            <li style="position: relative;" data-bind="visibleOnHover: { 'selector': '.assist-actions' }">
              <div class="assist-actions table-actions" style="opacity: 0;" >
                <a style="padding: 0 3px;" class="inactive-action" href="javascript:void(0);" data-bind="templatePopover : { contentTemplate: 'document-details-content', titleTemplate: 'document-details-title', minWidth: '350px' }">
                  <i class='fa fa-info' title="${ _('Details') }"></i>
                </a>
              </div>
              <a data-bind="attr: {'href': definition.absoluteUrl }, text: definition.name"></a>
            </li>
          </ul>
        </li>
      </ul>
      <ul class="nav assist-tables" data-bind="visible: hasErrors">
        <li class="assist-errors">
          <span>${ _('Error loading documents.') }</span>
        </li>
      </ul>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="assist-sources-template">
    <ul class="nav nav-no-margin">
      <li class="assist-inner-header">
        ${_('Sources')}
      </li>
    </ul>
    <ul class="nav assist-stretchable-list" data-bind="stretchDown">
      <li>
        <ul class="assist-tables" data-bind="foreach: sources">
          <li class="assist-table pointer">
            <a class="assist-table-link" href="javascript: void(0);" data-bind="text: name, click: function () { $parent.selectedSource($data); }"></a>
          </li>
        </ul>
      </li>
    </ul>
  </script>

  <script type="text/html" id="assist-db-header-actions">
    <div class="hover-actions assist-db-header-actions" data-bind="visible: hasEntries() && (!$parent.loading() && !$parent.hasErrors()">
      <span class="assist-tables-counter">(<span data-bind="text: filteredEntries().length"></span>)</span>
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: toggleSearch, css: { 'blue' : isSearchVisible }"><i class="pointer fa fa-search" title="${_('Search')}"></i></a>
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manually refresh the table list')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-databases-template">
    <ul class="nav nav-no-margin" data-bind="visibleOnHover: { selector: '.hover-actions', override: isSearchVisible() || loading() }" >
      <li class="assist-inner-header">
        ${_('Databases')}
        <!-- ko template: 'assist-db-header-actions' --><!-- /ko -->
      </li>
      <li data-bind="slideVisible: hasEntries() && isSearchVisible()">
        <div><input id="searchInput" class="clearable" type="text" placeholder="${ _('Database name...') }" style="margin-top:3px;width:90%;" data-bind="hasFocus: editingSearch, clearable: filter.query, value: filter.query, valueUpdate: 'afterkeydown'"/></div>
      </li>
    </ul>
    <ul class="nav assist-stretchable-list" data-bind="stretchDown">
      <li data-bind="visible: ! hasErrors()" >
        <ul class="assist-tables" data-bind="hueach: {data: filteredEntries, itemHeight: 20, scrollable: '.assist-stretchable-list', considerStretching: true}">
          <li class="assist-table pointer" data-bind="visibleOnHover: { selector: '.database-actions' }">
            <!-- ko template: { name: 'assist-entry-actions' } --><!-- /ko -->
            <a class="assist-table-link" href="javascript: void(0);" data-bind="text: definition.name, click: function () { $parent.selectedDatabase($data) }"></a>
          </li>
        </ul>
        <!-- ko if: hasEntries() && ! loading() && filteredEntries().length == 0 -->
        <ul class="assist-tables">
          <li class="assist-entry" style="font-style: italic;">${_('No results found')}</li>
        </ul>
        <!-- /ko -->
      </li>
      <li class="center" data-bind="visible: loading" >
        <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i><!--<![endif]-->
        <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
      </li>
      <li class="assist-errors" data-bind="visible: hasErrors">
        <span>${ _('Error loading databases.') }</span>
      </li>
    </ul>
  </script>

  <script type="text/html" id="assist-tables-template">
    <ul class="nav nav-no-margin" data-bind="visibleOnHover: { selector: '.hover-actions', override: $parent.reloading() || isSearchVisible() }">
      <li class="assist-inner-header" data-bind="visible: !$parent.loading() && !$parent.hasErrors()">
        ${_('Tables')}
        <!-- ko template: 'assist-db-header-actions' --><!-- /ko -->
      </li>
      <li data-bind="slideVisible: hasEntries() && isSearchVisible() && !$parent.loading() && !$parent.hasErrors()">
        <div><label class="checkbox inline-block margin-left-5"><input type="checkbox" data-bind="checked: filter.showTables" />Tables</label><label class="checkbox inline-block margin-left-10"><input type="checkbox" data-bind="checked: filter.showViews" />Views</label></div>
        <div><input id="searchInput" class="clearable" type="text" placeholder="${ _('Table name...') }" style="width:90%;" data-bind="hasFocus: editingSearch, clearable: filter.query, value: filter.query, valueUpdate: 'afterkeydown'"/></div>
      </li>
    </ul>
    <ul class="nav assist-stretchable-list" data-bind="stretchDown">
      <li class="table-container" data-bind="visible: ! hasErrors()">
        <div class="center" data-bind="visible: loading() || $parent.loading()">
          <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i><!--<![endif]-->
          <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
        </div>
        <!-- ko template: { ifnot: loading() || $parent.loading(), name: 'assist-entries' } --><!-- /ko -->
      </li>
      <li class="assist-errors" data-bind="visible: hasErrors">
        <span>${ _('Error loading tables.') }</span>
      </li>
    </ul>
    <div id="assistQuickLook" class="modal hide fade">
      <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <a class="tableLink pull-right" href="#" target="_blank" style="margin-right: 20px;margin-top:6px">
          <i class="fa fa-external-link"></i> ${ _('View in Metastore Browser') }
        </a>
        <h3>${_('Data sample for')} <span class="tableName"></span></h3>
      </div>
      <div class="modal-body" style="min-height: 100px">
        <!-- ko if: assistDbSource.loadingSamples -->
        <div class="loader">
          <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 30px; color: #DDD"></i><!--<![endif]-->
          <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
        </div>
        <!-- /ko -->
        <!-- ko ifnot: assistDbSource.loadingSamples -->
        <div style="overflow: auto">
          <!-- ko with: assistDbSource.samples -->
          <!-- ko if: rows.length == 0 -->
          <div class="alert">${ _('The selected table has no data.') }</div>
          <!-- /ko -->
          <!-- ko if: rows.length > 0 -->
          <table class="table table-striped table-condensed">
            <tr>
              <th style="width: 10px"></th>
              <!-- ko foreach: headers -->
              <th data-bind="text: $data"></th>
              <!-- /ko -->
            </tr>
            <tbody>
            <!-- ko foreach: rows -->
            <tr>
              <td data-bind="text: $index()+1"></td>
              <!-- ko foreach: $data -->
              <td style="white-space: pre;" data-bind="text: $data"></td>
              <!-- /ko -->
            </tr>
            <!-- /ko -->
            </tbody>
          </table>
          <!-- /ko -->
          <!-- /ko -->
        </div>
        <!-- /ko -->
      </div>
      <div class="modal-footer">
        <button class="btn btn-primary disable-feedback" data-dismiss="modal">${_('Ok')}</button>
      </div>
    </div>
  </script>

  <script type="text/html" id="assist-panel-switches">
    <div class="assist-panel-switches assist-fixed-height" style="display:none;">
      <!-- ko foreach: availablePanels -->
      <div class="inactive-action assist-type-switch" data-bind="click: function () { visible(!visible()) }, css: { 'blue': visible }, attr: { 'title': visible() ? '${ _('Hide') } ' + name : '${ _('Show') } ' + name }">
        <i class="fa fa-fw valign-middle" data-bind="css: icon"></i>
      </div>
      <!-- /ko -->
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
    <div style="position:relative; height: 100%;" data-bind="assistVerticalResizer: { panels: visiblePanels, assistHelper: assistHelper }">
      <!-- ko template: { if: availablePanels.length > 1, name: 'assist-panel-switches' }--><!-- /ko -->
      <div data-bind="visible: visiblePanels().length === 0" style="margin:10px; font-style: italic; display:none;">${_('Select your assist contents above.')}</div>
      <!-- ko foreach: visiblePanels -->
      <!-- ko template: { if: $parent.availablePanels.length > 1, name: 'assist-panel-inner-header', data: panelData }--><!-- /ko -->
      <!-- ko template: { name: templateName, data: panelData } --><!-- /ko -->
      <!-- /ko -->
    </div>
  </script>

  <script type="text/javascript" charset="utf-8">
    (function (factory) {
      if(typeof require === "function") {
        define('assistPanel', [
          'knockout',
          'desktop/js/assist/assistDbSource',
          'desktop/js/assist/assistHdfsEntry',
          'desktop/js/assist/assistDocuments',
          'desktop/js/assist/assistHelper',
          'tableStats'
        ], factory);
      } else {
        factory(ko, AssistDbSource, AssistHdfsEntry, AssistDocuments, AssistHelper);
      }
    }(function (ko, AssistDbSource, AssistHdfsEntry, AssistDocuments, AssistHelper) {

      /**
       * @param {Object} options
       * @param {AssistHelper} options.assistHelper
       * @param {string} options.type
       * @param {number} options.minHeight
       * @param {string} options.icon
       * @param {boolean} options.visible
       * @param {(AssistDbPanel|AssistHdfsPanel|AssistDocumentsPanel)} panelData
       * @constructor
       */
      function AssistInnerPanel (options) {
        var self = this;
        self.minHeight = options.minHeight;
        self.icon = options.icon;
        self.type = options.type;
        self.name = options.name;
        self.panelData = options.panelData;

        self.visible = ko.observable(options.visible);
        options.assistHelper.withTotalStorage('assist', 'showingPanel_' + self.type, self.visible, false, options.visible);
        self.templateName = 'assist-' + self.type + '-inner-panel'
      }

      /**
       * @param {Object} options
       * @param {AssistHelper} options.assistHelper
       * @param {Object} options.i18n
       * @param {Object[]} options.sourceTypes - All the available SQL source types
       * @param {string} options.sourceTypes[].name - Example: Hive SQL
       * @param {string} options.sourceTypes[].type - Example: hive
       * @param {string} [options.activeSourceType] - Example: hive
       * @param {Object} options.navigationSettings - enable/disable the links
       * @param {boolean} options.navigationSettings.openItem
       * @param {boolean} options.navigationSettings.showPreview
       * @param {boolean} options.navigationSettings.showStats

       * @constructor
       **/
      function AssistDbPanel (options) {
        var self = this;
        self.assistHelper = options.assistHelper;
        self.i18n = options.i18n;

        self.sources = ko.observableArray();
        var sourceIndex = {};
        $.each(options.sourceTypes, function (idx, sourceType) {
          sourceIndex[sourceType.type] = new AssistDbSource({
            assistHelper: self.assistHelper,
            i18n: self.i18n,
            type: sourceType.type,
            name: sourceType.name,
            navigationSettings: options.navigationSettings
          });
          self.sources.push(sourceIndex[sourceType.type]);
        });

        self.selectedSource = ko.observable(null);

        var setDatabaseWhenLoaded = function (databaseName) {
          if (self.selectedSource().loaded()) {
            self.selectedSource().setDatabase(databaseName);
          } else {
            var subscription = self.selectedSource().loaded.subscribe(function (newValue) {
              if (newValue) {
                self.selectedSource().setDatabase(databaseName);
                subscription.dispose();
              }
            });
            if (! self.selectedSource().loaded() && ! self.selectedSource().loading()) {
              self.selectedSource().initDatabases();
            }
          }
        };

        huePubSub.subscribe("assist.set.database", function (databaseDef) {
          if (! databaseDef.source || ! sourceIndex[databaseDef.source]) {
            return;
          }
          self.selectedSource(sourceIndex[databaseDef.source]);
          setDatabaseWhenLoaded(databaseDef.name);
        });

        huePubSub.subscribe("assist.get.database", function (source) {
          if (sourceIndex[source] && sourceIndex[source].selectedDatabase()) {
            huePubSub.publish("assist.database.set", {
              source: source,
              name: sourceIndex[source].selectedDatabase().databaseName
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
            newSource.initDatabases();
            self.assistHelper.setInTotalStorage('assist', 'lastSelectedSource', newSource.type);
          } else {
            self.assistHelper.setInTotalStorage('assist', 'lastSelectedSource');
          }
        });

        var storageSourceType = self.assistHelper.getFromTotalStorage('assist', 'lastSelectedSource');

        if (! self.selectedSource()) {
          if (options.activeSourceType) {
            self.selectedSource(sourceIndex[options.activeSourceType]);
            setDatabaseWhenLoaded();
          } else if (storageSourceType && sourceIndex[storageSourceType]) {
            self.selectedSource(sourceIndex[storageSourceType]);
            setDatabaseWhenLoaded();
          }
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

      /**
       * @param {Object} options
       * @param {AssistHelper} options.assistHelper
       * @param {Object} options.i18n
       * @constructor
       **/
      function AssistDocumentsPanel (options) {
        var self = this;
        self.documents = new AssistDocuments(options.assistHelper, options.i18n);
        self.documents.load();
      }

      /**
       * @param {Object} options
       * @param {AssistHelper} options.assistHelper
       * @constructor
       **/
      function AssistHdfsPanel (options) {
        var self = this;
        self.assistHelper = options.assistHelper;

        var lastKnownPath = self.assistHelper.getFromTotalStorage('assist', 'currentHdfsPath', '/');
        var parts = lastKnownPath.split('/');
        parts.shift();

        var currentEntry = new AssistHdfsEntry({
          definition: {
            name: '/',
            type: 'dir'
          },
          parent: null,
          assistHelper: self.assistHelper
        });

        currentEntry.loadDeep(parts, function (entry) {
          currentEntry = entry;
        });

        currentEntry.open(true);
        self.selectedHdfsEntry = ko.observable(currentEntry);

        huePubSub.subscribe('assist.selectHdfsEntry', function (entry) {
          self.selectedHdfsEntry(entry);
          self.assistHelper.setInTotalStorage('assist', 'currentHdfsPath', entry.path);
        });
      }

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
       * @param {boolean} params.sql.navigationSettings.showPreview - Example: true
       * @param {boolean} params.sql.navigationSettings.showStats - Example: true
       * @constructor
       */
      function AssistPanel (params) {
        var self = this;
        var i18n = {
          errorLoadingDatabases: "${ _('There was a problem loading the databases') }",
          errorLoadingTablePreview: "${ _('There was a problem loading the table preview.') }",
          documentTypes: {
            'query-hive' : "${ _('Hive Query') }",
            'query' : "${ _('Query') }",
            'notebook' : "${ _('Notebook') }"
          }
        };
        self.assistHelper = AssistHelper.getInstance({
          i18n: i18n,
          user: params.user
        });

        self.onlySql = params.onlySql;
        self.loading = ko.observable(false);

        self.availablePanels = [
          new AssistInnerPanel({
            panelData: new AssistDbPanel($.extend({
              assistHelper: self.assistHelper,
              i18n: i18n
            }, params.sql)),
            assistHelper: self.assistHelper,
            name: '${ _("SQL") }',
            type: 'db',
            icon: 'fa-database',
            minHeight: 55,
            visible: params.visibleAssistPanels && params.visibleAssistPanels.indexOf('sql') !== -1
          })
        ];

        if (! self.onlySql) {
          self.availablePanels.push(new AssistInnerPanel({
            panelData: new AssistHdfsPanel({
              assistHelper: self.assistHelper
            }),
            assistHelper: self.assistHelper,
            name: '${ _("HDFS") }',
            type: 'hdfs',
            icon: 'fa-folder-o',
            minHeight: 40,
            visible: params.visibleAssistPanels && params.visibleAssistPanels.indexOf('hdfs') !== -1
          }));
          self.availablePanels.push(new AssistInnerPanel({
            panelData: new AssistDocumentsPanel({
              assistHelper: self.assistHelper,
              i18n: i18n
            }),
            assistHelper: self.assistHelper,
            name: '${ _("Documents") }',
            type: 'documents',
            icon: 'fa-files-o',
            minHeight: 40,
            visible: params.visibleAssistPanels && params.visibleAssistPanels.indexOf('documents') !== -1
          }));
        }

        if (self.availablePanels.length == 1) {
          self.availablePanels[0].visible(true);
        }

        self.visiblePanels = ko.pureComputed(function () {
          var result = $.grep(self.availablePanels, function (panel) {
            return panel.visible();
          });
          return result;
        });
      }

      ko.components.register('assist-panel', {
        viewModel: AssistPanel,
        template: { element: 'assist-panel-template' }
      });
    }));
  </script>
</%def>