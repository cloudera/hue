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
from django.utils.html import escape
from desktop import conf
from desktop.lib.i18n import smart_unicode
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>

<%namespace name="components" file="components.mako" />
<%namespace name="assist" file="/assist.mako" />
<%namespace name="tableStats" file="/table_stats.mako" />
<%namespace name="require" file="/require.mako" />

<%
  if table.is_view:
    view_or_table_noun = _("View")
  else:
    view_or_table_noun = _("Table")
%>

${ commonheader(_("%s : %s") % (view_or_table_noun, table.name), app_name, user) | n,unicode }
${ components.menubar() }

${ require.config() }

${ tableStats.tableStats() }
${ assist.assistPanel() }

<link rel="stylesheet" href="${ static('desktop/ext/css/bootstrap-editable.css') }">
<link rel="stylesheet" href="${ static('metastore/css/metastore.css') }" type="text/css">
<link rel="stylesheet" href="${ static('notebook/css/notebook.css') }">
<style type="text/css">
% if conf.CUSTOM.BANNER_TOP_HTML.get():
  .show-assist {
    top: 110px!important;
  }
  .main-content {
    top: 112px!important;
  }
% endif
</style>

<script src="${ static('desktop/ext/js/bootstrap-editable.min.js') }" type="text/javascript" charset="utf-8"></script>
<script src="${ static('desktop/ext/js/d3.v3.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/html" id="metastore-breadcrumbs">
  <ul class="nav nav-pills hueBreadcrumbBar" id="breadcrumbs">
    <li>
      <i class="fa fa-th muted"></i>
    </li>
    <li>
      <a href="${url('metastore:databases')}">${_('Databases')}</a><span class="divider">&gt;</span>
    </li>
    <li>
      <a data-bind="text: activeDatabase, attr: { href: '/metastore/tables/' + activeDatabase() }"></a><span class="divider">&gt;</span>
    </li>
    <li>
      <span style="padding-left:12px" data-bind="text: activeTable"></span>
    </li>
  </ul>
</script>

<script type="text/html" id="metastore-columns-table">
  <table class="table table-striped table-condensed sampleTable">
    <thead>
    <tr>
      <th width="1%">&nbsp;</th>
      ## no stats for partition key type
      <th width="1%" class="no-sort">&nbsp;</th>
      <th width="1%">&nbsp;</th>
      <th>${_('Name')}</th>
      <th>${_('Type')}</th>
      <th>${_('Comment')}</th>
    </tr>
    </thead>
    <tbody data-bind="foreach: $data">
      <tr>
        ## start at 0
        <td data-bind="text: $index()"></td>
        ## no stats for partition key type
        <td>
         <span class="blue" data-bind="component: { name: 'table-stats', params: {
            alwaysActive: true,
            statsVisible: true,
            sourceType: 'hive',
            databaseName: $root.activeDatabase(),
            tableName: $root.activeTable(),
            columnName: name,
            fieldType: type,
            assistHelper: $root.assistHelper
          } }"></span>
        </td>
        <td class="pointer" data-bind="click: function() { favourite(!favourite()) }"><i style="color: #338bb8" class="fa" data-bind="css: {'fa-star': favourite, 'fa-star-o': !favourite() }"></i></td>
        <td title="${ _("Scroll to the column") }">
          <a href="javascript:void(0)" class="column-selector" data-bind="text: name"></a>
        </td>
        <td data-bind="text: type"></td>
        <td>
          <span data-bind="editable: comment, editableOptions: {enabled: true, placement: 'left', emptytext: 'Add a comment...' }" class="editable editable-click editable-empty">Add a comment...</span>
        </td>
      </tr>
    </tbody>
  </table>
</script>

