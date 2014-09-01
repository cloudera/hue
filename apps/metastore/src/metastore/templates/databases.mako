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
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
%>
<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="components" file="components.mako" />

${ commonheader(_('Databases'), 'metastore', user) | n,unicode }
${ components.menubar() }

<div class="container-fluid" id="databases">
  <div class="row-fluid">
  % if has_write_access:
    <div class="span3">
      <div class="sidebar-nav card-small">
        <ul class="nav nav-list">
          <li class="nav-header">${_('actions')}</li>
          <li><a href="${ url('beeswax:create_database') }"><i class="fa fa-plus-circle"></i> ${_('Create a new database')}</a></li>
        </ul>
      </div>
    </div>
    <div class="span9">
  %else:
    <div class="span12">
  % endif
      <div class="card card-small">
        <h1 class="card-heading simple">${ components.breadcrumbs(breadcrumbs) }</h1>
        <%actionbar:render>
          <%def name="search()">
            <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for database name')}">
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
                <a href="${ url('metastore:show_tables', database=database) }" data-row-selector="true">${ database }</a>
              </td>
            </tr>
          % endfor
          </tbody>
        </table>
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

<link rel="stylesheet" href="/metastore/static/css/metastore.css" type="text/css">

<script src="/static/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {
    var viewModel = {
      availableDatabases: ko.observableArray(${ databases_json | n,unicode }),
      chosenDatabases: ko.observableArray([])
    };

    ko.applyBindings(viewModel);

    var databases = $(".datatables").dataTable({
      "sDom": "<'row'r>t<'row'<'span8'i><''p>>",
      "bPaginate": false,
      "bLengthChange": false,
      "bInfo": false,
      "bFilter": true,
      "aoColumns": [
        {"bSortable": false, "sWidth": "1%" },
        null
      ],
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sZeroRecords": "${_('No matching records')}",
      }
    });

    $("#filterInput").keyup(function () {
      databases.fnFilter($(this).val());
    });

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
</script>

${ commonfooter(messages) | n,unicode }
