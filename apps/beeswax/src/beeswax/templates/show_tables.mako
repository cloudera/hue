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
<%namespace name="layout" file="layout.mako" />
${commonheader("Beeswax: Table List", "beeswax", "100px")}
${layout.menubar(section='tables')}

<div class="container-fluid">
	<h1>Beeswax: Table List</h1>
	<div class="row-fluid">
		<div class="span3">
			<div class="well sidebar-nav">
				<ul class="nav nav-list">
					<li class="nav-header">Actions</li>
					% if not examples_installed:
		        	<li><a href="#installSamples" data-toggle="modal">Install samples</a></li>
		      		% endif
		      		<li><a href="${ url('beeswax.create_table.import_wizard')}">Create a new table from file</a></li>
					<li><a href="${ url('beeswax.create_table.create_table')}">Create a new table manually</a></li>
				</ul>
			</div>
		</div>
		<div class="span9">
			<table class="table table-condensed table-striped datatables">
				<thead>
					<tr>
						<th>Table Name</th>
						<th>&nbsp;</th>
					</tr>
				</thead>
				<tbody>
				% for table in tables:
					<tr>
						<td>
							<a href="${ url("beeswax.views.describe_table", table=table) }">${ table }</a>
						</td>
						<td><a href="${ url("beeswax.views.read_table", table=table) }" class="btn">Browse Data</a></td>
					</tr>
				% endfor
				</tbody>
			</table>
		</div>
	</div>
</div>



% if not examples_installed:
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
% endif

<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$(".datatables").dataTable({
			"bPaginate": false,
		    "bLengthChange": false,
			"bInfo": false,
			"bFilter": false,
			"aoColumns": [
				null,
				{ "sWidth": "130px" },
			 ]
		});
		% if not examples_installed:
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
		% endif
	});
</script>

${commonfooter()}
