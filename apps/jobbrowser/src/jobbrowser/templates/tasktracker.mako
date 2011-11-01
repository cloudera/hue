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
${comps.header("Tracker " + tracker.trackerId + " - Job Browser", "Task Trackers", "Tracker details")}
<div>
	<h1>Tracker at ${ tracker.host } on port ${ tracker.httpPort }</h1>
	<div>
		<dl>
			<dt>ID</dt>
			<dd>${ tracker.trackerId }</dd>
			<dt>Last heard from at</dt>
			<dd>${ tracker.lastSeenFormatted }.</dd>
		</dl>
	</div>
	
	<h2>Memory Metrics</h2>
	<div>
		<dl>
			<dt>Total virtual memory:</dt>
			<dd>${tracker.totalVirtualMemory }</dd>
			<dt>Total physical memory: </dt>
			<dd>${tracker.totalPhysicalMemory }</dd>
			<dt>Available space: </dt>
			<dd>${tracker.availableSpace}</dd>
		</dl>
	</div>

	<h2>Map and Reduce</h2>
	<div>
		<dl>
			<dt>Map count:</dt>
			<dd>${tracker.mapCount}</dd>
			<dt>Reduce count:</dt>
			<dd>${tracker.reduceCount}</dd>
			<dt>Max map tasks:</dt>
			<dd>${tracker.maxMapTasks}</dd>
			<dt>Max reduce tasks:</dt>
			<dd>${tracker.maxReduceTasks}</dd>
		</dl>
	</div>
</div>

${comps.footer()}