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
${ layout.menubar(section='dashboard') }


<div class="container-fluid">
  ${ layout.dashboard_sub_menubar(section='workflows') }

  <div class="well hueWell">
    <form>
      ${ _('Filter:') } <input type="text" id="filterInput" class="input-xlarge search-query" placeholder="${ _('Search for username, name, etc...') }">

      <span class="pull-right">
        <span style="padding-right:10px;float:left;margin-top:3px">
        ${ _('Show only') }
        </span>
        <span class="btn-group" style="float:left">
          <a class="btn btn-date btn-info" data-value="1">${ _('1') }</a>
          <a class="btn btn-date btn-info" data-value="7">${ _('7') }</a>
          <a class="btn btn-date btn-info" data-value="15">${ _('15') }</a>
          <a class="btn btn-date btn-info" data-value="30">${ _('30') }</a>
        </span>
        <span style="float:left;padding-left:10px;padding-right:10px;margin-top:3px">${ _('days with status') }</span>
        <span class="btn-group" style="float:left;">
          <a class="btn btn-status btn-success" data-value='SUCCEEDED'>${ _('Succeeded') }</a>
          <a class="btn btn-status btn-warning" data-value='RUNNING'>${ _('Running') }</a>
          <a class="btn btn-status btn-danger" data-value='KILLED'>${ _('Killed') }</a>
        </span>
      </span>
   </form>
  </div>

  <div style="min-height:200px">
    <h1>${ _('Running') }</h1>
    <table class="table table-condensed" id="running-table">
      <thead>
        <tr>
          <th width="10%">${ _('Submission') }</th>
          <th width="10%">${ _('Status') }</th>
          <th width="30%">${ _('Name') }</th>
          <th width="10%">${ _('Progress') }</th>
          <th width="15%">${ _('Submitter') }</th>
          <th width="15%">${ _('Id') }</th>
          <th width="10%">${ _('Action') }</th>
        </tr>
      </thead>
      <tbody>
        % for job in jobs['running_jobs']:
          <tr>
            <td>${ utils.format_date(job.lastModTime) }</td>
            <td>
              <span class="label ${ utils.get_status(job.status) }">
                ${ job.status }
              </span>
            </td>
            <td>${ job.appName }</td>
            <td data-sort-value="${ job.get_progress() }">${ job.get_progress() }%</td>
            <td>${ job.user }</td>
            <td><a href="${ job.get_absolute_url() }" data-row-selector="true"></a>${ job.id }</td>
            <td>
              % if has_job_edition_permission(job, user):
	            <a title="${_('Kill %(workflow)s') % dict(workflow=job.id)}"
	              class="btn small confirmationModal"
	              alt="${ _('Are you sure you want to kill workflow %s?') %  job.id }"
	              href="javascript:void(0)"
	              data-url="${ url('oozie:manage_oozie_jobs', job_id=job.id, action='kill') }"
	              data-message="${ _('The workflow was killed!') }"
	              data-confirmation-message="${ _('Are you sure you\'d like to kill this job?') }">
	                ${ _('Kill') }
	            </a>
              % endif
            </td>
          </tr>
        % endfor
      </tbody>
    </table>
  </div>

  <div>
    <h1>${ _('Completed') }</h1>
    <table class="table table-condensed" id="completed-table">
      <thead>
        <tr>
          <th width="10%">${ _('Completion') }</th>
          <th width="10%">${ _('Status') }</th>
          <th width="35%">${ _('Name') }</th>
          <th width="10%">${ _('Duration') }</th>
          <th width="15%">${ _('Submitter') }</th>
          <th width="20%">${ _('Id') }</th>
        </tr>
      </thead>
      <tbody>
        % for job in jobs['completed_jobs']:
          <tr>
            <td>${ utils.format_date(job.endTime) }</td>
            <td>
              <span class="label
               % if job.status == 'SUCCEEDED':
                 label-success
               % elif job.is_running():
                  label-warning
               % else:
                 label-important
               % endif
               ">
                ${ job.status }
              </span>
            </td>
            <td>${ job.appName }</td>
            <td data-sort-value="${ utils.job_duration(job) }">${ utils.format_job_duration(job) }</td>
            <td>${ job.user }</td>
            <td><a href="${ job.get_absolute_url() }" data-row-selector="true"></a>${ job.id }</td>
          </tr>
        % endfor
      </tbody>
     </table>
   </div>
