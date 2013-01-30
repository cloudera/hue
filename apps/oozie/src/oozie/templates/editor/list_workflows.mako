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

${ commonheader(_("Oozie App"), "oozie", user, "100px") | n,unicode }
${ layout.menubar(section='workflows') }


<div class="container-fluid">
  <h1>${ _('Workflow Manager') }</h1>

  <%actionbar:render>
    <%def name="actions()">
        <button class="btn toolbarBtn" id="submit-btn" disabled="disabled"><i class="icon-play"></i> ${ _('Submit') }</button>
        <button class="btn toolbarBtn" id="schedule-btn" disabled="disabled"><i class="icon-calendar"></i> ${ _('Schedule') }</button>
        <button class="btn toolbarBtn" id="clone-btn" disabled="disabled"><i class="icon-retweet"></i> ${ _('Clone') }</button>
        <button class="btn toolbarBtn" id="delete-btn" disabled="disabled"><i class="icon-remove"></i> ${ _('Delete') }</button>
    </%def>

    <%def name="creation()">
        <a href="${ url('oozie:create_workflow') }" class="btn"><i class="icon-plus-sign"></i> ${ _('Create') }</a>
        <a href="${ url('oozie:import_workflow') }" class="btn"><i class="icon-plus-sign"></i> ${ _('Import') }</a>
        % if currentuser.is_superuser:
          <a href="#installSamples" data-toggle="modal" class="btn"><i class="icon-download-alt"></i> ${ _('Setup Examples') }</a>
        % endif
    </%def>
  </%actionbar:render>


  <table id="workflowTable" class="table datatables">
    <thead>
      <tr>
        <th width="1%"><div class="hueCheckbox selectAll" data-selectables="workflowCheck"></div></th>
        <th>${ _('Name') }</th>
        <th>${ _('Description') }</th>
        <th>${ _('Last Modification') }</th>
        <th>${ _('Steps') }</th>
        <th>${ _('Status') }</th>
        <th>${ _('Owner') }</th>
      </tr>
    </thead>
    <tbody>
      % for workflow in jobs:
        <tr>
          <td data-row-selector-exclude="true">
             <div class="hueCheckbox workflowCheck" data-row-selector-exclude="true"
              % if workflow.is_accessible(currentuser):
                  data-submit-url="${ url('oozie:submit_workflow', workflow=workflow.id) }"
                  data-schedule-url="${ url('oozie:schedule_workflow', workflow=workflow.id) }"
                  data-clone-url="${ url('oozie:clone_workflow', workflow=workflow.id) }"
              % endif
              % if workflow.is_editable(currentuser):
                  data-delete-url="${ url('oozie:delete_workflow', workflow=workflow.id) }"
              % endif
            ></div>
            % if workflow.is_accessible(currentuser):
              <a href="${ url('oozie:edit_workflow', workflow=workflow.id) }" data-row-selector="true"></a>
            % endif
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


<div id="submit-wf-modal" class="modal hide"></div>

<div id="deleteWf" class="modal hide fade">
  <form id="deleteWfForm" action="" method="POST">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3 id="deleteWfMessage">${ _('Delete this workflow?') }</h3>
    </div>
    <div class="modal-footer">
      <a href="#" class="btn" data-dismiss="modal">${ _('No') }</a>
      <input type="submit" class="btn btn-danger" value="${ _('Yes') }"/>
    </div>
  </form>
</div>

<div id="installSamples" class="modal hide fade">
  <form id="installSamplesForm" action="${url('oozie:setup_app')}" method="POST">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3>${ _('Set up the workspaces and examples?') }</h3>
    </div>
    <div class="modal-body">
      ${ _('Hue is going to re-create the workspaces and re-install the examples.') }
    </div>
    <div class="modal-footer">
      <a href="#" class="btn" data-dismiss="modal">${ _('No') }</a>
      <input type="submit" class="btn btn-primary" value="${ _('Yes') }"/>
    </div>
  </form>
</div>

<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function () {

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

    $(".workflowCheck").click(function () {
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
        var action_buttons = [
          ['#submit-btn', 'data-submit-url'],
          ['#schedule-btn', 'data-schedule-url'],
          ['#delete-btn', 'data-delete-url'],
          ['#clone-btn', 'data-clone-url']
        ];
        $.each(action_buttons, function (index) {
          if (selector.attr(this[1])) {
            $(this[0]).removeAttr("disabled");
          } else {
            $(this[0]).attr("disabled", "disabled");
          }
        });
      }
    }

    $("#delete-btn").click(function (e) {
      var _this = $(".hueCheckbox[checked='checked']");
      var _action = _this.attr("data-delete-url");
      $("#deleteWfForm").attr("action", _action);
      $("#deleteWfMessage").text(_this.attr("alt"));
      $("#deleteWf").modal("show");
    });

    $("#submit-btn").click(function () {
      var _this = $(".hueCheckbox[checked='checked']");
      var _action = _this.attr("data-submit-url");
      $.get(_action, function (response) {
          $("#submit-wf-modal").html(response);
          $("#submit-wf-modal").modal("show");
        }
      );
    });

    $("#clone-btn").click(function (e) {
      var _this = $(".hueCheckbox[checked='checked']");
      var _url = _this.attr("data-clone-url");
      $.post(_url, function (data) {
        window.location = data.url;
      });
    });

    $("#schedule-btn").click(function (e) {
      var _this = $(".hueCheckbox[checked='checked']");
      var _url = _this.attr("data-schedule-url");
      window.location.replace(_url);
    });

    var oTable = $("#workflowTable").dataTable({
      "sPaginationType":"bootstrap",
      'iDisplayLength':50,
      "bLengthChange":false,
      "sDom":"<'row'r>t<'row'<'span8'i><''p>>",
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

${commonfooter(messages) |n,unicode}
