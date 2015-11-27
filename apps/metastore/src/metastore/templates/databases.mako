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
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>
<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="components" file="components.mako" />
<%namespace name="assist" file="/assist.mako" />
<%namespace name="tableStats" file="/table_stats.mako" />
<%namespace name="require" file="/require.mako" />


${ commonheader(_('Databases'), 'metastore', user) | n,unicode }
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
                <li><a href="${ url('beeswax:create_database') }" title="${_('Create a new database')}"><i class="fa fa-plus-circle"></i></a></li>
                % endif
              </ul>
              <ul class="nav nav-pills hueBreadcrumbBar" id="breadcrumbs">
                <li>
                  <i class="fa fa-th-large muted"></i>
                </li>
                <li>
                  <a href="${url('metastore:databases')}">${_('Databases')}</a>
                </li>
              </ul>
            </h3>


            <%actionbar:render>
          <%def name="search()">
            <form id="searchQueryForm" action="${ url('metastore:databases') }" method="GET" class="inline">
              <input id="filterInput" type="text" name="filter" class="input-xlarge search-query" value="${ search_filter }" placeholder="${_('Search for database name')}" />
            </form>
          </%def>

          <%def name="actions()">
            % if has_write_access:
              <button id="dropBtn" class="btn toolbarBtn" title="${_('Drop the selected databases')}" disabled="disabled"><i class="fa fa-trash-o"></i>  ${_('Drop')}</button>
            % endif
          </%def>
        </%actionbar:render>

        <table class="table table-condensed datatables">
          <thead>
            <tr>
              <th width="1%"><div class="hueCheckbox selectAll fa" data-selectables="databaseCheck"></div></th>
              <th>${_('Database Name')}</th>
            </tr>
          </thead>
          <tbody>
          % for database in databases:
            <tr>
              <td data-row-selector-exclude="true" width="1%">
                <div class="hueCheckbox databaseCheck fa"
                   data-view-url="${ url('metastore:show_tables', database=database) }"
                   data-drop-name="${ database }"
                   data-row-selector-exclude="true"></div>
              </td>
              <td>
                <a class="databaseLink" href="${ url('metastore:show_tables', database=database) }" data-row-selector="true">${ database }</a>
              </td>
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



<div id="dropDatabase" class="modal hide fade">
  <form id="dropDatabaseForm" action="${ url('metastore:drop_database') }" method="POST">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3 id="dropDatabaseMessage">${_('Confirm action')}</h3>
    </div>
    <div class="modal-footer">
      <input type="button" class="btn" data-dismiss="modal" value="${_('Cancel')}" />
      <input type="submit" class="btn btn-danger" value="${_('Yes')}"/>
    </div>
    <div class="hide">
      <select name="database_selection" data-bind="options: availableDatabases, selectedOptions: chosenDatabases" size="5" multiple="true"></select>
    </div>
  </form>
</div>


<script type="text/javascript" charset="utf-8">

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
      self.availableDatabases = ko.observableArray(${ databases_json | n });
      self.chosenDatabases = ko.observableArray([]);

      huePubSub.subscribe("assist.table.selected", function (tableDef) {
        location.href = '/metastore/table/' + tableDef.database + '/' + tableDef.name;
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

      var databases = $(".datatables").dataTable({
        "sDom": "<'row'r>t<'row'<'span8'i><''p>>",
        "bPaginate": false,
        "bLengthChange": false,
        "bInfo": false,
        "aoColumns": [
          {"bSortable": false, "sWidth": "1%"},
          null,
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

      $(".databaseCheck").click(function () {
        if ($(this).attr("checked")) {
          $(this).removeClass("fa-check").removeAttr("checked");
        }
        else {
          $(this).addClass("fa-check").attr("checked", "checked");
        }
        $(".selectAll").removeAttr("checked").removeClass("fa-check");
        toggleActions();
      });

      $(".databaseLink").mouseover(function () {
        var _link = $(this);
        $.ajax({
          type: "GET",
          url: "/metastore/databases/" + $(this).text() + "/metadata",
          dataType: "json",
          data: {},
          success: function (response) {
            if (response && response.status == 0) {
              _link.attr("title", response.data.comment).tooltip("show");
            }
          },
        });
      });

      function toggleActions() {
        $(".toolbarBtn").attr("disabled", "disabled");
        var selector = $(".hueCheckbox[checked='checked']");
        if (selector.length >= 1) {
          $("#dropBtn").removeAttr("disabled");
        }
      }

      $("#dropBtn").click(function () {
        $.getJSON("${ url('metastore:drop_database') }", function (data) {
          $("#dropDatabaseMessage").text(data.title);
        });
        var _tempList = [];
        $(".hueCheckbox[checked='checked']").each(function (index) {
          _tempList.push($(this).data("drop-name"));
        });
        viewModel.chosenDatabases.removeAll();
        viewModel.chosenDatabases(_tempList);
        $("#dropDatabase").modal("show");
      });
    });


  });



</script>

${ commonfooter(messages) | n,unicode }
