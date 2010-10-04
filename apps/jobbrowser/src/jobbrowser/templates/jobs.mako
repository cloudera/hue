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
  from desktop import appmanager
  from django.template.defaultfilters import urlencode
%>
<%namespace name="comps" file="jobbrowser_components.mako" />
<%def name="get_state(option, state)">
%   if option == state:
      selected="true"
%   endif
</%def>

    % if len(jobs) > 0 or filtered:
      ${comps.header("Job Browser", toolbar=False)}
      <div id="job_browser_list" class="view">
        <h1 class="ccs-hidden">Jobs</h1>
        <div class="toolbar">
          <a href="/jobbrowser/jobs/"><img src="/jobbrowser/static/art/icon_large.png" class="jt_icon"/></a>
          <ul class="jt_filters">
            <form class="jt_filter_form" data-filters="SubmitOnChange" method="get" action="/jobbrowser/jobs/">
              <li class="ccs-inline"><b>Filter Jobs:</b></li>
              <li class="ccs-inline">
                <select name="state">
                  <option value="all" ${get_state('all', state_filter)}>All States</option>
                  <option value="running" ${get_state('running', state_filter)}>Running</option>
                  <option value="completed" ${get_state('completed', state_filter)}>Completed</option>
                  <option value="failed" ${get_state('failed', state_filter)}>Failed</option>
                  <option value="killed" ${get_state('killed', state_filter)}>Killed</option>
                </select>
              </li>
              <li class="ccs-inline">
                <input type="text" class="jt_filter" data-filters="OverText, ArtInput" data-art-input-type="search" name="user" title="User Name Filter" value="${user_filter}"/>
              </li>
              <li class="ccs-inline">
                <input type="text" class="jt_filter" data-filters="OverText, ArtInput" data-art-input-type="search" name="text" title="Text Filter" value="${text_filter}"/>
              </li>
            </form>
          </ul>
        </div>
    
    
        <table data-filters="HtmlTable" class="selectable sortable" cellpadding="0" cellspacing="0">
          <thead>
            <tr>
              <th>Name / Id</th>
              <th>Status</th>
              <th>User</th>
              <th>Maps/Reduces</th>
              <th>Queue</th>
              <th>Priority</th>
              <th>Duration</th>
              <th colspan="3">Date</th>
            </tr>
          </thead>

          <tbody>
            % if len(jobs) == 0:
              <tr>
                <td colspan="10">There were no jobs that match your search criteria.</td>
              </tr>
            % endif
            % for job in jobs:
            <tr data-dblclick-delegate="{'dblclick_loads':'.view_this_job'}">
              <td>${job.jobName}
                  <div class="jt_jobid">${job.jobId_short}</div>
              </td>
              <td><a href="${url('jobbrowser.views.jobs')}?${get_state_link(request, 'state', job.status.lower())}"
                    title="Show only ${job.status.lower()} jobs"
                    class="frame_tip status_link ${job.status.lower()}">${job.status.lower()}</a></td>
              <td><a href="${url('jobbrowser.views.jobs')}?${get_state_link(request, 'user', job.user.lower())}"
                    title="Show only ${job.user.lower()} jobs"
                    class="frame_tip user_link ${job.user.lower()}">${job.user}</a></td>
              <td class="jt_mrs">

                ${comps.mr_graph(job)}
              
              </td>
              <td>${job.queueName}</td>
              <td>${job.priority.lower()}</td>
              <td>${job.durationFormatted}</td>
              <td>${job.startTimeFormatted}</td>
              <td>
                % if job.status.lower() == 'running' or job.status.lower() == 'pending':
                  % if request.user.is_superuser or request.user.username == job.user:
                    <a href="${url('jobbrowser.views.kill_job', jobid=job.jobId)}?next=${request.get_full_path()|urlencode}" class="frame_tip jt_kill confirm_and_post" title="Kill this job">kill</a>
                  % endif
                % endif
              </td>
              <td><a href="${url('jobbrowser.views.single_job', jobid=job.jobId)}" class="frame_tip jt_view jt_slide_right view_this_job" title="View this job">view</a></td>
            </tr>
            % endfor
          </tbody>
        </table>
      % else:
        ${comps.header("Job Browser", toolbar=True)}
        <div class="jt-welcome">
          <h2>Welcome to the Job Browser</h2>
          <p>There aren't any jobs running. Let's fix that.</p>
          <a href="/jobsub/list/" target="JobSub" class='jt-jobdesigner-button'>Launch the Job Designer</a>
          % if "beeswax" in appmanager.DESKTOP_APPS:
            <a href="/beeswax/" target="Beeswax" class='jt-beeswax-button'>Launch Beeswax</a>
          % endif
        </div>
      % endif
      <div class="jt-show_trackers">
        <a href="/jobbrowser/trackers">view all task trackers &raquo;</a>
      </div>
    ${comps.footer()}
