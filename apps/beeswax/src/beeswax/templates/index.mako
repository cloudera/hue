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
<div class="container-fluid">
	<div class="row-fluid">
		<div class="span3">
			<div class="well sidebar-nav">
				<ul class="nav nav-list">
					<li class="nav-header">Examples</li>
					<li><a href="#installSamples" data-toggle="modal">Install Samples</a></li>
					<li class="nav-header">Tables</li>
					<li><a href="${ url('beeswax.views.show_tables') }">Show Tables</a></li>
				    <li><a href="${ url('beeswax.create_table.create_table') }">Create Table</a></li>
					<li class="nav-header">Queries</li>
					<li><a href="${ url('beeswax.views.list_designs') }">Saved Queries</a></li>
				    <li><a href="${ url('beeswax.views.execute_query') }">Execute Query</a></li>
				    <li><a href="${ url('beeswax.views.edit_report') }">Report Generator</a></li>
					<li><a href="${ url('beeswax.views.list_query_history') }">Query History</a></li>
					<li class="nav-header">Configuration</li>
					<li><a href="${ url('beeswax.views.configuration') }">Hive Configuration</a></li>
				    <li><a href="${ url('beeswax.views.configuration') }?include_hadoop=1">Extended Configuration</a></li>
				</ul>
			</div>
		</div>
		<div class="span9">
			<h1>Welcome to Beeswax for Hive</h1>
			To get started with Beeswax you'll first need set up some data.
			<a href="${ url('beeswax.create_table.create_table') }" class='btn'>Import Data</a>
			or <a href="#installSamples" data-toggle="modal">Install Samples</a>.
		</div>
	</div>
</div>

<div id="installSamples" class="modal hide fade">
	<div class="modal-header">
		<a href="#" class="close" data-dismiss="modal">&times;</a>
		<h3>Install samples</h3>
	</div>
	<div class="modal-body">
	  <div id="installSamplesMessage" class="alert">

	  </div>
	</div>
	<div class="modal-footer">
		<a href="#" id="installSamplesBtn" class="btn primary">Yes</a>
		<a href="#" class="btn secondary" data-dismiss="modal">No</a>
	</div>
</div>


<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$.getJSON("${ url('beeswax.views.install_examples') }",function(data){
			$("#installSamplesMessage").text(data.title);
		});

		$("#installSamplesBtn").click(function(){
			$.post(
				"${ url('beeswax.views.install_examples') }",
				{ submit:"Submit" },
			  	function(creationSucceeded){
					if (creationSucceeded){
						window.location.href = "/beeswax/tables";
					}
					else {
						$("#installSamplesMessage").addClass("alert-error").text("There was an error processing your request.");
					}
				}
			);

		});
	});
</script>
${commonfooter()}
