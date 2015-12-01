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
from desktop.views import commonheader, commonfooter, _ko
from django.utils.translation import ugettext as _
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="components" file="components.mako" />
<%namespace name="assist" file="/assist.mako" />
<%namespace name="tableStats" file="/table_stats.mako" />
<%namespace name="require" file="/require.mako" />


${ commonheader(_('Tables'), 'metastore', user) | n,unicode }
${ components.menubar() }

${ require.config() }

${ tableStats.tableStats() }
${ assist.assistPanel() }


<script src="${ static('desktop/ext/js/d3.v3.js') }" type="text/javascript" charset="utf-8"></script>

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
                % if has_write_access:
                <li><a href="${ url('beeswax:import_wizard', database=database) }" title="${_('Create a new table from a file')}"><i class="fa fa-files-o"></i></a></li>
                <li><a href="${ url('beeswax:create_table', database=database) }" title="${_('Create a new table manually')}"><i class="fa fa-wrench"></i></a></li>
                % endif
              </ul>
              <ul class="nav nav-pills hueBreadcrumbBar" id="breadcrumbs">
                <li>
                  <i class="fa fa-th-list muted"></i>
                </li>
                <li>
                  <a href="${url('metastore:databases')}">${_('Databases')}</a><span class="divider">&gt;</span>
                </li>
                <li>
                  <span style="padding-left:12px">${database}</span>
                </li>
              </ul>
            </h3>

            <%actionbar:render>
              <%def name="search()">
                <div>
                  ## Also available in Ajax, so ko-ifable
                  ## ${ database_meta.get('comment') }
                  ## ${ database_meta.get('location') }
                  ## ${ database_meta.get('owner_name') }
                  ## ${ database_meta.get('owner_type') }
                  ## ${ database_meta.get('parameters') }
                </div>
                <form id="searchQueryForm" action="${ url('metastore:show_tables') }" method="GET" class="inline">
                  <input id="filterInput" type="text" name="filter" class="input-xlarge search-query" value="${ search_filter }" placeholder="${_('Search for table name')}" />
                </form>
              </%def>
              <%def name="actions()">
                <button id="viewBtn" class="btn toolbarBtn" title="${_('Browse the selected table')}" disabled="disabled"><i class="fa fa-eye"></i> ${_('View')}</button>
                <button id="browseBtn" class="btn toolbarBtn" title="${_('Browse the selected table')}" disabled="disabled"><i class="fa fa-list"></i> ${_('Browse Data')}</button>
                % if has_write_access:
                <button id="dropBtn" class="btn toolbarBtn" title="${_('Delete the selected tables')}" disabled="disabled"><i class="fa fa-trash-o"></i>  ${_('Drop')}</button>
                % endif
              </%def>
            </%actionbar:render>
              <table class="table table-condensed datatables" data-tablescroller-disable="true">
                <thead>
                  <tr>
                    <th width="1%"><div class="hueCheckbox selectAll fa" data-selectables="tableCheck"></div></th>
                    <th>&nbsp;</th>
                    <th>${_('Table Name')}</th>
                    <th>${_('Comment')}</th>
                    <th>${_('Type')}</th>
                  </tr>
                </thead>
                <tbody>
                % for table in tables:
                  <tr>
                    <td data-row-selector-exclude="true" width="1%">
                      <div class="hueCheckbox tableCheck fa"
                           data-view-url="${ url('metastore:describe_table', database=database, table=table['name']) }"
                           data-browse-url="${ url('metastore:read_table', database=database, table=table['name']) }"
                           data-drop-name="${ table['name'] }"
                           data-row-selector-exclude="true"></div>
                    </td>
                    <td class="row-selector-exclude"><a href="javascript:void(0)" data-table="${ table['name'] }"><i class="fa fa-bar-chart" title="${ _('View statistics') }"></i></a></td>
                    <td>
                      <a class="tableLink" href="${ url('metastore:describe_table', database=database, table=table['name']) }" data-row-selector="true">${ table['name'] }</a>
                    </td>
                    <td>${ smart_unicode(table['comment']) if table['comment'] else '' }</td>
                    <td>${ smart_unicode(table['type']) }</td>
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




<div id="tableAnalysis" class="popover mega-popover right">
  <div class="arrow"></div>
  <h3 class="popover-title" style="text-align: left">
    <a class="pull-right pointer close-popover" style="margin-left: 8px"><i class="fa fa-times"></i></a>
    <a class="pull-right pointer stats-refresh" style="margin-left: 8px"><i class="fa fa-refresh"></i></a>
    <span class="pull-right stats-warning muted" rel="tooltip" data-placement="top" title="${ _('The column stats for this table are not accurate') }" style="margin-left: 8px"><i class="fa fa-exclamation-triangle"></i></span>
    <strong class="table-name"></strong> ${ _(' table analysis') }
  </h3>
  <div class="popover-content">
    <div class="tab-pane active" id="tableAnalysisStats">
      <div class="content"></div>
    </div>
  </div>
</div>


