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

${commonheader(_('Task Attempt: %(attemptId)s - Job Browser') % dict(attemptId=attempt.attemptId), "jobbrowser", user)}
<div class="container-fluid">
    <h1>${_('Task Attempt: %(attemptId)s - Job Browser') % dict(attemptId=attempt.attemptId)}</h1>
    <div class="row-fluid">
        <div class="span2">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('Attempt ID')}</li>
                    <li>${attempt.attemptId_short}</li>
                    <li class="nav-header">${_('Task')}</li>
                    <li><a href="${url('jobbrowser.views.single_task', jobid=joblnk.jobId, taskid=taskid)}" title="${_('View this task')}">${task.taskId_short}</a>
                    </li>
                    <li class="nav-header">${_('Job')}</li>
                    <li><a href="${url('jobbrowser.views.single_job', jobid=joblnk.jobId)}" title="${_('View this job')}">${joblnk.jobId_short}</a></li>
                    <li class="nav-header">${_('Status')}</li>
                    <li>
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
            <ul id="tabs" class="nav nav-tabs">
                <li class="active"><a href="#metadata" data-toggle="tab">${_('Metadata')}</a></li>
                <li><a href="#counters" data-toggle="tab">${_('Counters')}</a></li>
                <li><a href="${ url('jobbrowser.views.single_task_attempt_logs', jobid=task.jobId, taskid=task.taskId, attemptid=attempt.attemptId) }">${_('Logs')}</a></li>
            </ul>

            <div class="tab-content">
                <div class="tab-pane active" id="metadata">
                    <table id="metadataTable" class="table table-striped table-condensed">
                        <thead>
                        <tr>
                            <th>${_('Name')}</th>
                            <th>${_('Value')}</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr>
                            <td>${_('Attempt ID')}</td>
                            <td>${attempt.attemptId}</td>
                        </tr>
                        <tr>
                            <td>${_('Task ID')}</td>
                            <td><a href="${url('jobbrowser.views.single_task', jobid=joblnk.jobId, taskid=taskid)}" title="${_('View this task')}">${task.taskId}</a></td>
                        </tr>
                        <tr>
                            <td>${_('Task Type')}</td>
                            <td>${task.taskType}</td>
                        </tr>
                        <tr>
                            <td>${_('JobId')}</td>
                            <td><a href="${url('jobbrowser.views.single_job', jobid=joblnk.jobId)}" title="${_('View this job')}">${joblnk.jobId}</a></td>
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
                            <td><a href="/jobbrowser/trackers/${attempt.taskTrackerId}">${attempt.taskTrackerId}</a></td>
                        </tr>
                        <tr>
                            <td>${_('Phase')}</td>
                            <td>${attempt.phase}</td>
                        </tr>
                        <tr>
                            <td>${_('Output Size')}</td>
                            <td>${attempt.outputSize}</td>
                        </tr>
                        </tbody>
                    </table>
                </div>

                <div class="tab-pane" id="counters">
                    ${comps.task_counters(task.counters)}
                </div>
            </div>
        </div>
    </div>
</div>

<script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
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

        if (window.location.hash != null && window.location.hash.length > 1){
            $('#tabs a[href="#'+window.location.hash.substring(2)+'"]').tab('show');
        }
    });
</script>
${commonfooter(messages)}
