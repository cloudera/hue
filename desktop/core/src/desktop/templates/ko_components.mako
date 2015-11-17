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

  <script type="text/html" id="assist-panel-column-stats">
    <div class="pull-right filter" data-bind="visible: termsTabActive" style="display:none;">
      <input type="text" data-bind="textInput: prefixFilter" placeholder="${ _('Prefix filter...') }"/>
    </div>
    <ul class="nav nav-tabs" role="tablist" style="margin-bottom: 0">
      <li data-bind="click: function() { termsTabActive(false) }" class="active"><a href="#columnAnalysisStats" role="tab" data-toggle="tab">${ _('Stats') }</a></li>
      <li data-bind="click: function() { termsTabActive(true) }"><a href="#columnAnalysisTerms" role="tab" data-toggle="tab">${ _('Terms') }</a></li>
    </ul>
    <div class="tab-content">
      <div class="tab-pane active" id="columnAnalysisStats" style="text-align: left">
        <div class="alert" data-bind="visible: isComplexType" style="margin: 5px">${ _('Column stats are currently not supported for columns of type:') } <span data-bind="text: type"></span></div>
        <div class="content" data-bind="ifnot: isComplexType">
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
    <div class="assist-actions" data-bind="css: { 'table-actions' : definition.isTable, 'column-actions': definition.isColumn } " style="opacity: 0">
      <a class="inactive-action" href="javascript:void(0)" data-bind="visible: definition.isTable, click: showPreview"><i class="fa fa-list" title="${_('Preview Sample data')}"></i></a>
      <a class="inactive-action" href="javascript:void(0)" data-bind="visible: definition.isTable || definition.isColumn, click: showStats, css: { 'blue': statsVisible }"><i class='fa fa-bar-chart' title="${_('View statistics') }"></i></a>
    </div>
  </script>

  <script type="text/html" id="assist-entries">
    <ul data-bind="foreach: filteredEntries, css: { 'assist-tables': definition.isDatabase }, event: { 'scroll': assistSource.repositionActions }">
      <li data-bind="visibleOnHover: { override: statsVisible, selector: definition.isTable ? '.table-actions' : '.column-actions' }, css: { 'assist-table': definition.isTable, 'assist-column': definition.isColumn }">
        <!-- ko template: { if: definition.isTable || definition.isColumn, name: 'assist-entry-actions' } --><!-- /ko -->
        <a class="assist-column-link" data-bind="multiClick: { click: toggleOpen, dblClick: dblClick }, attr: {'title': definition.title }, css: { 'assist-field-link': ! definition.isTable, 'assist-table-link': definition.isTable }" href="javascript:void(0)">
          <span draggable="true" data-bind="text: definition.displayName, draggableText: { text: editorText }"></span>
        </a>
        <!-- ko template: { if: open(), name: 'assist-entries'  } --><!-- /ko -->
      </li>
    </ul>
    <!-- ko template: { if: ! hasEntries() && ! loading(), name: 'assist-no-entries' } --><!-- /ko -->
  </script>

  <script type="text/html" id="assist-panel-template">
    <ul class="nav nav-list" style="position:relative; border: none; padding: 0; background-color: #FFF; margin-bottom: 1px; width:100%;">
      <!-- ko if: availableSourceTypes.length > 1 -->
      <li class="nav-header">
        ${_('source')}
      </li>
      <li>
        <select data-bind="options: availableSourceTypes, select2: { width: '100%', placeholder: '${ _ko("Choose a source...") }', update: selectedSourceType }" class="input-medium" data-placeholder="${_('Choose a source...')}"></select>
      </li>
      <!-- /ko -->
      <!-- ko with: selectedSource -->
      <!-- ko template: { name: "assist-type-template" } --><!-- /ko -->
      <!-- /ko -->
    </ul>
  </script>

  <script type="text/html" id="assist-type-template">
    <div data-bind="visibleOnHover: { selector: '.hover-actions' }" style="position: relative; width:100%">
      <li class="nav-header">
        ${_('database')}
        <div class="pull-right" data-bind="css: { 'hover-actions' : ! reloading() }">
          <a class="inactive-action" href="javascript:void(0)" data-bind="click: reloadAssist"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin' : reloading }" title="${_('Manually refresh the table list')}"></i></a>
        </div>
      </li>

      <li data-bind="visible: ! hasErrors() && ! assistHelper.loading()" >
        <div data-bind="select2: { options: assistHelper.availableDatabases, value: assistHelper.activeDatabase, width: '100%', placeholder: '${ _ko("Choose a database...") }' }" class="input-medium" data-placeholder="${_('Choose a database...')}"></div>
      </li>

      <li class="center" data-bind="visible: assistHelper.loading()" >
        <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i><!--<![endif]-->
        <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
      </li>

      <li data-bind="visible: hasErrors">
        <span>${ _('The database list cannot be loaded.') }</span>
      </li>

      <li class="nav-header" style="margin-top:10px;" data-bind="visible: ! assistHelper.loading() && ! hasErrors()">
        ${_('tables')}
        <div class="pull-right" data-bind="visible: selectedDatabase() != null && selectedDatabase().hasEntries(), css: { 'hover-actions': ! filter(), 'blue': filter }">
          <!-- ko if: selectedDatabase() != null -->
          <span class="assist-tables-counter">(<span data-bind="text: selectedDatabase().filteredEntries().length"></span>)</span>
          <!-- /ko -->
          <a class="inactive-action" href="javascript:void(0)" data-bind="click: toggleSearch"><i class="pointer fa fa-search" title="${_('Search')}"></i></a>
        </div>
      </li>

      <!-- ko if: selectedDatabase() != null -->
        <li data-bind="slideVisible: selectedDatabase() != null && selectedDatabase().hasEntries() && options.isSearchVisible()">
          <div><input type="text" placeholder="${ _('Table name...') }" style="width:90%;" data-bind="value: filter, valueUpdate: 'afterkeydown'"/></div>
        </li>

      <div class="table-container">
        <div class="center" data-bind="visible: selectedDatabase() != null && selectedDatabase().loading()">
          <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i><!--<![endif]-->
          <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
        </div>
        <!-- ko template: { if: selectedDatabase() != null, name: 'assist-entries', data: selectedDatabase } --><!-- /ko -->
        </div>
      <!-- /ko -->
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

    <div id="tableAnalysis" style="position: fixed; display: none;" class="popover show mega-popover right" data-bind="visible: analysisStats() != null, with: analysisStats">
      <div class="arrow"></div>
      <h3 class="popover-title" style="text-align: left">
        <a class="pull-right pointer close-popover" style="margin-left: 8px" data-bind="click: function() { $parent.analysisStats(null) }"><i class="fa fa-times"></i></a>
        <a class="pull-right pointer stats-refresh" style="margin-left: 8px" data-bind="visible: !isComplexType, click: refresh"><i class="fa fa-refresh" data-bind="css: { 'fa-spin' : refreshing }"></i></a>
        <span class="pull-right stats-warning muted" data-bind="visible: inaccurate() && column == null" rel="tooltip" data-placement="top" title="${ _('The column stats for this table are not accurate') }" style="margin-left: 8px"><i class="fa fa-exclamation-triangle"></i></span>
        <i data-bind="visible: loading" class='fa fa-spinner fa-spin'></i>
        <!-- ko if: column == null -->
        <strong class="table-name" data-bind="text: table"></strong> ${ _(' table analysis') }
        <!-- /ko -->
        <!-- ko ifnot: column == null -->
        <strong class="table-name" data-bind="text: column"></strong> ${ _(' column analysis') }
        <!-- /ko -->
      </h3>
      <div class="popover-content">
        <div class="alert" style="text-align: left; display:none" data-bind="visible: hasError">${ _('There is no analysis available') }</div>
        <!-- ko if: isComplexType && snippet.type() == 'impala' -->
        <div class="alert" style="text-align: left">${ _('Column analysis is currently not supported for columns of type:') } <span data-bind="text: type"></span></div>
        <!-- /ko -->
        <!-- ko template: {if: column == null && ! hasError() && ! (isComplexType && snippet.type() == 'impala'), name: 'assist-panel-table-stats' } --><!-- /ko -->
        <!-- ko template: {if: column != null && ! hasError() && ! (isComplexType && snippet.type() == 'impala'), name: 'assist-panel-column-stats' } --><!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/javascript" charset="utf-8">
    (function (factory) {
      if(typeof require === "function") {
        require(['knockout', 'desktop/js/assist/assistSource'], factory);
      } else {
        factory(ko, AssistSource);
      }
    }(function (ko, AssistSource) {

      function AssistPanel(params) {
        var i18n = {
          errorLoadingTablePreview: "${ _('There was a problem loading the table preview.') }",
          errorLoadingStats: "${ _('There was a problem loading the stats.') }",
          errorRefreshingStats: "${ _('There was a problem refreshing the stats.') }",
          errorLoadingTerms: "${ _('There was a problem loading the terms.') }"
        }
        var notebookViewModel = params.notebookViewModel;
        var notebook = notebookViewModel.selectedNotebook();

        self.sourceIndex = {};
        $.each(notebookViewModel.availableSnippets(), function (index, snippet) {
          var settings = notebookViewModel.getSnippetViewSettings(snippet.type());

          var fakeSnippet = {
            type: snippet.type,
            getContext: function() {
              return {
                type: snippet.type()
              }
            },
            getAssistHelper: function() {
              return notebook.getAssistHelper(snippet.type());
            }
          };

          if (settings.sqlDialect) {
            self.sourceIndex[snippet.name()] = new AssistSource(fakeSnippet, i18n);
          }
        });

        self.availableSourceTypes = Object.keys(self.sourceIndex);

        self.selectedSourceType = ko.observable();
        self.selectedSource = ko.observable();

        self.selectedSourceType.subscribe(function (newSourceType) {
          var source = self.sourceIndex[newSourceType];
          if (! source.assistHelper.loaded()) {
            source.assistHelper.load(source.snippet);
          }
          self.selectedSource(source);
        });

        var lastSelectedSource =  $.totalStorage("hue.assist.lastSelectedSource." + notebookViewModel.user);
        if ($.inArray(lastSelectedSource, self.availableSourceTypes) !== -1) {
          self.selectedSourceType(lastSelectedSource);
        } else {
          self.selectedSourceType(self.availableSourceTypes[0]);
        }

        self.selectedSourceType.subscribe(function (newSourceType) {
          $.totalStorage("hue.assist.lastSelectedSource." + notebookViewModel.user, newSourceType);
        });
      }

      ko.components.register('assist-panel', {
        viewModel: AssistPanel,
        template: { element: 'assist-panel-template' }
      });
    }));
  </script>
