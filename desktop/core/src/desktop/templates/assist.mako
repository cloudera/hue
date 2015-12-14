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

<%def name="assistPanel()">
  <style>

    .assist {
      position: relative;
      height: 100%;
    }

    .assist-main {
      overflow-y: auto;
    }

    .assist-resizer {
      border-top: 1px solid #F1F1F1;
      margin-left: 5px;
      margin-right: 5px;
      cursor: row-resize;
      text-align: center;
      font-size: 12px;
      height: 8px;
      margin-bottom: 5px;
      color: #E1E1E1;
    }
    .assist-entry,a {
      white-space: nowrap;
    }

    .assist-tables {
      overflow-y: hidden;
      overflow-x: auto;
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

    .assist-actions  {
      position:absolute;
      right: 0;
      padding-right:4px;
      padding-left:4px;
      background-color: #FFF;
    }

    .assist-tables > li.selected .assist-actions {
      background-color: #EEE;
    }

    .assist .nav-header {
      padding-top: 0 !important;
      margin-top: 0 !important;
      margin-right: 0 !important;
      padding-right: 4px !important;
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
      <a class="inactive-action" href="javascript:void(0)" data-bind="visible: navigationSettings.openItem, click: openItem"><i class="fa fa-long-arrow-right" title="${_('Open')}"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-entries">
    <!-- ko if: hasEntries() && ! loading() && filteredEntries().length == 0 -->
    <ul class="assist-tables">
      <li class="assist-entry" style="font-style: italic;">${_('No results found')}</li>
    </ul>
    <!-- /ko -->
    <ul data-bind="foreach: filteredEntries, css: { 'assist-tables': definition.isDatabase }, event: { 'scroll': assistDbSource.repositionActions }">
      <li data-bind="visibleOnHover: { override: statsVisible, selector: (definition.isTable || definition.isView) ? '.table-actions' : '.column-actions' }, css: { 'assist-table': (definition.isTable || definition.isView), 'assist-column': definition.isColumn }">
        <!-- ko template: { if: definition.isTable || definition.isView || definition.isColumn, name: 'assist-entry-actions' } --><!-- /ko -->
        <a class="assist-entry" data-bind="multiClick: { click: toggleOpen, dblClick: dblClick }, attr: {'title': definition.title }, css: { 'assist-field-link': ! (definition.isTable || definition.isView), 'assist-table-link': (definition.isTable || definition.isView) }" href="javascript:void(0)">
          <!-- ko if: definition.isTable -->
            <i class="fa fa-fw fa-table muted"></i>
          <!-- /ko -->
          <!-- ko if: definition.isView -->
            <i class="fa fa-fw fa-eye muted"></i>
          <!-- /ko -->
          <span draggable="true" data-bind="text: definition.displayName, draggableText: { text: editorText }"></span>
        </a>
        <div class="center"  data-bind="visible: loading" style="display:none;">
          <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i><!--<![endif]-->
          <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
        </div>
        <!-- ko template: { if: open(), name: 'assist-entries'  } --><!-- /ko -->
      </li>
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

  <script type="text/html" id="assist-db-panel">
    <!-- ko template: { if: breadcrumb() !== null, name: 'assist-db-breadcrumb' } --><!-- /ko -->
    <ul class="nav nav-list" style="position:relative; border: none; padding: 0; background-color: #FFF; margin-bottom: 1px; margin-top:3px;width:100%;">
      <!-- ko template: { ifnot: selectedSource, name: 'assist-sources-template' } --><!-- /ko -->
      <!-- ko with: selectedSource -->
      <!-- ko template: { ifnot: selectedDatabase, name: 'assist-databases-template' }--><!-- /ko -->
      <!-- ko with: selectedDatabase -->
      <!-- ko template: { name: "assist-tables-template" } --><!-- /ko -->
      <!-- /ko -->
      <!-- /ko -->
    </ul>
  </script>

  <script type="text/html" id="assist-hdfs-panel">
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
    <ul class="nav nav-list" style="position:relative; border: none; padding: 0; background-color: #FFF; margin-bottom: 1px; margin-top:3px;width:100%;">

      <li class="nav-header" style="margin-top: 0">
        ${_('HDFS')}
      </li>
      <li class="center" data-bind="visible: loading">
        <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i><!--<![endif]-->
        <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
      </li>

      <li>
        <ul class="assist-tables" data-bind="foreach: entries">
          <li class="assist-entry assist-table-link">
            <a href="javascript:void(0)" class="assist-entry assist-table-link" data-bind="multiClick: { click: toggleOpen, dblClick: function () {} }, attr: {'title': definition.name }">
              <!-- ko if: definition.type === 'dir' -->
              <i class="fa fa-fw fa-folder muted"></i>
              <!-- /ko -->
              <!-- ko if: definition.type === 'file' -->
              <i class="fa fa-fw fa-file-o muted"></i>
              <!-- /ko -->
              <span data-bind="text: definition.name"></span>
            </a>
          </li>
        </ul>
      </li>
    </ul>
    <!-- /ko -->
  </script>

  <script type="text/html" id="assist-two-panel-layout">
    <div style="position:relative; height: 100%;">
      <div style="overflow: auto;">
        <!-- ko template: 'assist-db-panel' --><!-- /ko -->
      </div>
      <div class="assist-resizer" data-bind="assistVerticalResizer">
        <i class="fa fa-ellipsis-h"></i>
      </div>
      <div style="overflow: auto;">
        <!-- ko template: 'assist-hdfs-panel' --><!-- /ko -->
      </div>
    </div>
  </script>


  <script type="text/html" id="assist-panel-template">
    <div style="position:relative; height: 100%;">
      <!-- ko template: { if: showingDb() && showingHdfs(), name: 'assist-two-panel-layout' } --><!-- /ko -->
      <!-- ko template: { if: showingDb() && ! showingHdfs(), name: 'assist-db-panel' } --><!-- /ko -->
      <!-- ko template: { if: ! showingDb() && showingHdfs(), name: 'assist-hdfs-panel' } --><!-- /ko -->
    </div>
    <div style="position: absolute; bottom: 2px; left: 2px">
      <a href="javascript: void(0);" data-bind="click: function () { showingDb(!showingDb()) }, text: showingDb() ? 'Hide DB' : 'Show DB'"></a>
      <a href="javascript: void(0);" data-bind="click: function () { showingHdfs(!showingHdfs()) }, text: showingHdfs() ? 'Hide HDFS' : 'Show HDFS'"></a>
    </div>
  </script>

  <script type="text/html" id="assist-sources-template">
    <li class="nav-header" data-bind="visibleOnHover: { selector: '.hover-actions' }">
      ${_('sources')}
    </li>
    <li>
      <ul class="assist-tables" data-bind="foreach: sources">
        <li class="assist-table pointer">
          <a class="assist-table-link" href="javascript: void(0);" data-bind="text: name, click: function () { $parent.selectedSource($data); }"></a>
        </li>
      </ul>
    </li>
  </script>

  <script type="text/html" id="assist-databases-template">
    <li class="nav-header" data-bind="visibleOnHover: { selector: '.hover-actions' }">
      ${_('databases')}
      <div class="pull-right" data-bind="css: { 'hover-actions' : ! reloading() }">
        <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin' : reloading }" title="${_('Manually refresh the databases list')}"></i></a>
      </div>
    </li>
    <li data-bind="visible: ! hasErrors()" >
      <ul class="assist-tables" data-bind="foreach: databases">
        <li class="assist-table pointer" data-bind="visibleOnHover: { selector: '.database-actions' }">
          <!-- ko template: { name: 'assist-entry-actions' } --><!-- /ko -->
          <a class="assist-table-link" href="javascript: void(0);" data-bind="text: definition.name, click: function () { $parent.selectedDatabase($data) }"></a>
        </li>
      </ul>
    </li>
    <li class="center" data-bind="visible: loading" >
      <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i><!--<![endif]-->
      <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
    </li>
    <li data-bind="visible: hasErrors">
      <span>${ _('The database list cannot be loaded.') }</span>
    </li>
  </script>

  <script type="text/html" id="assist-tables-template">
    <div data-bind="visibleOnHover: { selector: '.hover-actions', override: $parent.reloading }" style="position: relative; width:100%">
      <li class="nav-header" style="margin-top: 0" data-bind="visible: !$parent.loading() && !$parent.hasErrors()">
        ${_('tables')}
        <div class="pull-right hover-actions" data-bind="visible: hasEntries() && !$parent.loading() && !$parent.hasErrors()">
          <span class="assist-tables-counter">(<span data-bind="text: filteredEntries().length"></span>)</span>
          <a class="inactive-action" href="javascript:void(0)" data-bind="click: toggleSearch, css: { 'blue' : isSearchVisible }"><i class="pointer fa fa-search" title="${_('Search')}"></i></a>
          <a class="inactive-action" href="javascript:void(0)" data-bind="click: function () { huePubSub.publish('assist.refresh'); }"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin blue' : $parent.reloading }" title="${_('Manually refresh the table list')}"></i></a>
        </div>
      </li>

      <li data-bind="slideVisible: hasEntries() && isSearchVisible() && !$parent.loading() && !$parent.hasErrors()">
        <div><label class="checkbox inline-block margin-left-5"><input type="checkbox" data-bind="checked: filter.showTables" />Tables</label><label class="checkbox inline-block margin-left-10"><input type="checkbox" data-bind="checked: filter.showViews" />Views</label></div>
        <div><input id="searchInput" type="text" placeholder="${ _('Table name...') }" style="width:90%;" data-bind="hasFocus: editingSearch, clearable: filter.query, value: filter.query, valueUpdate: 'afterkeydown'"/></div>
      </li>

      <div class="table-container">
        <div class="center" data-bind="visible: loading() || $parent.loading()">
          <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i><!--<![endif]-->
          <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
        </div>
        <!-- ko template: { ifnot: loading() || $parent.loading(), name: 'assist-entries' } --><!-- /ko -->
      </div>
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

  <script type="text/javascript" charset="utf-8">
    (function (factory) {
      if(typeof require === "function") {
        define('assistPanel', ['knockout', 'desktop/js/assist/assistDbSource', 'desktop/js/assist/assistHdfsEntry', 'desktop/js/assist/assistHelper', 'tableStats'], factory);
      } else {
        factory(ko, AssistDbSource, AssistHdfsEntry, AssistHelper);
      }
    }(function (ko, AssistDbSource, AssistHdfsEntry, AssistHelper) {

      /**
       * @param {Object} params
       * @param {Object[]} params.sourceTypes - All the available SQL source types
       * @param {string} params.sourceTypes[].name - Example: Hive SQL
       * @param {string} params.sourceTypes[].type - Example: hive
       * @param {string} [params.activeSourceType] - Example: hive
       * @param {string} params.user
       * @param {Object} params.navigationSettings - enable/disable the links
       * @param {boolean} params.navigationSettings.openItem - Example: true
       * @param {boolean} params.navigationSettings.showPreview - Example: true
       * @param {boolean} params.navigationSettings.showStats - Example: true
       * @constructor
       */
      function AssistPanel (params) {
        var self = this;
        var i18n = {
          errorLoadingDatabases: "${ _('There was a problem loading the databases') }",
          errorLoadingTablePreview: "${ _('There was a problem loading the table preview.') }"
        };

        self.showingDb = ko.observable(true);
        self.showingHdfs = ko.observable(true);

        var assistHelper = new AssistHelper(i18n, params.user);
        self.sources = ko.observableArray();
        var sourceIndex = {};
        $.each(params.sourceTypes, function (idx, sourceType) {
          sourceIndex[sourceType.type] = new AssistDbSource({
            assistHelper: assistHelper,
            i18n: i18n,
            type: sourceType.type,
            name: sourceType.name,
            navigationSettings: params.navigationSettings
          });
          self.sources.push(sourceIndex[sourceType.type]);
        });

        self.selectedHdfsEntry = ko.observable(new AssistHdfsEntry({
          definition: {
            name: '/',
            type: 'dir'
          },
          parent: null,
          assistHelper: assistHelper
        }));
        self.selectedHdfsEntry().open(true);

        huePubSub.subscribe('assist.selectHdfsEntry', function (entry) {
          self.selectedHdfsEntry(entry);
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

        huePubSub.publish("assist.ready");

        self.selectedSource.subscribe(function (newSource) {
          if (newSource) {
            newSource.initDatabases();
            $.totalStorage("hue.assist.lastSelectedSource." + self.user, newSource.type);
          } else {
            $.totalStorage("hue.assist.lastSelectedSource." + self.user, null);
          }
        });

        var storageSourceType =  $.totalStorage("hue.assist.lastSelectedSource." + self.user);

        if (! self.selectedSource()) {
          if (params.activeSourceType) {
            self.selectedSource(sourceIndex[params.activeSourceType]);
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

      AssistPanel.prototype.back = function () {
        var self = this;
        if (self.selectedSource() && self.selectedSource().selectedDatabase()) {
          self.selectedSource().selectedDatabase(null)
        } else if (self.selectedSource()) {
          self.selectedSource(null);
        }
      };

      ko.components.register('assist-panel', {
        viewModel: AssistPanel,
        template: { element: 'assist-panel-template' }
      });
    }));
  </script>
</%def>