<%def name="partition_column_table(cols, id, withStats=False, limit=10000)">
  <table id="${id}" class="table table-striped table-condensed sampleTable
  %if withStats:
  skip-extender
  %endif
  ">
    <thead>
      <tr>
        <th width="1%">&nbsp;</th>
        %if withStats:
          <th width="1%" class="no-sort">&nbsp;</th>
        %endif
        <th>${_('Name')}</th>
        <th>${_('Type')}</th>
      </tr>
    </thead>
    <tbody>
      % for column in cols[:limit]:
        <tr>
          <td>${ loop.index }</td>
          %if withStats:
            <td class="row-selector-exclude">
              <a href="javascript:void(0)" data-column="${ column.name }">
                <i class="fa fa-bar-chart" title="${ _('View statistics') }"></i>
              </a>
            </td>
          %endif
          <td title="${ _("Scroll to the column") }">
            <a href="javascript:void(0)" data-row-selector="true" class="column-selector">${ column.name }</a>
          </td>
          <td>${ column.type }</td>
        </tr>
      % endfor
    </tbody>
  </table>
</%def>

<script type="text/html" id="metastore-samples-table">
  <div style="overflow: auto">
    <table id="sampleTable" class="table table-striped table-condensed sampleTable">
      <tr>
        <th style="width: 10px"></th>
        <!-- ko foreach: headers -->
        <th data-bind="text: $data"></th>
        <!-- /ko -->
      </tr>
      <tbody>
        <!-- ko foreach: rows -->
          <tr>
            <td data-bind="text: $index"></td>
            <!-- ko foreach: $data -->
              <td data-bind="text: $data"></td>
            <!-- /ko -->
          </tr>
        <!-- /ko -->
      </tbody>
    </table>
  </div>

  <div id="jumpToColumnAlert" class="alert hide" style="margin-top: 12px;">
    <button type="button" class="close" data-dismiss="alert">&times;</button>
    <strong>${_('Did you know?')}</strong>
    <ul>
      <li>${ _('If the sample contains a large number of columns, click a row to select a column to jump to') }</li>
    </ul>
  </div>
</script>

<script type="text/html" id="metastore-table-stats">
  <!-- ko with: tableDetails -->
  <h4>${ _('Stats') }
    <!-- ko if: $root.refreshingTableStats -->
    <i class="fa fa-refresh fa-spin"></i>
    <!-- /ko -->
    <!-- ko ifnot: $root.refreshingTableStats -->
    <a class="pointer" href="javascript: void(0);" data-bind="click: $root.refreshTableStats"><i class="fa fa-refresh"></i></a>
    <!-- /ko -->
    <span data-bind="visible: ! details.stats.COLUMN_STATS_ACCURATE" rel="tooltip" data-placement="top" title="${ _('The column stats for this table are not accurate') }"><i class="fa fa-exclamation-triangle"></i></span>
  </h4>
  <div class="row-fluid">
    <div class="span6">
      <div title="${ _('Owner') }">
        <a data-bind="{attr: { 'href': '/useradmin/users/view/' + details.properties.owner } }">
          <i class="fa fa-fw fa-user muted"></i> <span data-bind="text: details.properties.owner"></span>
        </a>
      </div>
      <div title="${ _('Created') }"><i class="fa fa-fw fa-clock-o muted"></i> <span data-bind="text: details.properties.create_time"></span></div>
      <div title="${ _('Format') }"><i class="fa fa-fw fa-file-o muted"></i> <span data-bind="text: details.properties.format"></span></div>
      <div title="${ _('Compressed?') }"><i class="fa fa-fw fa-archive muted"></i> <span data-bind="visible: details.properties.compressed" style="display:none;">${_('Compressed')}</span><span data-bind="visible: !details.stats.compressed" style="display:none;">${_('Not compressed')}</span></div>
    </div>

    <div class="span6">
      <div><a data-bind="attr: {'href': hdfs_link, 'rel': path_location }"><i class="fa fa-fw fa-hdd-o"></i> ${_('Location')}</a></div>
      <!-- ko with: $root.tableStats -->
      <div title="${ _('Number of files') }"><i class="fa fa-fw fa-files-o muted"></i> <span data-bind="text: numFiles"></span></div>
      <div title="${ _('Number of rows') }"><i class="fa fa-fw fa-list muted"></i> <span data-bind="text: numRows"></span></div>
      <div title="${ _('Total size') }"><i class="fa fa-fw fa-tasks muted"></i> <span data-bind="text: totalSize"></span></div>
      <!-- /ko -->
    </div>
  </div>
  <!-- /ko -->
</script>

