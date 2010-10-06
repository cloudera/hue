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
%>

<%def name="task_table(tasks)">
  <table data-filters="HtmlTable" class="selectable sortable" cellpadding="0" cellspacing="0">
    <thead>
      <tr>
        <th>Tasks</th>
        <th colspan="2">Type</th>
      </tr>
    </thead>
    <tbody>
      % for task in tasks:
        <tr data-dblclick-delegate="{'dblclick_loads':'.view_task'}">
          <td class="task_table_id">${task.taskId_short}</td>
          <td class="task_table_type">${task.taskType}</td>
          <td class="jtask_view_col"><a class="frame_tip jtask_view jt_slide_right view_task" title="View this task"
                 href="${ url('jobbrowser.views.single_task', jobid=job.jobId, taskid=task.taskId) }">View</a></td>
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

  ${comps.header("Job: " + job.jobId + " :: Job Browser")}
    
    <div id="job_browser_job" class="view jframe_padded">
      <div class="jtv_meta_top clearfix">
        <dl>
          <dt>Job ID</dt>
          <dd>${job.jobId}</dd>
          <dt>User</dt>
          <dd>${job.user}</dd>
        </dl>
        <dl>
          <dt>Status</dt>
          <dd>${job.status.lower()}</dd>
          <dt>Output</dt>
          <dd>
          <%
            output_dir = job.conf_keys.get('mapredOutputDir', "")
            location_url = location_to_url(request, output_dir)
            basename = os.path.basename(output_dir)
            dir_name = basename.split('/')[-1]
          %>
          % if location_url != None:
            <a class="jt-output_dir" href="${location_url}" title="${output_dir}" target="FileBrowser">${dir_name}</a>
          % else:
            ${dir_name}
          % endif
          <dd>
        </dl>
        % if job.status.lower() == 'running' or job.status.lower() == 'pending':
        <dl>
          <dt>Kill Job:</dt>
          <dd>
          <a href="${url('jobbrowser.views.kill_job', jobid=job.jobId)}" class="frame_tip jt_kill confirm_and_post" title="Kill this job">kill</a>
          </dd>
        </dl>
        % endif

      </div>

      <div data-filters="Tabs">
        <ul class="tabs jtv_tabs ccs-right clearfix">
          <li><span>Tasks</span></li>
          <li><span>Metadata</span></li>
          <li><span>Counters</span></li>
        </ul>

        <ul class="tab_sections ccs-clear">
          <li>
            <div class="jt_mr_display">
              <dl class="jtv_graph">
                <dt>Maps:</dt>
                <dd>${comps.mr_graph_maps(job)}</dd>
                <dt>Reduces:</dt>
                <dd>${comps.mr_graph_reduces(job, right_border=True)}</dd>
              </dl>
            </div>
            <% 
            task_table_size = '100%'
            if failed_tasks:
              task_table_size = '49%' 
            %>
            %if failed_tasks:
            <div class="jt_task_list jt_failed_tasks ccs-inline" style="width: ${task_table_size};">
              <h3>
                <a class="ccs-right" href="${url('jobbrowser.views.tasks', jobid=job.jobId)}?taskstate=failed">view failed tasks &raquo;</a>
                Failed Tasks
              </h3>
              <div class="jt_task_list_container">
                ${task_table(failed_tasks)}
              </div>
            </div>
            %endif
            <div class="jt_task_list jt_recent_tasks ccs-inline" style="width: ${task_table_size}">
              <h3>
                <a class="ccs-right" href="${url('jobbrowser.views.tasks', jobid=job.jobId)}">View All Tasks &raquo;</a>
                Recent Tasks
              </h3>
              <div class="jt_task_list_container">
                ${task_table(recent_tasks)}
              </div>
            </div>
            
          </li>
          <li>
            <table data-filters="HtmlTable" class="jt_meta_table sortable" cellpadding="0" cellspacing="0">
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
              <tr>
                <td colspan="2" class="jt-raw_delimiter">Raw Configuration:</td>
              </tr>
              % for key, value in sorted(job.full_job_conf.items()):
                <tr>
                  <td>${key}</td>
                  <td>${value}</td>
                </tr>
              % endfor
              </tbody>
            </table>
          </li>
          <li>
            ${comps.job_counters(job.counters)}
          </li>
        </ul>
      </div>


    ${comps.footer()}
