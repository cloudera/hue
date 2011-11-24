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
${wrappers.head("Beeswax: Create table from file", section='tables')}
<div class="sidebar">
	<div class="well">
		<h6>Actions</h6>
		<ul>
      		<li><a href="${ url('beeswax.create_table.import_wizard')}">Create a new table from file</a></li>
			<li><a href="${ url('beeswax.create_table.create_table')}">Create a new table manually</a></li>
		</ul>
    </div>
</div>


<div class="content">
	<h1>Create a new table from file</h1>
	<ul class="pills">
	  <li class="active"><a href="${ url('beeswax.create_table.import_wizard') }">Step 1: Choose File</a></li>
	  <li><a href="#">Step 2: Choose Delimiter</a></li>
	  <li><a href="#">Step 3: Define Columns</a></li>
	</ul>
	<br/>
	<form action="${action}" method="POST">
		<fieldset>
			<legend>Name Your Table and Choose A File</legend>
			<div class="clearfix">
				${comps.label(file_form["name"])}
				<div class="input">
					${comps.field(file_form["name"], attrs=dict(
						placeholder="table_name",
						klass=""
					))}
					<span class="help-block">
					Name of the new table.  Table names must be globally unique.  Table names tend to correspond as well to the directory where the data will be stored.
					</span>
				</div>
			</div>
			<div class="clearfix">
				${comps.label(file_form["comment"])}
				<div class="input">
					${comps.field(file_form["comment"], attrs=dict(
						placeholder="Optional",
						klass=""
					))}
					<span class="help-block">
					Use a table comment to describe your table.  For example, you might mention the data's provenance, and any caveats users of this table should expect.
					</span>
				</div>
			</div>
			<div class="clearfix">
				${comps.label(file_form["path"])}
				<div class="input">
					${comps.field(file_form["path"], attrs=dict(
						placeholder="/user/user_name/data_dir",
						klass=""
					))}
					<span class="help-inline"><a id="pathChooser" href="#" data-filechooser-destination="path">Choose File</a></span>
					<span class="help-block">
					The HDFS path to the file that you would like to base this new table definition on.  It can be compressed (gzip) or not.
					</span>
				</div>
			</div>
			<div class="clearfix">
				${comps.label(file_form["do_import"])}
				<div class="input">
					${comps.field(file_form["do_import"], render_default=True, attrs=dict(
						klass=""
					))}
					<span class="help-block">
					Check this box if you want to import the data in this file after creating the table definition.  Leave it unchecked if you just want to define an empty table.
					</span>
				</div>
			</div>
		</fieldset>
		<div class="actions">
			<input type="submit" class="btn primary" name="submit_file" value="Choose a delimiter" />
		</div>
	</form>
	
</div>
<div id="chooseFile" class="modal hide fade">
	<div class="modal-header">
		<a href="#" class="close">&times;</a>
		<h3>Choose a file</h3>
	</div>
	<div class="modal-body">  
		<div id="filechooser">
		</div>
	</div>
	<div class="modal-footer">
	</div>
</div>

<style>
	#filechooser {
		min-height:100px;
		overflow-y:scroll;
	}
</style>


<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$("#pathChooser").click(function(){
			var _destination = $(this).attr("data-filechooser-destination");
			$("#filechooser").jHueFileChooser({
				onFileChoose: function(filePath){
					$("input[name='"+_destination+"']").val(filePath);
					$("#chooseFile").modal("hide");
				}
			});
			$("#chooseFile").modal("show");
		});
		
		$("#chooseFile").modal({
			keyboard: true,
			backdrop: true
		})
	});
</script>

${wrappers.foot()}
