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
  import os
  from jobbrowser.views import format_counter_name
  from filebrowser.views import location_to_url  
  from desktop.views import commonheader, commonfooter

  from django.template.defaultfilters import urlencode
  from django.utils.translation import ugettext as _
%>

<%def name="task_table(tasks)">
    <table class="taskTable table table-striped table-condensed">
        <thead>
        <tr>
            <th>${_('Logs')}</th>
            <th>${_('Tasks')}</th>
            <th>${_('Type')}</th>
        </tr>
        </thead>
        <tbody>
            % for task in tasks:
            <tr>
                <td data-row-selector-exclude="true">
                %if task.taskAttemptIds:
                    <a href="${ url('jobbrowser.views.single_task_attempt_logs', jobid=task.jobId, taskid=task.taskId, attemptid=task.taskAttemptIds[-1]) }" data-row-selector-exclude="true"><i class="icon-tasks"></i></a>
                %endif
                </td>
                <td><a title="${_('View this task')}" href="${ url('jobbrowser.views.single_task', jobid=job.jobId, taskid=task.taskId) }" data-row-selector="true">${task.taskId_short}</a></td>
                <td>${task.taskType}</td>
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
${commonheader(_('Job: %(jobId)s - Job Browser') % dict(jobId=job.jobId), "jobbrowser", user)}

<div class="container-fluid">
    <h1>${_('Job: %(jobId)s - Job Browser') % dict(jobId=job.jobId)}</h1>
    <div class="row-fluid">
        <div class="span2">
            <div class="well sidebar-nav">
                <ul class="nav nav-list">
                    <li class="nav-header">${_('Job ID')}</li>
                    <li>${job.jobId}</li>
                    <li class="nav-header">${_('User')}</li>
                    <li>${job.user}</li>
                    <li class="nav-header">${_('Status')}</li>
                    <li>
                        ${comps.get_status(job)}
                    </li>
                    <li class="nav-header">${_('Logs')}</li>
                    <li><a href="${ url('jobbrowser.views.job_single_logs', jobid=job.jobId) }">${_('View logs')}</a></li>
                    % if job.status.lower() == 'running' or job.status.lower() == 'pending':
                        <li class="nav-header">${_('Kill Job')}</li>
                        <li>
                          <a href="#" title="${_('Kill this job')}" onclick="$('#kill-job').submit()">${_('Kill this job')}</a>
                          <form id="kill-job" action="${url('jobbrowser.views.kill_job', jobid=job.jobId)}?next=${request.get_full_path()|urlencode}" method="POST"></form>
                        </li>
                    % endif
                    % if not job.is_retired:
                        <li class="nav-header">${_('Maps:')}</li>
                        <li>${comps.mr_graph_maps(job)}</li>
                        <li class="nav-header">${_('Reduces:')}</li>
                        <li>${comps.mr_graph_reduces(job)}</li>
                    % endif

                    <%
                        output_dir = job.conf_keys.get('mapredOutputDir', "")
                        location_url = location_to_url(request, output_dir)
                        basename = os.path.basename(output_dir)
                        dir_name = basename.split('/')[-1]
                    %>
                    % if dir_name != '':
                        <li class="nav-header">${_('Output')}</li>
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
                    % endif
                </ul>
            </div>
        </div>
        <div class="span10">
            <ul class="nav nav-tabs">
                <li class="active"><a href="#tasks" data-toggle="tab">${_('Tasks')}</a></li>
                <li><a href="#metadata" data-toggle="tab">${_('Metadata')}</a></li>
                % if not job.is_retired:
                <li><a href="#counters" data-toggle="tab">${_('Counters')}</a></li>
                % endif
            </ul>

            <div class="tab-content">
                <div class="tab-pane active" id="tasks">
                    % if job.is_retired:
                       ${ _('This jobs is ')} <span class="label label-warning">${ _('retired') }</span> ${ _(' and so has little information available.') }
                       <br/>
                       <br/>
                    % else:
                        %if failed_tasks:
                            <div>
                                <h3>
                                    <a href="${url('jobbrowser.views.tasks', jobid=job.jobId)}?taskstate=failed">${_('View Failed Tasks')} &raquo;</a>
                                    ${_('Failed Tasks')}
                                </h3>
                                <div>
                                ${task_table(failed_tasks)}
                                </div>
                            </div>
                        %endif
                        <div>
                            <a style="float:right;margin-right:10px" href="${url('jobbrowser.views.tasks', jobid=job.jobId)}">${_('View All Tasks')} &raquo;</a>
                            <h3>
                                ${_('Recent Tasks')}
                            </h3>
                            <div>
                                ${task_table(recent_tasks)}
                            </div>
                        </div>
                    % endif
                </div>
                <div id="metadata" class="tab-pane">
                    <div class="well hueWell">
                        <form class="form-search">
                            ${_('Filter: ')}<input type="text" id="metadataFilter" class="input-xlarge search-query" placeholder="${_('Text Filter')}">
                        </form>
                    </div>
                    <table id="metadataTable" class="table table-striped table-condensed">
                        <thead>
                            <th>${_('Name')}</th>
                            <th>${_('Value')}</th>
                        </thead>
                        <tbody>
                        <tr>
                            <td>${_('ID')}</td>
                            <td>${job.jobId}</td>
                        </tr>
                        <tr>
                            <td>${_('User')}</td>
                            <td>${job.user}</td>
                        </tr>
                        % if not job.is_retired:
                        <tr>
                            <td>${_('Maps')}</td>
                            <td>${job.finishedMaps} of ${job.desiredMaps}</td>
                        </tr>
                        <tr>
                            <td>${_('Reduces')}</td>
                            <td>${job.finishedReduces} of ${job.desiredReduces}</td>
                        </tr>
                        % endif
                        <tr>
                            <td>${_('Started')}</td>
                            <td>${job.startTimeFormatted}</td>
                        </tr>
                        % if not job.is_retired:
                        <tr>
                            <td>${_('Ended')}</td>
                            <td>${job.finishTimeFormatted}</td>
                        </tr>
                        <tr>
                            <td>${_('Duration')}</td>
                            <td>${job.duration}</td>
                        </tr>
                        % endif
                        <tr>
                            <td>${_('Status')}</td>
                            <td>${job.status}</td>
                        </tr>
                            ${rows_for_conf_vars(job.conf_keys)}

                        </tbody>
                    </table>
                    <h3>${_('Raw configuration:')}</h3>
                    <table id="rawConfigurationTable" class="table table-striped table-condensed">
                        <thead>
                        <th>${_('Name')}</th>
                        <th>${_('Value')}</th>
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
                { "sWidth": "1%", "bSortable": false },
                { "sWidth": "50%" },
                { "sWidth": "49%" }
            ],
            "aaSorting": [[ 1, "asc" ]]
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
        $("a[data-row-selector='true']").jHueRowSelector();
    });
</script>


${commonfooter(messages)}
