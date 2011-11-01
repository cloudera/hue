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

  ${comps.header("Task View: Job: " + jobid, "Tasks")}
  <%def name="selected(val, state)">
  %   if val is not None and state is not None and val in state:
        selected="true"
  %   endif
  </%def>


	<div class="toolbar">
		<ul>
			<form method="get" action="/jobbrowser/jobs/${jobid}/tasks">
				<b>Filter tasks:</b>
				<li>
					<select name="taskstate" class="submitter">
						<option value="">All states</option>
						<option value="succeeded" ${selected('succeeded', taskstate)}>succeeded</option>
						<option value="running" ${selected('running', taskstate)}>running</option>
						<option value="failed" ${selected('failed', taskstate)}>failed</option>
						<option value="killed" ${selected('killed', taskstate)}>killed</option>
						<option value="pending" ${selected('pending', taskstate)}>pending</option>
					</select>
				</li>
				<li>
					<select name="tasktype" class="submitter">
						<option value="">All types</option>
						<option value="map" ${selected('map', tasktype)}>maps</option>
						<option value="reduce" ${selected('reduce', tasktype)}>reduces</option>
						<option value="job_cleanup" ${selected('job_cleanup', tasktype)}>cleanups</option>
						<option value="job_setup" ${selected('job_setup', tasktype)}>setups</option>
					</select>
				</li>
				<li>
					<input type="text" name="tasktext"  class="submitter" title="Text filter" placeholder="Text Filter"
					% if tasktext:
					value="${tasktext}"
					% endif
					/>
				</li>
			</form>
		</ul>
	</div>

	<div class="clear"></div>


	% if len(page.object_list) == 0:
	<p>There were no tasks that match your search criteria.</p>
	% else:

	<table class="datatables">
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
			<tr data-dblclick-delegate="{'dblclick_loads':'.view_task'}">
				<td>${t.taskId_short}</td>
				<td>${t.taskType}</td>
				<td>${"%d" % (t.progress * 100)}%</td>
				<td><a href="${url('jobbrowser.views.tasks', jobid=jobid)}?${get_state_link(request, 'taskstate', t.state.lower())}"
					title="Show only ${t.state.lower()} tasks"
					class="${t.state.lower()}">${t.state.lower()}</a></td>
					<td>${t.mostRecentState}</td>
					<td>${t.execStartTimeFormatted}</td>
					<td>${t.execFinishTimeFormatted}</td>
					<td><a href="/jobbrowser/jobs/${jobid}/tasks/${t.taskId}" class="view_task jt_slide_right">Attempts</a></td>
				</tr>
				%endfor
		</tbody>
	</table>
	%endif
	
	<script type="text/javascript" charset="utf-8">
		$(document).ready(function(){
			$(".datatables").dataTable({
				"bPaginate": false,
			    "bLengthChange": false,
			    "bFilter": false,
				"bInfo": false,
			});
		});
	</script>

  ${comps.footer()}
