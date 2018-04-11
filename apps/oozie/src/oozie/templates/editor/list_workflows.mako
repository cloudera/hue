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
  import time as py_time
%>
<%namespace name="actionbar" file="../actionbar.mako" />
<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="utils" file="../utils.inc.mako" />

${ commonheader(_("Workflows"), "oozie", user, request) | n,unicode }
${ layout.menubar(section='workflows') }

<style type="text/css">
  input.search-query {
    vertical-align: top;
  }
</style>

<div class="container-fluid">
  <div class="card card-small">
  <h1 class="card-heading simple">${ _('Workflow Manager') }</h1>

  <%actionbar:render>
    <%def name="search()">
      <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for name, description, etc...')}">
    </%def>

    <%def name="actions()">
      <div class="btn-toolbar" style="display: inline; vertical-align: middle">
        <button class="btn toolbarBtn" id="submit-btn" disabled="disabled"><i class="fa fa-play"></i> ${ _('Submit') }</button>
        <button class="btn toolbarBtn" id="schedule-btn" disabled="disabled"><i class="fa fa-calendar"></i> ${ _('Schedule') }</button>
        <button class="btn toolbarBtn" id="clone-btn" disabled="disabled"><i class="fa fa-files-o"></i> ${ _('Copy') }</button>
        <button class="btn toolbarBtn" id="export-btn" disabled="disabled"><i class="fa fa-upload"></i> ${ _('Export') }</button>
        <div id="delete-dropdown" class="btn-group" style="vertical-align: middle">
          <button id="trash-btn" class="btn toolbarBtn" disabled="disabled"><i class="fa fa-times"></i> ${_('Move to trash')}</button>
          <button id="trash-btn-caret" class="btn toolbarBtn dropdown-toggle" data-toggle="dropdown" disabled="disabled">
            <span class="caret"></span>
          </button>
          <ul class="dropdown-menu">
            <li><a href="javascript:void(0);" id="destroy-btn" title="${_('Delete forever')}"><i class="fa fa-bolt"></i> ${_('Delete forever')}</a></li>
          </ul>
        </div>
      </div>
    </%def>

    <%def name="creation()">
      <a href="${ url('oozie:create_workflow') }" class="btn"><i class="fa fa-plus-circle"></i> ${ _('Create') }</a>
      <a href="${ url('oozie:import_workflow') }" class="btn"><i class="fa fa-download"></i> ${ _('Import') }</a>
      &nbsp;&nbsp;
      <a href="${ url('oozie:list_trashed_workflows') }" class="btn"><i class="fa fa-trash-o"></i> ${ _('Trash') }</a>
    </%def>
  </%actionbar:render>


  <table id="workflowTable" class="table datatables">
    <thead>
      <tr>
        <th width="1%"><div class="hue-checkbox selectAll fa" data-selectables="workflowCheck"></div></th>
        <th>${ _('Name') }</th>
        <th>${ _('Description') }</th>
        <th>${ _('Last Modified') }</th>
        <th>${ _('Steps') }</th>
        <th>${ _('Status') }</th>
        <th>${ _('Owner') }</th>
      </tr>
    </thead>
    <tbody>
      % for workflow in jobs:
        <tr>
          <td data-row-selector-exclude="true">
             <div class="hue-checkbox workflowCheck fa" data-row-selector-exclude="true"
              % if workflow.can_read(user):
                  data-submit-url="${ url('oozie:submit_workflow', workflow=workflow.id) }"
                  data-schedule-url="${ url('oozie:schedule_workflow', workflow=workflow.id) }"
                  data-clone-url="${ url('oozie:clone_workflow', workflow=workflow.id) }"
                  data-export-url="${ url('oozie:export_workflow', workflow=workflow.id) }"
              % endif
              % if workflow.is_editable(user):
                  data-delete-id="${ workflow.id }"
              % endif
            ></div>
            % if workflow.can_read(user):
              <a href="${ url('oozie:edit_workflow', workflow=workflow.id) }" data-row-selector="true"></a>
            % endif
          </td>
          <td>
            ${ workflow.name }
          </td>
          <td>${ workflow.description }</td>

          <td nowrap="nowrap" data-sort-value="${ py_time.mktime(workflow.last_modified.timetuple()) }">${ utils.format_date(workflow.last_modified) }</td>
          <td><span class="badge badge-info">${ workflow.actions.count() }</span></td>
          <td>
            <span class="label label-info">${ workflow.status }</span>
          </td>
          <td>${ workflow.owner.username }</td>
        </tr>
      % endfor
    </tbody>
  </table>

  </div>
</div>

<div class="hueOverlay" data-bind="visible: isLoading">
  <i class="fa fa-spinner fa-spin big-spinner"></i>
</div>

<div id="submit-wf-modal" class="modal hide"></div>

<div id="trashWf" class="modal hide fade">
  <form id="trashWfForm" action="${ url('oozie:delete_workflow') }" method="POST">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 id="trashWfMessage" class="modal-title">${ _('Move the selected workflow(s) to trash?') }</h2>
    </div>
    <div class="modal-footer">
      <a href="#" class="btn" data-dismiss="modal">${ _('No') }</a>
      <input type="submit" class="btn btn-danger" value="${ _('Yes') }"/>
    </div>
    <div class="hide">
      <select name="job_selection" data-bind="options: availableJobs, selectedOptions: chosenJobs" size="5" multiple="true"></select>
    </div>
  </form>
