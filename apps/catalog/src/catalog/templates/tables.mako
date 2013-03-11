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
<%namespace name="layout" file="layout.mako" />

${ commonheader(_('Tables'), 'catalog', user) | n,unicode }

<div class="container-fluid">
    <h1>${_('Tables')}</h1>
    <div class="row-fluid">
        <div class="span3">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <span>
                    <li class="nav-header">${_('database')}</li>
                    <li>
                       <form action="${ url('catalog:show_tables') }" id="db_form" method="POST">
                         ${ db_form | n,unicode }
                       </form>
                    </li>
                    </span>
                    <li class="nav-header">${_('Actions')}</li>
                    % if not examples_installed:
                    <li><a href="#installSamples" data-toggle="modal">${_('Install samples')}</a></li>
                    % endif
                    <li><a href="${ url('beeswax:import_wizard', database=database) }">${_('Create a new table from a file')}</a></li>
                    <li><a href="${ url('beeswax:create_table', database=database) }">${_('Create a new table manually')}</a></li>
                </ul>
            </div>
        </div>
        <div class="span9">
          <%actionbar:render>
            <%def name="actions()">
                <button id="viewBtn" class="btn toolbarBtn" title="${_('Browse the selected table')}" disabled="disabled"><i class="icon-eye-open"></i> ${_('View')}</button>
                <button id="browseBtn" class="btn toolbarBtn" title="${_('Browse the selected table')}" disabled="disabled"><i class="icon-list"></i> ${_('Browse Data')}</button>
                <button id="dropBtn" class="btn toolbarBtn" title="${_('Delete the selected tables')}" disabled="disabled"><i class="icon-trash"></i>  ${_('Drop')}</button>
            </%def>
          </%actionbar:render>
            <table class="table table-condensed table-striped datatables">
                <thead>
                  <tr>
                    <th width="1%"><div class="hueCheckbox selectAll" data-selectables="tableCheck"></div></th>
                    <th>${_('Table Name')}</th>
                  </tr>
                </thead>
                <tbody>
                % for table in tables:
                  <tr>
                    <td data-row-selector-exclude="true" width="1%">
                      <div class="hueCheckbox tableCheck"
                           data-view-url="${ url('catalog:describe_table', database=database, table=table) }"
                           data-browse-url="${ url('catalog:read_table', database=database, table=table) }"
                           data-drop-name="${ table }"
                           data-row-selector-exclude="true"></div>
                    </td>
                    <td>
                      <a href="${ url('catalog:describe_table', database=database, table=table) }" data-row-selector="true">${ table }</a>
                    </td>
                  </tr>
                % endfor
                </tbody>
            </table>
        </div>
    </div>
</div>

% if not examples_installed:
<div id="installSamples" class="modal hide fade">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3>${_('Install samples')}</h3>
  </div>
  <div class="modal-body">
    <div id="installSamplesMessage">

    </div>
  </div>
  <div class="modal-footer">
    <a href="#" class="btn" data-dismiss="modal">${_('Cancel')}</a>
    <a href="#" id="installSamplesBtn" class="btn btn-primary">${_('Yes, install samples')}</a>
  </div>
</div>
% endif

<div id="dropTable" class="modal hide fade">
  <form id="dropTableForm" action="${ url('catalog:drop_table', database=database) }" method="POST">
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

<script src="/static/ext/js/jquery/plugins/jquery.cookie.js"></script>
<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {
    var viewModel = {
        availableTables : ko.observableArray(${ tables_json | n }),
        chosenTables : ko.observableArray([])
    };

    ko.applyBindings(viewModel);

    var tables = $(".datatables").dataTable({
      "sDom":"<'row'r>t<'row'<'span8'i><''p>>",
      "bPaginate":false,
      "bLengthChange":false,
      "bInfo":false,
      "bFilter":true,
      "aoColumns":[
        {"bSortable":false, "sWidth":"1%" },
        null
      ],
      "oLanguage":{
        "sEmptyTable":"${_('No data available')}",
        "sZeroRecords":"${_('No matching records')}",
      }
    });

    $("#filterInput").keyup(function () {
      tables.fnFilter($(this).val());
    });

    $("a[data-row-selector='true']").jHueRowSelector();

    $("#id_database").change(function () {
      $.cookie("hueBeeswaxLastDatabase", $(this).val(), {expires:90});
      $('#db_form').submit();
    });

    % if not examples_installed:
        $.getJSON("${ url('beeswax:install_examples') }", function (data) {
          $("#installSamplesMessage").text(data.title);
        });

        $("#installSamplesBtn").click(function () {
          $.post(
              "${ url('beeswax:install_examples') }",
              { submit:"Submit" },
              function (result) {
                if (result.creationSucceeded) {
                  window.location.href = "${ url('catalog:show_tables') }";
                }
                else {
                  var message = "${_('There was an error processing your request:')} " + result.message;
                  $("#installSamplesMessage").addClass("alert").addClass("alert-error").text(message);
                }
              }
          );
        });
    % endif

    $(".selectAll").click(function () {
      if ($(this).attr("checked")) {
        $(this).removeAttr("checked").removeClass("icon-ok");
        $("." + $(this).data("selectables")).removeClass("icon-ok").removeAttr("checked");
      }
      else {
        $(this).attr("checked", "checked").addClass("icon-ok");
        $("." + $(this).data("selectables")).addClass("icon-ok").attr("checked", "checked");
      }
      toggleActions();
    });

    $(".tableCheck").click(function () {
      if ($(this).attr("checked")) {
        $(this).removeClass("icon-ok").removeAttr("checked");
      }
      else {
        $(this).addClass("icon-ok").attr("checked", "checked");
      }
      $(".selectAll").removeAttr("checked").removeClass("icon-ok");
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
      $.getJSON("${ url('catalog:drop_table', database=database) }", function(data) {
        $("#dropTableMessage").text(data.title);
      });
      viewModel.chosenTables.removeAll();
      $(".hueCheckbox[checked='checked']").each(function( index ) {
        viewModel.chosenTables.push($(this).data("drop-name"));
      });
      $("#dropTable").modal("show");
    });
  });
</script>

${ commonfooter(messages) | n,unicode }
