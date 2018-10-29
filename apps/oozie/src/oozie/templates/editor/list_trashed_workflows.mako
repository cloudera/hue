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

${ commonheader(_("Trashed Workflows"), "oozie", user, request) | n,unicode }
${ layout.menubar(section='workflows') }


<div class="container-fluid">
  <div class="card card-small">
  <h1 class="card-heading simple">${ _('Workflow Trash') }</h1>

  <%actionbar:render>
    <%def name="search()">
      <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for name, description, etc...')}">
    </%def>

    <%def name="actions()">
      <button type="button" id="restore-btn" class="btn toolbarBtn" disabled="disabled" title="${ _('Restore the selected workflows') }">
        <i class="fa fa-cloud-upload"></i> ${ _('Restore') }
      </button>
      <button type="button" id="destroy-btn" class="btn toolbarBtn" disabled="disabled" title="${ _('Delete the selected workflows') }">
        <i class="fa fa-bolt"></i> ${ _('Delete forever') }
      </button>
    </%def>

    <%def name="creation()">
      <button type="button" id="purge-btn" class="btn" title="${ _('Delete all the workflows') }">
        <i class="fa fa-fire"></i> ${ _('Empty trash') }
      </button>
      <a href="${ url('oozie:list_workflows') }" id="home-btn" class="btn" title="${ _('Go to workflow manager') }">
        <i class="fa fa-home"></i> ${ _('Back') }
      </a>
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
             <div class="hue-checkbox workflowCheck fa" data-row-selector-exclude="true" data-workflow-id="${ workflow.id }"></div>
          </td>
          <td>
            ${ workflow.name }
          </td>
          <td>${ workflow.description }</td>

          <td nowrap="nowrap" data-sort-value="${py_time.mktime(workflow.last_modified.timetuple())}">${ utils.format_date(workflow.last_modified) }</td>
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

<div id="purgeWfs" class="modal hide fade">
  <form id="purgeWfsForm" action="${ url('oozie:delete_workflow') }?skip_trash=true" method="POST">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 id="purgeWfsMessage" class="modal-title">${ _('Delete all trashed workflow(s)?') }</h2>
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

<div id="restoreWf" class="modal hide fade">
  <form id="restoreWfForm" action="${ url('oozie:restore_workflow') }" method="POST">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 id="restoreWfMessage" class="modal-title">${ _('Restore the selected workflow(s)?') }</h2>
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
        chosenJobs : ko.observableArray([])
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
      var selector = $(".hue-checkbox.workflowCheck[checked='checked']");
      var can_delete = $(".hue-checkbox.workflowCheck[checked='checked'][data-workflow-id]");
      if (can_delete.length >= 1 && can_delete.length == selector.length) {
        $("#destroy-btn").removeAttr("disabled");
        $("#restore-btn").removeAttr("disabled");
      }
    }

    $("#destroy-btn").click(function (e) {
      viewModel.chosenJobs.removeAll();
      $(".hue-checkbox[checked='checked']").each(function( index ) {
        viewModel.chosenJobs.push($(this).data("workflow-id"));
      });
      $("#destroyWf").modal("show");
    });

    $("#purge-btn").click(function (e) {
      viewModel.chosenJobs.removeAll();
      $(".hue-checkbox").each(function( index ) {
        viewModel.chosenJobs.push($(this).data("workflow-id"));
      });
      $("#purgeWfs").modal("show");
    });

    $("#restore-btn").click(function (e) {
      viewModel.chosenJobs.removeAll();
      $(".hue-checkbox[checked='checked']").each(function( index ) {
        viewModel.chosenJobs.push($(this).data("workflow-id"));
      });
      $("#restoreWf").modal("show");
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
