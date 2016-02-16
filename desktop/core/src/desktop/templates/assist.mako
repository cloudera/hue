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
      display: none;
      position: relative;
      padding: 0 0 0 10px;
      overflow: hidden;
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
      padding-top: 0px;
      padding-left: 0px;
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
      display: flex;
      flex-flow: column nowrap;
      align-items: stretch;
      height:100%;
    }

    .assist-flex-header {
      overflow: hidden;
      position: relative;
      flex: 0 0 25px;
      white-space: nowrap;
    }

    .assist-flex-table-search {
      overflow: hidden;
      position: relative;
      flex: 0 0 65px;
      white-space: nowrap;
    }

    .assist-flex-search {
      overflow: hidden;
      position: relative;
      flex: 0 0 43px;
      white-space: nowrap;
    }

    .assist-flex-fill {
      position: relative;
      flex: 1 1 100%;
      white-space: nowrap;
      overflow-x: hidden;
      overflow-y: auto;
    }

    .database-tree ul {
      margin: 0 !important;
    }

    .database-tree ul li {
      padding-left: 15px;
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
          sourceType: sourceType,
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
        <span data-bind="visible: navigationSettings.showStats, component: { name: 'table-stats', params: { statsVisible: statsVisible, sourceType: sourceType, snippet: assistDbSource.snippet, databaseName: databaseName, tableName: tableName, columnName: columnName, fieldType: definition.type, assistHelper: assistDbSource.assistHelper }}"></span>
        <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.openItem, click: openItem"><i class="fa fa-long-arrow-right" title="${_('Open')}"></i></a>
      </div>
      <a class="assist-entry assist-table-link" href="javascript:void(0)" data-bind="multiClick: { click: toggleOpen, dblClick: dblClick }, attr: {'title': definition.title }"><i class="fa fa-fw fa-table muted valign-middle"></i><span draggable="true" data-bind="text: definition.displayName, draggableText: { text: editorText }"></span></a>
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
        <a class="assist-entry" href="javascript:void(0)" data-bind="multiClick: { click: toggleOpen, dblClick: dblClick }, attr: {'title': definition.title }, css: { 'assist-field-link': !definition.isView, 'assist-table-link': definition.isView }">
          <!-- ko if: definition.isView -->
            <i class="fa fa-fw fa-eye muted valign-middle"></i>
          <!-- /ko -->
          <span draggable="true" data-bind="text: definition.displayName, draggableText: { text: editorText }"></span>
        </a>
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
      <a data-bind="click: back">
        <i class="fa fa-chevron-left" style="font-size: 15px;margin-right:8px;"></i>
        <i data-bind="visible: selectedSource() && ! selectedSource().selectedDatabase()" style="display:none;font-size: 14px;line-height: 16px;vertical-align: top;" class="fa fa-server"></i>
        <i data-bind="visible: selectedSource() && selectedSource().selectedDatabase()" style="display:none;font-size: 14px;line-height: 16px;vertical-align: top;" class="fa fa-database"></i>
        <span style="font-size: 14px;line-height: 16px;vertical-align: top;" data-bind="text: breadcrumb"></span></a>
    </div>
  </script>

  <script type="text/html" id="assist-db-inner-panel">
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
          <div data-bind="visible: ! loading() && ! hasErrors()">
            <ul class="assist-tables" data-bind="foreachVisible: {data: entries, minHeight: 20, container: '.assist-hdfs-scrollable' }">
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
                  <span draggable="true" data-bind="text: definition.name, draggableText: { text: '\'' + path + '\'' }"></span>
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
    </div>
  </script>

  <script type="text/html" id="file-details-content">
    <!-- ko with: definition -->
    <div class="assist-details-wrap">
      <div><div class="assist-details-header">${ _('Description') }</div><div class="assist-details-value" data-bind="text: description"></div></div>
      <div><div class="assist-details-header">${ _('Modified') }</div><div class="assist-details-value" data-bind="text: last_modified"></div></div>
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
               <span data-bind="text: definition().name"></span>
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
        <li class="assist-table pointer">
          <a class="assist-table-link" href="javascript: void(0);" data-bind="text: name, click: function () { $parent.selectedSource($data); }"></a>
        </li>
      </ul>
    </div>
  </script>

  <script type="text/html" id="ask-for-invalidate-title">
    <a class="pull-right pointer close-popover inactive-action"><i class="fa fa-times"></i></a>
  </script>

  <script type="text/html" id="ask-for-invalidate-content">
    <label class="checkbox" style="margin-bottom: 2px;"><input type="checkbox" data-bind="checked: invalidateOnRefresh" /> ${ _('Invalidate metadata') }</label>
    <div style="display: inline-block; margin-left: 20px; font-style: italic">${ _('This could take a noticeable amount of time') }</div>
    <label class="checkbox" style="margin-top: 4px;"><input type="checkbox" data-bind="checked: dontAskForInvalidateTemp" /> ${ _('Remember my decision') }</label>
    <div style="width: 100%; display: inline-block; margin-top: 5px;"><button class="pull-right btn btn-primary" data-bind="click: function () { huePubSub.publish('close.popover'); triggerRefresh(); }, clickBubble: false">${ _('Refresh') }</button></div>
  </script>

  <script type="text/html" id="assist-db-header-actions">
    <div class="assist-db-header-actions" data-bind="visible: hasEntries() && (!$parent.loading() && !$parent.hasErrors()">
      <span class="assist-tables-counter">(<span data-bind="text: filteredEntries().length"></span>)</span>
      <!-- ko ifnot: loading -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: toggleSearch, css: { 'blue' : isSearchVisible }"><i class="pointer fa fa-search" title="${_('Search')}"></i></a>
      <!-- ko if: sourceType === 'impala' -->
      <!-- ko if: dontAskForInvalidate -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: triggerRefresh"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manually refresh the table list')}"></i></a>
      <!-- /ko -->
      <!-- ko ifnot: dontAskForInvalidate -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="templatePopover : { contentTemplate: 'ask-for-invalidate-content', titleTemplate: 'ask-for-invalidate-title', trigger: 'click', minWidth: '320px' }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manually refresh the table list')}"></i></a>
      <!-- /ko -->
      <!-- /ko -->
      <!-- ko if: sourceType !== 'impala' -->
      <a class="inactive-action" href="javascript:void(0)" data-bind="click: triggerRefresh"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : loading }" title="${_('Manually refresh the table list')}"></i></a>
      <!-- /ko -->
      <!-- /ko -->
      <!-- ko if: loading -->
      <span style="color: #aaa;"><i class="fa fa-search" title="${_('Search')}"></i></span>
      <i class="fa fa-refresh fa-spin blue" title="${_('Manually refresh the table list')}"></i></a>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="assist-databases-template">
    <div class="assist-flex-header" data-bind="visibleOnHover: { selector: '.hover-actions', override: loading() || isSearchVisible() }">
      <div class="assist-inner-header" data-bind="visible: ! hasErrors()">
        ${_('Databases')}
        <!-- ko template: 'assist-db-header-actions' --><!-- /ko -->
      </div>
    </div>
    <div class="assist-flex-search" data-bind="visible: hasEntries() && isSearchVisible() && ! hasErrors()">
      <div><input id="searchInput" class="clearable" type="text" placeholder="${ _('Database name...') }" style="margin-top:3px;width:90%;" data-bind="hasFocus: editingSearch, clearable: filter.query, value: filter.query, valueUpdate: 'afterkeydown'"/></div>
    </div>
    <div class="assist-flex-fill assist-db-scrollable" data-bind="visible: ! hasErrors() && ! loading()" style="display: none;">
      <!-- ko if: hasEntries() && ! loading() && filteredEntries().length == 0 -->
      <ul class="assist-tables">
        <li class="assist-entry no-entries">${_('No results found')}</li>
      </ul>
      <!-- /ko -->
      <ul class="assist-tables" data-bind="foreachVisible: {data: filteredEntries, minHeight: 20, container: '.assist-db-scrollable' }">
        <li class="assist-table pointer" data-bind="visibleOnHover: { selector: '.database-actions' }">
          <!-- ko template: { name: 'assist-entry-actions' } --><!-- /ko -->
          <a class="assist-table-link" href="javascript: void(0);" data-bind="text: definition.name, click: function () { $parent.selectedDatabase($data) }"></a>
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
      <div><label class="checkbox inline-block margin-left-5"><input type="checkbox" data-bind="checked: filter.showTables" />Tables</label><label class="checkbox inline-block margin-left-10"><input type="checkbox" data-bind="checked: filter.showViews" />Views</label></div>
      <div><input id="searchInput" class="clearable" type="text" placeholder="${ _('Table name...') }" style="width:90%;" data-bind="hasFocus: editingSearch, clearable: filter.query, value: filter.query, valueUpdate: 'afterkeydown'"/></div>
    </div>
    <div class="assist-flex-fill assist-db-scrollable" data-bind="visible: ! hasErrors() && ! loading() && ! $parent.loading()" style="display: none;">
      <!-- ko template: 'assist-db-entries' --><!-- /ko -->
    </div>
    <div class="assist-flex-fill" data-bind="visible: loading() || $parent.loading()" style="display: none;">
      <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
    </div>
    <div class="assist-flex-fill" data-bind="visible: hasErrors() && ! loading() && ! $parent.loading()" style="display: none;">
      <span class="assist-errors">${ _('Error loading tables.') }</span>
    </div>

    <div id="assistQuickLook" class="modal hide fade">
      <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <a class="tableLink pull-right" href="#" target="_blank" style="margin-right: 20px;margin-top:6px">
          <i class="fa fa-external-link"></i> ${ _('View in Metastore Browser') }
        </a>
        <h3>${_('Data sample for')} <span class="tableName"></span></h3>
      </div>
      <div class="modal-body" style="min-height: 100px">
        <!-- ko hueSpinner: { spin: assistDbSource.loadingSamples, center: true, size: 'large' } --><!-- /ko -->
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
          'desktop/js/assist/assistHelper',
          'desktop/js/fileBrowser/hueFileEntry',
          'tableStats'
        ], factory);
      } else {
        factory(ko, AssistDbSource, AssistHdfsEntry, AssistHelper, HueFileEntry);
      }
    }(function (ko, AssistDbSource, AssistHdfsEntry, AssistHelper, HueFileEntry) {

      ko.bindingHandlers.assistFileDroppable = {
        init: function(element, valueAccessor, allBindings, boundEntry) {
          var dragData;
          huePubSub.subscribe('file.browser.dragging', function (data) {
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
            self.assistHelper.setInTotalStorage('assist', 'lastSelectedSource', newSource.sourceType);
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

        self.activeEntry = ko.observable();
        self.activeEntry(new HueFileEntry({
          activeEntry: self.activeEntry,
          trashEntry: ko.observable,
          assistHelper: options.assistHelper,
          app: 'documents',
          definition: {
            name: '/',
            type: 'directory'
          }
        }));
      }

      /**
       * @param {Object} options
       * @param {AssistHelper} options.assistHelper
       * @constructor
       **/
      function AssistHdfsPanel (options) {
        var self = this;
        self.assistHelper = options.assistHelper;

        self.selectedHdfsEntry = ko.observable();
        var reload = function () {
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
            self.selectedHdfsEntry(entry);
            entry.open(true);
          });
        };

        reload();

        huePubSub.subscribe('assist.selectHdfsEntry', function (entry) {
          self.selectedHdfsEntry(entry);
          self.assistHelper.setInTotalStorage('assist', 'currentHdfsPath', entry.path);
        });

        huePubSub.subscribe('assist.hdfs.refresh', function () {
          huePubSub.publish('assist.clear.hdfs.cache');
          reload();
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
            minHeight: 75,
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
            minHeight: 50,
            visible: params.visibleAssistPanels && params.visibleAssistPanels.indexOf('hdfs') !== -1
          }));
          <%
            from beeswax.conf import USE_NEW_EDITOR
          %>
          % if USE_NEW_EDITOR.get():
          self.availablePanels.push(new AssistInnerPanel({
            panelData: new AssistDocumentsPanel({
              assistHelper: self.assistHelper,
              i18n: i18n
            }),
            assistHelper: self.assistHelper,
            name: '${ _("Documents") }',
            type: 'documents',
            icon: 'fa-files-o',
            minHeight: 50,
            visible: params.visibleAssistPanels && params.visibleAssistPanels.indexOf('documents') !== -1
          }));
          % endif
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