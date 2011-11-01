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
${comps.header("Job Browser", "Jobs", trackersLink=True)}
<div class="toolbar">
	<form action="/jobbrowser/jobs" method="GET">
		<b>Filter jobs:</b>
		<ul>
			<li>
				<select name="state" class="submitter">
					<option value="all" ${get_state('all', state_filter)}>All States</option>
					<option value="running" ${get_state('running', state_filter)}>Running</option>
					<option value="completed" ${get_state('completed', state_filter)}>Completed</option>
					<option value="failed" ${get_state('failed', state_filter)}>Failed</option>
					<option value="killed" ${get_state('killed', state_filter)}>Killed</option>
				</select>
			</li>
			<li>
				<input type="text" name="user" title="User Name Filter" value="${user_filter}" placeholder="User Name Filter" class="submitter"/>
			</li>
			<li>
				<input type="text" name="text" title="Text Filter" value="${text_filter}" placeholder="Text Filter" class="submitter"/>
			</li>
		</ul>
	</form>
</div>
<div class="clear"></div>

% if len(jobs) == 0:
<p>There were no jobs that match your search criteria.</p>
% else:
<table class="datatables">
	<thead>
		<tr>
			<th>Name / Id</th>
			<th>Status</th>
			<th>User</th>
			<th>Maps/Reduces</th>
			<th>Queue</th>
			<th>Priority</th>
			<th>Duration</th>
			<th>Date</th>
			<th></th>
		</tr>
	</thead>
	<tbody>
		% for job in jobs:
		<tr>
			<td>${job.jobName}
				<div class="jobbrowser_jobid_short">${job.jobId_short}</div>
			</td>
			<td>
				<a href="${url('jobbrowser.views.jobs')}?${get_state_link(request, 'state', job.status.lower())}" title="Show only ${job.status.lower()} jobs">${job.status.lower()}</a>
			</td>
			<td>
				<a href="${url('jobbrowser.views.jobs')}?${get_state_link(request, 'user', job.user.lower())}" title="Show only ${job.user.lower()} jobs">${job.user}</a>
			</td>
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
				<a href="${url('jobbrowser.views.kill_job', jobid=job.jobId)}?next=${request.get_full_path()|urlencode}" title="Kill this job">Kill</a> -
				% endif
				% endif
				<a href="${url('jobbrowser.views.single_job', jobid=job.jobId)}" title="View this job">View</a></td>
			</tr>
			% endfor
		</tbody>
	</table>
	% endif



	% else:
	${comps.header("Job Browser", "Welcome to the Job Browser")}
	<div>
		<p>There aren't any jobs running. Let's fix that.</p>
		<a href="/jobsub/list/">Launch the Job Designer</a>
		% if "beeswax" in appmanager.DESKTOP_APPS:
		or <a href="/beeswax/">Launch Beeswax</a>
		% endif
	</div>
	% endif

	<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$(".datatables").dataTable({
			"bPaginate": false,
			"bLengthChange": false,
			"bFilter": false,
			"bInfo": false,
			"aoColumns": [
			null,
			null,
			null,
			null,
			null,
			null,
			null,
			null,
			{"bSortable":false}
			]
		});
	});
	</script>


${comps.footer()}