<a title="${_('Toggle Assist')}" class="pointer show-assist" data-bind="visible: !$root.isLeftPanelVisible() && $root.assistAvailable(), click: function() { $root.isLeftPanelVisible(true); }">
  <i class="fa fa-chevron-right"></i>
</a>

<div class="main-content">
  <div class="vertical-full container-fluid">
    <div class="vertical-full">
      <div class="vertical-full row-fluid panel-container">

        <div class="assist-container left-panel" data-bind="visible: $root.isLeftPanelVisible() && $root.assistAvailable()">
          <a title="${_('Toggle Assist')}" class="pointer hide-assist" data-bind="click: function() { $root.isLeftPanelVisible(false) }">
            <i class="fa fa-chevron-left"></i>
          </a>
          <div class="assist" data-bind="component: {
              name: 'assist-panel',
              params: {
                sourceTypes: [{
                  name: 'hive',
                  type: 'hive'
                }],
                user: '${user.username}',
                navigationSettings: {
                  openItem: true,
                  showPreview: true,
                  showStats: false
                }
              }
            }"></div>
        </div>
        <div class="resizer" data-bind="visible: $root.isLeftPanelVisible() && $root.assistAvailable(), splitDraggable : { appName: 'notebook', leftPanelVisible: $root.isLeftPanelVisible }"><div class="resize-bar">&nbsp;</div></div>
        <div class="right-panel">

          <div class="metastore-main">
            <h3>
              <ul class="nav nav-pills pull-right" style="margin-top: -8px">
                <li><a class="pointer"><i class="fa fa-star"></i></a></li>
                <li><a href="#" id="import-data-btn" title="${_('Import Data')}"><i class="fa fa-arrow-circle-o-down"></i></a></li>
                <li><a href="${ url('metastore:read_table', database=database, table=table.name) }" title="${_('Browse Data')}"><i class="fa fa-list"></i></a></li>
                % if has_write_access:
                  <li><a href="#dropTable" data-toggle="modal" title="${_('Drop')} ${view_or_table_noun}"><i class="fa fa-times"></i></a></li>
                % endif
                <li><a href="${ table.hdfs_link }" rel="${ table.path_location }" title="${_('View File Location')}"><i class="fa fa-share-square-o"></i></a></li>
                % if table.partition_keys:
                  <li><a href="${ url('metastore:describe_partitions', database=database, table=table.name) }" title="${_('Show Partitions')} (${ len(partitions) })"><i class="fa fa-sitemap"></i></a></li>
                % endif
              </ul>
              <!-- ko template: 'metastore-breadcrumbs' --><!-- /ko -->
            </h3>
            <div class="clearfix"></div>

            <span data-bind="editable: tableComment, editableOptions: {enabled: true, placement: 'right', emptytext: 'Add a description...' }" class="editable editable-click editable-empty">Add a description...</span>

            <ul class="nav nav-pills margin-top-30">
              <li><a href="#overview" data-toggle="tab">${_('Overview')}</a></li>
              <li><a href="#columns" data-toggle="tab">${_('Columns')} (<span data-bind="text: columns().length"></span>)</a></li>
              % if table.partition_keys:
                <li><a href="#partitionColumns" data-toggle="tab">${_('Partition Columns')}</a></li>
              % endif
              % if sample is not None:
                <li><a href="#sample" data-toggle="tab">${_('Sample')}</a></li>
              % endif
              <li><a href="#permissions" data-toggle="tab">${_('Permissions')}</a></li>
              <li><a href="#queries" data-toggle="tab">${_('Queries')}</a></li>
              <li><a href="#analysis" data-toggle="tab">${_('Analyse')}</a></li>
              <li><a href="#lineage" data-toggle="tab">${_('Lineage')}</a></li>
              <li><a href="#properties" data-toggle="tab">${ _('Properties') }</a></li>
            </ul>

            <div class="tab-content margin-top-10" style="border: none">
              <div class="tab-pane" id="overview">

                <div class="row-fluid margin-top-10">
                  <div class="span6 tile">
                    <!-- ko template: 'metastore-table-stats' --><!-- /ko -->
                  </div>

                  <div class="span2 tile">
                    <h4>${ _('Sharing') }</h4>
                    <div title="${ _('Tags') }"><i class="fa fa-fw fa-tags muted"></i> ${ _('No tags') }</div>
                    <div title="${ _('Users') }"><i class="fa fa-fw fa-users muted"></i> ${ _('No users') }</div>
                  </div>

                  <div class="span4 tile">
                    <h4>${ _('Comments') }</h4>
                    <div>
                      <i class="fa fa-fw fa-comments-o muted"></i> ${ _('No comments available yet.') }
                    </div>
                  </div>
                </div>

                <div class="tile">
                  <h4>${ _('Starred columns') } (<span data-bind="text: favouriteColumns().length"></span>)</h4>
                  <!-- ko with: favouriteColumns -->
                  <!-- ko template: "metastore-columns-table" --><!-- /ko -->
                  <!-- /ko -->

                  <a class="pointer" data-bind="click: function() { $('li a[href=\'#columns\']').click(); }">${_('View more...')}</a>
                </div>

                <div class="tile">
                  <h4>${ _('Sample') }</h4>
                  % if sample:
                    <!-- ko with: samplesPreview -->
                    <!-- ko template: 'metastore-samples-table' --><!-- /ko -->
                    <!-- /ko -->
                    <a class="pointer" data-bind="click: function() { $('li a[href=\'#sample\']').click(); }">${_('View more...')}</a>
                  % else:
                    ${ _('Table sampling took too long.') }
                  % endif
                </div>

                % if table.partition_keys:
                <div class="tile">
                  <h4>${ _('Partitions') }</h4>
                    ${ partition_column_table(table.partition_keys, "partitionTable", limit=3) }
                    <a class="pointer" data-bind="click: function() { $('li a[href=\'#partitionColumns\']').click(); }">${_('View more...')}</a>
                </div>
                % endif
              </div>

              <div class="tab-pane" id="columns">
                <!-- ko with: columns -->
                <!-- ko template: "metastore-columns-table" --><!-- /ko -->
                <!-- /ko -->
              </div>

              % if table.partition_keys:
              <div class="tab-pane" id="partitionColumns">
                ${ partition_column_table(table.partition_keys, "partitionTable") }
              </div>
              % endif

              % if sample is not None:
              <div class="tab-pane" id="sample">
              % if error_message:
                <div class="alert alert-error">
                  <h3>${_('Error!')}</h3>
                  <pre>${ error_message }</pre>
                </div>
              % else:
                <!-- ko with: samples -->
                <!-- ko template: 'metastore-samples-table' --><!-- /ko -->
                <!-- /ko -->
              % endif
              </div>
              % endif

              <div class="tab-pane" id="permissions">
                ${ _('Not available') }
              </div>

              <div class="tab-pane" id="queries">
                <i class="fa fa-spinner fa-spin" data-bind="visible: loadingQueries"></i>
                <table data-bind="visible: !loadingQueries()" class="table table-condensed">
                  <thead>
                    <tr>
                      <th width="20%">${ _('Name') }</th>
                      <th>${ _('Query') }</th>
                      <th width="20%">${ _('Owner') }</th>
                    </tr>
                  </thead>
                  <tbody data-bind="foreach: queries">
                    <tr class="pointer" data-bind="click: function(){ location.href=doc.absoluteUrl; }">
                      <td data-bind="text: doc.name"></td>
                      <td><code data-bind="text: data.snippets[0].statement_raw"></code></td>
                      <td><code data-bind="text: doc.owner"></code></td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div class="tab-pane" id="analysis">
                ${ _('Not available') }
              </div>

              <div class="tab-pane" id="lineage">
                ${ _('Not available') }
              </div>

              <div class="tab-pane" id="properties">
                <table class="table table-striped table-condensed">
                  <thead>
                    <tr>
                      <th>${ _('Name') }</th>
                      <th>${ _('Value') }</th>
                      <th>${ _('Comment') }</th>
                    </tr>
                  </thead>
                  <tbody>
                    % for prop in table.properties:
                      <tr>
                        <td>${ smart_unicode(prop['col_name']) }</td>
                        <td>${ smart_unicode(prop['data_type']) if prop['data_type'] else '' }</td>
                        <td>${ smart_unicode(prop['comment']) if prop['comment'] else '' }&nbsp;</td>
                      </tr>
                     % endfor
                  </tbody>
                </table>
              </div>
            </div>

          </div>

        </div>
    </div>
  </div>
