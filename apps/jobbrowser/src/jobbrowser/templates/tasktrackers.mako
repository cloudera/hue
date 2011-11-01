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
${comps.header("Task Trackers - Job Browser","Task Trackers")}


<table class="datatables">
	<thead>
		<tr>
			<th>Name</th>
			<th>Host</th>
			<th>Port</th>
			<th>Last Seen</th>
			<th>Available Space</th>
			<th>Failure Count</th>
			<th>Map Count</th>
			<th>Reduce Count</th>
			<th>Max Map Tasks</th>
			<th>Max Reduce Tasks</th>
		</tr>
	</thead>
	<tbody>
		% for t in trackers:
		<tr>
			<td><a href="/jobbrowser/trackers/${t.trackerId}">${t.trackerId}</a></td>
			<td>${t.host}</td>
			<td>${t.httpPort}</td>
			<td>${t.lastSeenFormatted}</td>
			<td>${t.availableSpace}</td>
			<td>${t.failureCount}</td>
			<td>${t.mapCount}</td>
			<td>${t.reduceCount}</td>
			<td>${t.maxMapTasks}</td>
			<td>${t.maxReduceTasks}</td>
		</tr>
		% endfor
	</tbody>
</table>
<div id="trackerDialog"></div>
<script type="text/javascript" charset="utf-8">
$(document).ready(function(){
	$(".datatables").dataTable({
		"bPaginate": false,
		"bLengthChange": false,
		"bFilter": false,
		"bInfo": false				
	});
});
</script>

${comps.footer()}
