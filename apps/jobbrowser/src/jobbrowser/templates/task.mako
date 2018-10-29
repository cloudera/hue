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

${ commonheader(_('Job Task: %(taskId)s') % dict(taskId=task.taskId_short), "jobbrowser", user, request) | n,unicode }
${ comps.menubar() }

<link href="${ static('jobbrowser/css/jobbrowser.css') }" rel="stylesheet">

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <div class="sidebar-nav" style="padding-top: 0">
        <ul class="nav nav-list">
          <li class="nav-header">${_('Task ID')}</li>
          <li class="white truncate-text" title="${task.taskId_short}">${task.taskId_short}</li>
          <li class="nav-header">${_('Job')}</li>
          <li><a href="${url('jobbrowser.views.single_job', job=joblnk.jobId)}" class="truncate-text" title="${joblnk.jobId_short}">${joblnk.jobId_short}</a></li>
          <li class="nav-header">${_('Status')}</li>
          <li class="white">
            % if task.state.lower() == 'running' or task.state.lower() == 'pending':
                <span class="label label-warning">${task.state.lower()}</span>
            % elif task.state.lower() == 'succeeded':
                <span class="label label-success">${task.state.lower()}</span>
            % else:
                <span class="label">${task.state.lower()}</span>
            % endif
          </li>
      </ul>
    </div>
  </div>
    <div class="span10">
      <div class="card card-small">
        <h1 class="card-heading simple">${_('Job Task: %(taskId)s') % dict(taskId=task.taskId_short)}</h1>
        <div class="card-body">
          <p>
            <ul class="nav nav-tabs">
              <li class="active"><a href="#attempts" data-toggle="tab">${_('Attempts')}</a></li>
              <li><a href="#metadata" data-toggle="tab">${_('Metadata')}</a></li>
              <li><a href="#counters" data-toggle="tab">${_('Counters')}</a></li>
            </ul>

            <div class="tab-content">
              <div class="tab-pane active" id="attempts">
                <table id="attemptsTable" class="table table-condensed">
                  <thead>
                    <tr>
                      <th>${_('Logs')}</th>
                      <th>${_('Attempt ID')}</th>
                      <th>${_('Progress')}</th>
                      <th>${_('State')}</th>
                      <th>${_('Task Tracker')}</th>
                      <th>${_('Start Time')}</th>
                      <th>${_('End Time')}</th>
                      % if task.is_mr2:
                        <th>${_('Node Address')}</th>
                      %endif
                      <th>${_('Phase')}</th>
                      % if not task.is_mr2:
                        <th>${_('Shuffle Finish')}</th>
                        <th>${_('Sort Finish')}</th>
                        <th>${_('Map Finish')}</th>
                      % endif
                    </tr>
                  </thead>
                  <tbody>
                  % for attempt in task.attempts:
                    <tr>
                      <td data-row-selector-exclude="true"><a href="${ url('single_task_attempt_logs', job=joblnk.jobId, taskid=task.taskId, attemptid=attempt.attemptId) }" data-row-selector-exclude="true"><i class="fa fa-tasks"></i></a></td>
                      <td><a title="${_('View this attempt')}" href="${ url('single_task_attempt', job=joblnk.jobId, taskid=task.taskId, attemptid=attempt.attemptId) }" data-row-selector="true">${attempt.attemptId_short}</a></td>
                      <td>${"%d" % (attempt.progress * 100)}%</td>
                      <td><span class="status_link ${attempt.state}">${attempt.state}</span></td>
                      <td>
                        % if task.is_mr2:
                          ${ comps.get_container_link(task.state, attempt.nodeHttpAddress, attempt.taskTrackerId) }
                        % else:
                          <a href="/jobbrowser/trackers/${attempt.taskTrackerId}" class="task_tracker_link">${attempt.taskTrackerId}</a>
                        % endif
                      </td>
                      <td>${attempt.startTimeFormatted}</td>
                      <td>${attempt.finishTimeFormatted}</td>
                      % if task.is_mr2:
                        <td>${attempt.nodeHttpAddress}</td>
                      % endif
                      <td>${attempt.phase}</td>
                      % if not task.is_mr2:
                        <td>${attempt.shuffleFinishTimeFormatted}</td>
                        <td>${attempt.sortFinishTimeFormatted}</td>
                        <td>${attempt.mapFinishTimeFormatted}</td>
                      % endif
                    </tr>
                  % endfor
                  </tbody>
                </table>
              </div>
              <div id="metadata" class="tab-pane">
                <table id="metadataTable" class="table table-condensed">
                  <thead>
                    <tr>
                      <th>${_('Name')}</th>
                      <th>${_('Value')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>${_('Task id')}</td>
                      <td>${task.taskId}</td>
                    </tr>
                    <tr>
                      <td>${_('Type')}</td>
                      <td>${task.taskType}</td>
                    </tr>
                    <tr>
                      <td>${_('JobId')}</td>
                      <td><a href="${url('jobbrowser.views.single_job', job=joblnk.jobId)}" title="${_('View this job')}">${joblnk.jobId}</a></td>
                    </tr>
                    <tr>
                      <td>${_('State')}</td>
                      <td>${task.state}</td>
                    </tr>
                    <tr>
                      <td>${_('Status')}</td>
                      <td>${task.mostRecentState}</td>
                    </tr>
                    <tr>
                      <td>${_('Start Time')}</td>
                      <td>${task.startTimeFormatted}</td>
                    </tr>
                    <tr>
                      <td>${_('Execution Start Time')}</td>
                      <td>${task.execStartTimeFormatted}</td>
                    </tr>
                    <tr>
                      <td>${_('Execution Finish Time')}</td>
                      <td>${task.execFinishTimeFormatted}</td>
                    </tr>
                    <tr>
                      <td>${_('Progress')}</td>
                      <td>${"%d" % (task.progress * 100)}%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div id="counters" class="tab-pane">
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
    $("#attemptsTable").dataTable({
      "bPaginate": false,
      "bLengthChange": false,
      "bInfo": false,
      "bFilter": false,
      "aaSorting": [
        [ 1, "asc" ]
      ],
      "oLanguage": {
        "sEmptyTable": "${_('No data available')}",
        "sZeroRecords": "${_('No matching records')}",
      }
    });

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

    $("a[data-row-selector='true']").jHueRowSelector();
  });
</script>


${ commonfooter(request, messages) | n,unicode }