</div>



<div id="dropTable" class="modal hide fade">
  <form id="dropTableForm" method="POST" action="${ url('metastore:drop_table', database=database) }">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>

      <h3>${_('Drop Table')}</h3>
    </div>
    <div class="modal-body">
      <div id="dropTableMessage">
      </div>
    </div>
    <div class="modal-footer">
      <input type="button" class="btn" data-dismiss="modal" value="${_('Cancel')}"/>
      <input type="submit" class="btn btn-danger" value="${_('Yes, drop this table')}"/>
    </div>
    <div class="hide">
      <select name="table_selection">
        <option value="${ table.name }" selected>${ table.name }</option>
      </select>
    </div>
  </form>
</div>

<div id="import-data-modal" class="modal hide fade"></div>
</div>

<div id="columnAnalysis" class="popover mega-popover right">
  <div class="arrow"></div>
  <h3 class="popover-title" style="text-align: left">
    <a class="pull-right pointer close-popover" style="margin-left: 8px"><i class="fa fa-times"></i></a>
    <a class="pull-right pointer stats-refresh" style="margin-left: 8px"><i class="fa fa-refresh"></i></a>
    <strong class="column-name"></strong> ${ _(' column analysis') }
  </h3>
  <div class="popover-content">
    <div class="pull-right hide filter">
      <input id="columnAnalysisTermsFilter" type="text" placeholder="${ _('Prefix filter...') }"/>
    </div>
    <ul class="nav nav-tabs" role="tablist">
      <li class="active"><a href="#columnAnalysisStats" role="tab" data-toggle="tab">${ _('Stats') }</a></li>
      <li><a href="#columnAnalysisTerms" role="tab" data-toggle="tab">${ _('Terms') }</a></li>
    </ul>
    <div class="tab-content">
      <div class="tab-pane active" id="columnAnalysisStats" style="text-align: left">
        <div class="content"></div>
      </div>
      <div class="tab-pane" id="columnAnalysisTerms" style="text-align: left">
        <div class="alert">${ _('There are no terms to be shown') }</div>
        <div class="content"></div>
      </div>
    </div>
  </div>
