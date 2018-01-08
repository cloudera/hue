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
<%namespace name="comps" file="jobbrowser_components.mako" />

${ commonheader(_('Task Attempt: %(attemptId)s') % dict(attemptId=attempt.attemptId_short), "jobbrowser", user, request) | n,unicode }
${ comps.menubar() }

<link href="${ static('jobbrowser/css/jobbrowser.css') }" rel="stylesheet">

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav" style="padding-top: 0">
        <ul class="nav nav-list">
          <li class="nav-header">${_('Attempt ID')}</li>
          <li class="white truncate-text" title="${attempt.attemptId_short}">${attempt.attemptId_short}</li>
          <li class="nav-header">${_('Task')}</li>
          <li><a href="${url('jobbrowser.views.single_task', job=joblnk.jobId, taskid=taskid)}"
                 class="truncate-text" title="${task.taskId_short}">${task.taskId_short}</a>
          </li>
          <li class="nav-header">${_('Job')}</li>
          <li><a href="${url('jobbrowser.views.single_job', job=joblnk.jobId)}"
                 class="truncate-text" title="${joblnk.jobId_short}">${joblnk.jobId_short}</a></li>
          <li class="nav-header">${_('Status')}</li>
          <li class="white">
            <%
              status = attempt.state.lower()
            %>
            % if status == 'running' or status == 'pending':
                <span class="label label-warning">${status}</span>
            % elif status == 'succeeded':
                <span class="label label-success">${status}</span>
            % else:
                <span class="label">${status}</span>
            % endif
          </li>
        </ul>
      </div>
    </div>

    <div class="span10">
      <div class="card card-small">
        <h1 class="card-heading simple">${_('Task Attempt: %(attemptId)s') % dict(attemptId=attempt.attemptId_short)}</h1>

        <div class="card-body">
          <p>
          <ul id="tabs" class="nav nav-tabs">
            <li class="active"><a href="#metadata" data-toggle="tab">${_('Metadata')}</a></li>
            <li><a href="#counters" data-toggle="tab">${_('Counters')}</a></li>
            <li><a
                href="${ url('single_task_attempt_logs', job=task.jobId, taskid=task.taskId, attemptid=attempt.attemptId) }">${_('Logs')}</a>
            </li>
          </ul>

          <div class="tab-content">
            <div class="tab-pane active" id="metadata">
              <table id="metadataTable" class="table table-condensed">
                <thead>
                <tr>
                  <th>${_('Name')}</th>
                  <th>${_('Value')}</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                  <td>${_('Attempt ID')}</td>
                  <td>${attempt.attemptId_short}</td>
                </tr>
                <tr>
                  <td>${_('Task ID')}</td>
                  <td><a href="${url('jobbrowser.views.single_task', job=joblnk.jobId, taskid=taskid)}"
                         title="${_('View this task')}">${task.taskId_short}</a></td>
                </tr>
                <tr>
                  <td>${_('Task Type')}</td>
                  <td>${task.taskType}</td>
                </tr>
                <tr>
                  <td>${_('JobId')}</td>
                  <td><a href="${url('jobbrowser.views.single_job', job=joblnk.jobId)}"
                         title="${_('View this job')}">${joblnk.jobId_short}</a></td>
                </tr>
                <tr>
                  <td>${_('State')}</td>
                  <td>${attempt.state}</td>
                </tr>
                <tr>
                  <td>${_('Start Time')}</td>
                  <td>${attempt.startTimeFormatted}</td>
                </tr>
                <tr>
                  <td>${_('Finish Time')}</td>
                  <td>${attempt.finishTimeFormatted}</td>
                </tr>
                <tr>
                  <td>${_('Progress')}</td>
                  <td>${"%d" % (attempt.progress * 100)}%</td>
                </tr>
                <tr>
                  <td>${_('Task Tracker')}</td>
                  <td>
                      % if attempt.is_mr2:
                        ${ comps.get_container_link(status, attempt.nodeHttpAddress, attempt.taskTrackerId) }
                      % else:
                        <a href="/jobbrowser/trackers/${attempt.taskTrackerId}"
                           class="task_tracker_link">${attempt.taskTrackerId}</a>
                      % endif
                  </td>
                </tr>
                <tr>
                  <td>${_('Phase')}</td>
                  <td>${attempt.phase}</td>
                </tr>
                <tr>
                  <td>${_('Output Size')}</td>
                  <td>${attempt.outputSize}</td>
                </tr>
                % if not attempt.is_mr2:
                <tr>
                  <td>${_('Shuffle Finish')}</td>
                  <td>${attempt.shuffleFinishTimeFormatted}</td>
                </tr>
                <tr>
                  <td>${_('Sort Finish')}</td>
                  <td>${attempt.sortFinishTimeFormatted}</td>
                </tr>
                <tr>
                  <td>${_('Map Finish')}</td>
                  <td>${attempt.mapFinishTimeFormatted}</td>
                </tr>
                % endif
                % if attempt.is_mr2:
                  <tr>
                    <td>${_('Node Address')}</td>
                    <td>${attempt.nodeHttpAddress}</td>
                  </tr>
                % endif
                </tbody>
              </table>
            </div>

            <div class="tab-pane" id="counters">
                % if task.is_mr2:
                        ${ comps.task_counters_mr2(task.counters) }
                % else:
                        ${ comps.task_counters(task.counters) }
                % endif
            </div>
          </div>
          </p>
        </div>
      </div>
    </div>
  </div>
</div>

<script src="${ static('jobbrowser/js/utils.js') }" type="text/javascript" charset="utf-8"></script>

<script type="text/javascript">
  $(document).ready(function () {
    $("#metadataTable").dataTable({
      "bPaginate": false,
      "bLengthChange": false,
      "bInfo": false,
      "bAutoWidth": false,
      "bFilter": false,
      "aoColumns": [
        { "sWidth": "30%" },
        { "sWidth": "70%" }
      ],
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sZeroRecords": "${_('No matching records')}",
      }
    });

    $(".taskCountersTable").dataTable({
      "bPaginate": false,
      "bLengthChange": false,
      "bInfo": false,
      "bFilter": false,
      "bAutoWidth": false,
      "aoColumns": [
        { "sWidth": "30%" },
        { "sWidth": "70%" }
      ],
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sZeroRecords": "${_('No matching records')}",
      }
    });

    if (window.location.hash != null && window.location.hash.length > 1) {
      $('#tabs a[href="#' + window.location.hash.substring(2).replace(/(<([^>]+)>)/ig, "") + '"]').tab('show');
    }
  });
</script>

${ commonfooter(request, messages) | n,unicode }