</%def>

<%def name="jvmMemoryInput()">
  <script type="text/html" id="jvm-memory-input-template">
    <input type="text" class="input-small" data-bind="numericTextInput: { value: value, precision: 0, allowEmpty: true }" /> <select class="input-mini" data-bind="options: units, value: selectedUnit" />
  </script>

  <script type="text/javascript" charset="utf-8">
    (function (factory) {
      if(typeof require === "function") {
        require(['knockout'], factory);
      } else {
        factory(ko);
      }
    }(function (ko) {
      (function () {
        var JVM_MEM_PATTERN = /([0-9]+)([MG])$/;
        var UNITS = {'MB': 'M', 'GB': 'G'};

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

        JvmMemoryInputViewModel.prototype.updateValueObservable = function () {
          if (isNaN(this.value()) || this.value() === '') {
            this.valueObservable(undefined);
          } else {
            this.valueObservable(this.value() + UNITS[this.selectedUnit()]);
          }
        };

        ko.components.register('jvm-memory-input', {
          viewModel: JvmMemoryInputViewModel,
          template: {element: 'jvm-memory-input-template'}
        });
      }());
    }));
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
      <a class="inactive-action pointer" style="padding: 3px 10px 3px 3px;;" data-bind="click: addValue">
        <i class="fa fa-plus"></i>
      </a>
    </div>
  </script>

  <script type="text/javascript" charset="utf-8">
    (function (factory) {
      if(typeof require === "function") {
        require(['knockout'], factory);
      } else {
        factory(ko);
      }
    }(function (ko) {
      (function () {
        function CsvListInputViewModel(params) {
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
            initialValues[i] = {value: ko.observable(initialValues[i].trim())};
            initialValues[i].value.subscribe(this.updateValueObservable, this);
          }
          this.values = ko.observableArray(initialValues);
          this.values.subscribe(this.updateValueObservable, this);
        }

        CsvListInputViewModel.prototype.addValue = function () {
          var newValue = {value: ko.observable('')};
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
          template: {element: 'csv-list-input-template'}
        });
      }());
    }));
  </script>
