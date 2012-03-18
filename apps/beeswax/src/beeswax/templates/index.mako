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
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />
${commonheader("Beeswax", "beeswax", "100px")}
${layout.menubar(section='tables')}

<div class="sidebar">
	<div class="well">
		<h4>Examples</h4>
		<ul>
			<li><a href="${ url('beeswax.views.install_examples') }">Install examples</a></li>
		</ul>
    	<h4>Tables</h4>
		<ul>
			<li><a href="${ url('beeswax.views.show_tables') }">Show tables</a></li>
		    <li><a href="${ url('beeswax.create_table.create_table') }">Create Table</a></li>
		</ul>
		<h4>Queries</h4>
		<ul>
			<li><a href="${ url('beeswax.views.list_designs') }">Saved Queries</a></li>
		    <li><a href="${ url('beeswax.views.execute_query') }">Execute Query</a></li>
		    <li><a href="${ url('beeswax.views.edit_report') }">Report Generator</a></li>
			<li><a href="${ url('beeswax.views.list_query_history') }">Query History</a></li>
		</ul>
		<h4>Configuration</h4>
		<ul>
			<li><a href="${ url('beeswax.views.configuration') }">Hive Configuration</a></li>
		    <li><a href="${ url('beeswax.views.configuration') }?include_hadoop=1">Extended Configuration</a></li>
		</ul>
	</div>
</div>

<div class="content">
	<h2>Welcome to Beeswax for Hive</h2>
	<p>To get started with Beeswax you'll first need set up some data.</p>
	<a href="${ url('beeswax.create_table.create_table') }" class='btn large'>Import Data</a>
	<a href="${ url('beeswax.views.install_examples') }" class='btn large'>Install Samples</a>
</div>
${commonfooter()}