</div>

<script src="${ static('beeswax/js/stats.utils.js') }"></script>

<script type="text/javascript" charset="utf-8">

  var STATS_PROBLEMS = "${ _('There was a problem loading the stats.') }";

  require([
    "knockout",
    "ko.charts",
    "desktop/js/assist/assistHelper",
    "assistPanel",
    "tableStats",
    "knockout-mapping",
    "knockout-sortable",
    "knockout-deferred-updates",
    "ko.editable",
    "ko.hue-bindings"
  ], function (ko, charts, AssistHelper) {

    function MetastoreColumn(vm, extendedColumn) {
      var self = this;
      self.vm = vm;
      ko.mapping.fromJS(extendedColumn, {}, self);

      self.favourite = ko.observable(false);

      self.comment.subscribe(function (newValue) {
        $.post("${ url('metastore:alter_column', database=database, table=table.name) }", {
          column: self.name(),
          comment: newValue
        }, function () {
          self.vm.assistHelper.clearCache({
            sourceType: 'hive',
            databaseName: self.vm.activeDatabase(),
            tableName: self.vm.activeTable(),
            fields: []
          })
        });
      })
    }

    /**
     * @param {Object} options
     * @param {Object} options.i18n
     * @param {string} options.i18n.errorLoadingDatabases
     * @param {string} options.i18n.errorLoadingTablePreview
     * @param {string} options.user
     * @constructor
     */
    function MetastoreViewModel(options) {
      var self = this;
      self.assistAvailable = ko.observable(true);
      self.isLeftPanelVisible = ko.observable(self.assistAvailable() && $.totalStorage('spark_left_panel_visible') != null && $.totalStorage('spark_left_panel_visible'));

      self.activeDatabase = ko.observable('${database}');
      self.activeTable = ko.observable('${table.name}');
      self.tableComment = ko.observable();

      %if table.comment:
      self.tableComment('${ smart_unicode(table.comment) }');
      %endif

      self.tableComment.subscribe(function (newValue) {
        $.post("${ url('metastore:alter_table', database=database, table=table.name) }", {
          comment: newValue ? newValue : ""
        });
      })
      self.assistHelper = new AssistHelper(options)

      self.columns = ko.observableArray();
      self.favouriteColumns = ko.observableArray();
      self.samplesPreview = ko.observable();
      self.samples = ko.observable();
      self.tableDetails = ko.observable();
      self.tableStats = ko.observable();
      self.refreshingTableStats = ko.observable(false);

      var fetchColumns = function () {
        self.assistHelper.fetchFields({
          sourceType: "hive",
          databaseName: self.activeDatabase(),
          tableName: self.activeTable(),
          fields: [],
          successCallback: function (data) {
            self.columns($.map(data.extended_columns, function (column) { return new MetastoreColumn(self, column) }));
            self.favouriteColumns(self.columns().slice(0, 3));
          },
          errorCallback: function (data) {
            console.log('ERRRROR!');
            console.log(data);
          }
        })
      }

      var fetchTableSample = function () {
        self.assistHelper.fetchTableSample({
          sourceType: "hive",
          databaseName: self.activeDatabase(),
          tableName: self.activeTable(),
          dataType: "json",
          successCallback: function (data) {
            self.samples(data);
            self.samplesPreview({
              headers: self.samples().headers,
              rows: self.samples().rows.slice(0, 3)
            });
          },
          errorCallback: function (data) {
            console.log('ERRRROR!');
            console.log(data);
          }
        })
      }

      var fetchDetails = function () {
        self.assistHelper.fetchTableDetails({
          sourceType: "hive",
          databaseName: self.activeDatabase(),
          tableName: self.activeTable(),
          successCallback: function (data) {
            self.tableDetails(data);
            self.tableStats(data.details.stats);
            self.refreshingTableStats(false);
          },
          errorCallback: function (data) {
            self.refreshingTableStats(false);
            console.log('ERRRROR!');
            console.log(data);
          }
        })
      }

      self.initialize = function () {
        fetchColumns();
        fetchTableSample();
        fetchDetails();
      }

      self.initialize();

      huePubSub.subscribe("assist.table.selected", function (tableDef) {
        self.activeDatabase(tableDef.database);
        self.activeTable(tableDef.name)
        self.initialize();
      });

      huePubSub.subscribe("assist.database.selected", function (databaseDef) {
        console.log(databaseDef);
      });

      self.refreshTableStats = function () {
        if (self.refreshingTableStats()) {
          return;
        }
        self.refreshingTableStats(true);
        self.assistHelper.refreshTableStats({
          tableName: self.activeTable(),
          databaseName: self.activeDatabase(),
          sourceType: "hive",
          successCallback: function (data) {
            fetchDetails();
          },
          errorCallback: function (data) {
            self.refreshingTableStats(false);
            console.log('ERRRROR!');
            console.log(data);
          }
        })
      }

      self.isLeftPanelVisible.subscribe(function(newValue) {
        $.totalStorage('spark_left_panel_visible', newValue);
      });

      self.loadingQueries = ko.observable(false);
      self.queries = ko.observableArray([]);
    }

    $(document).ready(function () {
      var options = {
        user: '${ user.username }',
        i18n : {
          errorLoadingDatabases: "${ _('There was a problem loading the databases') }",
          errorLoadingTablePreview: "${ _('There was a problem loading the table preview.') }"
        }
      }

      var viewModel = new MetastoreViewModel(options);

      ko.applyBindings(viewModel);

      $('a[data-toggle="tab"]').on('shown', function (e) {
        if ($(e.target).attr("href") == "#queries") {
          viewModel.loadingQueries(true);
          $.getJSON("${ url('metastore:table_queries', database=database, table=table.name) }", function (data) {
            viewModel.queries(data.queries);
            viewModel.loadingQueries(false);
          });
        }
      });

      window.hueDebug = {
        viewModel: viewModel,
        ko: ko
      };
    });
  });

  $(document).ready(function () {
    function selectColumn(col) {
      var _t = $("#sampleTable");
      var _col = _t.find("th").filter(function() {
        return $.trim($(this).text()).indexOf(col) > -1;
      });
      _t.find(".columnSelected").removeClass("columnSelected");
      _t.find("tr td:nth-child(" + (_col.index() + 1) + ")").addClass("columnSelected");
      $("a[href='#sample']").click();

    }

    $(".column-selector").on("click", function () {
      selectColumn($.trim($(this).text().split("(")[0]));
    });

    if (window.location.hash != "") {
      if (window.location.hash.indexOf("col=") > -1) {
        window.setTimeout(function(){
          selectColumn(window.location.hash.split("=")[1]);
        }, 200)
      }
    }

    % if has_write_access:
      $.getJSON("${ url('metastore:drop_table', database=database) }", function (data) {
        $("#dropTableMessage").text(data.title);
      });
    % endif

    $('a[data-toggle="tab"]').on('shown', function (e) {
      var sortables = [];
      $(".sampleTable").not('.initialized').each(function () {
        var _id = $(this).attr("id");
        if (sortables[_id] === undefined) {
          sortables[_id] = [];
        }
        $('#' + _id + ' thead th').each(function () {
          if ($(this).hasClass('no-sort')) {
            sortables[_id].push({
              "bSortable": false
            });
          } else {
            sortables[_id].push(null);
          }
        });
      });

      for (var id in sortables) {
        $("#" + id).addClass("initialized");
        % if len(table.cols) < 1000:
##         $("#" + id).dataTable({
##           "aoColumns": sortables[id],
##           "bPaginate": false,
##           "bLengthChange": false,
##           "bInfo": false,
##           "bFilter": false,
##           "bAutoWidth": false,
##           "fnInitComplete": function () {
##             $(this).parent().jHueTableScroller();
##             if (! $(this).hasClass("skip-extender")) {
##               $(this).jHueTableExtender({
##                 hintElement: "#jumpToColumnAlert",
##                 fixedHeader: true
##               });
##             }
##           },
##           "oLanguage": {
##             "sEmptyTable": "${_('No data available')}",
##             "sZeroRecords": "${_('No matching records')}"
##           }
##         });
        % endif
      }
      if ($(e.target).attr("href") == "#columnAnalysisTerms") {
        $("#columnAnalysis .filter").removeClass("hide");
      }
      if ($(e.target).attr("href") == "#columnAnalysisStats") {
        $("#columnAnalysis .filter").addClass("hide");
      }
    });

    $("#import-data-btn").click(function () {
      $.get("${ url('metastore:load_table', database=database, table=table.name) }", function (response) {
          $("#import-data-modal").html(response['data']);
          $("#import-data-modal").modal("show");
        }
      );
    });

    // convert link text to URLs in comment column (Columns tab)
    hueUtils.text2Url(document.querySelectorAll('.sampleTable td:last-child'));

    $('a[data-toggle="tab"]:eq(0)').click();

    $("a[data-column]").on("click", function () {
      var _link = $(this);
      var _col = _link.data("column");
      var statsUrl = "/beeswax/api/table/${database}/${table.name}/stats/" + _col;
      var refreshUrl = "/beeswax/api/analyze/${database}/${table.name}/" + _col;
      var termsUrl = "/beeswax/api/table/${database}/${table.name}/terms/" + _col + "/";
      $("#columnAnalysisStats .content").html("<i class='fa fa-spinner fa-spin'></i>");
      $("#columnAnalysis").show().css("top", _link.position().top - $("#columnAnalysis").outerHeight() / 2 + _link.outerHeight() / 2).css("left", _link.position().left + _link.outerWidth());
      showColumnStats(statsUrl, refreshUrl, termsUrl, _col, STATS_PROBLEMS, function () {
        $("#columnAnalysis").show().css("top", _link.position().top - $("#columnAnalysis").outerHeight() / 2 + _link.outerHeight() / 2).css("left", _link.position().left + _link.outerWidth());
      });
    });

    $(document).on("click", "#columnAnalysis .close-popover", function () {
      $("#columnAnalysis").hide();
    });

  });
</script>

${ commonfooter(messages) | n,unicode }
