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

${ commonheader(_("Trashed Coordinators"), "oozie", user, "100px") | n,unicode }
${ layout.menubar(section='coordinators') }


<div class="container-fluid">
  <h1>${ _('Coordinator Trash') }</h1>

  <%actionbar:render>
    <%def name="search()">
      <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for name, description, etc...')}">
    </%def>

    <%def name="actions()">
        <a href="${ url('oozie:list_coordinators') }" id="home-btn" class="btn" title="${ _('Got to coordinator manager') }">
          <i class="icon-home"></i> ${ _('Coordinators') }
        </a>
        &nbsp;&nbsp;
        <button class="btn toolbarBtn" id="restore-btn" disabled="disabled" title="${_('Restore the selected coordinators')}">
          <i class="icon-cloud-upload"></i> ${ _('Restore') }
        </button>
        <button class="btn toolbarBtn" id="destroy-btn" disabled="disabled" title="${_('Delete the selected coordinators')}">
          <i class="icon-bolt"></i> ${ _('Delete forever') }
        </button>
    </%def>

    <%def name="creation()">
        <button class="btn" id="purge-btn"><i class="icon-fire"></i> ${ _('Empty') }</button>
    </%def>
  </%actionbar:render>

  <table id="coordinatorTable" class="table datatables">
    <thead>
      <tr>
        <th width="1%"><div class="hueCheckbox selectAll" data-selectables="coordinatorCheck"></div></th>
        <th>${ _('Name') }</th>
        <th>${ _('Description') }</th>
        <th>${ _('Workflow') }</th>
        <th>${ _('Frequency') }</th>
        <th>${ _('Status') }</th>
        <th>${ _('Last Modified') }</th>
        <th>${ _('Owner') }</th>
      </tr>
    </thead>
    <tbody>
      %for coordinator in jobs:
        <tr>
          <td data-row-selector-exclude="true">
            <div class="hueCheckbox coordinatorCheck" data-row-selector-exclude="true" data-coordinator-id="${ coordinator.id }"></div>
          </td>
          <td>${ coordinator.name }</td>
          <td>${ coordinator.description }</td>
          <td>
            % if coordinator.workflow is not None:
              ${ coordinator.workflow }
            % endif
          </td>
          <td>${ coordinator.text_frequency }</td>
          <td>
            <span class="label label-info">${ coordinator.status }</span>
          </td>
          <td nowrap="nowrap" data-sort-value="${py_time.mktime(coordinator.last_modified.timetuple())}">${ utils.format_date(coordinator.last_modified) }</td>
          <td>${ coordinator.owner.username }</td>
        </tr>
      %endfor
    </tbody>
  </table>
</div>


<div id="purge-job" class="modal hide">
  <form id="purgeForm" action="${ url('oozie:delete_coordinator') }?skip_trash=true" method="POST">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3 id="purgeMessage">${ _('Delete all coordinator(s)?') }</h3>
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


<div id="destroy-job" class="modal hide">
  <form id="purgeForm" action="${ url('oozie:delete_coordinator') }?skip_trash=true" method="POST">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3 id="purgeMessage">${ _('Delete the selected coordinator(s)?') }</h3>
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


<div id="restore-job" class="modal hide">
  <form id="restoreWfForm" action="${ url('oozie:restore_coordinator') }" method="POST">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3 id="restoreWfMessage">${ _('Restore the selected coordinator(s)?') }</h3>
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

<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/knockout-2.1.0.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {
    var viewModel = {
        availableJobs : ko.observableArray(${ json_jobs | n }),
        chosenJobs : ko.observableArray([])
    };

    ko.applyBindings(viewModel);

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

    $(".coordinatorCheck").click(function () {
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
      var can_modify = $(".hueCheckbox[checked='checked'][data-coordinator-id]");
      if (can_modify.length >= 1 && can_modify.length == selector.length) {
        $("#destroy-btn").removeAttr("disabled");
        $("#restore-btn").removeAttr("disabled");
      }
    }

    $("#purge-btn").click(function (e) {
      viewModel.chosenJobs.removeAll();
      $(".hueCheckbox").each(function( index ) {
        viewModel.chosenJobs.push($(this).data("coordinator-id"));
      });
      $("#purge-job").modal("show");
    });

    $("#destroy-btn").click(function (e) {
      viewModel.chosenJobs.removeAll();
      $(".hueCheckbox[checked='checked']").each(function( index ) {
        viewModel.chosenJobs.push($(this).data("coordinator-id"));
      });
      $("#destroy-job").modal("show");
    });

    $("#restore-btn").click(function (e) {
      viewModel.chosenJobs.removeAll();
      $(".hueCheckbox[checked='checked']").each(function( index ) {
        viewModel.chosenJobs.push($(this).data("coordinator-id"));
      });
      $("#restore-job").modal("show");
    });

    var oTable = $("#coordinatorTable").dataTable({
      "sPaginationType":"bootstrap",
      'iDisplayLength':50,
      "bLengthChange":false,
      "sDom":"<'row'r>t<'row'<'span8'i><''p>>",
      "aoColumns":[
        { "bSortable":false },
        null,
        null,
        null,
        null,
        { "sSortDataType":"dom-sort-value", "sType":"numeric" },
        null,
        null
      ],
      "aaSorting":[
        [ 6, "desc" ]
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

${ commonfooter(messages) | n,unicode }
