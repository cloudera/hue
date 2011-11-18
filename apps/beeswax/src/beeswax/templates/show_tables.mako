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
<%namespace name="wrappers" file="header_footer.mako" />
${wrappers.head("Beeswax: Table List", section='tables')}
<div class="sidebar">
	<div class="well">
		<h6>Actions</h6>
		<ul>
			% if not examples_installed:
        	<li><a href="#" data-controls-modal="installSamples" data-backdrop="true" data-keyboard="true">Install samples</a></li>
      		% endif
      		<li><a href="${ url('beeswax.create_table.import_wizard')}">Create a new table from file</a></li>
			<li><a href="${ url('beeswax.create_table.create_table')}">Create a new table manually</a></li>
		</ul>
    </div>
</div>

<div class="content">
	<h1>Tables</h1>
  <table class="datatables">
    <thead>
      <tr>
        <th>Table Name</th>
        <th>Browse</th>
      </tr>
    </thead>
    <tbody>
      % for table in tables:
        <tr>
          <td>
            <a href="${ url("beeswax.views.describe_table", table=table) }">${ table }</a>
          </td>
          <td><a href="${ url("beeswax.views.read_table", table=table) }">Browse Data</a></td>
        </tr>
      % endfor
    </tbody>
  </table>
	<div class="row">
		<div class="span16">&nbsp;</div>
	</div>
</div>
% if not examples_installed:
<div id="installSamples" class="modal hide fade">
	<div class="modal-header">
		<a href="#" class="close">&times;</a>
		<h3>Install samples</h3>
	</div>
	<div class="modal-body">  
	  <div id="installSamplesMessage" class="alert-message block-message warning">
	        
	  </div>
	</div>
	<div class="modal-footer">
		<a href="#" id="installSamplesBtn" class="btn primary" value="Yes"/>
		<a href="#" class="btn secondary hideModal">No</a>
	</div>
</div>
% endif

<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$(".datatables").dataTable({
			"bPaginate": false,
		    "bLengthChange": false,
			"bInfo": false,
			"bFilter": false
		});
		% if not examples_installed:
		$.getJSON("${ url('beeswax.views.install_examples') }",function(data){
			$("#installSamplesMessage").text(data.title);
		});
		$(".hideModal").click(function(){
			$(this).closest(".modal").modal("hide");
		});
		$("#installSamplesBtn").click(function(){
			$.post("${ url('beeswax.views.install_examples') }", {submit:"Submit"}).error(function(){
				$("#installSamplesMessage").removeClass("warning").addClass("error").text("There was an error processing your request.");
			});
		});
		% endif
	});
</script>

${wrappers.foot()}
