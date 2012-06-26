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
<%namespace name="comps" file="jobbrowser_components.mako" />
<%!
  from jobbrowser.views import format_counter_name
  from filebrowser.views import location_to_url
  import os
  import re
  from desktop.views import commonheader, commonfooter
  from django.template.defaultfilters import urlencode
%>

<%def name="task_table(tasks)">
    <table class="taskTable table table-striped table-condensed">
        <thead>
        <tr>
            <th>Tasks</th>
            <th>Type</th>
            <th>&nbsp;</th>
        </tr>
        </thead>
        <tbody>
                % for task in tasks:
                <tr>
                    <td>${task.taskId_short}</td>
                    <td>${task.taskType}</td>
                    <td>
                        <a title="View this task" href="${ url('jobbrowser.views.single_task', jobid=job.jobId, taskid=task.taskId) }">View</a>
                    </td>
                </tr>
                % endfor
        </tbody>
    </table>
</%def>
<%def name="rows_for_conf_vars(rows)">
    %  for k, v in rows.iteritems():
        <tr>
            <td>${format_counter_name(k)}</td>
        <%
            splitArray = v.split(",")
        %>
        <td>
            % for i, val in enumerate(splitArray):
            <%
                url_splitted = request.fs.urlsplit(val)
                is_hdfs_uri = bool(url_splitted[1])
            %>
            % if is_hdfs_uri:
                <%
                    if request.fs.isfile(url_splitted[2]):
                      target = "FileViewer"
                    else:
                      target = "FileBrowser"
                %>
                    <a href="${location_to_url(request, val)}" title="${val}" target="${target}">${val}</a>
                % if i != len(splitArray) - 1:
                        <br>
                % endif
            % else:
                ${val}
            % endif
            % endfor
        </td>
        </tr>
    % endfor
</%def>
${commonheader("Job: " + job.jobId + " - Job Browser", "jobbrowser")}