</div>

<div id="destroyWf" class="modal hide fade">
  <form id="destroyWfForm" action="${ url('oozie:delete_workflow') }?skip_trash=true" method="POST">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 id="destroyWfMessage" class="modal-title">${ _('Delete the selected workflow(s)?') }</h2>
    </div>
    <div class="modal-footer">
      <a href="#" class="btn" data-dismiss="modal">${ _('No') }</a>
      <input type="submit" class="btn btn-danger" value="${ _('Yes') }"/>
    </div>
    <div class="hide">
      <select name="job_selection" data-bind="options: availableJobs, selectedOptions: chosenJobs" size="5" multiple="true"></select>
    </div>
  </form>
</div>


<script src="${ static('desktop/ext/js/datatables-paging-0.1.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
  $(document).ready(function () {
    var viewModel = {
      availableJobs : ko.observableArray(${ json_jobs | n }),
      chosenJobs : ko.observableArray([]),
      isLoading: ko.observable(false)
    };

    ko.applyBindings(viewModel);

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

    $(".workflowCheck").click(function () {
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
      var selector = $(".hue-checkbox[checked='checked']:not(.selectAll)");
      if (selector.length == 1) {
        var action_buttons = [
          ['#submit-btn', 'data-submit-url'],
          ['#schedule-btn', 'data-schedule-url'],
          ['#clone-btn', 'data-clone-url'],
          ['#export-btn', 'data-export-url']
        ];
        $.each(action_buttons, function (index) {
          if (selector.attr(this[1])) {
            $(this[0]).removeAttr("disabled");
          } else {
            $(this[0]).attr("disabled", "disabled");
          }
        });
      }
      var can_delete = $(".hue-checkbox[checked='checked'][data-delete-id]");
      if (can_delete.length > 0 && can_delete.length == selector.length) {
        $("#trash-btn").removeAttr("disabled");
        $("#trash-btn-caret").removeAttr("disabled");
      }
    }

    $("#trash-btn").click(function (e) {
      viewModel.chosenJobs.removeAll();
      $(".hue-checkbox[checked='checked']").each(function( index ) {
        viewModel.chosenJobs.push($(this).data("delete-id"));
      });
      $("#trashWf").modal("show");
    });

    $("#destroy-btn").click(function (e) {
      viewModel.chosenJobs.removeAll();
      $(".hue-checkbox[checked='checked']").each(function( index ) {
        viewModel.chosenJobs.push($(this).data("delete-id"));
      });
      $("#destroyWf").modal("show");
    });

    $("#submit-btn").click(function () {
      var _this = $(".hue-checkbox[checked='checked']");
      var _action = _this.attr("data-submit-url");
      $.get(_action, function (response) {
          $("#submit-wf-modal").html(response);
          $("#submit-wf-modal").modal("show");
        }
      );
    });

    $("#clone-btn").click(function (e) {
      viewModel.isLoading(true);
      var _this = $(".hue-checkbox[checked='checked']");
      var _url = _this.attr("data-clone-url");
      $.post(_url, function (data) {
        window.location = data.url;
      });
    });

    $("#schedule-btn").click(function (e) {
      viewModel.isLoading(true);
      var _this = $(".hue-checkbox[checked='checked']");
      var _url = _this.attr("data-schedule-url");
      window.location.replace(_url);
    });

    $("#export-btn").click(function (e) {
      viewModel.isLoading(true);
      var _this = $(".hue-checkbox[checked='checked']");
      var _url = _this.attr("data-export-url");
      window.location.replace(_url);
      window.setTimeout(function(){
        viewModel.isLoading(false);
      }, 500);
    });

    var oTable = $("#workflowTable").dataTable({
      "sPaginationType":"bootstrap",
      'iDisplayLength':50,
      "bLengthChange":false,
      "sDom": "<'row'r>t<'row-fluid'<'dt-pages'p><'dt-records'i>>",
      "aoColumns":[
        { "bSortable":false },
        null,
        null,
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null,
        null,
        null
      ],
      "aaSorting":[
        [3, 'desc'],
        [ 1, 'asc' ]
      ],
      "oLanguage":{
        "sEmptyTable":"${_('No data available')}",
        "sInfo":"${_('Showing _START_ to _END_ of _TOTAL_ entries')}",
        "sInfoEmpty":"${_('Showing 0 to 0 of 0 entries')}",
        "sInfoFiltered":"${_('(filtered from _MAX_ total entries)')}",
        "sZeroRecords":"${_('No matching records')}",
        "oPaginate":{
          "sFirst":"${_('First')}",
          "sLast":"${_('Last')}",
          "sNext":"${_('Next')}",
          "sPrevious":"${_('Previous')}"
        }
      },
      "fnDrawCallback":function (oSettings) {
        $("a[data-row-selector='true']").jHueRowSelector();
      }
    });

    $("#filterInput").keydown(function (e) {
      if (e.which == 13) {
        e.preventDefault();
        return false;
      }
    });

    $("#filterInput").keyup(function () {
      oTable.fnFilter($(this).val());
    });

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${commonfooter(request, messages) | n,unicode}
