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

${ commonheader(_("Bundles"), "oozie", user, request) | n,unicode }
${ layout.menubar(section='bundles') }

<style type="text/css">
  input.search-query {
    vertical-align: top;
  }
</style>

<div class="container-fluid">
  <div class="card card-small">
  <h1 class="card-heading simple">${ _('Bundle Manager') }</h1>

  <%actionbar:render>
    <%def name="search()">
      <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search for name, description, etc...')}">
    </%def>

    <%def name="actions()">
      <div class="btn-toolbar" style="display: inline; vertical-align: middle">
        <button class="btn toolbarBtn" id="submit-btn" disabled="disabled"><i class="fa fa-play"></i> ${ _('Submit') }</button>
        <button class="btn toolbarBtn" id="clone-btn" disabled="disabled"><i class="fa fa-files-o"></i> ${ _('Copy') }</button>
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
      <a href="${ url('oozie:create_bundle') }" class="btn"><i class="fa fa-plus-circle"></i> ${ _('Create') }</a>
      &nbsp;&nbsp;
      <a href="${ url('oozie:list_trashed_bundles') }" class="btn"><i class="fa fa-trash-o"></i> ${ _('View trash') }</a>
    </%def>
  </%actionbar:render>

  <table id="bundleTable" class="table datatables">
    <thead>
      <tr>
        <th width="1%"><div class="hue-checkbox selectAll fa" data-selectables="bundleCheck"></div></th>
        <th width="10%">${ _('Name') }</th>
        <th width="20%">${ _('Description') }</th>
        <th width="35%">${ _('Coordinators') }</th>
        <th>${ _('Kick off') }</th>
        <th>${ _('Status') }</th>
        <th>${ _('Last Modified') }</th>
        <th>${ _('Owner') }</th>
      </tr>
    </thead>
    <tbody>
      % for bundle in jobs:
        <tr>
          <td data-row-selector-exclude="true">
            <div class="hue-checkbox bundleCheck fa" data-row-selector-exclude="true"
              % if bundle.can_read(user):
                  data-clone-url="${ url('oozie:clone_bundle', bundle=bundle.id) }"
                  data-submit-url="${ url('oozie:submit_bundle', bundle=bundle.id) }"
              % endif
              % if bundle.is_editable(user):
                  data-delete-id="${ bundle.id }"
              % endif
              >
            </div>
            % if bundle.can_read(user):
              <a href="${ url('oozie:edit_bundle', bundle=bundle.id) }" data-row-selector="true"/>
            % endif
          </td>
          <td>${ bundle.name }</td>
          <td>${ bundle.description }</td>
          <td>
             % for bundled in bundle.coordinators.all():
               ${ bundled.coordinator.name }
		       % if not loop.last:
		        ,
		       % endif
             % endfor
          </td>
          <td>${ bundle.kick_off_time }</td>
          <td>
            <span class="label label-info">${ bundle.status }</span>
          </td>
          <td nowrap="nowrap" data-sort-value="${py_time.mktime(bundle.last_modified.timetuple())}">${ utils.format_date(bundle.last_modified) }</td>
          <td>${ bundle.owner.username }</td>
        </tr>
      %endfor
    </tbody>
  </table>
</div>
</div>

<div class="hueOverlay" data-bind="visible: isLoading">
  <i class="fa fa-spinner fa-spin big-spinner"></i>
</div>

<div id="submit-job-modal" class="modal hide"></div>

<div id="trash-job" class="modal hide">
  <form id="trashForm" action="${ url('oozie:delete_bundle') }" method="POST">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 id="trashMessage" class="modal-title">${ _('Move the selected bundle(s) to trash?') }</h2>
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
  <form id="destroyForm" action="${ url('oozie:delete_bundle') }?skip_trash=true" method="POST">
    ${ csrf_token(request) | n,unicode }
    <div class="modal-header">
      <button type="button" class="close" data-dismiss="modal" aria-label="${ _('Close') }"><span aria-hidden="true">&times;</span></button>
      <h2 id="destroyMessage" class="modal-title">${ _('Delete the selected bundle(s)?') }</h2>
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

    $(".bundleCheck").click(function () {
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
          ['#bundle-btn', 'data-bundle-url'],
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
      $("#trash-job").modal("show");
    });

    $("#destroy-btn").click(function (e) {
      viewModel.chosenJobs.removeAll();
      $(".hue-checkbox[checked='checked']").each(function( index ) {
        viewModel.chosenJobs.push($(this).data("delete-id"));
      });
      $("#destroy-job").modal("show");
    });

    $("#submit-btn").click(function () {
      var _this = $(".hue-checkbox[checked='checked']");
      var _action = _this.attr("data-submit-url");
      $.get(_action, function (response) {
          $("#submit-job-modal").html(response);
          $("#submit-job-modal").modal("show");
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

    var oTable = $("#bundleTable").dataTable({
      "sPaginationType":"bootstrap",
      'iDisplayLength':50,
      "bLengthChange":false,
      "sDom": "<'row'r>t<'row-fluid'<'dt-pages'p><'dt-records'i>>",
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

${ commonfooter(request, messages) | n,unicode }