</div>


<div id="confirmation" class="modal hide">
  <div class="modal-header">
    <a href="#" class="close" data-dismiss="modal">&times;</a>
    <h3 class="message"></h3>
  </div>
  <div class="modal-footer">
    <a class="btn primary" href="javascript:void(0);">${_('Yes')}</a>
    <a href="#" class="btn secondary" data-dismiss="modal">${_('No')}</a>
  </div>
</div>


<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript" charset="utf-8">
  $(document).ready(function() {
    var runningTable = $('#running-table').dataTable( {
      'sPaginationType': 'bootstrap',
      'iDisplayLength': 50,
      "bLengthChange": false,
      "sDom": "<'row'r>t<'row'<'span6'i><''p>>",
      "aoColumns": [
           { "sType": "date" },
            null,
            null,
            { "sSortDataType": "dom-sort-value", "sType": "numeric" },
            null,
            null,
            { "bSortable": false }
        ],
        "aaSorting": [[ 0, "desc" ]],
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

    var completedTable = $('#completed-table').dataTable( {
      'sPaginationType': 'bootstrap',
      'iDisplayLength': 50,
      "bLengthChange": false,
      "sDom": "<'row'r>t<'row'<'span6'i><''p>>",
      "aoColumns": [
            { "sType": "date" },
            null,
            null,
            { "sSortDataType": "dom-sort-value", "sType": "numeric" },
            null,
            null
        ],
        "aaSorting": [[ 0, "desc" ]],
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
      runningTable.fnFilter($(this).val());
      completedTable.fnFilter($(this).val());
      drawTable();
    });


    $("a.btn-status").click(function() {
      $(this).toggleClass('active');
      drawTable();
    });

    $("a.btn-date").click(function() {
      $("a.btn-date").not(this).removeClass('active');
      $(this).toggleClass('active');
      drawTable();
    });

    function drawTable(){
      runningTable.fnDraw();
      completedTable.fnDraw();

      hash = "#";
      if ($("a.btn-date.active").length > 0) {
        hash += "date=" + $("a.btn-date.active").text();
      }
      window.location.hash = hash;
    }

    $.fn.dataTableExt.afnFiltering.push(
      function(oSettings, aData, iDataIndex) {
        urlHashes = ""

        statusBtn = $('a.btn-status.active');
        statusFilter = true;
        if (statusBtn.length > 0) {
          statuses = []
          $.each(statusBtn, function() {
            statuses.push($(this).attr('data-value'));
          });
          statusFilter = aData[1].match(RegExp(statuses.join('|'), "i")) != null;
        }

        dateBtn = $('a.btn-date.active');
        dateFilter = true;
        if (dateBtn.length > 0) {
          minAge = new Date() - parseInt(dateBtn.attr('data-value')) * 1000 * 60 * 60 * 24;
          dateFilter = Date.parse(aData[0]) >= minAge;
        }

        return statusFilter && dateFilter;
      }
    );

    $("a[data-row-selector='true']").jHueRowSelector();

    $(".confirmationModal").click(function(){
      var _this = $(this);
      $("#confirmation .message").text(_this.attr("data-confirmation-message"));
      $("#confirmation").modal("show");
      $("#confirmation a.primary").click(function() {
        _this.trigger('confirmation');
      });
    });

    $(".confirmationModal").bind('confirmation', function() {
      var _this = this;
      $.post($(this).attr("data-url"),
        { 'notification': $(this).attr("data-message") },
        function(response) {
          if (response['status'] != 0) {
            $.jHueNotify.error("${ _('Problem: ') }" + response['data']);
          } else {
            window.location.reload();
          }
        }
      );
      return false;
    });

  });
</script>

${ commonfooter(messages) }
