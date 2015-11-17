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
      margin-left: 0;
    }

    .assist-columns > li {
      padding: 6px 5px;
      white-space: nowrap;
    }

    .assist-actions  {
      position:absolute;
      right: 0;
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
      <!-- ko template: 'assist-sources-template' --><!-- /ko -->
      <!-- ko with: selectedSource -->
      <!-- ko template: { name: "assist-tables-template" } --><!-- /ko -->
      <!-- /ko -->
    </ul>
  </script>

  <script type="text/html" id="assist-sources-template">
    <!-- ko if: availableSourceTypes.length > 1 -->
    <li class="nav-header">
      ${_('source')}
    </li>
    <li>
      <ul data-bind="foreach: availableSourceTypes">
        <li data-bind="text: $data, click: function () { selectedSourceType($data) }"></li>
      </ul>
    </li>
    <!-- /ko -->
  </script>

  <script type="text/html" id="assist-databases-template">
    <li class="nav-header">
      ${_('database')}
      <div class="pull-right" data-bind="css: { 'hover-actions' : ! reloading() }">
        <a class="inactive-action" href="javascript:void(0)" data-bind="click: reloadAssist"><i class="pointer fa fa-refresh" data-bind="css: { 'fa-spin' : reloading }" title="${_('Manually refresh the table list')}"></i></a>
      </div>
    </li>
    <li data-bind="visible: ! hasErrors() && ! assistHelper.loading()" >
      <ul data-bind="foreach: assistHelper.availableDatabases">
        <li data-bind="text: $data, click: function () { $parent.assistHelper.activeDatabase($data) }"></li>
      </ul>
    </li>
    <li class="center" data-bind="visible: assistHelper.loading()" >
      <!--[if !IE]><!--><i class="fa fa-spinner fa-spin" style="font-size: 20px; color: #BBB"></i><!--<![endif]-->
      <!--[if IE]><img src="${ static('desktop/art/spinner.gif') }"/><![endif]-->
    </li>
    <li data-bind="visible: hasErrors">
      <span>${ _('The database list cannot be loaded.') }</span>
    </li>
  </script>

  <script type="text/html" id="assist-tables-template">
    <div data-bind="visibleOnHover: { selector: '.hover-actions' }" style="position: relative; width:100%">
      <!-- ko template: 'assist-databases-template' --><!-- /ko -->

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