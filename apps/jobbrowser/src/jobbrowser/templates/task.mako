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

${commonheader(_('Job Task: %(taskId)s - Job Browser') % dict(taskId=task.taskId), "jobbrowser", user)}

<div class="container-fluid">
    <h1>${_('Job Task: %(taskId)s - Job Browser') % dict(taskId=task.taskId)}</h1>
    <div class="row-fluid">
        <div class="span2">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('Task ID')}</li>
                    <li>${task.taskId_short}</li>
                    <li class="nav-header">${_('Job')}</li>
                    <li><a href="${url('jobbrowser.views.single_job', jobid=joblnk.jobId)}" title="${_('View this job')}">${joblnk.jobId_short}</a></li>
                    <li class="nav-header">${_('Status')}</li>
                    <li>
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
            <ul class="nav nav-tabs">
                <li class="active"><a href="#attempts" data-toggle="tab">${_('Attempts')}</a></li>
                <li><a href="#metadata" data-toggle="tab">${_('Metadata')}</a></li>
                <li><a href="#counters" data-toggle="tab">${_('Counters')}</a></li>
            </ul>

            <div class="tab-content">
                <div class="tab-pane active" id="attempts">
                    <table id="attemptsTable" class="table table-striped table-condensed">
                        <thead>
                        <tr>
                            <th>${_('Logs')}</th>
                            <th>${_('Attempt ID')}</th>
                            <th>${_('Progress')}</th>
                            <th>${_('State')}</th>
                            <th>${_('Task Tracker')}</th>
                            <th>${_('Start Time')}</th>
                            <th>${_('End Time')}</th>
                            <th>${_('Output Size')}</th>
                            <th>${_('Phase')}</th>
                            <th>${_('Shuffle Finish')}</th>
                            <th>${_('Sort Finish')}</th>
                            <th>${_('Map Finish')}</th>
                        </tr>
                        </thead>
                        <tbody>
                                % for attempt in task.attempts:
                                <tr>
                                    <td data-row-selector-exclude="true"><a href="${ url('jobbrowser.views.single_task_attempt_logs', jobid=joblnk.jobId, taskid=task.taskId, attemptid=attempt.attemptId) }" data-row-selector-exclude="true"><i class="icon-tasks"></i></a></td>
                                    <td><a title="${_('View this attempt')}"
                                           href="${ url('jobbrowser.views.single_task_attempt', jobid=joblnk.jobId, taskid=task.taskId, attemptid=attempt.attemptId) }" data-row-selector="true">${attempt.attemptId_short}</a></td>
                                    <td>${"%d" % (attempt.progress * 100)}%</td>
                                    <td><span class="status_link ${attempt.state}">${attempt.state}</span></td>
                                    <td><a href="/jobbrowser/trackers/${attempt.taskTrackerId}" class="task_tracker_link">${attempt.taskTrackerId}</a></td>
                                    <td>${attempt.startTimeFormatted}</td>
                                    <td>${attempt.finishTimeFormatted}</td>
                                    <td>${attempt.outputSize}</td>
                                    <td>${attempt.phase}</td>
                                    <td>${attempt.shuffleFinishTimeFormatted}</td>
                                    <td>${attempt.sortFinishTimeFormatted}</td>
                                    <td>${attempt.mapFinishTimeFormatted}</td>
                                </tr>
                                % endfor
                        </tbody>
                    </table>
                </div>
                <div id="metadata" class="tab-pane">
                    <table id="metadataTable" class="table table-striped table-condensed">
                        <thead>
                        <th>${_('Name')}</th>
                        <th>${_('Value')}</th>
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
                            <td><a href="${url('jobbrowser.views.single_job', jobid=joblnk.jobId)}" title="${_('View this job')}">${joblnk.jobId}</a></td>
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
                    ${comps.task_counters(task.counters)}
                </div>
            </div>
        </div>
    </div>
</div>

<script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
        $("#attemptsTable").dataTable({
            "bPaginate": false,
            "bLengthChange": false,
            "bInfo": false,
            "bFilter": false,
            "aaSorting": [[ 1, "asc" ]]
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
            ]
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
            ]
        });

        $("a[data-row-selector='true']").jHueRowSelector();
    });
</script>


${commonfooter(messages)}
