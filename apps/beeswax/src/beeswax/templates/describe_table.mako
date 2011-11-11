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
<%namespace name="comps" file="beeswax_components.mako" />
<%
  if is_view:
    view_or_table_noun = "View"
  else:
    view_or_table_noun = "Table"
%>
${wrappers.head("Beeswax %s Metadata: %s" % (view_or_table_noun, table.tableName), section='tables')}
<%def name="column_table(cols)">

    <table class="datatables">
      <thead>
        <tr>
          <th>Name</th>
          <th>Type</th>
          <th>Comment</th>
        </tr>
      </thead>
      <tbody>
        % for column in cols:
          <tr>
            <td>${ column.name }</td>
            <td>${ column.type }</td>
            <td>${ column.comment or "" }</td>
          </tr>
        % endfor
      </tbody>
    </table>

</%def>

<div class="sidebar">
	<div class="well">
		<h6>Actions</h6>
		<ul>
        <li><a href="#" data-controls-modal="importData" data-backdrop="true" data-keyboard="true">Import Data</a></li>
		<li><a href="${ url("beeswax.views.read_table", table=table_name) }">Browse Data</a></li>
        <li><a href="#" data-controls-modal="dropTable" data-backdrop="true" data-keyboard="true">Drop ${view_or_table_noun}</a></li>
        <li><a href="${hdfs_link}" rel="${ table.sd.location }">View File Location</a></li>
		</ul>
      	
    </div>
</div>

<div class="content">

	<h1>Table: ${table.tableName}</h1>
	% if table.parameters.get("comment", False):
    <h5>${ table.parameters.get("comment") }</h5>
	% endif
	
	<ul class="tabs">
		<li class="active"><a href="#columns">Columns</a></li>
        % if len(table.partitionKeys) > 0:
			<li><a href="#partitionColumns">Partition Columns</a></li>
        % endif
		% if top_rows is not None:
			<li><a href="#sample">Sample</a></li>
		% endif
	</ul>
	
	<div class="tab-content">
		<div class="active tab-pane" id="columns">
			${column_table(table.sd.cols)}
		</div>
        % if len(table.partitionKeys) > 0:
          <div class="tab-pane" id="partitionColumns">
            ${column_table(table.partitionKeys)}
            <a href="${ url("beeswax.views.describe_partitions", table=table_name) }">Show Partitions</a>
          </div>
        % endif
		% if top_rows is not None:
			<div class="tab-pane" id="sample">
				<table class="datatables">
	              <thead>
	                <tr>
	                  % for col in table.sd.cols:
	                    <th>${col.name}</th>
	                  % endfor
	                </tr>
	              </thead>
	              <tbody>
	                % for i, row in enumerate(top_rows):
	                  <tr>
	                    % for item in row:
	                      <td>${ item }</td>
	                    % endfor
	                  </tr>
	                % endfor
	              </tbody>
	            </table>
        	</div>
		% endif
</div>
</div>

<div id="dropTable" class="modal hide fade">
	<form id="dropTableForm" method="POST" action="${ url("beeswax.views.drop_table", table=table_name) }">
	<div class="modal-header">
		<a href="#" class="close">&times;</a>
		<h3>Drop Table</h3>
	</div>
	<div class="modal-body">  
	  <div id="dropTableMessage" class="alert-message block-message warning">
	        
	  </div>
	</div>
	<div class="modal-footer">
		<input type="submit" class="btn primary" value="Yes"/>
		<a href="#" class="btn secondary hideModal">No</a>
	</div>
	</form>
</div>



<div id="importData" class="modal hide fade">
	<form method="POST" action="${ url("beeswax.views.load_table", table=table_name) }" class="form-stacked">
	<div class="modal-header">
		<a href="#" class="close">&times;</a>
		<h3>Import data</h3>
	</div>
	<div class="modal-body">  
	  <div class="alert-message block-message warning">
	        <p>Note that loading data will move data from its location into the table's storage location.</p>
	  </div>
	

      
	  <div class="clearfix">
	  ${comps.label(load_form["path"], title_klass='loadPath', attrs=dict(
        ))}
    	<div class="input">
		     ${comps.field(load_form["path"], title_klass='loadPath', attrs=dict(
		       klass='loadPath span8'
		       ))}
		</div>
		</div>
      
      % for pf in load_form.partition_columns:
		<div class="clearfix">
			${comps.label(load_form[pf], render_default=True)}
	    	<div class="input">
	        	${comps.field(load_form[pf], render_default=True, attrs=dict(
			       klass='span8'
			       ))}
			</div>
		</div>

      % endfor  
	
		<div class="clearfix">
			<div class="input">
				<input type="checkbox" name="overwrite"/> Overwrite existing data
			</div>
		</div>
	  

	<div id="filechooser">
	</div>
	</div>
	<div class="modal-footer">
		<input type="submit" class="btn primary" value="Submit"/>
		<a href="#" class="btn secondary hideModal">Cancel</a>
	</div>
	</form>
</div>

<style>
	#filechooser {
		display:none;
		height:100px;
		overflow-y:scroll;
	}
</style>

<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$(".tabs").tabs();
		$("#filechooser").jHueFileChooser({
			onFileChoose: function(filePath){
				$(".loadPath").val(filePath);
				$("#filechooser").slideUp();
			}
		});
		$(".datatables").dataTable({
			"bPaginate": false,
		    "bLengthChange": false,
			"bInfo": false,
			"bFilter": false
		});
		
		$.getJSON("${ url("beeswax.views.drop_table", table=table_name) }",function(data){
			$("#dropTableMessage").text(data.title);
		});
		$(".hideModal").click(function(){
			$(this).closest(".modal").modal("hide");
		});
		$(".loadPath").click(function(){
			$("#filechooser").slideDown();
		});

	});
</script>

${wrappers.foot()}
