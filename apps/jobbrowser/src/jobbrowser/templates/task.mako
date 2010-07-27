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

  ${comps.header("Job Task: " + task.taskId + ":: Job Browser")}

    <div id="job_browser_job" class="view jframe_padded">
      <div class="jtv_meta_top clearfix">
        <dl>
          <dt>Task ID</dt>
          <dd>${task.taskId_short}</dd>
          <dt>Job</dt>
          <td><a href="${url('jobbrowser.views.single_job', jobid=joblnk.jobId)}" class="frame_tip jt_view" title="View this job">${joblnk.jobId_short}</a></td>
        </dl>
        <dl>
          <dt>Status</dt>
          <dd>${task.state.lower()}</dd>
        </dl>
      </div>

      <div class="ccs-tab_ui">
        <ul class="ccs-tabs jtv_tabs ccs-right clearfix">
          <li><span>Attempts</span></li>
          <li><span>Metadata</span></li>
          <li><span>Counters</span></li>
        </ul>

        <ul class="ccs-tab_sections ccs-clear">
          <li>
            <table border="0" cellpadding="0" cellspacing="0" data-filters="HtmlTable" class="jt_meta_table sortable">
              <thead>
                <tr>
                 <th>Attempt ID</th>
                 <th>Progress</th>
                 <th>State</th>
                 <th>Task Tracker</th>
                 <th>Start Time</th>
                 <th>End Time</th>
                 <th>Output Size</th>
                 <th>Phase</th>
                 <th>Shuffle Finish</th>
                 <th>Sort Finish</th>
                 <th>Map Finish</th>
                 <th>View</th>
                </tr>
              </thead>
              <tbody>
                % for attempt in task.attempts:
                 <tr>
                   <td>${attempt.attemptId_short}</td>
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
                   <td><a class="frame_tip jtask_view jt_slide_right" title="View this attempt"
                          href="${ url('jobbrowser.views.single_task_attempt', jobid=joblnk.jobId, taskid=task.taskId, attemptid=attempt.attemptId) }"></a></td>
                 </tr>
                % endfor
              </tbody>
            </table>
          </li>
          <li>
            <table data-filters="HtmlTable" class="jt_meta_table sortable" cellpadding="0" cellspacing="0">
              <thead>
                <th>Name</th>
                <th>Value</th>
              </thead>
              <tbody>
                <tr>
                  <td>Task id</td>
                  <td>${task.taskId}</td>
                </tr>
                <tr>
                  <td>Type</td>
                  <td>${task.taskType}</td>
                </tr>
                <tr>
                  <td>JobId</td>
                  <td><a href="${url('jobbrowser.views.single_job', jobid=joblnk.jobId)}" class="frame_tip jt_view" title="View this job">${joblnk.jobId}</a></td>
                </tr>
                <tr>
                  <td>State</td>
                  <td>${task.state}</td>
                </tr>
                <tr>
                  <td>Status</td>
                  <td>${task.mostRecentState}</td>
                </tr>
                <tr>
                  <td>Start Time</td>
                  <td>${task.startTimeFormatted}</td>
                </tr>
                <tr>
                  <td>Execution Start Time</td>
                  <td>${task.execStartTimeFormatted}</td>
                </tr>
                <tr>
                  <td>Execution Finish Time</td>
                  <td>${task.execFinishTimeFormatted}</td>
                </tr>
                <tr>
                  <td>Progress</td>
                  <td>${"%d" % (task.progress * 100)}%</td>
                </tr>
              </tbody>
            </table>

          </li>
          <li>
            ${comps.task_counters(task.counters)}
          </li>
        </ul>
      </div>


    ${comps.footer()}
