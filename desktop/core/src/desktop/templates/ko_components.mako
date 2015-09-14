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
    .assist-tables {
      overflow-y: hidden;
      overflow-x: auto;
      margin-left: 7px;
    }

    .assist-tables a {
      text-decoration: none;
    }

    .assist-tables li {
      list-style: none;
    }

    .assist-tables > li {
      position: relative;
      padding-top: 2px;
      padding-bottom: 2px;
    }

    .assist-tables > li:hover .hover-actions-2nd {
      visibility: visible;
      opacity: 1;
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

    .assist-columns {
      margin-left: 0px;
    }

    .assist-columns > li {
      padding: 6px 5px;
      white-space: nowrap;
    }

    .assist-actions  {
      position:absolute;
      right: 0px;
      padding-right:4px;
      padding-left:4px;
      background-color: #FFF;
    }

    .assist .nav-header {
      margin-right: 0 !important;
      padding-right: 4px !important;
    }
  </style>

  <script type="text/html" id="assist-panel-table-stats">
    <div class="content">
      <!-- ko if: statRows().length -->
      <table class="table table-striped">
        <tbody data-bind="foreach: statRows">
          <tr><th data-bind="text: data_type"></th><td data-bind="text: comment"></td></tr>
        </tbody>
      </table>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/html" id="assist-panel-column-no-stats">
    <div class="arrow"></div>
    <h3 class="popover-title" style="text-align: left">
      <a class="pull-right pointer close-popover" style="margin-left: 8px" data-bind="click: function() { $parent.analysisStats(null) }"><i class="fa fa-times"></i></a>
      <strong class="table-name" data-bind="text: column"></strong> ${ _(' column analysis') }
    </h3>
    <div class="popover-content">
      <div style="text-align: left">${ _('Column analysis is currently not supported for columns of type:') } <span data-bind="text: type"></span></div>
    </div>
  </script>

  <script type="text/html" id="assist-panel-column-stats">
    <div class="pull-right filter" data-bind="visible: termsTabActive" style="display:none;">
      <input type="text" data-bind="textInput: prefixFilter" placeholder="${ _('Prefix filter...') }"/>
    </div>
    <ul class="nav nav-tabs" role="tablist">
      <li data-bind="click: function() { termsTabActive(false) }"class="active"><a href="#columnAnalysisStats" role="tab" data-toggle="tab">${ _('Stats') }</a></li>
      <li data-bind="click: function() { termsTabActive(true) }"><a href="#columnAnalysisTerms" role="tab" data-toggle="tab">${ _('Terms') }</a></li>
    </ul>
    <div class="tab-content">
      <div class="tab-pane active" id="columnAnalysisStats" style="text-align: left">
        <div class="content">
          <table class="table table-striped">
            <tbody data-bind="foreach: statRows">
              <tr><th data-bind="text: Object.keys($data)[0]"></th><td data-bind="text: $data[Object.keys($data)[0]]"></td></tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="tab-pane" id="columnAnalysisTerms" style="text-align: left">
        <i style="margin: 5px;" data-bind="visible: loadingTerms" class='fa fa-spinner fa-spin'></i>
        <div class="alert" data-bind="visible: ! loadingTerms() && terms().length == 0">${ _('There are no terms to be shown') }</div>
        <div class="content">
          <table class="table table-striped" data-bind="visible: ! loadingTerms()">
            <tbody data-bind="foreach: terms">
              <tr><td data-bind="text: name"></td><td style="width: 40px"><div class="progress"><div class="bar-label" data-bind="text: count"></div><div class="bar bar-info" style="margin-top: -20px;" data-bind="style: { 'width' : percent + '%' }"></div></div></td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="assist-no-entries">
    <ul class="assist-tables">
      <li data-bind="visible: definition.isDatabase">
        <span>${_('The selected database has no tables.')}</span>
      </li>
      <li data-bind="visible: definition.isTable">
        <span>${_('The selected table has no columns.')}</span>
      </li>
    </ul>
  </script>

  <script type="text/html" id="assist-entry-actions">
    <div class="assist-actions" data-bind="css: { 'hover-actions-2nd': definition.isTable,  'hover-actions-3rd': definition.isColumn, 'show-actions': statsVisible }">
      <a href="javascript:void(0)" data-bind="visible: definition.isTable, click: showPreview"><i class="fa fa-list" title="${_('Preview Sample data')}"></i></a>
      <a href="javascript:void(0)" data-bind="visible: definition.isTable || definition.isColumn, click: showStats, css: { 'blue': statsVisible }"><i class='fa fa-bar-chart' title="${_('View statistics') }"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-entries">
    <div class="center" data-bind="visible: loading">
      <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i><!--<![endif]-->
      <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
    </div>

    <ul data-bind="foreach: filteredEntries, css: { 'assist-tables': definition.isDatabase }, event: { 'scroll': assistPanel.repositionActions }">
      <li data-bind="css: { 'assist-table reveals-actions-2nd': definition.isTable, 'assist-column reveals-actions-3rd': definition.isColumn }">
        <!-- ko template: { if: definition.isTable || definition.isColumn, name: 'assist-entry-actions' } --><!-- /ko -->
        <a class="assist-column-link" data-bind="click: toggleOpen, attr: {'title': definition.title }, css: { 'assist-field-link': ! definition.isTable, 'assist-table-link': definition.isTable }" href="javascript:void(0)">
          <span data-bind="text: definition.displayName, event: { 'dblclick': dblClick }"></span>
        </a>
        <!-- ko template: { if: open(), name: 'assist-entries'  } --><!-- /ko -->
      </li>
    </ul>
    <!-- ko template: { if: ! hasEntries() && ! loading(), name: 'assist-no-entries' } --><!-- /ko -->
  </script>

  <script type="text/html" id="assist-panel-template">
    <div class="reveals-actions" style="position: relative; width:100%">
      <ul class="nav nav-list" style="position:relative; border: none; padding: 0; background-color: #FFF; margin-bottom: 1px; width:100%;">
        <li class="nav-header">
          ${_('database')}
          <div class="pull-right" data-bind="css: { 'hover-actions' : ! reloading() }">
            <a href="javascript:void(0)" data-bind="click: reloadAssist"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin' : reloading }" title="${_('Manually refresh the table list')}"></i></a>
          </div>
        </li>

        <li data-bind="visible: ! hasErrors() && ! loadingDatabases()" >
          <select data-bind="options: availableDatabaseNames, select2: { width: '100%', placeholder: '${ _ko("Choose a database...") }', update: assistHelper.activeDatabase }" class="input-medium" data-placeholder="${_('Choose a database...')}"></select>
        </li>

        <li class="center" data-bind="visible: loadingDatabases" >
          <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i><!--<![endif]-->
          <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
        </li>

        <li data-bind="visible: hasErrors">
          <span>${ _('The database list cannot be loaded.') }</span>
        </li>

        <li class="nav-header" style="margin-top:10px;" data-bind="visible: ! loadingDatabases()">
          ${_('tables')}
          <div class="pull-right" data-bind="visible: selectedDatabase() != null && selectedDatabase().hasEntries(), css: { 'hover-actions': ! filter(), 'blue': filter }">
            <a href="javascript:void(0)" data-bind="click: toggleSearch"><i class="pointer fa fa-search" title="${_('Search')}"></i></a>
          </div>
        </li>

        <!-- ko if: selectedDatabase() != null -->
          <li data-bind="slideVisible: selectedDatabase() != null && selectedDatabase().hasEntries() && options.isSearchVisible()">
            <div><input type="text" placeholder="${ _('Table name...') }" style="width:90%;" data-bind="value: filter, valueUpdate: 'afterkeydown'"/></div>
          </li>

        <div class="table-container">
          <!-- ko template: { if: selectedDatabase() != null, name: 'assist-entries', data: selectedDatabase } --><!-- /ko -->
          </div>
        <!-- /ko -->
      </ul>
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
        <div class="loader">
          <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 30px; color: #DDD"></i><!--<![endif]-->
          <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
        </div>
        <div class="sample"></div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-primary disable-feedback" data-dismiss="modal">${_('Ok')}</button>
      </div>
    </div>

    <div id="tableAnalysis" style="position: fixed; display: none;" class="popover show right" data-bind="css: { 'mega-popover': analysisStats() != null && !analysisStats().isComplexType }, visible: analysisStats() != null, with: analysisStats">
      <!-- ko template: {if: isComplexType, name: 'assist-panel-column-no-stats' } --><!-- /ko -->
      <!-- ko ifnot: isComplexType -->
      <div class="arrow"></div>
      <h3 class="popover-title" style="text-align: left">
        <a class="pull-right pointer close-popover" style="margin-left: 8px" data-bind="click: function() { $parent.analysisStats(null) }"><i class="fa fa-times"></i></a>
        <a class="pull-right pointer stats-refresh" style="margin-left: 8px" data-bind="click: refresh"><i class="fa fa-refresh" data-bind="css: { 'fa-spin' : refreshing }"></i></a>
        <span class="pull-right stats-warning muted" data-bind="visible: inaccurate" rel="tooltip" data-placement="top" title="${ _('The column stats for this table are not accurate') }" style="margin-left: 8px"><i class="fa fa-exclamation-triangle"></i></span>
        <i data-bind="visible: loading" class='fa fa-spinner fa-spin'></i>
        <!-- ko if: column == null -->
        <strong class="table-name" data-bind="text: table"></strong> ${ _(' table analysis') }
        <!-- /ko -->
        <!-- ko ifnot: column == null -->
        <strong class="table-name" data-bind="text: column"></strong> ${ _(' column analysis') }
        <!-- /ko -->
      </h3>
      <div class="popover-content">
        <!-- ko template: {if: column == null, name: 'assist-panel-table-stats' } --><!-- /ko -->
        <!-- ko template: {ifnot: column == null, name: 'assist-panel-column-stats' } --><!-- /ko -->
      </div>
      <!-- /ko -->
    </div>
  </script>

  <script type="text/javascript" charset="utf-8">
    (function() {
      function AssistEntry (definition, parent, assistPanel, filter) {
        var self = this;
        self.definition = definition;

        self.assistPanel = assistPanel;
        self.parent = parent;
        self.filter = filter;

        self.loaded = false;
        self.loading = ko.observable(false);
        self.open = ko.observable(false);
        self.entries = ko.observableArray([]);
        self.statsVisible = ko.observable(false);

        self.open.subscribe(function(newValue) {
          if (newValue && self.entries().length == 0) {
            self.loadEntries();
          }
        });

        self.hasEntries = ko.computed(function() {
          return self.entries().length > 0;
        });

        self.filteredEntries = ko.computed(function () {
          if (self.filter == null || self.filter().length === 0) {
            return self.entries();
          }
          var result = [];
          $.each(self.entries(), function (index, entry) {
            if (entry.definition.name.toLowerCase().indexOf(self.filter()) > -1) {
              result.push(entry);
            }
          });
          return result;
        });
      }

      AssistEntry.prototype.loadEntries = function() {
        var self = this;
        if (self.loading()) {
          return;
        }
        self.loading(true);
        self.entries([]);

        // Defer this part to allow ko to react on empty entries and loading
        window.setTimeout(function() {
          self.assistPanel.assistHelper.fetchPanelData(self.getHierarchy(), function(data) {
            if (typeof data.tables !== "undefined") {
              self.entries($.map(data.tables, function(tableName) {
                return self.createEntry({
                  name: tableName,
                  displayName: tableName,
                  title: tableName,
                  isTable: true
                });
              }));
            } else if (typeof data.extended_columns !== "undefined" && data.extended_columns !== null) {
              self.entries($.map(data.extended_columns, function (columnDef) {
                var displayName = columnDef.name;
                if (typeof columnDef.type !== "undefined" && columnDef.type !== null) {
                  displayName += ' (' + columnDef.type + ')'
                }
                var title = displayName;
                if (typeof columnDef.comment !== "undefined" && columnDef.comment !== null) {
                  title += ' ' + columnDef.comment;
                }
                var shortType = null;
                if (typeof columnDef.type !== "undefined" && columnDef.type !== null) {
                  shortType = columnDef.type.match(/^[^<]*/g)[0]; // everything before '<'
                }
                return self.createEntry({
                  name: columnDef.name,
                  displayName: displayName,
                  title: title,
                  isColumn: true,
                  type: shortType
                });
              }));
            } else if (typeof data.columns !== "undefined" && data.columns !== null) {
              self.entries($.map(data.columns, function(columnName) {
                return self.createEntry({
                  name: columnName,
                  displayName: columnName,
                  title: columnName,
                  isColumn: true
                });
              }));
            } else if (typeof data.type !== "undefined" && data.type !== null) {
              if (data.type === "map") {
                self.entries([
                  self.createEntry({
                    name: "key",
                    displayName: "key (" + data.key.type + ")",
                    title: "key (" + data.key.type + ")"
                  }),
                  self.createEntry({
                    name: "value",
                    displayName: "value (" + data.value.type + ")",
                    title: "value (" + data.value.type + ")",
                    isMapValue: true
                  })
                ]);
              } else if (data.type == "struct") {
                self.entries($.map(data.fields, function(field) {
                  return self.createEntry({
                    name: field.name,
                    displayName: field.name + " (" + field.type + ")",
                    title: field.name + " (" + field.type + ")"
                  });
                }));
              } else if (data.type == "array") {
                self.entries([
                  self.createEntry({
                    name: "item",
                    displayName: "item (" + data.item.type + ")",
                    title: "item (" + data.item.type + ")",
                    isArray: true
                  })
                ]);
              }
            }
            self.loading(false);
          }, function() {
            self.assistPanel.hasErrors(true);
            self.loading(false);
          });
        }, 10);
      };

      AssistEntry.prototype.createEntry = function(definition) {
        var self = this;
        return new AssistEntry(definition, self, self.assistPanel, null)
      };

      AssistEntry.prototype.getHierarchy = function () {
        var self = this;
        var parts = [];
        var entry = self;
        while (entry != null) {
          parts.push(entry.definition.name);
          entry = entry.parent;
        }
        parts.reverse();
        return parts;
      };

      AssistEntry.prototype.dblClick = function (data, event) {
        var self = this;
        if (self.definition.isTable) {
          huePubSub.publish('assist.dblClickItem', self.definition.name);
        } else if (self.definition.isColumn) {
          huePubSub.publish('assist.dblClickItem', self.definition.name + ", ");
        } else {
          var parts = [];
          var entry = self;
          while (entry != null) {
            if (entry.definition.isTable) {
              break;
            }
            if (entry.definition.isArray || entry.definition.isMapValue) {
              parts.push("[]");
            } else {
              parts.push(entry.definition.name);
              parts.push(".");
            }
            entry = entry.parent;
          }
          parts.reverse();
          parts.push(", ");
          huePubSub.publish('assist.dblClickItem', parts.slice(1).join(""));
        }
      };

      AssistEntry.prototype.toggleOpen = function () {
        var self = this;
        self.open(!self.open());
      };

      AssistEntry.prototype.showPreview = function () {
        var self = this;
        var $assistQuickLook = $("#assistQuickLook");

        var hierarchy = self.getHierarchy();
        var databaseName = hierarchy[0];
        var tableName = hierarchy[1];

        $assistQuickLook.find(".tableName").text(self.definition.name);
        $assistQuickLook.find(".tableLink").attr("href", "/metastore/table/" + self.assistPanel.assistHelper.activeDatabase() + "/" + tableName);
        $assistQuickLook.find(".sample").empty("");
        $assistQuickLook.attr("style", "width: " + ($(window).width() - 120) + "px;margin-left:-" + (($(window).width() - 80) / 2) + "px!important;");

        self.assistPanel.assistHelper.fetchTableHtmlPreview(tableName, function(data) {
          $assistQuickLook.find(".loader").hide();
          $assistQuickLook.find(".sample").html(data);
        }, function(e) {
          if (e.status == 500) {
            $(document).trigger("error", "${ _('There was a problem loading the table preview.') }");
            $("#assistQuickLook").modal("hide");
          }
        });

        $assistQuickLook.modal("show");
      };

      AssistEntry.prototype.showStats = function (data, event) {
        var self = this;

        if (self.statsVisible()) {
          self.statsVisible(false);
          self.assistPanel.analysisStats(null);
          return;
        }

        var hierarchy = self.getHierarchy();
        var databaseName = hierarchy[0];
        var tableName = hierarchy[1];
        var columnName = hierarchy.length == 3 ? hierarchy[2] : null;

        self.statsVisible(true);
        self.assistPanel.analysisStats(new TableStats(databaseName, tableName, columnName, self.assistPanel.assistHelper, self.definition.type));

        var catchChange = self.assistPanel.analysisStats.subscribe(function(newValue) {
          if (newValue === null || newValue.database !== databaseName || newValue.table !== tableName || newValue.column !== columnName) {
            self.statsVisible(false);
            catchChange.dispose();
          }
        });
        $("#tableAnalysis").data("targetElement", $(event.target));
        window.setTimeout(self.assistPanel.refreshPosition, 20);
      };

      function TableStats (database, table, column, assistHelper, type) {
        var self = this;

        self.database = database;
        self.table = table;
        self.column = column;
        self.assistHelper = assistHelper;

        self.loading = ko.observable(false);
        self.refreshing = ko.observable(false);
        self.loadingTerms = ko.observable(false);
        self.inaccurate = ko.observable(false);
        self.statRows = ko.observableArray();
        self.terms = ko.observableArray();
        self.termsTabActive = ko.observable(false);
        self.prefixFilter = ko.observable().extend({'throttle': 500});
        self.type = type
        self.isComplexType = /^(map|array|struct)/i.test(type);

        self.prefixFilter.subscribe(function (newValue) {
          self.fetchTerms();
        });

        self.termsTabActive.subscribe(function (newValue) {
          if (self.terms().length == 0 && newValue) {
            self.fetchTerms();
          }
        });

        self.fetchData();
      }

      TableStats.prototype.fetchData = function () {
        var self = this;
        self.loading(true);
        self.assistHelper.fetchStats(self.table, self.column != null ? self.column : null, function (data) {
          if (data && data.status == 0) {
            self.statRows(data.stats);
            var inaccurate = true;
            for(var i = 0; i < data.stats.length; i++) {
              if (data.stats[i].data_type == "COLUMN_STATS_ACCURATE" && data.stats[i].comment == "true") {
                inaccurate = false;
                break;
              }
            }
            self.inaccurate(inaccurate);
          } else {
            $("#tableAnalysis").hide();
          }
          self.loading(false);
        },
        function (e) {
          if (e.status == 500) {
            $(document).trigger("error", "${ _('There was a problem loading the stats.') }");
            $("#tableAnalysis").hide();
          }
          self.loading(false);
        });
      };

      TableStats.prototype.refresh = function () {
        var self = this;
        if (self.refreshing()) {
          return;
        }
        var shouldFetchTerms = self.termsTabActive() || self.terms().length > 0;
        self.refreshing(true);

        self.assistHelper.refreshTableStats(self.table, function() {
          self.refreshing(false);
          self.fetchData();
          if (shouldFetchTerms) {
            self.fetchTerms();
          }
        }, function(message) {
          self.refreshing(false);
          $(document).trigger("error", message || "${ _('There was a problem refreshing the stats.') }");
        });
      };

      TableStats.prototype.fetchTerms = function () {
        var self = this;
        if (self.column == null) {
          return;
        }

        self.loadingTerms(true);
        self.assistHelper.fetchTerms(self.table, self.column, self.prefixFilter(), function (data) {
          if (data && data.status == 0) {
            self.terms($.map(data.terms, function (term) {
              return {
                name: term[0],
                count: term[1],
                percent: (parseFloat(term[1]) / parseFloat(data.terms[0][1])) * 100
              }
            }));
          } else {
            $("#tableAnalysis").hide();
            $(document).trigger("error", "${ _('There was a problem loading the terms.') }");
          }
          self.loadingTerms(false);
        }, function (e) {
          if (e.status == 500) {
            $("#tableAnalysis").hide();
            $(document).trigger("error", "${ _('There was a problem loading the terms.') }");
          }
          self.loadingTerms(false);
        });
      };

      function AssistPanel(params) {
        var self = this;

        self.hasErrors = ko.observable(false);
        self.simpleStyles = ko.observable(false);

        self.filter = ko.observable("").extend({ rateLimit: 150 });

        self.filterActive = ko.computed(function () {
          return self.filter().length !== 0;
        });

        self.options = ko.mapping.fromJS($.extend({
          isSearchVisible: false,
          lastSelectedDb: null
        }, $.totalStorage(params.appName + ".assist.options") || {}));

        $.each(Object.keys(self.options), function (index, key) {
          if (ko.isObservable(self.options[key])) {
            self.options[key].subscribe(function() {
              $.totalStorage(params.appName + ".assist.options", ko.mapping.toJS(self.options))
            });
          }
        });

        self.assistHelper = params.assistHelper;
        self.app = self.assistHelper.options.app;

        self.databases = ko.observableArray();
        self.selectedDatabase = ko.observable();

        self.reloading = ko.observable(false);
        self.loadingDatabases = ko.observable(true);

        self.loadingTables = ko.computed(function() {
          return typeof self.selectedDatabase() != "undefined" && self.selectedDatabase() !== null && self.selectedDatabase().loading();
        });

        self.selectedDatabase.subscribe(function(newValue) {
          if (newValue != null && !newValue.hasEntries() && !newValue.loading()) {
              newValue.loadEntries()
          }
        });

        // We need the names because select2 does not support objects
        self.availableDatabaseNames = ko.observableArray();

        self.fetchDatabases(function() {
          self.assistHelper.activeDatabase.subscribe(function(newValue) {
            window.setTimeout(function() {
              self.setDatabase(newValue);
            }, 10);
          });

          if ($.inArray(self.assistHelper.activeDatabase(), self.availableDatabaseNames()) > -1) {
            self.setDatabase(self.assistHelper.activeDatabase());
            return;
          }
          if ($.inArray(self.options.lastSelectedDb(), self.availableDatabaseNames()) > -1) {
            self.assistHelper.activeDatabase(self.options.lastSelectedDb());
          } else if ($.inArray("default", self.availableDatabaseNames()) > -1) {
            self.assistHelper.activeDatabase("default");
          } else if (self.availableDatabaseNames().length > 0) {
            self.assistHelper.activeDatabase(self.availableDatabaseNames()[0]);
          }

        });

        self.modalItem = ko.observable();
        self.analysisStats = ko.observable();

        var lastOffset = { top: -1, left: -1 };
        var $tableAnalysis = $("#tableAnalysis");
        self.refreshPosition = function () {
          if (self.analysisStats() == null) {
            return;
          }
          var targetElement = $tableAnalysis.data("targetElement");
          if (targetElement != null && targetElement.is(":visible")) {
            var newTop = targetElement.offset().top - $(window).scrollTop();
            if (targetElement != null && (lastOffset.left != targetElement.offset().left || lastOffset.top != newTop)) {
              lastOffset.left = targetElement.offset().left;
              lastOffset.top = newTop;
              var newCssTop = lastOffset.top - $tableAnalysis.outerHeight() / 2 + targetElement.outerHeight() / 2;
              $tableAnalysis.css("top", newCssTop).css("left", lastOffset.left + targetElement.outerWidth());
              if ((newCssTop + $tableAnalysis.outerHeight() / 2) < 70) {
                $tableAnalysis.hide();
              } else {
                $tableAnalysis.show();
              }
            }
          } else {
            $tableAnalysis.hide();
          }
        };
        window.setInterval(self.refreshPosition, 200);

        self.repositionActions = function(data, event) {
          if (data.definition.isDatabase) {
            var $container = $(event.target);
            $container.find(".assist-actions").css('right', -$container.scrollLeft() + 'px');
          }
        };
      }

      AssistPanel.prototype.setDatabase = function(name) {
        var self = this;
        if (name == null) {
          return;
        }
        self.options.lastSelectedDb(name);

        self.selectedDatabase(ko.utils.arrayFirst(self.databases(), function(database) {
          return name === database.definition.name;
        }));
      };

      AssistPanel.prototype.toggleSearch = function () {
        var self = this;
        self.options.isSearchVisible(!self.options.isSearchVisible());
      };

      AssistPanel.prototype.reloadAssist = function() {
        var self = this;
        self.reloading(true);
        self.loadingDatabases(true);
        self.selectedDatabase(null);
        self.assistHelper.clearCache();
        self.fetchDatabases(function() {
          self.setDatabase(self.options.lastSelectedDb());
        });
      };

      AssistPanel.prototype.fetchDatabases = function(callback) {
        var self = this;

        self.assistHelper.fetchDatabases(function(data) {
          self.databases($.map(data.databases, function(databaseName) {
            return new AssistEntry({
              name: databaseName,
              displayName: databaseName,
              title: databaseName,
              isDatabase: true
            }, null, self, self.filter);
          }));
          self.availableDatabaseNames(data.databases);

          self.reloading(false);
          self.loadingDatabases(false);
          if (callback) {
            callback();
          }
        }, function() {
          self.loadingDatabases(false);
          self.reloading(false);
          self.hasErrors(true);
        });
      };

      ko.components.register('assist-panel', {
        viewModel: AssistPanel,
        template: { element: 'assist-panel-template' }
      });
    }());
  </script>
</%def>

<%def name="jvmMemoryInput()">
  <script type="text/html" id="jvm-memory-input-template">
    <input type="text" class="input-small" data-bind="numericTextInput: { value: value, precision: 0, allowEmpty: true }" /> <select class="input-mini" data-bind="options: units, value: selectedUnit" />
  </script>

  <script type="text/javascript" charset="utf-8">
    (function() {
      var JVM_MEM_PATTERN = /([0-9]+)([MG])$/;
      var UNITS = { 'MB' : 'M', 'GB' : 'G' };

      function JvmMemoryInputViewModel(params) {
        this.valueObservable = params.value;
        this.units = Object.keys(UNITS);
        this.selectedUnit = ko.observable();
        this.value = ko.observable('');

        var match = JVM_MEM_PATTERN.exec(this.valueObservable());
        if (match && match.length === 3) {
          this.value(match[1]);
          this.selectedUnit(match[2] === 'M' ? 'MB' : 'GB');
        }

        this.value.subscribe(this.updateValueObservable, this);
        this.selectedUnit.subscribe(this.updateValueObservable, this);
      }

      JvmMemoryInputViewModel.prototype.updateValueObservable = function() {
        if (isNaN(this.value()) || this.value() === '') {
          this.valueObservable(undefined);
        } else {
          this.valueObservable(this.value() + UNITS[this.selectedUnit()]);
        }
      };

      ko.components.register('jvm-memory-input', {
        viewModel: JvmMemoryInputViewModel,
        template: { element: 'jvm-memory-input-template' }
      });
    }());
  </script>
</%def>


<%def name="csvListInput()">
  <script type="text/html" id="csv-list-input-template">
    <ul data-bind="sortable: values, visible: values().length" class="unstyled">
      <li style="margin-bottom: 4px">
        <div class="input-append">
          <!-- ko ifnot: $parent.inputTemplate -->
          <input type="text" data-bind="textInput: value, valueUpdate: 'afterkeydown', attr: { placeholder: $parent.placeholder }"/>
          <!-- /ko -->
          <!-- ko template: { if: $parent.inputTemplate, name: $parent.inputTemplate } --><!-- /ko -->
          <span class="add-on move-widget muted"><i class="fa fa-arrows"></i></span>
        </div>
        <a href="#" data-bind="click: function(){ $parent.removeValue(this); }">
          <i class="fa fa-minus"></i>
        </a>
      </li>
    </ul>
    <div style="min-width: 280px; margin-top: 5px;">
      <a class="pointer" style="padding: 3px 10px 3px 3px;;" data-bind="click: addValue">
        <i class="fa fa-plus"></i>
      </a>
    </div>
  </script>

  <script type="text/javascript" charset="utf-8">
    (function() {
      function CsvListInputViewModel (params) {
        this.valueObservable = params.value;
        this.isArray = $.isArray(this.valueObservable());
        this.placeholder = params.placeholder || '';
        this.inputTemplate = params.inputTemplate || null;

        var initialValues;
        if (this.isArray) {
          initialValues = ko.mapping.toJS(this.valueObservable());
        } else {
          initialValues = this.valueObservable() != null ? this.valueObservable().split(",") : [];
        }
        for (var i = 0; i < initialValues.length; i++) {
          initialValues[i] = { value: ko.observable(initialValues[i].trim()) };
          initialValues[i].value.subscribe(this.updateValueObservable, this);
        }
        this.values = ko.observableArray(initialValues);
        this.values.subscribe(this.updateValueObservable, this);
      }

      CsvListInputViewModel.prototype.addValue = function () {
        var newValue = { value: ko.observable('') };
        newValue.value.subscribe(this.updateValueObservable, this);
        this.values.push(newValue);
      };

      CsvListInputViewModel.prototype.removeValue = function (valueToRemove) {
        this.values.remove(valueToRemove);
      };

      CsvListInputViewModel.prototype.updateValueObservable = function () {
        var cleanValues = $.map(this.values(), function (item) {
          return item.value();
        });
        cleanValues = $.grep(cleanValues, function (value) {
          return value;
        });
        this.valueObservable(this.isArray ? cleanValues : cleanValues.join(','));
      };

      ko.components.register('csv-list-input', {
        viewModel: CsvListInputViewModel,
        template: { element: 'csv-list-input-template' }
      });
    }());
  </script>
</%def>