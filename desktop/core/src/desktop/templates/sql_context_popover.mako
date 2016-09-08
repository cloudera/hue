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
      padding: 0 9px 14px 9px;
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
      margin-left: -10px;
      margin-right: -10px;
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
  </style>


  <script type="text/html" id="sql-context-table-details">
    <!-- ko with: fetchedData -->
      <div style="margin: 15px;" data-bind="foreach: extended_columns">
        <div>
          <a class="pointer" data-bind="text: name, attr: { title: comment }, click: function() { huePubSub.publish('sql.context.popover.scroll.to.column', name); }"></a> (<span data-bind="text: type.indexOf('<') !== -1 ? type.substring(0, type.indexOf('<')) : type, attr: { title: type }"></span>)
        </div>
      </div>
      <div style="clear: both; margin-top: 20px;">
        ${ _("Show in ") } <a class="pointer"  data-bind="click: function() { huePubSub.publish('sql.context.popover.show.in.assist') }">${ _("Assist") }</a><br />
        ${ _("Open in ") } <a class="pointer"  data-bind="click: function() { huePubSub.publish('sql.context.popover.open.in.metastore') }">${ _("Metastore") }</a>, <a class="pointer" data-bind="attr: { href: hdfs_link }" target="_blank">${ _("File Browser") }</a>
      </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="sql-context-column-details">
    <!-- ko with: fetchedData -->
    <div style="margin: 15px;">
      <div><a class="pointer" data-bind="text: name, attr: { title: comment }, click: function() { huePubSub.publish('sql.context.popover.scroll.to.column', name); }"></a> (<span data-bind="text: type.indexOf('<') !== -1 ? type.substring(0, type.indexOf('<')) : type, attr: { title: type }"></span>)</div>
      <div style="margin-top: 10px; font-weight: bold;">${ _("Comment") }</div>
      <div data-bind="text: comment"></div>
    </div>
    <div style="clear: both; margin-top: 20px;">
      ${ _("Show in ") } <a class="pointer"  data-bind="click: function() { huePubSub.publish('sql.context.popover.show.in.assist') }">${ _("Assist") }</a><br />
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="sql-context-table-and-column-sample">
    <!-- ko with: fetchedData -->
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
    <!-- /ko -->
  </script>

  <script type="text/html" id="sql-context-table-analysis">
    <!-- ko with: fetchedData -->
      <div class="content" data-bind="niceScroll">
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
    <!-- /ko -->
  </script>

  <script type="text/html" id="sql-context-column-analysis">
    <!-- ko with: fetchedData -->
      <div class="content" data-bind="niceScroll">
        <table class="table table-condensed">
          <tbody data-bind="foreach: stats">
            <tr>
              <th data-bind="text: Object.keys($data)[0], style:{'border-top-color': $index() == 0 ? '#ffffff' : '#e5e5e5'}" style="background-color: #FFF"></th>
              <td data-bind="text: $data[Object.keys($data)[0]], style:{'border-top-color': $index() == 0 ? '#ffffff' : '#e5e5e5'}" style="background-color: #FFF"></td>
            </tr>
          </tbody>
        </table>
      </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="sql-context-function-details">
    <div style="padding: 8px" data-bind="with: details">
      <p style="margin: 10px 10px 18px 10px;"><span style="white-space: pre; font-family: monospace;" data-bind="text: signature"></span></p>
      <p><span data-bind="text: description"></span></p>
    </div>
  </script>

  <script type="text/html" id="sql-context-popover-template">
    <div class="sql-context-popover sql-context-popover-bottom" data-bind="css: orientationClass, style: { left: left() + 'px', top: top() + 'px' }">
      <div class="sql-context-popover-arrow"></div>
      <div class="sql-context-popover-title">
        <i class="pull-left fa muted" data-bind="css: iconClass" style="margin-top: 3px"></i> <span data-bind="text: title"></span>
        <a class="pull-right pointer inactive-action" data-bind="click: close"><i class="fa fa-fw fa-times"></i></a>
        <a class="pull-right pointer inactive-action" data-bind="visible: isTable, click: function() { huePubSub.publish('sql.context.popover.open.in.metastore') }"><i style="margin-top: 3px;" title="${ _('Open in Metastore...') }" class="fa fa-fw fa-external-link"></i></a>
      </div>
      <div class="sql-context-popover-content">
        <!-- ko with: contents -->
        <ul class="nav nav-pills sql-context-tabs" data-bind="foreach: tabs">
          <li data-bind="click: function () { $parent.activeTab(id); }, css: { 'active' : $parent.activeTab() === id }">
            <a class="sql-context-tab" data-toggle="tab" data-bind="text: label, attr: { href: '#' + id }"></a>
          </li>
        </ul>
        <div class="tab-content" style="border: none; overflow: auto; height: 365px;" data-bind="foreach: tabs">
          <div class="tab-pane" id="sampleTab" data-bind="attr: { id: id }, css: { 'active' : $parent.activeTab() === id }" style="overflow: hidden">
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
        self.activeTab = ko.observable('details');

        self.tabs.push({
          id: 'details',
          label: '${ _("Details") }',
          template: isColumn ? 'sql-context-column-details' : 'sql-context-table-details',
          templateData: self.details,
          errorText: '${ _("There was a problem loading the details.") }'
        });

        self.tabs.push({
          id: 'sample',
          label: '${ _("Sample") }',
          template: 'sql-context-table-and-column-sample',
          templateData: self.sample,
          errorText: '${ _("There was a problem loading the samples.") }'
        });

        self.details.fetch(function (data) {
          if (isColumn || data.partition_keys.length === 0) {
            self.tabs.push({
              id: 'analysis',
              label: '${ _("Analysis") }',
              template: isColumn ? 'sql-context-column-analysis' : 'sql-context-table-analysis',
              templateData: self.analysis,
              errorText: '${ _("There was a problem loading the analysis.") }'
            });
          }
        });

        self.activeTab.subscribe(function (newValue) {
          if (newValue === 'sample' && typeof self.sample.fetchedData() === 'undefined') {
            self.sample.fetch(self.initializeSamplesTable);
          } else if (newValue === 'analysis' && typeof self.analysis.fetchedData() === 'undefined') {
            self.analysis.fetch();
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
        window.setTimeout(function() {
          $(document).on('click', hideOnClickOutside);
        }, 0);
      })
    });
  </script>
</%def>