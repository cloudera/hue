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

<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="utils" file="../utils.inc.mako" />

${ commonheader(_("Oozie App"), "oozie", user, "100px") }
${ layout.menubar(section='coordinators') }


<div class="container-fluid">
  <h1>${ _('Coordinator Editor') }</h1>

  <div class="well hueWell">
    <div class="btn-group pull-right">
      <a href="${ url('oozie:create_coordinator') }" class="btn"><i class="icon-plus-sign"></i> ${ _('Create') }</a>
    </div>

    <div class="row-fluid">
      <div class="span4">
        <form>
            ${ _('Filter:') }
            <input id="filterInput" class="input-xlarge search-query" type="text" placeholder="${ _('Search for username, name, etc...') }">
        </form>
      </div>
      <div class="span4">
        <button class="btn action-buttons" id="submit-btn" disabled="disabled"><i class="icon-play"></i> ${ _('Submit') }</button>
      &nbsp;&nbsp;&nbsp;&nbsp;
      <button class="btn action-buttons" id="clone-btn" disabled="disabled"><i class="icon-retweet"></i> ${ _('Copy') }</button>
      <button class="btn action-buttons" id="delete-btn" disabled="disabled"><i class="icon-remove"></i> ${ _('Delete') }</button>
      </div>
    </div>
  </div>

  <br/>

  <table id="coordinatorTable" class="table datatables">
    <thead>
      <tr>
        <th></th>
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
        <tr class="action-row">
          <td class=".btn-large action-column" data-row-selector-exclude="true" style="background-color: white;">
            <input type="radio" name="action" data-row-selector-exclude="true"
              % if coordinator.is_accessible(currentuser):
                  data-clone-url="${ url('oozie:clone_coordinator', coordinator=coordinator.id) }"
                  data-submit-url="${ url('oozie:submit_coordinator', coordinator=coordinator.id) }"
              % endif
              % if coordinator.is_editable(currentuser):
                  data-delete-url="${ url('oozie:delete_coordinator', coordinator=coordinator.id) }"
              % endif
              >
            </input>
            % if coordinator.is_accessible(currentuser):
              <a href="${ url('oozie:edit_coordinator', coordinator=coordinator.id) }" data-row-selector="true"/>
            % endif
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
          <td nowrap="nowrap">${ utils.format_date(coordinator.last_modified) }</td>
          <td>${ coordinator.owner.username }</td>
        </tr>
      %endfor
    </tbody>
  </table>
</div>


<div id="submit-job-modal" class="modal hide"></div>

<div id="delete-job" class="modal hide">
  <form id="deleteWfForm" action="" method="POST">
    <div class="modal-header">
      <a href="#" class="close" data-dismiss="modal">&times;</a>
      <h3 id="deleteWfMessage">${ _('Delete this coordinator?') }</h3>
    </div>
    <div class="modal-footer">
      <input type="submit" class="btn primary" value="${ _('Yes') }"/>
      <a href="#" class="btn secondary" data-dismiss="modal">${ _('No') }</a>
    </div>
  </form>
</div>


<style>
  td .btn-large {
  cursor: crosshair;
  }

  .action-column {
    cursor: auto;
  }
</style>


<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function() {

    $(".action-row").click(function(e){
      var select_btn = $(this).find('input');
      select_btn.prop("checked", true);

      $(".action-row").css("background-color", "");
      $(this).css("background-color", "#ECF4F8");

      $(".action-buttons").attr("disabled", "disabled");

      update_action_buttons_status();
    });

    function update_action_buttons_status() {
      var select_btn = $('input[name=action]:checked');

      var action_buttons = [
        ['#submit-btn', 'data-submit-url'],
        ['#bundle-btn', 'data-bundle-url'],
        ['#delete-btn', 'data-delete-url'],
        ['#clone-btn', 'data-clone-url']]

      $.each(action_buttons, function(index) {
        if (select_btn.attr(this[1])) {
          $(this[0]).removeAttr('disabled');
        } else {
          $(this[0]).attr("disabled", "disabled");
        }
      });
    }

    update_action_buttons_status();

    $("#delete-btn").click(function(e){
      var _this = $('input[name=action]:checked');
      var _action = _this.attr("data-delete-url");
      $("#deleteWfForm").attr("action", _action);
      $("#deleteWfMessage").text(_this.attr("alt"));
      $("#delete-job").modal("show");
    });

    $('#submit-btn').click(function() {
      var _this = $('input[name=action]:checked');
      var _action = _this.attr("data-submit-url");

      $.get(_action,  function(response) {
          $('#submit-job-modal').html(response);
          $('#submit-job-modal').modal('show');
        }
      );
     });

    $(".deleteConfirmation").click(function(){
      var _this = $(this);
      var _action = _this.attr("data-url");
      $("#deleteWfForm").attr("action", _action);
      $("#deleteWfMessage").text(_this.attr("alt"));
      $("#delete-job").modal("show");
    });

    $("#clone-btn").click(function(e){
      var _this = $('input[name=action]:checked');
      var _url = _this.attr("data-clone-url");

      $.post(_url, function(data) {
        window.location = data.url;
      });
    });

    var oTable = $('#coordinatorTable').dataTable( {
      "sPaginationType": "bootstrap",
      'iDisplayLength': 50,
      "bLengthChange": false,
      "sDom": "<'row'r>t<'row'<'span8'i><''p>>",
      "aoColumns": [
        { "bSortable": false },
        null,
        null,
        null,
        null,
        null,
        { "sType": "date" },
        null
      ],
      "aaSorting": [[ 4, "desc" ]],
      "oLanguage": {
            "sEmptyTable":     "${_('No data available in table')}",
            "sInfo":           "${_('Showing _START_ to _END_ of _TOTAL_ entries')}",
            "sInfoEmpty":      "${_('Showing 0 to 0 of 0 entries')}",
            "sInfoFiltered":   "${_('(filtered from _MAX_ total entries)')}",
            "sZeroRecords":    "${_('No matching records found')}",
            "oPaginate": {
                "sFirst":    "${_('First')}",
                "sLast":     "${_('Last')}",
                "sNext":     "${_('Next')}",
                "sPrevious": "${_('Previous')}"
            }
        }
    });

    $('#filterInput').keydown(function(e) {
      if (e.which == 13) {
        e.preventDefault();
        return false;
      }
    });

    $("#filterInput").keyup(function() {
      oTable.fnFilter($(this).val());
    });

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>

${commonfooter(messages)}