</%def>

<%def name="addSnippetMenu()">
  <script type="text/html" id="add-snippet-menu-template">
    <div class="add-snippet-button" style="position:relative; width:65px; text-align: center;">
      <i class="pointer fa fa-plus-circle fa-5x" title="${ _('Add a new snippet') }" data-bind="click: addLastUsedSnippet, event: { 'mouseenter': showHistory, 'mouseleave': hideHistory }"></i>
      <div class="select-snippet-button" title="${ _('Select snippet') }" data-bind="fadeVisible: { value: hasAdditionalSnippets && showingSelectSnippet(), fadeOut: true }, click: showSnippetModal, event: { 'mouseenter': showHistory, 'mouseleave': hideHistory }">...</div>
      <div class="all-alternatives" data-bind="foreach: snippetHistory">
        <div class="add-snippet-alt pointer" style="display:none;" data-bind="
            event: { 'mouseenter': $parent.showHistory, 'mouseleave': $parent.hideHistory },
            fadeVisible: { value: $parent.showingHistory(), fadeOut: true, speed: 'slow' },
            style: { 'left': $parent.positions[$index()].left, 'top': $parent.positions[$index()].top },
            click: $parent.addNewSnippet">
          <div data-bind="text: name()"></div>
        </div>
      </div>
    </div>

    <div id="addSnippetModal" class="modal hide fade">
      <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>${ _('Add Snippet') }</h3>
      </div>
      <div class="modal-body" style="min-height: 100px">
        <ul class="snippet-list-alts" data-bind="foreach: availableSnippets">
          <li data-bind="click: function() { $parent.addNewSnippet($data) }">
            <div style="width: 30px; display:inline-block;">
            <!-- ko if: $root.getSnippetViewSettings(type()).snippetImage -->
            <img class="snippet-icon" data-bind="attr: { 'src': $root.getSnippetViewSettings(type()).snippetImage }">
            <!-- /ko -->
            <!-- ko if: $root.getSnippetViewSettings(type()).snippetIcon -->
            <i style="margin-left: 6px; color: #338bb8;" class="fa snippet-icon" data-bind="css: $root.getSnippetViewSettings(type()).snippetIcon"></i>
            <!-- /ko -->
            </div>
            <span data-bind="text: name"></span>
          </li>
        </ul>
      </div>
      <div class="modal-footer">
        <button class="btn btn-primary disable-feedback" data-dismiss="modal">${_('Close')}</button>
      </div>
    </div>
  </script>

  <script type="text/javascript" charset="utf-8">
    (function (factory) {
      if(typeof require === "function") {
        require(['knockout'], factory);
      } else {
        factory(ko);
      }
    }(function (ko) {
      (function () {
        var WHEEL_RADIUS = 75;
        var PLUS_ICON_RADIUS = 27.859; // FA-5X

        var calculatePositions = function (alternativeCount) {
          var radius = WHEEL_RADIUS;
          var radIncrements = 2 * Math.PI / alternativeCount;
          var currentRad = -0.5 * Math.PI;

          var result = [];

          for (var i = 0; i < alternativeCount; i++) {
            result.push({
              left: radius * Math.cos(currentRad) + PLUS_ICON_RADIUS + 'px',
              top: radius * Math.sin(currentRad) + PLUS_ICON_RADIUS + 'px'
            });
            currentRad += radIncrements;
          }

          return result;
        };

        function AddSnippetMenuViewModel(params) {
          var self = this;
          self.notebook = params.notebook;
          self.availableSnippets = params.availableSnippets;
          self.snippetHistory = ko.observableArray([].concat(self.availableSnippets.slice(0, 5)));
          self.lastUsedSnippet = self.snippetHistory()[0];
          self.roundCount = 0;
          self.positions = calculatePositions(self.snippetHistory().length);
          self.showingHistory = ko.observable(false);
          self.hasAdditionalSnippets = params.availableSnippets().length > 5;
          self.showingSelectSnippet = ko.observable(false);

          self.addLastUsedSnippet = function () {
            self.addNewSnippet(self.lastUsedSnippet);
          };

          self.showSnippetModal = function () {
            $("#addSnippetModal").modal('show');
          };

          self.addNewSnippet = function (alternative) {
            clearTimeout(hideTimeout);
            self.showingHistory(false);
            self.showingSelectSnippet(false);
            $("#addSnippetModal").modal('hide');

            // When fewer than 5 it's always in history
            if (self.snippetHistory().indexOf(alternative) == -1) {
              self.snippetHistory.splice(4 - self.roundCount, 1, alternative);
              self.roundCount = (self.roundCount + 1) % 5;
            }

            self.lastUsedSnippet = alternative;
            self.notebook.newSnippet(alternative.type())
          };

          var hideTimeout = -1;

          self.showHistory = function () {
            clearTimeout(hideTimeout);
            self.showingHistory(true);
            self.showingSelectSnippet(true);
          };

          self.hideHistory = function () {
            clearTimeout(hideTimeout);
            hideTimeout = window.setTimeout(function () {
              self.showingHistory(false);
              self.showingSelectSnippet(false);
            }, 500);
          };
        }

        ko.components.register('add-snippet-menu', {
          viewModel: AddSnippetMenuViewModel,
          template: {element: 'add-snippet-menu-template'}
        });
      }());
    }));
  </script>
