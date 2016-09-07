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

  <script type="text/html" id="sql-context-table-sample">
    <!-- ko with: tableStats -->
    <!-- ko hueSpinner: { spin: loadingSamples, center: true, size: 'large' } --><!-- /ko -->
    <!-- ko ifnot: loadingSamples -->
    <div class="sample-scroll" style="text-align: left; padding: 3px; overflow: hidden">
      <!-- ko with: samples -->
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
      <!-- /ko -->
    </div>
    <!-- /ko -->
  </script>

  <script type="text/html" id="sql-context-table-analysis">
    <!-- ko with: tableStats -->
      <!-- ko hueSpinner: { spin: loadingStats, center: true, size: 'large' } --><!-- /ko -->
      <!-- ko ifnot: loadingStats -->
        <div class="alert" style="text-align: left; display:none" data-bind="visible: statsHasError">${ _('There is no table analysis available') }</div>
        <!-- ko ifnot: statsHasError -->
          <div class="content" data-bind="niceScroll">
            <!-- ko if: statRows().length -->
              <table class="table table-striped">
                <tbody data-bind="foreach: statRows">
                <tr><th data-bind="text: data_type, style:{'border-top-color': $index() == 0 ? '#ffffff' : '#e5e5e5'}" style="background-color: #FFF"></th><td data-bind="text: $parents[1].formatAnalysisValue(data_type, comment), style:{'border-top-color': $index() == 0 ? '#ffffff' : '#e5e5e5'}" style="background-color: #FFF"></td></tr>
                </tbody>
              </table>
            <!-- /ko -->
          </div>
        <!-- /ko -->
      <!-- /ko -->
    <!-- /ko -->
  </script>

  <script type="text/html" id="sql-context-column-sample">
    Column sample
  </script>

  <script type="text/html" id="sql-context-function-details">
    <div style="padding: 8px" data-bind="with: func">
      <p><span style="white-space: pre; font-family: monospace;" data-bind="text: signature"></span></p>
      <p><span data-bind="text: description"></span></p>
    <div>
  </script>

  <script type="text/html" id="sql-context-popover-template">
    <div class="sql-context-popover sql-context-popover-bottom" data-bind="css: orientationClass, style: { left: left() + 'px', top: top() + 'px' }">
      <div class="sql-context-popover-arrow"></div>
      <div class="sql-context-popover-title">
        <i class="pull-left fa muted" data-bind="css: iconClass" style="margin-top: 3px"></i> <span data-bind="text: title"></span>
        <a class="pull-right pointer inactive-action" data-bind="click: close"><i class="fa fa-fw fa-times"></i></a>
        <a class="pull-right pointer inactive-action" data-bind="visible: isTable, click: openInMetastore"><i style="margin-top: 3px;" title="${ _('Open in metastore...') }" class="fa fa-fw fa-external-link"></i></a>
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
            <!-- ko template: { name: template, data: $parent } --><!-- /ko -->
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

      var intervals = [];

      var hidePopover = function () {
        $('#sqlContextPopover').remove();
        $(document).off('click', hideOnClickOutside);
        intervals.forEach(function (interval) {
          window.clearInterval(interval);
        });
      };

      var hideOnClickOutside = function (event) {
        if (!$.contains($('#sqlContextPopover')[0], event.target)) {
          hidePopover();
        }
      };

      var i18n = {
        errorLoadingStats: "${ _('There was a problem loading the stats.') }",
        errorRefreshingStats: "${ _('There was a problem refreshing the stats.') }",
        errorLoadingTerms: "${ _('There was a problem loading the terms.') }"
      };

      function tableContextTabs(data, snippet) {
        var self = this;
        self.tabs = ko.observableArray([
          { id: 'sample', label: '${ _("Sample") }', template: 'sql-context-table-sample' }
        ]);
        self.activeTab = ko.observable('sample');

        var database = data.identifierChain.length > 1 ? data.identifierChain[0].name : snippet.database();
        var tableName = data.identifierChain[data.identifierChain.length - 1].name;

        self.tableStats = new TableStats({
          i18n: i18n,
          sourceType: snippet.type(),
          databaseName: database,
          tableName: tableName,
          apiHelper: ApiHelper.getInstance(),
          showViewMore: false
        });

        self.activeTab.subscribe(function (newValue) {
          self.tableStats.activeTab(newValue);
        });

        self.tableStats.showAnalysis.subscribe(function (newValue) {
          if (newValue && self.tabs().length === 1) {
            self.tabs.push({ id: 'analysis', label: '${ _("Analysis") }', template: 'sql-context-table-analysis' });
          }
        });

        self.formatAnalysisValue = function (type, val) {
          if (type === 'last_modified_time' || type === 'transient_lastDdlTime') {
            return localeFormat(val * 1000);
          }
          if (type.toLowerCase().indexOf('size') > -1) {
            return filesize(val);
          }
          return val;
        };

        self.loadingSamples = ko.observable(true);

        huePubSub.subscribe('sample.rendered', function (data) {
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
        });
      }

      function columnContextTabs(data) {
        var self = this;
        self.tabs = [
          { id: 'sample', label: '${ _("Sample") }', template: 'sql-context-column-sample' }
        ];
        self.activeTab = ko.observable('sample');
      }

      function functionContextTabs(data, snippet) {
        var self = this;
        self.tabs = [
          { id: 'details', label: '${ _("Details") }', template: 'sql-context-function-details' }
        ];
        self.activeTab = ko.observable('details');
        self.func = ko.observable(sqlFunctions.findFunction(snippet.type(), data.function));
      }

      function sqlContextPopoverViewModel(params) {
        var self = this;
        self.left = ko.observable();
        self.top = ko.observable();
        self.data = params.data;
        self.snippet = params.snippet;
        self.close = hidePopover;
        var orientation = params.orientation || 'bottom';
        self.contents = null;

        intervals.push(window.setInterval(function () {
          var $t = $('.samples-table');
          if ($t.length === 0) {
            return;
          }

          if ($t.data('plugin_jHueTableExtender')) {
            $t.data('plugin_jHueTableExtender').drawHeader();
            $t.data('plugin_jHueTableExtender').drawFirstColumn();
          }
          $t.parents('.dataTables_wrapper').getNiceScroll().resize();
        }, 300));

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
          self.contents = new tableContextTabs(self.data, self.snippet);
          self.title = self.data.identifierChain[self.data.identifierChain.length - 1].name;
          self.iconClass = 'fa-table'
        } else if (self.isColumn) {
          self.contents = new columnContextTabs(self.data);
          self.title = self.data.identifierChain[self.data.identifierChain.length - 1].name;
          self.iconClass = 'fa-columns'
        } else if (self.isFunction) {
          self.contents = new functionContextTabs(self.data, self.snippet);
          self.title = self.data.function;
          self.iconClass = 'fa-superscript'
        } else {
          self.title = '';
          self.iconClass = 'fa-info'
        }
        self.orientationClass = 'sql-context-popover-' + orientation;
      }

      sqlContextPopoverViewModel.prototype.dispose = function () {
        hidePopover();
      };

      sqlContextPopoverViewModel.prototype.openInMetastore = function () {
        var self = this;
        if (self.isTable) {
          if (self.data.identifierChain.length === 1) {
            window.open("/metastore/table/" + self.snippet.database() + "/" + self.data.identifierChain[0].name, '_blank');
          } else if (token.identifierChain.length === 2) {
            window.open("/metastore/table/" + self.data.identifierChain[0].name + '/' + self.data.identifierChain[1].name, '_blank');
          }
        }
      };

      ko.components.register('sql-context-popover', {
        viewModel: sqlContextPopoverViewModel,
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