<div class="container-fluid">
    <h1>Job: ${job.jobId} - Job Browser</h1>
    <div class="row-fluid">
        <div class="span2">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">Job ID</li>
                    <li>${job.jobId}</li>
                    <li class="nav-header">User</li>
                    <li>${job.user}</li>
                    <li class="nav-header">Status</li>
                    <li>
                            % if job.status.lower() == 'running' or job.status.lower() == 'pending':
                                <span class="label label-warning">${job.status.lower()}</span>
                            % elif job.status.lower() == 'succeeded':
                                <span class="label label-success">${job.status.lower()}</span>
                            % else:
                                <span class="label">${job.status.lower()}</span>
                            % endif
                    </li>
                    % if job.status.lower() == 'running' or job.status.lower() == 'pending':
                            <li class="nav-header">Kill Job</li>
                            <li><a href="#" title="Kill this job" onclick="$('#kill-job').submit()">Kill this job</a>
                                <form id="kill-job" action="${url('jobbrowser.views.kill_job', jobid=job.jobId)}?next=${request.get_full_path()|urlencode}" method="POST"></form></li>
                    % endif
                    <li class="nav-header">Output</li>
                    <li>
                        <%
                            output_dir = job.conf_keys.get('mapredOutputDir', "")
                            location_url = location_to_url(request, output_dir)
                            basename = os.path.basename(output_dir)
                            dir_name = basename.split('/')[-1]
                        %>
                        % if location_url != None:
                                <a href="${location_url}" title="${output_dir}">${dir_name}</a>
                        % else:
                            ${dir_name}
                        % endif
                    </li>
                </ul>
            </div>
        </div>
        <div class="span10">
            <ul class="nav nav-tabs">
                <li class="active"><a href="#tasks" data-toggle="tab">Tasks</a></li>
                <li><a href="#metadata" data-toggle="tab">Metadata</a></li>
                <li><a href="#counters" data-toggle="tab">Counters</a></li>
            </ul>

            <div class="tab-content">
                <div class="tab-pane active" id="tasks">
                    <strong>Maps:</strong> ${comps.mr_graph_maps(job)}
                    <strong>Reduces:</strong> ${comps.mr_graph_reduces(job)}
                    %if failed_tasks:
                            <div>
                                <h3>
                                    <a href="${url('jobbrowser.views.tasks', jobid=job.jobId)}?taskstate=failed">View Failed Tasks &raquo;</a>
                                    Failed Tasks
                                </h3>
                                <div>
                                ${task_table(failed_tasks)}
                                </div>
                            </div>
                    %endif
                    <div>
                        <a style="float:right;margin-right:10px" href="${url('jobbrowser.views.tasks', jobid=job.jobId)}">View All Tasks &raquo;</a>
                        <h3>
                            Recent Tasks
                        </h3>
                        <div>
                            ${task_table(recent_tasks)}
                        </div>
                    </div>

                </div>
                <div id="metadata" class="tab-pane">
                    <div class="well hueWell">
                        <form class="form-search">
                            Filter: <input id="metadataFilter" class="input-xlarge search-query" placeholder="Text Filter">
                        </form>
                    </div>
                    <table id="metadataTable" class="table table-striped table-condensed">
                        <thead>
                        <th>Name</th>
                        <th>Value</th>
                        </thead>
                        <tbody>
                        <tr>
                            <td>ID</td>
                            <td>${job.jobId}</td>
                        </tr>
                        <tr>
                            <td>User</td>
                            <td>${job.user}</td>
                        </tr>
                        <tr>
                            <td>Maps</td>
                            <td>${job.finishedMaps} of ${job.desiredMaps}</td>
                        </tr>
                        <tr>
                            <td>Reduces</td>
                            <td>${job.finishedReduces} of ${job.desiredReduces}</td>
                        </tr>
                        <tr>
                            <td>Started</td>
                            <td>${job.startTimeFormatted}</td>
                        </tr>
                        <tr>
                            <td>Ended</td>
                            <td>${job.finishTimeFormatted}</td>
                        </tr>
                        <tr>
                            <td>Duration</td>
                            <td>${job.duration}</td>
                        </tr>
                        <tr>
                            <td>Status</td>
                            <td>${job.status}</td>
                        </tr>
                            ${rows_for_conf_vars(job.conf_keys)}

                        </tbody>
                    </table>
                    <h3>Raw configuration:</h3>
                    <table id="rawConfigurationTable" class="table table-striped table-condensed">
                        <thead>
                        <th>Name</th>
                        <th>Value</th>
                        </thead>
                        <tbody>

                                % for key, value in sorted(job.full_job_conf.items()):
                                <tr>
                                    <td width="20%">${key}</td>
                                    <td>
                                        <div class="wordbreak">
                                        ${value}
                                        </div>
                                    </td>
                                </tr>
                                % endfor
                        </tbody>
                    </table>

                </div>
                <div id="counters" class="tab-pane">
                    ${comps.job_counters(job.counters)}
                </div>
            </div>
        </div>
    </div>
</div>



<script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
        $(".taskTable").dataTable({
            "bPaginate": false,
            "bLengthChange": false,
            "bInfo": false,
            "bAutoWidth": false,
            "aoColumns": [
                { "sWidth": "40%" },
                { "sWidth": "40%" },
                { "sWidth": "20%" }
            ]
        });
        var _metadataTable = $("#metadataTable").dataTable({
            "bPaginate": false,
            "bLengthChange": false,
            "bInfo": false,
            "bAutoWidth": false,
            "aoColumns": [
                { "sWidth": "30%" },
                { "sWidth": "70%" }
            ]
        });
        var _rawConfigurationTable = $("#rawConfigurationTable").dataTable({
            "bPaginate": false,
            "bLengthChange": false,
            "bInfo": false,
            "bAutoWidth": false,
            "aoColumns": [
                { "sWidth": "30%" },
                { "sWidth": "70%" }
            ]
        });

        $("#metadataFilter").keydown(function(){
            _metadataTable.fnFilter($(this).val());
            _rawConfigurationTable.fnFilter($(this).val());
        });

        $(".jobCountersTable").dataTable({
            "bPaginate": false,
            "bLengthChange": false,
            "bInfo": false,
            "bAutoWidth": false,
            "aoColumns": [
                { "sWidth": "40%" },
                { "sWidth": "20%" },
                { "sWidth": "20%" },
                { "sWidth": "20%" }
            ]
        });

        $(".dataTables_wrapper").css("min-height","0");
        $(".dataTables_filter").hide();

    });
</script>


${commonfooter()}