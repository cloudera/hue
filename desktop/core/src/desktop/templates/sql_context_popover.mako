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
from metadata.conf import has_navigator
%>

<%def name="sqlContextPopover()">
  <style>
    .sql-context-popover {
      position: absolute;
      top: 0;
      left: 0;
      z-index: 1060;
      display: block;
      width: 450px;
      height: 425px;
      padding: 1px;
      text-align: left;
      text-align: start;
      background-color: #fff;
      -webkit-background-clip: padding-box;
      background-clip: padding-box;
      border: 1px solid transparent;
    }

    .sql-context-popover.sql-context-popover-top {
      margin-top: -5px;
    }

    .sql-context-popover.sql-context-popover-top .sql-context-popover-arrow {
      bottom: -6px;
      left: 50%;
      margin-left: -6px;
      border-top-color: #338BB8;
      border-bottom-width: 0;
    }

    .sql-context-popover.sql-context-popover-top .sql-context-popover-arrow::after {
      bottom: 1px;
      margin-left: -3px;
      content: "";
      border-top-color: #338BB8;
      border-bottom-width: 0;
    }

    .sql-context-popover.sql-context-popover-right {
      margin-left: 5px;
    }

    .sql-context-popover.sql-context-popover-right .sql-context-popover-arrow {
      top: 50%;
      left: -6px;
      margin-top: -6px;
      border-right-color: #338BB8;
      border-left-width: 0;
    }

    .sql-context-popover.sql-context-popover-right .sql-context-popover-arrow::after {
      bottom: -3px;
      left: 1px;
      content: "";
      border-right-color: #338BB8;
      border-left-width: 0;
    }

    .sql-context-popover.sql-context-popover-bottom {
      margin-top: 7px;
    }

    .sql-context-popover.sql-context-popover-bottom .sql-context-popover-arrow {
      top: -6px;
      left: 50%;
      margin-left: -6px;
      border-top-width: 0;
      border-bottom-color: #338BB8;
    }

    .sql-context-popover.sql-context-popover-bottom .sql-context-popover-arrow::after {
      top: 3px;
      margin-left: -3px;
      content: "";
      border-top-width: 0;
      border-bottom-color: #338BB8;
    }

    .sql-context-popover.sql-context-popover-left {
      margin-left: -5px;
    }

    .sql-context-popover.sql-context-popover-left .sql-context-popover-arrow {
      top: 50%;
      right: -6px;
      margin-top: -3px;
      border-right-width: 0;
      border-left-color: #338BB8;
    }

    .sql-context-popover.sql-context-popover-left .sql-context-popover-arrow::after {
      right: 2px;
      bottom: -3px;
      content: "";
      border-right-width: 0;
      border-left-color: #338BB8;
    }

    .sql-context-popover-title {
      padding: 6px 10px;
      margin: 0;
      font-size: 0.9rem;
      background-color: #fff;
    }

    .sql-context-popover-title:empty {
      display: none;
    }

    .sql-context-popover-content {
      padding: 0;
      overflow: hidden;
    }

    .sql-context-popover-arrow, .sql-context-popover-arrow::after {
      position: absolute;
      display: block;
      width: 0;
      height: 0;
      border-color: transparent;
      border-style: solid;
    }

    .sql-context-tabs {
      border-bottom: 1px solid #ebebeb;
      margin-left: -1px;
      margin-right: -1px;
      padding-left: 15px;
    }

    .sql-context-tab {
      padding-top: 0 !important;
      padding-bottom: 5px !important;
      margin-bottom: -1px !important
    }

    .sql-context-popover-arrow {
      border-width: 6px;
    }

    .popover-arrow::after {
      content: "";
      border-width: 5px;
    }

    .sql-context-flex {
      position: relative;
      display: flex;
      flex-flow: column nowrap;
      height: 100%;
    }

    .sql-context-flex-header {
      flex: 0 0 35px;
    }

    .sql-context-flex-fill {
      position: relative;
      flex: 1 1 100%;
      overflow: auto;
    }

    .sql-context-flex-bottom-links {
      flex: 0 0 35px;
      border-top: 1px solid #ebebeb;
      z-index: 100;
      background-color: #FFF;
    }

    .sql-context-link-row {
      float: right;
      margin: 10px 15px 0 10px;
    }

    .sql-context-link-row a {
      margin-left: 10px;
    }

    .sql-context-inline-search {
      border-radius: 8px !important;
      min-height: 18px !important;
      height: 18px !important;
      margin: 0 5px 0 5px !important;
      padding-right: 18px !important;
    }

    .sql-context-empty-columns {
      letter-spacing: 0.035em;
      margin-top: 50px;
      font-size: 14px;
      color: #737373;
      text-align: center;
    }
  </style>


  <script type="text/html" id="sql-context-table-details">
    <div class="sql-context-flex">
      <div class="sql-context-flex-fill" data-bind="with: fetchedData">
        <!-- ko component: { name: 'sql-columns-table', params: { columns: extended_columns } } --><!-- /ko -->
      </div>
      <div class="sql-context-flex-bottom-links">
        <div class="sql-context-link-row">
          <a class="inactive-action pointer" data-bind="click: function() { huePubSub.publish('sql.context.popover.show.in.assist') }"><i style="font-size: 11px;" title="Show in Assist..." class="fa fa-search"></i> ${ _("Assist") }</a>
          <a class="inactive-action pointer" data-bind="click: function() { huePubSub.publish('sql.context.popover.open.in.metastore') }"><i style="font-size: 11px;" title="Open in Metastore..." class="fa fa-external-link"></i> ${ _("Metastore") }</a>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="sql-context-column-details">
    <div class="sql-context-flex">
      <div class="sql-context-flex-fill">
        <div style="margin: 15px;" data-bind="with: fetchedData">
          <a class="pointer" data-bind="text: name, attr: { title: comment }, click: function() { huePubSub.publish('sql.context.popover.scroll.to.column', name); }"></a> (<span data-bind="text: type.indexOf('<') !== -1 ? type.substring(0, type.indexOf('<')) : type, attr: { title: type }"></span>)
          <!-- ko if: comment -->
          <div style="margin-top: 10px; font-weight: bold;">${ _("Comment") }</div>
          <div data-bind="text: comment"></div>
          <!-- /ko -->
        </div>
      </div>
      <div class="sql-context-flex-bottom-links">
        <div class="sql-context-link-row">
          <a class="inactive-action pointer" data-bind="click: function() { huePubSub.publish('sql.context.popover.show.in.assist') }"><i style="font-size: 11px;" title="Show in Assist..." class="fa fa-search"></i> ${ _("Assist") }</a>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="sql-context-table-and-column-sample">
    <div class="sql-context-flex">
      <div style="overflow: hidden;" class="sql-context-flex-fill" data-bind="with: fetchedData">
        <div class="sample-scroll" style="text-align: left; padding: 3px; overflow: hidden">
          <!-- ko if: rows.length == 0 -->
          <div class="alert">${ _('The selected table has no data.') }</div>
          <!-- /ko -->
          <!-- ko if: rows.length > 0 -->
          <table id="samples-table" class="samples-table table table-striped table-condensed">
            <thead>
            <tr>
              <th style="width: 10px">&nbsp;</th>
              <!-- ko foreach: headers -->
              <th data-bind="text: $data"></th>
              <!-- /ko -->
            </tr>
            </thead>
            <tbody>
            </tbody>
          </table>
          <!-- /ko -->
        </div>
      </div>
      <div class="sql-context-flex-bottom-links">
        <div class="sql-context-link-row">
          <a class="inactive-action pointer" data-bind="click: function() { huePubSub.publish('sql.context.popover.show.in.assist') }"><i style="font-size: 11px;" title="Show in Assist..." class="fa fa-search"></i> ${ _("Assist") }</a>
          <a class="inactive-action pointer" data-bind="visible: ! $parent.isColumn, click: function() { huePubSub.publish('sql.context.popover.open.in.metastore') }"><i style="font-size: 11px;" title="Open in Metastore..." class="fa fa-external-link"></i> ${ _("Metastore") }</a>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="sql-context-table-analysis">
    <div class="sql-context-flex">
      <div style="overflow: hidden;" class="sql-context-flex-fill" data-bind="with: fetchedData, niceScroll">
        <!-- ko if: stats.length > 0 -->
          <table class="table table-striped">
            <tbody data-bind="foreach: stats">
              <tr>
                <th data-bind="text: data_type, style:{'border-top-color': $index() == 0 ? '#ffffff' : '#e5e5e5'}" style="background-color: #FFF"></th>
                <td data-bind="text: $parents[1].formatAnalysisValue(data_type, comment), style:{'border-top-color': $index() == 0 ? '#ffffff' : '#e5e5e5'}" style="background-color: #FFF"></td>
              </tr>
            </tbody>
          </table>
        <!-- /ko -->
      </div>
      <div class="sql-context-flex-bottom-links">
        <div class="sql-context-link-row">
          <a class="inactive-action pointer" data-bind="click: function() { huePubSub.publish('sql.context.popover.show.in.assist') }"><i style="font-size: 11px;" title="Show in Assist..." class="fa fa-search"></i> ${ _("Assist") }</a>
          <a class="inactive-action pointer" data-bind="visible: ! $parent.isColumn, click: function() { huePubSub.publish('sql.context.popover.open.in.metastore') }"><i style="font-size: 11px;" title="Open in Metastore..." class="fa fa-external-link"></i> ${ _("Metastore") }</a>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="sql-context-column-analysis">
    <div class="sql-context-flex">
      <div style="overflow: hidden;" class="sql-context-flex-fill" data-bind="with: fetchedData, niceScroll">
        <table class="table table-condensed">
          <tbody data-bind="foreach: stats">
            <tr>
              <th data-bind="text: Object.keys($data)[0], style:{'border-top-color': $index() == 0 ? '#ffffff' : '#e5e5e5'}" style="background-color: #FFF"></th>
              <td data-bind="text: $data[Object.keys($data)[0]], style:{'border-top-color': $index() == 0 ? '#ffffff' : '#e5e5e5'}" style="background-color: #FFF"></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="sql-context-flex-bottom-links">
        <div class="sql-context-link-row">
          <a class="inactive-action pointer" data-bind="click: function() { huePubSub.publish('sql.context.popover.show.in.assist') }"><i style="font-size: 11px;" title="Show in Assist..." class="fa fa-search"></i> ${ _("Assist") }</a>
          <a class="inactive-action pointer" data-bind="visible: ! $parent.isColumn, click: function() { huePubSub.publish('sql.context.popover.open.in.metastore') }"><i style="font-size: 11px;" title="Open in Metastore..." class="fa fa-external-link"></i> ${ _("Metastore") }</a>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="sql-context-function-details">
    <div style="padding: 8px" data-bind="with: details">
      <p style="margin: 10px 10px 18px 10px;"><span style="white-space: pre; font-family: monospace;" data-bind="text: signature"></span></p>
      <p><span data-bind="text: description"></span></p>
    </div>
  </script>

  <script type="text/html" id="sql-context-table-partitions">
    <div class="sql-context-flex">
      <div style="overflow: hidden;" class="sql-context-flex-fill" data-bind="with: fetchedData, niceScroll">
        <div style="margin: 10px 5px 0 10px;">
          <span style="font-size: 15px; font-weight: 300;">${_('Columns')}</span>
        </div>
        <div>
          <table class="table table-striped table-condensed table-nowrap">
            <thead>
            <tr>
              <th style="width: 1%">&nbsp;</th>
              <th>${_('Name')}</th>
            </tr>
            </thead>
            <tbody data-bind="foreach: partition_keys_json">
            <tr>
              <td data-bind="text: $index()+1"></td>
              <td><a href="#" data-bind="text: $data, click: function() { huePubSub.publish('sql.context.popover.scroll.to.column', $data); }"></a></td>
            </tr>
            </tbody>
          </table>
        </div>
        <div style="margin: 10px 5px 0 10px;">
          <span style="font-size: 15px; font-weight: 300;">${_('Partitions')}</span>
        </div>
        <table class="table table-striped table-condensed table-nowrap">
          <thead>
            <tr>
              <th style="width: 1%">&nbsp;</th>
              <th>${_('Values')}</th>
              <th>${_('Spec')}</th>
              <th>${_('Browse')}</th>
            </tr>
          </thead>
          <tbody data-bind="foreach: partition_values_json">
            <tr>
              <td data-bind="text: $index()+1"></td>
              <td><a href="#" data-bind="click: function () { window.open(readUrl, '_blank'); return false; }, text: '[\'' + columns.join('\',\'') + '\']'"></a></td>
              <td data-bind="text: partitionSpec"></td>
              <td>
                <a href="#" data-bind="click: function () { window.open(readUrl, '_blank'); return false; }" title="${_('Data')}"><i class="fa fa-th"></i></a> <a href="#" data-bind="click: function () { window.open(browseUrl, '_blank'); return false; }" title="${_('Files')}"><i class="fa fa-file-o"></i></a>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="sql-context-flex-bottom-links">
        <div class="sql-context-link-row">
          <a class="inactive-action pointer" data-bind="click: function() { huePubSub.publish('sql.context.popover.show.in.assist') }"><i style="font-size: 11px;" title="Show in Assist..." class="fa fa-search"></i> ${ _("Assist") }</a>
          <a class="inactive-action pointer" data-bind="click: function() { huePubSub.publish('sql.context.popover.open.in.metastore') }"><i style="font-size: 11px;" title="Open in Metastore..." class="fa fa-external-link"></i> ${ _("Metastore") }</a>
        </div>
      </div>
    </div>
  </script>

  <script type="text/html" id="sql-context-popover-template">
    <div class="sql-context-popover sql-context-popover-bottom" data-bind="css: orientationClass, style: { left: left() + 'px', top: top() + 'px' }">
      <div class="sql-context-popover-arrow"></div>
      <div class="sql-context-popover-title">
        <i class="pull-left fa muted" data-bind="css: iconClass" style="margin-top: 3px"></i> <span data-bind="text: title"></span>
        <a class="pull-right pointer inactive-action" data-bind="click: close"><i class="fa fa-fw fa-times"></i></a>
      </div>
      <div class="sql-context-popover-content">
        <!-- ko with: contents -->
        <ul class="nav nav-pills sql-context-tabs" data-bind="foreach: tabs">
          <li data-bind="click: function () { $parent.activeTab(id); }, css: { 'active' : $parent.activeTab() === id }">
            <a class="sql-context-tab" data-toggle="tab" data-bind="text: label, attr: { href: '#' + id }"></a>
          </li>
        </ul>
        <div class="tab-content" style="border: none; overflow: auto; height: 365px;" data-bind="foreach: tabs">
          <div class="tab-pane" id="sampleTab" data-bind="attr: { id: id }, css: { 'active' : $parent.activeTab() === id }" style="height: 100%; overflow: hidden;">
            <!-- ko with: templateData -->
              <!-- ko hueSpinner: { spin: loading, center: true, size: 'large' } --><!-- /ko -->
              <!-- ko if: ! loading() && hasErrors() -->
                <div class="alert" data-bind="text: $parent.errorText"></div>
              <!-- /ko -->
              <!-- ko if: ! loading() && ! hasErrors() -->
                <!-- ko template: { name: $parent.template } --><!-- /ko -->
              <!-- /ko -->
            <!-- /ko -->
          </div>
        </div>
        <!-- /ko -->
      </div>
    </div>
  </script>

  <script type="text/html" id="sql-columns-table-template">
    <div class="sql-context-flex">
      <div class="sql-context-flex-header">
        <div style="margin: 10px 5px 0 10px;">
          <span style="font-size: 15px; font-weight: 300;">${_('Columns')}</span>
          <a href="#" data-bind="toggle: searchVisible"><i class="snippet-icon fa fa-search inactive-action" data-bind="css: { 'blue': searchVisible }"></i></a>
          <input class="input-large sql-context-inline-search" type="text" data-bind="visible: searchVisible, hasFocus: searchFocus, clearable: searchInput, valueUpdate:'afterkeydown'" placeholder="${ _('Search...') }">
        </div>
      </div>
      <div class="sql-context-flex-fill sql-columns-table" style="position:relative; height: 100%; overflow-y: auto;">
        <table style="width: 100%" class="table table-striped table-condensed table-nowrap">
          <thead>
            <tr data-bind="visible: filteredColumns().length !== 0">
              <th width="6%">&nbsp;</th>
              <th width="60%">${_('Name')}</th>
              <th width="34%">${_('Type')}</th>
              <th width="6%">&nbsp;</th>
            </tr>
          </thead>
          <tbody data-bind="foreachVisible: { data: filteredColumns, minHeight: 29, container: '.sql-columns-table', pubSubDispose: 'sql.context.popover.dispose' }">
            <tr>
              <td data-bind="text: $index()+$indexOffset()+1"></td>
              <td style="overflow: hidden;">
                <a href="javascript:void(0)" class="column-selector" data-bind="text: name, click: function() { huePubSub.publish('sql.context.popover.scroll.to.column', name); }" title="${ _("Show sample") }"></a>
              </td>
              <td><span data-bind="text: type, attr: { 'title': extendedType }, tooltip: { placement: 'bottom' }"></span></td>
              <td><i class="snippet-icon fa fa-question-circle" data-bind="visible: comment, attr: { 'title': comment }, tooltip: { placement: 'bottom' }"></i></td>
            </tr>
          </tbody>
        </table>
        <div class="sql-context-empty-columns" data-bind="visible: filteredColumns().length === 0">${_('No columns found')}</div>
      </div>
    </div>
  </script>

  <script type="text/javascript" charset="utf-8">
    require([
      'knockout',
      'desktop/js/apiHelper',
      'desktop/js/assist/tableStats',
      'desktop/js/sqlFunctions'
    ], function (ko, ApiHelper, TableStats, sqlFunctions) {

      var hidePopover = function () {
        $('#sqlContextPopover').remove();
        $(document).off('click', hideOnClickOutside);
        huePubSub.publish('sql.context.popover.dispose');
        huePubSub.publish('sql.context.popover.hidden');
      };

      var hideOnClickOutside = function (event) {
        if (!$.contains($('#sqlContextPopover')[0], event.target)) {
          hidePopover();
        }
      };

      function TableAndColumnTabContents(identifierChain, snippet, apiFunction) {
        var self = this;
        self.identifierChain = identifierChain;
        self.snippet = snippet;
        self.apiHelper = ApiHelper.getInstance();
        self.apiFunction = apiFunction;

        self.fetchedData = ko.observable();
        self.loading = ko.observable(false);
        self.hasErrors = ko.observable(false);
      }

      TableAndColumnTabContents.prototype.formatAnalysisValue = function (type, val) {
        if (type === 'last_modified_time' || type === 'transient_lastDdlTime') {
          return localeFormat(val * 1000);
        }
        if (type.toLowerCase().indexOf('size') > -1) {
          return filesize(val);
        }
        return val;
      };

      TableAndColumnTabContents.prototype.fetch = function (callback) {
        var self = this;
        if (self.loading()) {
          return;
        }
        self.loading(true);
        self.hasErrors(false);

        self.apiFunction.bind(self.apiHelper)({
          sourceType: self.snippet.type(),
          identifierChain: self.identifierChain,
          defaultDatabase: self.snippet.database(),
          silenceErrors: true,
          successCallback: function (data) {
            if (typeof data.extended_columns !== 'undefined') {
              data.extended_columns.forEach(function (column) {
                column.extendedType = column.type.replace(/</g, '&lt;').replace(/>/g, '&lt;');
                if (column.type.indexOf('<') !== -1) {
                  column.type = column.type.substring(0, column.type.indexOf('<'));
                }
              });
            }
            self.fetchedData(data);
            self.loading(false);
            if (typeof callback === 'function') {
              callback(data);
            }
          },
          errorCallback: function () {
            self.loading(false);
            self.hasErrors(true);
          }
        });
      };

      function TableAndColumnContextTabs(data, snippet, isColumn) {
        var self = this;
        self.tabs = ko.observableArray();

        var apiHelper = ApiHelper.getInstance();

        self.details = new TableAndColumnTabContents(data.identifierChain, snippet, apiHelper.fetchAutocomplete);
        self.sample = new TableAndColumnTabContents(data.identifierChain, snippet, apiHelper.fetchSamples);
        self.analysis = new TableAndColumnTabContents(data.identifierChain, snippet, apiHelper.fetchAnalysis);
        self.partitions = new TableAndColumnTabContents(data.identifierChain, snippet, apiHelper.fetchPartitions);

        self.activeTab = ko.observable('details');

        self.tabs.push({
          id: 'details',
          label: '${ _("Details") }',
          template: isColumn ? 'sql-context-column-details' : 'sql-context-table-details',
          templateData: self.details,
          errorText: '${ _("There was a problem loading the details.") }',
          isColumn: isColumn
        });

        self.tabs.push({
          id: 'sample',
          label: '${ _("Sample") }',
          template: 'sql-context-table-and-column-sample',
          templateData: self.sample,
          errorText: '${ _("There was a problem loading the samples.") }',
          isColumn: isColumn
        });

        self.details.fetch(function (data) {
          if (isColumn || data.partition_keys.length === 0) {
            self.tabs.push({
              id: 'analysis',
              label: '${ _("Analysis") }',
              template: isColumn ? 'sql-context-column-analysis' : 'sql-context-table-analysis',
              templateData: self.analysis,
              errorText: '${ _("There was a problem loading the analysis.") }',
              isColumn: isColumn
            });
          } else if (!isColumn && data.partition_keys.length > 0) {
            self.tabs.push({
              id: 'partitions',
              label: '${ _("Partitions") }',
              template: 'sql-context-table-partitions',
              templateData: self.partitions,
              errorText: '${ _("There was a problem loading the partitions.") }',
              isColumn: isColumn
            });
          }
        });

        self.activeTab.subscribe(function (newValue) {
          if (newValue === 'sample' && typeof self.sample.fetchedData() === 'undefined') {
            self.sample.fetch(self.initializeSamplesTable);
          } else if (newValue === 'analysis' && typeof self.analysis.fetchedData() === 'undefined') {
            self.analysis.fetch();
          } else if (newValue === 'partitions' && typeof self.partitions.fetchedData() === 'undefined') {
            self.partitions.fetch();
          }
        });

        var samplesInterval = window.setInterval(function () {
          if (self.activeTab() !== 'sample') {
            return;
          }
          var $t = $('.samples-table');
          if ($t.length === 0) {
            return;
          }

          if ($t.data('plugin_jHueTableExtender')) {
            $t.data('plugin_jHueTableExtender').drawHeader();
            $t.data('plugin_jHueTableExtender').drawFirstColumn();
          }
          $t.parents('.dataTables_wrapper').getNiceScroll().resize();
        }, 300);

        var performScrollToColumn = function (colName) {
          self.activeTab('sample');
          window.setTimeout(function () {
            var _t = $('.samples-table');
            var _col = _t.find("th").filter(function () {
              return $.trim($(this).text()).endsWith(colName);
            });
            _t.find(".columnSelected").removeClass("columnSelected");
            var _colSel = _t.find("tr th:nth-child(" + (_col.index() + 1) + ")");
            if (_colSel.length > 0) {
              _t.find("tr td:nth-child(" + (_col.index() + 1) + ")").addClass("columnSelected");
              _t.parent().animate({
                scrollLeft: _colSel.position().left + _t.parent().scrollLeft() - _t.parent().offset().left - 30
              }, 300, function(){
                _t.data('scrollToCol', _col.index());
                _t.data('scrollToRow', null);
                _t.data('scrollAnimate', true);
                _t.parent().trigger('scroll');
              });
            }
          }, 0);
        };

        var scrollToSubscription = huePubSub.subscribe('sql.context.popover.scroll.to.column', function (colName) {
          if (typeof self.sample.fetchedData() === 'undefined') {
            self.sample.fetch(function (data) {
              self.initializeSamplesTable(data);
              window.setTimeout(function () {
                performScrollToColumn(colName);
              }, 0);
            });
          } else {
            performScrollToColumn(colName);
          }
        });

        var showInAssistSubscription = huePubSub.subscribe('sql.context.popover.show.in.assist', function () {
          huePubSub.publish('assist.db.highlight', {
            sourceType: snippet.type(),
            path: apiHelper.identifierChainToPath(data.identifierChain, snippet.database())
          });
          huePubSub.publish('sql.context.popover.hide')
        });

        var openInMetastoreSubscription = huePubSub.subscribe('sql.context.popover.open.in.metastore', function () {
          window.open('/metastore/table/' + apiHelper.identifierChainToPath(data.identifierChain, snippet.database()).join('/'), '_blank');
        });

        var disposeSubscription = huePubSub.subscribe('sql.context.popover.dispose', function () {
          window.clearInterval(samplesInterval);
          disposeSubscription.remove();
          scrollToSubscription.remove();
          openInMetastoreSubscription.remove();
          showInAssistSubscription.remove();
        });
      }

      TableAndColumnContextTabs.prototype.initializeSamplesTable = function (data) {
        window.setTimeout(function () {
          var $t = $('.samples-table');

          if ($t.parent().hasClass('dataTables_wrapper')) {
            if ($t.parent().data('scrollFnDt')) {
              $t.parent().off('scroll', $t.parent().data('scrollFnDt'));
            }
            $t.unwrap();
            if ($t.children('tbody').length > 0) {
              $t.children('tbody').empty();
            }
            else {
              $t.children('tr').remove();
            }
            $t.data('isScrollAttached', null);
            $t.data('data', []);
          }
          var dt = $t.hueDataTable({
            i18n: {
              NO_RESULTS: "${_('No results found.')}",
              OF: "${_('of')}"
            },
            fnDrawCallback: function (oSettings) {
            },
            scrollable: '.dataTables_wrapper',
            forceInvisible: 10
          });

          $t.parents('.dataTables_wrapper').height(350);

          $t.jHueTableExtender({
            fixedHeader: true,
            fixedFirstColumn: true,
            fixedFirstColumnTopMargin: -1,
            headerSorting: false,
            includeNavigator: false,
            parentId: 'sampleTab',
            classToRemove: 'samples-table',
            clonedContainerPosition: 'fixed'
          });

          $t.parents('.dataTables_wrapper').niceScroll({
            cursorcolor: "#CCC",
            cursorborder: "1px solid #CCC",
            cursoropacitymin: 0,
            cursoropacitymax: 0.75,
            scrollspeed: 100,
            mousescrollstep: 60,
            cursorminheight: 20,
            horizrailenabled: true
          });

          if (data && data.rows) {
            var _tempData = [];
            $.each(data.rows, function (index, row) {
              var _row = row.slice(0); // need to clone the array otherwise it messes with the caches
              _row.unshift(index + 1);
              _tempData.push(_row);
            });
            if (_tempData.length > 0) {
              dt.fnAddData(_tempData);
            }
          }
        }, 0);
      };

      function FunctionContextTabs(data, snippet) {
        var self = this;
        self.func = ko.observable({
          details: sqlFunctions.findFunction(snippet.type(), data.function),
          loading: ko.observable(false),
          hasErrors: ko.observable(false)
        });

        self.tabs = [
          { id: 'details', label: '${ _("Details") }', template: 'sql-context-function-details', templateData: self.func }
        ];
        self.activeTab = ko.observable('details');
      }

      function SqlContextPopoverViewModel(params) {
        var self = this;
        self.left = ko.observable();
        self.top = ko.observable();
        self.data = params.data;
        self.snippet = params.snippet;
        self.close = hidePopover;
        var orientation = params.orientation || 'bottom';
        self.contents = null;

        switch (orientation) {
          case 'left':
            break;
          case 'top':
            self.left(params.source.left + Math.round((params.source.right - params.source.left) / 2) - 225);
            self.top(params.source.top - 300);
            break;
          case 'right':
            break;
          case 'bottom':
            self.left(params.source.left + Math.round((params.source.right - params.source.left) / 2) - 225);
            self.top(params.source.bottom);
        }

        self.isTable = params.data.type === 'table';
        self.isColumn = params.data.type === 'column';
        self.isFunction = params.data.type === 'function';

        if (self.isTable) {
          self.contents = new TableAndColumnContextTabs(self.data, self.snippet, false);
          self.title = self.data.identifierChain[self.data.identifierChain.length - 1].name;
          self.iconClass = 'fa-table'
        } else if (self.isColumn) {
          self.contents = new TableAndColumnContextTabs(self.data, self.snippet, true);
          self.title = self.data.identifierChain[self.data.identifierChain.length - 1].name;
          self.iconClass = 'fa-columns'
        } else if (self.isFunction) {
          self.contents = new FunctionContextTabs(self.data, self.snippet);
          self.title = self.data.function;
          self.iconClass = 'fa-superscript'
        } else {
          self.title = '';
          self.iconClass = 'fa-info'
        }
        self.orientationClass = 'sql-context-popover-' + orientation;
      }

      SqlContextPopoverViewModel.prototype.dispose = function () {
        hidePopover();
      };

      ko.components.register('sql-context-popover', {
        viewModel: SqlContextPopoverViewModel,
        template: { element: 'sql-context-popover-template' }
      });

      huePubSub.subscribe('sql.context.popover.hide', hidePopover);

      huePubSub.subscribe('sql.context.popover.show', function (details) {
        hidePopover();
        var $sqlContextPopover = $('<div id="sqlContextPopover" data-bind="component: { name: \'sql-context-popover\', params: $data }" />');
        $('body').append($sqlContextPopover);
        ko.applyBindings(details, $sqlContextPopover[0]);
        huePubSub.publish('sql.context.popover.shown');
        window.setTimeout(function() {
          $(document).on('click', hideOnClickOutside);
        }, 0);
      });


      function SqlColumnsTable(params) {
        var self = this;

        var columns = params.columns;

        self.searchInput = ko.observable('');
        self.searchVisible = ko.observable(false);
        self.searchFocus = ko.observable(false);

        self.searchVisible.subscribe(function (newValue) {
          if (newValue) {
            self.searchFocus(true);
          }
        });

        self.filteredColumns = ko.pureComputed(function () {
          if (self.searchInput() === '') {
            return columns;
          }
          var query = self.searchInput();
          return columns.filter(function (column) {
            return column.name.indexOf(query) !== -1 || column.comment.indexOf(query) !== -1;
          })
        });
      }

      ko.components.register('sql-columns-table', {
        viewModel: SqlColumnsTable,
        template: { element: 'sql-columns-table-template' }
      });
    });
  </script>
</%def>