<div id="dropTable" class="modal hide fade">
  <form id="dropTableForm" action="${ url('metastore:drop_table', database=database) }" method="POST">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3 id="dropTableMessage">${_('Confirm action')}</h3>
    </div>
    <div class="modal-footer">
      <input type="button" class="btn" data-dismiss="modal" value="${_('Cancel')}" />
      <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
    </div>
    <div class="hide">
      <select name="table_selection" data-bind="options: availableTables, selectedOptions: chosenTables" size="5" multiple="true"></select>
    </div>
  </form>
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

    function MetastoreViewModel(options) {
      var self = this;
      self.assistAvailable = ko.observable(true);
      self.isLeftPanelVisible = ko.observable(self.assistAvailable() && $.totalStorage('spark_left_panel_visible') != null && $.totalStorage('spark_left_panel_visible'));

      self.assistHelper = new AssistHelper(options);
      self.availableTables = ko.observableArray(${ table_names | n });
      self.chosenTables = ko.observableArray([]);

      huePubSub.subscribe("assist.table.selected", function (tableDef) {
        location.href = '/metastore/table/${database}/' + tableDef.name;
      });

      huePubSub.subscribe("assist.database.selected", function (databaseDef) {
        location.href = '/metastore/tables/' + databaseDef.name;
      });

      self.isLeftPanelVisible.subscribe(function (newValue) {
        $.totalStorage('spark_left_panel_visible', newValue);
      });
    }

    $(document).ready(function () {
      var options = {
        user: '${ user.username }',
        i18n: {
          errorLoadingDatabases: "${ _('There was a problem loading the databases') }",
          errorLoadingTablePreview: "${ _('There was a problem loading the table preview.') }"
        }
      }

      var viewModel = new MetastoreViewModel(options);

      ko.applyBindings(viewModel);

      window.hueDebug = {
        viewModel: viewModel,
        ko: ko
      };

      if (location.getParameter("error") != "") {
        $.jHueNotify.error(location.getParameter("error"));
      }

      var tables = $(".datatables").dataTable({
        "sDom": "<'row'r>t<'row'<'span8'i><''p>>",
        "bPaginate": false,
        "bLengthChange": false,
        "bInfo": false,
        "bFilter": true,
        "aoColumns": [
          {"bSortable": false, "sWidth": "1%"},
          {"bSortable": false, "sWidth": "1%"},
          null,
          null,
          null
        ],
        "oLanguage": {
          "sEmptyTable": "${_('No data available')}",
          "sZeroRecords": "${_('No matching records')}",
        }
      });

      var _searchInputValue = $("#filterInput").val();

      $("#filterInput").jHueDelayedInput(function () {
        if ($("#filterInput").val() != _searchInputValue) {
          $("#searchQueryForm").submit();
        }
      });

      $("#filterInput").focus();
      $("#filterInput").val(_searchInputValue); // set caret at the end of the field

      $("a[data-row-selector='true']").jHueRowSelector();

      $("a[data-table]").on("click", function () {
        var _link = $(this);
        var statsUrl = "/beeswax/api/table/${database}/" + _link.data("table") + "/stats/";
        var refreshUrl = "/beeswax/api/analyze/${database}/" + _link.data("table") + "/";
        $("#tableAnalysisStats .content").html("<i class='fa fa-spinner fa-spin'></i>");
        $("#tableAnalysis").show().css("top", _link.position().top - $("#tableAnalysis").outerHeight() / 2 + _link.outerHeight() / 2).css("left", _link.position().left + _link.outerWidth());
        showTableStats(statsUrl, refreshUrl, _link.data("table"), STATS_PROBLEMS, function () {
          $("#tableAnalysis").show().css("top", _link.position().top - $("#tableAnalysis").outerHeight() / 2 + _link.outerHeight() / 2).css("left", _link.position().left + _link.outerWidth());
        });
      });

      $(document).on("click", "#tableAnalysis .close-popover", function () {
        $("#tableAnalysis").hide();
      });

      $(".selectAll").click(function () {
        if ($(this).attr("checked")) {
          $(this).removeAttr("checked").removeClass("fa-check");
          $("." + $(this).data("selectables")).removeClass("fa-check").removeAttr("checked");
        }
        else {
          $(this).attr("checked", "checked").addClass("fa-check");
          $("." + $(this).data("selectables")).addClass("fa-check").attr("checked", "checked");
        }
        toggleActions();
      });

      $(".tableCheck").click(function () {
        if ($(this).attr("checked")) {
          $(this).removeClass("fa-check").removeAttr("checked");
        }
        else {
          $(this).addClass("fa-check").attr("checked", "checked");
        }
        $(".selectAll").removeAttr("checked").removeClass("fa-check");
        toggleActions();
      });

      function toggleActions() {
        $(".toolbarBtn").attr("disabled", "disabled");
        var selector = $(".hueCheckbox[checked='checked']");
        if (selector.length == 1) {
          if (selector.data("view-url")) {
            $("#viewBtn").removeAttr("disabled").click(function () {
              location.href = selector.data("view-url");
            });
          }
          if (selector.data("browse-url")) {
            $("#browseBtn").removeAttr("disabled").click(function () {
              location.href = selector.data("browse-url")
            });
          }
        }
        if (selector.length >= 1) {
          $("#dropBtn").removeAttr("disabled");
        }
      }

      $("#dropBtn").click(function () {
        $.getJSON("${ url('metastore:drop_table', database=database) }", function (data) {
          $("#dropTableMessage").text(data.title);
        });
        var _tempList = [];
        $(".hueCheckbox[checked='checked']").each(function (index) {
          _tempList.push($(this).data("drop-name"));
        });
        viewModel.chosenTables.removeAll();
        viewModel.chosenTables(_tempList);
        $("#dropTable").modal("show");
      });
    });
  });

</script>

${ commonfooter(messages) | n,unicode }