</%def>

<%def name="downloadSnippetResults()">
  <script type="text/html" id="download-results-template">
    <form method="POST" action="${ url('notebook:download') }" class="download-form" style="display: inline">
      ${ csrf_token(request) | n,unicode }
      <input type="hidden" name="notebook"/>
      <input type="hidden" name="snippet"/>
      <input type="hidden" name="format"/>
    </form>

    <div class="hover-dropdown" data-bind="visible: snippet.status() == 'available' && snippet.result.hasSomeResults() && snippet.result.type() == 'table'" style="display:none;">
      <a class="snippet-side-btn inactive-action dropdown-toggle pointer" style="padding-right:0" data-toggle="dropdown">
        <i class="fa fa-download"></i>
      </a>
      <ul class="dropdown-menu">
        <li>
          <a class="inactive-action download" href="javascript:void(0)" data-bind="click: downloadCsv" title="${ _('Download first rows as CSV') }">
            <i class="fa fa-file-o"></i> ${ _('CSV') }
          </a>
        </li>
        <li>
          <a class="inactive-action download" href="javascript:void(0)" data-bind="click: downloadXls" title="${ _('Download first rows as XLS') }">
            <i class="fa fa-file-excel-o"></i> ${ _('Excel') }
          </a>
        </li>
      </ul>
    </div>
  </script>

  <script type="text/javascript" charset="utf-8">
    (function (factory) {
      if(typeof require === "function") {
        require(['knockout'], factory);
      } else {
        factory(ko);
      }
    }(function (ko) {
      function DownloadResultsViewModel (params, element) {
        var self = this;
        self.$downloadForm = $(element).find(".download-form");
        self.snippet = params.snippet;
        self.notebook = params.notebook;
      }

      DownloadResultsViewModel.prototype.download = function (format) {
        var self = this;
        self.$downloadForm.find('input[name=\'format\']').val(format);
        self.$downloadForm.find('input[name=\'notebook\']').val(ko.mapping.toJSON(self.notebook.getContext()));
        self.$downloadForm.find('input[name=\'snippet\']').val(ko.mapping.toJSON(self.snippet.getContext()));
        self.$downloadForm.submit();
      };

      DownloadResultsViewModel.prototype.downloadXls = function () {
        var self = this;
        self.download("xls");
      };

      DownloadResultsViewModel.prototype.downloadCsv = function () {
        var self = this;
        self.download("csv");
      };

      ko.components.register('downloadSnippetResults', {
        viewModel: { createViewModel: function (params, componentInfo) {
          return new DownloadResultsViewModel(params, componentInfo.element);
        }},
        template: { element: 'download-results-template' }
      });
    }));
  </script>
</%def>