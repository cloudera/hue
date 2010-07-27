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

  ${comps.header("Task Attempt: " + attempt.attemptId + ":: Job Browser")}

    <div id="job_browser_job" class="view jframe_padded">
      <div class="jtv_meta_top clearfix">
        <dl>
          <dt>Attempt ID</dt>
          <dd>${attempt.attemptId_short}</dd>
          <dt>Task</dt>
          <td><a href="${url('jobbrowser.views.single_task', jobid=joblnk.jobId, taskid=taskid)}" class="frame_tip jt_view" title="View this task">${task.taskId_short}</a></td>
        </dl>
        <dl>
          <dt>Job</dt>
          <td><a href="${url('jobbrowser.views.single_job', jobid=joblnk.jobId)}" class="frame_tip jt_view" title="View this job">${joblnk.jobId_short}</a></td>
        </dl>
        <dl>
          <dt>Status</dt>
          <dd>${attempt.state.lower()}</dd>
        </dl>
      </div>

      <div class="ccs-tab_ui">
        <ul class="ccs-tabs jtv_tabs ccs-right clearfix">
          <li><span>Metadata</span></li>
          <li><span>Counters</span></li>
          <li><span>Logs</span></li>
        </ul>

        <ul class="ccs-tab_sections ccs-clear">
          <li>
            <table data-filters="HtmlTable" class="jt_meta_table sortable" cellpadding="0" cellspacing="0">
              <thead>
                <th>Name</th>
                <th>Value</th>
              </thead>
              <tbody>
                <tr>
                  <td>Attempt id</td>
                  <td>${attempt.attemptId}</td>
                </tr>
                <tr>
                  <td>Task id</td>
                  <td><a href="${url('jobbrowser.views.single_task', jobid=joblnk.jobId, taskid=taskid)}" class="frame_tip jt_view" title="View this task">${task.taskId}</a></td>
                </tr>
                <tr>
                  <td>Task Type</td>
                  <td>${task.taskType}</td>
                </tr>
                <tr>
                  <td>JobId</td>
                  <td><a href="${url('jobbrowser.views.single_job', jobid=joblnk.jobId)}" class="frame_tip jt_view" title="View this job">${joblnk.jobId}</a></td>
                </tr>
                <tr>
                  <td>State</td>
                  <td>${attempt.state}</td>
                </tr>
                <tr>
                  <td>Start Time</td>
                  <td>${attempt.startTimeFormatted}</td>
                </tr>
                <tr>
                  <td>Finish Time</td>
                  <td>${attempt.finishTimeFormatted}</td>
                </tr>
                <tr>
                  <td>Progress</td>
                  <td>${"%d" % (attempt.progress * 100)}%</td>
                </tr>
                <tr>
                  <td>Task Tracker</td>
                  <td><a href="/jobbrowser/trackers/${attempt.taskTrackerId}">${attempt.taskTrackerId}</a></td>
                </tr>
                <tr>
                  <td>Phase</td>
                  <td>${attempt.phase}</td>
                </tr>
                <tr>
                  <td>Output Size</td>
                  <td>${attempt.outputSize}</td>
                </tr>
              </tbody>
            </table>

          </li>
          <li>
            ${comps.task_counters(task.counters)}
          </li>

          <li class="jt-logs">
            <%
              log_stdout = logs[0]
              log_stderr = logs[1]
              log_syslog = logs[2]
            %>
<%def name="format_log(raw)">
## have to remove any indentation here or it breaks inside the pre tags
% for line in raw.split('\n'):
${ line | h,trim }
% endfor
</%def>
            <h2>stdout</h2>
            % if not log_stdout:
<pre>-- empty --</pre>
            % else:
<pre>${format_log(log_stdout)}</pre>
            % endif
            <h2>stderr</h2>
            % if not log_stderr:
<pre>-- empty --</pre>
            % else:
<pre>${format_log(log_stderr)}</pre>
            % endif
            <h2>syslog</h2>
            % if not log_syslog:
<pre>-- empty --</pre>
            % else:
<pre>${format_log(log_syslog)}</pre>
            % endif
          </li>
        </ul>
      </div>

    ${comps.footer()}
