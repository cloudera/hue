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
%>
<%namespace name="comps" file="jobbrowser_components.mako" />

${commonheader("Task Attempt: " + attempt.attemptId + ":: Job Browser", "jobbrowser")}
<div class="container-fluid">
    <h1>Task Attempt: ${attempt.attemptId} :: Job Browser</h1>
    <div class="row-fluid">
      <div class="span2">
        <div class="well sidebar-nav">
          <h6>Attempt ID</h6>
          ${attempt.attemptId_short}

          <h6>Task</h6>
          <a href="${url('jobbrowser.views.single_task', jobid=joblnk.jobId, taskid=taskid)}"
                class="frame_tip jt_view" title="View this task">${task.taskId_short}</a>

          <h6>Job</h6>
          <a href="${url('jobbrowser.views.single_job', jobid=joblnk.jobId)}"
                class="frame_tip jt_view" title="View this job">${joblnk.jobId_short}</a>

          <h6>Status</h6>
          ${attempt.state.lower()}
        </div>
      </div>

      <div class="span10">
        <ul class="nav nav-tabs">
          <li class="active"><a href="#metadata" data-toggle="tab">Metadata</a></li>
          <li><a href="#counters" data-toggle="tab">Counters</a></li>
          <li><a href="#logs" data-toggle="tab">Logs</a></li>
        </ul>

        <div class="tab-content">
          <div class="tab-pane active" id="metadata">
            <table class="table">
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
          </div>

          <div class="tab-pane" id="counters">
            ${comps.task_counters(task.counters)}
          </div>

          <div class="tab-pane jt-logs" id="logs">
            <%
              log_diagnostic = logs[0]
              log_stdout = logs[1]
              log_stderr = logs[2]
              log_syslog = logs[3]
            %>
  <%def name="format_log(raw)">
  ## have to remove any indentation here or it breaks inside the pre tags
  % for line in raw.split('\n'):
  ${ line | h,trim }
  % endfor
  </%def>
            <h2>task diagnostic log</h2>
            % if not log_diagnostic:
  <pre>-- empty --</pre>
            % else:
  <pre>${format_log(log_diagnostic)}</pre>
            % endif
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
          </div>
        </div>
      </div>
    </div>
</div>
${commonfooter()}
