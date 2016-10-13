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
from desktop.conf import USE_NEW_SIDE_PANELS
from desktop.lib.i18n import smart_unicode
from desktop.views import _ko
from django.utils.translation import ugettext as _
from metadata.conf import has_navigator
%>


<%def name="assistPanel(is_s3_enabled=False)">
  <%namespace name="sqlContextPopover" file="/sql_context_popover.mako" />
  <%namespace name="nav_components" file="/nav_components.mako" />

  ${ sqlContextPopover.sqlContextPopover() }
  ${ nav_components.nav_tags(readOnly=not user.has_hue_permission(action="write", app="metadata")) }

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
      -ms-flex: 1;
      flex: 1;
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
      position: absolute;
      overflow: hidden;
      padding-right: 3px;
      top: 10px;
      right: 0;
      bottom: 2px;
      left: 10px;
    }

    .assist-inner-header {
      width: 100%;
      color: #737373;
      margin-left:3px;
      margin-bottom:2px;
      font-weight: bold;
      margin-top: 0
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

    .assist-file-entry {
      margin-right: 15px;
      border: 1px solid transparent;
    }

    .assist-file-entry-drop {
      border: 1px solid #338BB8 !important;
    }

    .assist-tables {
      margin-left: 0;
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
      margin-right: 15px;
      overflow-x: hidden;
    }

    .assist-tables > li.selected {
      background-color: #EEE;
    }

    .assist-breadcrumb {
      padding-top: 0;
      padding-left: 0;
    }

    .assist-breadcrumb span {
      color: #737373;
    }

    .assist-breadcrumb a:not(.inactive-action) {
      cursor: pointer;
      text-decoration: none;
      color: #737373;
      -webkit-transition: color 0.2s ease;
      -moz-transition: color 0.2s ease;
      -ms-transition: color 0.2s ease;
      transition: color 0.2s ease;
    }

    .assist-breadcrumb-text {
      font-size: 14px;
      line-height: 16px;
      vertical-align: top;
    }

    .assist-breadcrumb-back {
      font-size: 15px;
      margin-right:8px;
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

    .assist-db-header-actions {
      position:absolute;
      top: 0;
      right: 0;
      padding-left:4px;
      padding-right: 13px;
      background-color: #FFF;
    }

    .assist-db-header-actions > * {
      margin-left: 2px;
    }

    .assist-actions {
      position:absolute;
      top: 0;
      right: 0;
      padding-left:4px;
      background-color: #FFF;
    }

    .assist-file-actions  {
      position:absolute;
      top: 0;
      right: 0;
      padding-right: 2px;
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

    .highlightable {
      -webkit-transition: all .5s linear;
      -moz-transition: all .5s linear;
      -o-transition: all .5s linear;
      transition: all .5s linear;
    }

    .highlight {
      color: #338BB8 !important;
      padding-left: 8px;
    }

    .assist-details-header {
      display: table-cell;
      width: 95px;
      font-weight: bold;
    }

    .assist-details-value {
      display: table-cell;
    }

    .no-entries {
      font-style: italic;
    }

    .assist-flex-panel {
      position: relative;
      display: -ms-flexbox;
      display: flex;
      -ms-flex-flow: column nowrap;
      flex-flow: column nowrap;
      align-items: stretch;
      height:100%;
    }

    .assist-flex-header {
      overflow: hidden;
      position: relative;
      -ms-flex: 0 0 25px;
      flex: 0 0 25px;
      white-space: nowrap;
    }

    .assist-flex-table-search {
      overflow: hidden;
      position: relative;
      -ms-flex: 0 0 65px;
      flex: 0 0 65px;
      white-space: nowrap;
    }

    .assist-flex-search {
      overflow: hidden;
      position: relative;
      -ms-flex: 0 0 43px;
      flex: 0 0 43px;
      white-space: nowrap;
    }

    .assist-flex-fill {
      position: relative;
      -ms-flex: 1 1 100%;
      flex: 1 1 100%;
      white-space: nowrap;
      overflow-x: hidden;
      overflow-y: auto;
      outline: none !important;
    }

    .database-tree ul {
      margin: 0 !important;
    }

    .database-tree ul li {
      padding-left: 15px;
    }

    .nav-assist-search {
      display: -ms-flexbox;
      display: flex;
      position: relative;
      -ms-flex: 1 1 29px;
      flex: 1 1 29px;
      padding: 10px;
    }

    .nav-assist-search > i {
      position: absolute;
      top: 17px;
      left: 17px;
      font-size: 15px;
      color: #ccc;
    }

    .nav-assist-search > input {
      -ms-flex: 1 1 100%;
      flex: 1 1 100%;
      height: 27px;
      box-shadow: none;
      border: 1px solid #DDD;
      border-radius: 4px;
      padding-left: 26px;
    }

    .result-entry {
      clear: both;
      overflow: hidden;
      margin: 0 10px 15px 10px;
    }

    .result-entry .doc-desc {
      font-style: italic;
      font-size: 12px;
      line-height: 15px;
      white-space: normal;
      margin-left: 35px;
    }

    .nav-search-tags {
      display: inline-block;
      margin-left: 3px;
    }

    .nav-search-tags div {
      display: inline-block;
      margin: 0 1px;
      line-height: 10px;
      font-size: 11px;
      padding: 3px 6px;
      color: #FFF;
      background-color: #338BB8;
      border-radius: 6px;
    }

    .result-entry .icon-col {
      width: 35px;
      float:left;
      vertical-align: top;
      padding-top: 7px;
      font-size: 20px;
      color: #338bb8;
    }

    .result-entry .doc-col {
      white-space: nowrap;
    }

    .doc-col-no-desc {
      padding-top: 7px;
    }

    .result-entry .hue-icon {
      font-size: 30px;
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
      <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, click: function (data, event) { showContextPopover(data, event, navigationSettings.pinEnabled); }, css: { 'blue': statsVisible }"><i class="fa fa-bar-chart" title="${_('Show details')}"></i></a>
      <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.openItem || (navigationSettings.openDatabase && definition.isDatabase), click: openItem"><i class="fa fa-long-arrow-right" title="${_('Open')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-table-entry">
    <li class="assist-table" data-bind="visibleOnHover: { override: statsVisible, selector: '.table-actions' }">
      <div class="assist-actions table-actions" style="opacity: 0">
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.showStats, click: function (data, event) { showContextPopover(data, event, navigationSettings.pinEnabled); }, css: { 'blue': statsVisible }"><i class="fa fa-bar-chart" title="${_('Show details')}"></i></a>
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.openItem, click: openItem"><i class="fa fa-long-arrow-right" title="${_('Open')}"></i></a>
      </div>
      <a class="assist-entry assist-table-link" href="javascript:void(0)" data-bind="multiClick: { click: toggleOpen, dblClick: dblClick }, attr: {'title': definition.title }, draggableText: { text: editorText,  meta: {'type': 'sql', 'table': tableName, 'database': databaseName} }"><i class="fa fa-fw fa-table muted valign-middle"></i><span data-bind="text: definition.displayName, css: { 'highlight': highlight }"></span></a>
      <div class="center" data-bind="visible: loading" style="display:none;"><i class="fa fa-spinner fa-spin assist-spinner"></i></div>
      <!-- ko template: { if: open, name: 'assist-db-entries'  } --><!-- /ko -->
    </li>
  </script>

  <script type="text/html" id="assist-db-entries">
    <!-- ko if: hasEntries() && ! loading() && filteredEntries().length == 0 -->
    <ul class="assist-tables">
      <li class="assist-entry no-entries">${_('No results found')}</li>
    </ul>
    <!-- /ko -->
    <ul class="database-tree" data-bind="foreachVisible: { data: filteredEntries, minHeight: (definition.isTable || definition.isView ? 20 : 25), container: '.assist-db-scrollable' }, css: { 'assist-tables': definition.isDatabase }">
      <!-- ko template: { if: definition.isTable, name: 'assist-table-entry' } --><!-- /ko -->
      <!-- ko ifnot: definition.isTable && ! hasErrors() -->
      <li data-bind="visible: ! hasErrors(), visibleOnHover: { override: statsVisible, selector: definition.isView ? '.table-actions' : '.column-actions' }, css: { 'assist-table': definition.isView, 'assist-column': definition.isColumn }">
        <!-- ko template: { if: definition.isView || definition.isColumn, name: 'assist-entry-actions' } --><!-- /ko -->
        <!-- ko if: expandable -->
        <a class="assist-entry" href="javascript:void(0)" data-bind="multiClick: { click: toggleOpen, dblClick: dblClick }, attr: {'title': definition.title }, css: { 'assist-field-link': !definition.isView, 'assist-table-link': definition.isView }">
          <!-- ko if: definition.isView -->
            <i class="fa fa-fw fa-eye muted valign-middle"></i>
          <!-- /ko -->
          <span class="highlightable" data-bind="css: {'query-builder-menu': definition.isColumn, 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName}, text: definition.displayName, draggableText: { text: editorText, meta: {'type': 'sql', 'column': columnName, 'table': tableName, 'database': databaseName} }"></span>
        </a>
        <!-- /ko -->
        <!-- ko ifnot: expandable -->
        <div style="cursor: default;" class="assist-entry" href="javascript:void(0)" data-bind="multiClick: { dblClick: dblClick }, attr: {'title': definition.title }, css: { 'assist-field-link': !definition.isView, 'assist-table-link': definition.isView }">
          <!-- ko if: definition.isView -->
          <i class="fa fa-fw fa-eye muted valign-middle"></i>
          <!-- /ko -->
          <span class="highlightable" data-bind="css: {'query-builder-menu': definition.isColumn, 'highlight': highlight}, attr: {'column': columnName, 'table': tableName, 'database': databaseName}, text: definition.displayName, draggableText: { text: editorText, meta: {'type': 'sql', 'column': columnName, 'table': tableName, 'database': databaseName} }"></span>
        </div>
        <!-- /ko -->
        <div class="center" data-bind="visible: loading" style="display:none;"><i class="fa fa-spinner fa-spin assist-spinner"></i></div>
        <!-- ko template: { if: open, name: 'assist-db-entries'  } --><!-- /ko -->
      </li>
      <!-- ko if: definition.isTable && hasErrors() -->
      <li class="assist-errors">
        <span >${ _('Error loading columns.') }</span>
      </li>
      <!-- /ko -->
      <!-- /ko -->
    </ul>
    <!-- ko template: { if: ! hasEntries() && ! loading() && (definition.isTable || definition.isView), name: 'assist-no-table-entries' } --><!-- /ko -->
    <!-- ko template: { if: ! hasEntries() && ! loading() && definition.isDatabase, name: 'assist-no-database-entries' } --><!-- /ko -->
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
        <!-- ko template: { name: "assist-tables-template" } --><!-- /ko -->
        <!-- /ko -->
        <!-- /ko -->
      </div>
      <!-- ko with: $parents[1] -->
      <!-- ko template: { if: searchInput() !== '' && navigatorEnabled(), name: 'nav-search-result' } --><!-- /ko -->
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
    <div class="assist-db-header-actions"style="margin-top: -1px;">
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
      <!-- ko template: { if: (searchInput() !== '' || searchHasFocus()) && navigatorEnabled(), name: 'nav-search-result' } --><!-- /ko -->
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
    <div class="assist-db-header-actions"style="margin-top: -1px;">
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
          <div>
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
      <!-- ko template: { if: (searchInput() !== '' || searchHasFocus()) && navigatorEnabled(), name: 'nav-search-result' } --><!-- /ko -->
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

  <script type="text/html" id="assist-file-panel">
    <div class="assist-flex-header assist-breadcrumb">
      <!-- ko with: activeEntry -->
      <!-- ko ifnot: isRoot -->
      <a href="javascript: void(0);" data-bind="click: function () { parent.makeActive(); }">
        <i class="fa fa-chevron-left" style="font-size: 15px;margin-right:8px;"></i>
        <i class="fa fa-folder-o" style="font-size: 14px; line-height: 16px; vertical-align: top; margin-right:4px;"></i>
        <span style="font-size: 14px;line-height: 16px;vertical-align: top;" data-bind="text: definition().name"></span>
      </a>
      <!-- /ko -->

      <!-- ko if: isRoot -->
      <div>
        <i class="fa fa-folder-o" style="font-size: 14px; line-height: 16px;vertical-align: top;margin-right:4px;"></i>
        <span style="font-size: 14px;line-height: 16px;vertical-align: top;">/</span>
      </div>
      <!-- /ko -->
      <!-- /ko -->
    </div>
    <div class="assist-flex-fill assist-file-scrollable">
      <!-- ko with: activeEntry -->
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
    </div>
  </script>

  <script type="text/html" id="assist-documents-inner-panel">
    <div class="assist-inner-panel">
      <div class="assist-flex-panel">
        <!-- ko template: 'assist-file-panel' --><!-- /ko -->
      </div>
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
    <div style="width: 100%; display: inline-block; margin-top: 5px;"><button class="pull-right btn btn-primary" data-bind="css: { 'btn-primary': invalidateOnRefresh() !== 'invalidateAndFlush', 'btn-danger': invalidateOnRefresh() === 'invalidateAndFlush' }, click: function () { huePubSub.publish('close.popover'); triggerRefresh(); }, clickBubble: false">${ _('Refresh') }</button></div>
  </script>

  <script type="text/html" id="assist-db-header-actions">
    <div class="assist-db-header-actions">
      <span class="assist-tables-counter">(<span data-bind="text: filteredEntries().length"></span>)</span>
      <!-- ko ifnot: loading -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: toggleSearch, css: { 'blue' : isSearchVisible }"><i class="pointer fa fa-filter" title="${_('Filter')}"></i></a>
      <!-- ko if: sourceType === 'impala' -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="templatePopover : { contentTemplate: 'ask-for-invalidate-content', titleTemplate: 'ask-for-invalidate-title', trigger: 'click', minWidth: '320px' }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manually refresh the table list')}"></i></a>
      <!-- /ko -->
      <!-- ko if: sourceType !== 'impala' -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: triggerRefresh"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manually refresh the table list')}"></i></a>
      <!-- /ko -->
      <!-- /ko -->
      <!-- ko if: loading -->
      <span style="color: #aaa;"><i class="fa fa-filter" title="${_('Filter tables')}"></i></span>
      <i class="fa fa-refresh fa-spin blue" title="${_('Manually refresh the table list')}"></i></a>
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
      <div><input id="searchInput" class="clearable" type="text" placeholder="${ _('Database name...') }" style="margin-top:3px;width:90%;" data-bind="hasFocus: editingSearch, clearable: filter.query, value: filter.query, valueUpdate: 'afterkeydown'"/></div>
    </div>
    <div class="assist-flex-fill assist-db-scrollable" data-bind="visible: ! hasErrors() && ! loading() && hasEntries()" style="display: none;">
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
    <div class="assist-flex-fill" data-bind="visible: loading" style="display: none;">
      <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
    </div>
    <div class="assist-flex-fill" data-bind="visible: hasErrors() && ! loading()" style="display: none;">
      <span class="assist-errors">${ _('Error loading databases.') }</span>
    </div>
    <div class="assist-flex-fill" data-bind="visible: ! hasErrors() && ! loading() && ! hasEntries()" style="display: none;">
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
      <div><input id="searchInput" class="clearable" type="text" placeholder="${ _('Table name...') }" style="width:90%;" data-bind="hasFocus: editingSearch, clearable: filter.query, value: filter.query, valueUpdate: 'afterkeydown'"/></div>
    </div>
    <div class="assist-flex-fill assist-db-scrollable" data-bind="visible: ! hasErrors() && ! loading()" style="display: none;">
      <!-- ko template: 'assist-db-entries' --><!-- /ko -->
    </div>
    <div class="assist-flex-fill" data-bind="visible: loading() || $parent.loading()" style="display: none;">
      <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
    </div>
    <div class="assist-flex-fill" data-bind="visible: hasErrors() && ! loading()" style="display: none;">
      <span class="assist-errors">${ _('Error loading tables.') }</span>
    </div>
  </script>

  <style>
    .nav-autocomplete {
      background-color: #F8F8F8;
    }

    .nav-autocomplete-item .ui-state-focus {
      border: 1px solid #DBE8F1;
      background-color: #DBE8F1 !important;
    }

    .nav-autocomplete-item-link {
      height: 44px;
      overflow:hidden;
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
        <div style="padding: 8px;"><i style="color: #338bb8" class="fa fa-fw" data-bind="css: icon"></i></div>
        <div>
          <div style="font-size: 14px; color: #338bb8" data-bind="text: label, style: { 'padding-top': description ? 0 : '8px' }"></div>
          <!-- ko if: description -->
          <div style="display:inline-block; width: 170px; overflow: hidden; white-space: nowrap; text-overflow:ellipsis; font-size: 12px;" data-bind="text: description"></div>
          <!-- /ko -->
        </div>
      </div>
    </a>
  </script>

  <script type="text/html" id="assist-panel-navigator-search">
    <!-- ko if: navigatorEnabled -->
      <div class="nav-assist-search">
        <i class="fa fa-search" data-bind="css: { 'blue': searchHasFocus() || searchInput() }"></i>
        <input id="appendedInput" placeholder="${ _('Search...') }" type="text" data-bind="autocomplete: {
            source: navAutocompleteSource,
            itemTemplate: 'nav-search-autocomp-item',
            classPrefix: 'nav-',
            showOnFocus: true,
            reopenPattern: /.*:$/
          },
          hasFocus: searchHasFocus,
          clearable: { value: searchInput, onClear: function () { huePubSub.publish('autocomplete.close'); } },
          textInput: searchInput,
          valueUpdate: 'afterkeydown'">
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
      <div style="position: relative; flex: 0 0 29px;" class="assist-panel-switches">
        <!-- ko foreach: availablePanels -->
        <div class="inactive-action assist-type-switch" data-bind="click: function () { $parent.visiblePanel($data); }, css: { 'blue': $parent.visiblePanel() === $data }, attr: { 'title': name }">
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
      <!-- ko hueSpinner: { spin: searching, center: true, size: 'large' } --><!-- /ko -->
      <!-- ko if: !searching() -->
      <!-- ko if: searchResult().length == 0 -->
        <div class="result-entry">${ _('No result found.') }</div>
      <!-- /ko -->
      <div data-bind="foreach: searchResult" style="overflow-x:hidden">
        <div class="result-entry">
          <div class="icon-col">
            <i class="fa fa-fw valign-middle" data-bind="css: icon"></i>
          </div>
          <div class="doc-col" data-bind="css: { 'doc-col-no-desc' : !hasDescription }">
            <!-- ko if: typeof click !== 'undefined' -->
            <a class="pointer" data-bind="click: click, text: parentPath + ' ' + originalName" target="_blank" ></a>
            <!-- /ko -->
            <!-- ko if: typeof click === 'undefined' -->
            <a class="pointer" data-bind="attr: { 'href': link }, text: originalName" target="_blank" ></a>
            <!-- /ko -->
            <div class="nav-search-tags" data-bind="foreach: tags"><div data-bind="text: $data"></div></div>
            <!-- ko if: hasDescription -->
              <div class="doc-desc" data-bind="text: description"></div>
            <!-- /ko -->
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
       * @param {boolean} options.visible
       * @param {boolean} [options.showNavSearch] - Default true
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
        self.showNavSearch = typeof options.showNavSearch !== 'undefined' ? options.showNavSearch : true;

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
      function AssistDbPanel (options) {
        var self = this;
        self.apiHelper = options.apiHelper;
        self.i18n = options.i18n;

        self.sources = ko.observableArray();
        var sourceIndex = {};
        $.each(options.sourceTypes, function (idx, sourceType) {
          sourceIndex[sourceType.type] = new AssistDbSource({
            apiHelper: self.apiHelper,
            i18n: self.i18n,
            type: sourceType.type,
            name: sourceType.name,
            navigationSettings: options.navigationSettings
          });
          self.sources.push(sourceIndex[sourceType.type]);
        });

        huePubSub.subscribe('assist.db.highlight', function (location) {
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
            if (newSource.databases().length === 0) {
              newSource.initDatabases();
            }
            self.apiHelper.setInTotalStorage('assist', 'lastSelectedSource', newSource.sourceType);
          } else {
            self.apiHelper.setInTotalStorage('assist', 'lastSelectedSource');
          }
        });

        var storageSourceType = self.apiHelper.getFromTotalStorage('assist', 'lastSelectedSource');

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
        var reload = function () {
          var lastKnownPath = self.apiHelper.getFromTotalStorage('assist', 'currentHdfsPath', '/');
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

        reload();

        huePubSub.subscribe('assist.selectHdfsEntry', function (entry) {
          self.selectedHdfsEntry(entry);
          self.apiHelper.setInTotalStorage('assist', 'currentHdfsPath', entry.path);
        });

        huePubSub.subscribe('assist.hdfs.refresh', function () {
          huePubSub.publish('assist.clear.hdfs.cache');
          reload();
        });
      }


      /**
       * @param {Object} options
       * @param {ApiHelper} options.apiHelper
       * @constructor
       **/
      function AssistS3Panel (options) {
        var self = this;
        self.apiHelper = options.apiHelper;

        self.selectedS3Entry = ko.observable();
        var reload = function () {
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

        reload();

        huePubSub.subscribe('assist.selectS3Entry', function (entry) {
          self.selectedS3Entry(entry);
          self.apiHelper.setInTotalStorage('assist', 'currentS3Path', entry.path);
        });

        huePubSub.subscribe('assist.s3.refresh', function () {
          huePubSub.publish('assist.clear.s3.cache');
          reload();
        });
      }

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
        'SUB_OPERATION': 'fa-code-fork'
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
            'query-hive' : "${ _('Hive Query') }",
            'query' : "${ _('Query') }",
            'notebook' : "${ _('Notebook') }"
          }
        };
        self.apiHelper = ApiHelper.getInstance({
          i18n: i18n,
          user: params.user
        });

        self.navigatorEnabled = ko.observable('${ has_navigator(user) }' === 'True');

        self.searchInput = ko.observable('').extend({ rateLimit: 500 });
        self.searchResult = ko.observableArray();

        self.searchHasFocus = ko.observable(false);
        self.searching = ko.observable(false);

        self.searchInput.subscribe(function (newValue) {
          self.performSearch(newValue);
        });

        var lastQuery = -1;

        self.loading = ko.observable(false);

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

        % if USE_NEW_SIDE_PANELS.get():
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
          showNavSearch: false,
          visible: params.visibleAssistPanels && params.visibleAssistPanels.indexOf('documents') !== -1
        }));
        % endif

        self.performSearch = function () {
          if (self.searchInput() === lastQuery) {
            return;
          }
          if (self.searching()) {
            window.setTimeout(function() {
              self.performSearch();
            }, 100);
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

          $.post('/metadata/api/navigator/search_entities', {
            query_s: self.searchInput(),
            limit: 25,
            sources: ko.mapping.toJSON([self.visiblePanel().type])
          }, function (data) {
            data.entities.forEach(function (entity) {
              entity.icon = NAV_TYPE_ICONS[entity.type];
              switch (entity.type) {
                case 'DATABASE': {
                  entity.click = function () {
                    showInAssist(entity);
                  };
                  break;
                }
                case 'TABLE': {
                  entity.click = function () {
                    showInAssist(entity);
                  };
                  break;
                }
                case 'VIEW': {
                  entity.click = function () {
                    showInAssist(entity);
                  }
                }
                case 'FIELD': {
                  entity.click = function () {
                    showInAssist(entity);
                  };
                  break;
                }
                case 'SOURCE': {
                  entity.description = '${ _("Cluster") }: ' + entity.clusterName;
                  entity.link = entity.sourceUrl;
                  break;
                }
                case 'OPERATION_EXECUTION': {
                  entity.link = '/jobbrowser/jobs/' + entity.jobID;
                  break;
                }
                case 'DIRECTORY': {
                  entity.description = entity.parentPath;
                  entity.link = '/filebrowser/#' + entity.fileSystemPath;
                  break;
                }
                case 'FILE': {
                  entity.description = entity.parentPath;
                  entity.link = '/filebrowser/#' + entity.fileSystemPath;
                  break;
                }
                case 'SUB_OPERATION': {
                  entity.description = entity.metaClassName;
                  break;
                }
                case 'PARTITION': {}
                case 'OPERATION': {}
              }
              entity.hasDescription = typeof entity.description !== 'undefined' && entity.description !== null && entity.description.length > 0;
            });
            self.searchResult(data.entities);
            self.searching(false);
          }).fail(function (xhr, textStatus, errorThrown) {
            $(document).trigger("error", xhr.responseText);
            self.searching(false);
          });
        };

        self.visiblePanel = ko.observable(self.availablePanels[0]);
        self.visiblePanel.subscribe(function(newValue) {
          if (self.navigatorEnabled()) {
            lastQuery = 'refresh';
            self.performSearch();
          }
          if (newValue.type === 'documents') {
            newValue.panelData.init();
          }
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
            query:  request.term + '*',
            successCallback: function (data) {
              var values = [];
              if (isFacet && typeof data.facets !== 'undefined') { // Is typed facet, e.g. type: type:bla
                var facetInQuery = facetMatch[1];
                if (typeof data.facets[facetInQuery] !== 'undefined') {
                  Object.keys(data.facets[facetInQuery]).forEach(function (facetValue) {
                    if (partial === '' || facetValue.indexOf(partial) !== -1) {
                      values.push({ data: { label: facetInQuery + ':' + facetValue, icon: NAV_FACET_ICON, description: '' }, value: beforePartial + facetValue})
                    }
                  });
                }
              } else {
                if (typeof data.facets !== 'undefined') {
                  Object.keys(data.facets).forEach(function (facet) {
                    if (partial.length === 0 || facet.indexOf(partial) !== -1) {
                      if (Object.keys(data.facets[facet]).length > 0) {
                        values.push({ data: { label: facet + ':', icon: NAV_FACET_ICON, description: Object.keys(data.facets[facet]).join(', ') }, value: beforePartial + facet + ':'});
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
                if (values.length > 0) {
                  values.push({ divider: true });
                }
                if (typeof data.results !== 'undefined') {
                  data.results.forEach(function (result) {
                    values.push({ data: { label: result.originalName, icon: NAV_TYPE_ICONS[result.type],  description: result.parentPath }, value: beforePartial + result.originalName });
                  });
                }
              }
              if (values.length > 0 && values[values.length - 1].divider) {
                values.pop();
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
</%def>
