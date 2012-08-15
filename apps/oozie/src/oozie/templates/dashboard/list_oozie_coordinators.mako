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

${commonheader(_("Oozie App"), "oozie", "100px")}
${layout.menubar(section='dashboard')}


<div class="container-fluid">
  ${ layout.dashboard_sub_menubar(section='coordinators') }

  <div class="well hueWell">
    <form>
      ${ _('Filter:') } <input id="filterInput" class="input-xlarge search-query" placeholder="Search for username, name, etc...">

      <span class="pull-right">
        <span style="padding-right:10px;float:left">
        ${ _('Show only') }
         <a class="btn btn-submitter btn-info active">
          <span class="btn-submitter">${ _('Mine') }</span>
          <span class="btn-submitter hide">${ _('All') }</span>
         </a>
        ${ _('from the last') }
        </span>
        <span class="btn-group" style="float:left">
          <a class="btn btn-date btn-info">1</a>
          <a class="btn btn-date btn-info">7</a>
          <a class="btn btn-date btn-info">15</a>
          <a class="btn btn-date btn-info">30</a>
        </span>
        <span style="float:left;padding-left:10px;padding-right:10px;margin-top:3px">${ _('days with status') }</span>
        <span class="btn-group" style="float:left;">
	      <a class="btn btn-status btn-success">Succeeded</a>
	      <a class="btn btn-status btn-warning">Running</a>
	      <a class="btn btn-status btn-danger">Killed</a>
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
        %for job in jobs['running_jobs']:
          <tr>
            <td>${ utils.format_date(job.endTime) }</td>
            <td>
              <span class="label ${ utils.get_status(job.status) }">
                ${ job.status }
              </span>
            </td>
            <td>${ job.appName }</td>
            <td>${ job.get_progress() }%</td>
            <td>${ job.user }</td>
            <td><a href="${ job.get_absolute_url() }" data-row-selector="true"></a>${ job.id }</td>
            <td>
               <a type="button" class="btn manage-oozie-job-btn" data-url="${ url('oozie:manage_oozie_jobs', job_id=job.id, action='kill') }">
                 ${ _('Kill') }
               </button>
           </td>
          </tr>
        %endfor
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
        %for job in jobs['completed_jobs']:
          <tr>
            <td>${ utils.format_date(job.endTime) }</td>
            <td>
              <span class="label
               % if job.status == 'SUCCEEDED':
                 label-success
               % elif job.status == 'RUNNING':
                  label-warning
               % else:
                 label-important
               % endif
               ">
                ${job.status}
              </span>
            </td>
            <td>${ job.appName }</td>
            <td>-</td>
            <td>${job.user}</td>
            <td><a href="${ job.get_absolute_url() }" data-row-selector="true"></a>${ job.id }</td>
          </tr>
        %endfor
      </tbody>
     </table>
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
            null,
            null,
            null,
            { "bSortable": false }
        ],
        "aaSorting": [[ 0, "desc" ]]
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
            null,
            null,
            null
        ],
        "aaSorting": [[ 0, "desc" ]]
    });


    $("#filterInput").keyup(function() {
        runningTable.fnFilter($(this).val());
        completedTable.fnFilter($(this).val());

        hash = "#";

        if ($("a.btn-date.active").length > 0) {
          hash += "date=" + $("a.btn-date.active").text();
        }

        window.location.hash = hash;
    });


    $("a.btn-status").click(function() {
       $(this).toggleClass('active');
        $("#filterInput").keyup();
    });

    $("a.btn-date").click(function() {
      $("a.btn-date").not(this).removeClass('active');
      $(this).toggleClass('active');
      $("#filterInput").keyup();
    });

    $("a.btn-submitter").click(function() {
      $("a.btn-submitter").toggleClass('active');
      $("span.btn-submitter").toggleClass('hide');
      $("#filterInput").keyup();
    });

    $.fn.dataTableExt.afnFiltering.push(
      function(oSettings, aData, iDataIndex) {

        urlHashes = ""

        statusBtn = $('a.btn-status.active');
        statusFilter = true;
        if (statusBtn.length > 0) {
          statuses = []
         $.each(statusBtn.contents(), function() {
            statuses.push($(this).text());
          });
          statusFilter = aData[1].match(RegExp(statuses.join('|'), "i")) != null;
        }

        dateBtn = $('a.btn-date.active');
        dateFilter = true;
        if (dateBtn.length > 0) {
          minAge = new Date() - parseInt(dateBtn.text()) * 1000 * 60 * 60 * 24;
          dateFilter = Date.parse(aData[0]) >= minAge;
        }

        submitterBtn = $('a.btn-submitter.active');
        submitterFilter = true;
        if (submitterBtn.length > 0) {
          submitterFilter = aData[4] == '${ user }';
        }

        return statusFilter && dateFilter && submitterFilter;
      }
    );

    $("a[data-row-selector='true']").jHueRowSelector();

    $(".manage-oozie-job-btn").click(function() {
       // are you sure?
       var row = $(this).closest("tr");
       $.post($(this).attr("data-url"),
          function(response) {
            if (response['status'] != 0) {
              alert('Problem :' + response['data']);
            } else {
              $.jHueNotify.error('Killed !')
              row.remove();
            }
          }
        );
        return false;
    });
  });
</script>

${commonfooter(messages)}
