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
<%
  from jobbrowser.views import get_state_link
%>

<%namespace name="comps" file="jobbrowser_components.mako" />

  ${comps.header("Task View: Job: " + jobid, toolbar=False)}
  <%def name="selected(val, state)">
  %   if val is not None and state is not None and val in state:
        selected="true"
  %   endif
  </%def>
  <%def name="pageref(num)">
    href="?page=${num}&${filter_params}"
  </%def>
  <%def name="prevpage()">
    ${pageref(page.previous_page_number())}
  </%def>
  <%def name="nextpage()">
    ${pageref(page.next_page_number())}
  </%def>
  <%def name="toppage()">
    ${pageref(1)}
  </%def>
  <%def name="bottompage()">
    ${pageref(page.num_pages())}
  </%def>


  <div id="job_browser_task_list" class="view">
    <h1 class="ccs-hidden">Tasks for Job ${jobid}</h1>
    <div class="toolbar">
      <a href="/jobbrowser/jobs/"><img src="/jobbrowser/static/art/icon_large.png" class="jt_icon"/></a>
      <div class="jtv_nav">
        <div class="ccs-inline">
          Showing ${page.start_index()} to ${page.end_index()} of ${page.total_count()} tasks
        </div>
        <div class="jtv_offset_controls ccs-inline">
          <a title="Beginning of File" class="jtv_offset_begin" ${toppage()}>Beginning of File</a>
          <a title="Previous Block" class="jtv_offset_previous" ${prevpage()}>Previous Block</a>
          <div class="jtv_nav_pages">page <span class="jtv_page">${page.number} of ${page.num_pages()}</span></div>
          <a title="Next Block" class="jtv_offset_next" ${nextpage()}>Next Block</a>
          <a title="End of File" class="jtv_offset_end" ${bottompage()}>End of File</a>
        </div>

      </div>
      <ul class="jt_filters">
        <form class="jtv_filter_form submit_on_change" method="get" action="/jobbrowser/jobs/${jobid}/tasks">
          <li class="ccs-inline">
            <select name="taskstate">
              <option value="">All states</option>
              <option value="succeeded" ${selected('succeeded', taskstate)}>succeeded</option>
              <option value="running" ${selected('running', taskstate)}>running</option>
              <option value="failed" ${selected('failed', taskstate)}>failed</option>
              <option value="killed" ${selected('killed', taskstate)}>killed</option>
              <option value="pending" ${selected('pending', taskstate)}>pending</option>
            </select>
          </li>
          <li class="ccs-inline">
            <select name="tasktype">
              <option value="">All types</option>
              <option value="map" ${selected('map', tasktype)}>maps</option>
              <option value="reduce" ${selected('reduce', tasktype)}>reduces</option>
              <option value="job_cleanup" ${selected('job_cleanup', tasktype)}>cleanups</option>
              <option value="job_setup" ${selected('job_setup', tasktype)}>setups</option>
            </select>
          </li>
          <li class="ccs-inline">
            <input type="text" name="tasktext" class="jtv_filter" data-filters="OverText" title="text filter"
              % if tasktext:
                value="${tasktext}"
              % endif
            />
          </li>
        </form>
      </ul>
    </div>
    <table class="ccs-data_table" cellpadding="0" cellspacing="0">
      <thead>
         <tr>
           <th>Task ID</th>
           <th>Type</th>
           <th>Progress</th>
           <th>Status</th>
           <th>State</th>
           <th>Start Time</th>
           <th>End Time</th>
           <th>View Attempts</th>
        </tr>
      </thead>
      <tbody>
        %for t in page.object_list:
         <tr>
            <td>${t.taskId_short}</td>
            <td>${t.taskType}</td>
            <td>${"%d" % (t.progress * 100)}%</td>
            <td><a href="${url('jobbrowser.views.tasks', jobid=jobid)}?${get_state_link(request, 'taskstate', t.state.lower())}"
                  title="Show only ${t.state.lower()} tasks"
                  class="frame_tip status_link ${t.state.lower()}">${t.state.lower()}</a></td>
            <td>${t.mostRecentState}</td>
            <td>${t.execStartTimeFormatted}</td>
            <td>${t.execFinishTimeFormatted}</td>
            <td><a href="/jobbrowser/jobs/${jobid}/tasks/${t.taskId}" class="jt_slide_right">Attempts</a></td>
         </tr>
        %endfor
      </tbody>
    </table>
  ${comps.footer()}
