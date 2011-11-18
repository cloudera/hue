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
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="wrappers" file="header_footer.mako" />
${wrappers.head("Beeswax: Create table manually", section='tables')}
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
	<h1>Create a new table manually</h1>
	<ul class="pills">
		<li class="active"><a href="#step1" class="step">Step 1: Name</a></li>
	    <li><a href="#step2" class="step">Step 2: Record Format</a></li>
	    <li><a href="#step3" class="step">Step 3: Serialization</a></li>
	    <li><a href="#step4" class="step">Step 4: File Format</a></li>
	    <li><a href="#step5" class="step">Step 5: Location</a></li>
	    <li><a href="#step6" class="step">Step 6: Columns</a></li>
	</ul>
	<br/>
	<form action="#" method="POST" id="mainForm">
		<div id="step1" class="stepDetails">
			<fieldset>
				<legend>Create your table</legend>
				<div class="clearfix">
					<div class="input">
						<span>Let's start with a name and description for where we'll store your data.</span>
					</div>
				</div>
				<div class="clearfix">
					${comps.label(table_form["name"])}
					<div class="input">
						${comps.field(table_form["name"], attrs=dict(
							placeholder='table_name',
			              )
			            )}
						<span class="help-block">
						Name of the new table.  Table names must be globally unique.  Table names tend to correspond as well to the directory where the data will be stored.
						</span>
					</div>
				</div>
				<div class="clearfix">
					${comps.label(table_form["comment"])}
					<div class="input">
						${comps.field(table_form["comment"], attrs=dict(
							placeholder='Optional',
			              )
			            )}
						<span class="help-block">
						Use a table comment to describe your table.  For example, you might mention the data's provenance, and any caveats users of this table should expect.
						</span>
					</div>
				</div>
			</fieldset>
		</div>
		<div id="step2" class="stepDetails hidden">
			<fieldset>
				<legend>Choose Your Record Format</legend>
				<div class="clearfix">
					<div class="input">
						<span>Individual records are broken up into columns
				          either with delimiters (e.g., CSV or TSV) or using
				          a specific serialization / deserialization (SerDe) implementation.
				          (One common specialized SerDe is for parsing out columns with a regular
				          expression.)</span>
					</div>
				</div>
				<% 
	              selected = table_form["row_format"].data or table_form["row_format"].field.initial
	            %>
				<div class="clearfix">
					<label id="formatRadio">Record format</label>
					<div class="input">
						<ul class="inputs-list">
							<li>
								<label>
			                    	<input type="radio" name="table-row_format" value="Delimited" 
					                  % if selected == "Delimited":
					                    checked
					                  % endif
					                >
									<span>Delimited</span>
								</label>
								<span class="help-block">
								Data files use delimiters, like commas (CSV) or tabs.
								</span>
			                </li>
							<li>
								<label>
			                    	<input type="radio" name="table-row_format" value="SerDe" 
					                  % if selected == "SerDe":
					                    checked
					                  % endif
					                >
									<span>SerDe</span>
								</label>
								<span class="help-block">
								Enter a specialized serialization implementation.
								</span>
							</li>
						</ul>
					</div>
				</div>
			</fieldset>
		</div>
		<div id="step3" class="stepDetails hidden">
			<fieldset>
				<legend>Configure Record Serialization</legend>
				<div id="step3Delimited" class="stepDetailsInner">
					<div class="clearfix">
						<div class="input">
							<span>Hive only supports single-character delimiters. </span>
						</div>
					</div>
					<div class="clearfix">
						${comps.label(table_form["field_terminator"])}
						<div class="input">
							${comps.field(table_form["field_terminator"], render_default=True)}
							<span class="help-block">
							Enter the column delimiter.  Must be a single character.  Use syntax like "\001" or "\t" for special characters.
							</span>
						</div>
					</div>
					<div class="clearfix">
						${comps.label(table_form["collection_terminator"])}
						<div class="input">
							${comps.field(table_form["collection_terminator"], render_default=True)}
							<span class="help-block">
							Use for array types.
							</span>
						</div>
					</div>
					<div class="clearfix">
						${comps.label(table_form["map_key_terminator"])}
						<div class="input">
							${comps.field(table_form["map_key_terminator"], render_default=True)}
							<span class="help-block">
							Use for map types.
							</span>
						</div>
					</div>
				</div>
				<div id="step3SerDe" class="hidden stepDetailsInner">
					<div class="clearfix">
						${comps.label(table_form["serde_name"])}
						<div class="input">
							${comps.field(table_form["serde_name"], attrs=dict(
								placeholder='com.acme.hive.SerDe',
				              )
				            )}
							<span class="help-block">
							Enter the Java Classname of your SerDe. <em>e.g.</em>, org.apache.hadoop.hive.contrib.serde2.RegexSerDe
							</span>
						</div>
					</div>
					<div class="clearfix">
						${comps.label(table_form["serde_properties"])}
						<div class="input">
							${comps.field(table_form["serde_properties"], attrs=dict(
								placeholder='"prop" = "value", "prop2" = "value2"',
				              )
				            )}
							<span class="help-block">
							Properties to pass to the (de)serialization mechanism. <em>e.g.,</em>, "input.regex" = "([^ ]*) ([^ ]*) ([^ ]*) (-|\\[[^\\]]*\\]) ([^ \"]*|\"[^\"]*\") (-|[0-9]*) (-|[0-9]*)(?: ([^ \"]*|\"[^\"]*\") ([^ \"]*|\"[^\"]*\"))?", "output.format.string" = "%1$s %2$s %3$s %4$s %5$s %6$s %7$s %8$s %9$s"
							</span>
						</div>
					</div>
				</div>
			</fieldset>
		</div>
		<div id="step4" class="stepDetails hidden">
			<fieldset>
				<legend>Choose a File Format</legend>
				<div class="clearfix">
					<div class="input">
						Use <strong>TextFile</strong> for newline-delimited text files.
						Use <strong>SequenceFile</strong> for Hadoop's binary serialization format.
						Use <strong>InputFormat</strong> to choose a custom implementation.<br/>
					</div>
				</div>
				
				<div class="clearfix">
					<label id="fileFormatRadio">File format</label>
					<div class="input">
						${comps.field(table_form["file_format"],
			              render_default=True, 
			              klass="bw-file_formats",
			              notitle=True
			            )}		
					</div>
				</div>
				<div id="inputFormatDetails" class="hidden">
					<div class="clearfix">
						${comps.label(table_form["input_format_class"])}
						<div class="input">
							${comps.field(table_form["input_format_class"], attrs=dict(
								placeholder='com.acme.data.MyInputFormat',
				              )
				            )}
							<span class="help-block">
							Java Class used to read data
							</span>
						</div>
					</div>
					<div class="clearfix">
						${comps.label(table_form["output_format_class"])}
						<div class="input">
							${comps.field(table_form["output_format_class"], attrs=dict(
								placeholder='com.acme.data.MyOutputFormat',
				              )
				            )}
							<span class="help-block">
							Java Class used to write data
							</span>
						</div>
					</div>
				</div>
			</fieldset>
		</div>
		<div id="step5" class="stepDetails hidden">
			<fieldset>
				<legend>Choose Where Your Table's Data is Stored</legend>
				
				<div class="clearfix">
					<label>Location</label>
					<div class="input">
						<ul class="inputs-list">
							<li>
								<label>
			                    	${comps.field(table_form["use_default_location"],
						                render_default=True
						              )}
									<span>Use default location</span>
								</label>
								<span class="help-block">
									Store your table in the default location (controlled by Hive, and typically <em>/user/hive/warehouse/table_name</em>).
								</span>
			                </li>
						</ul>
					</div>
				</div>
				
				<div id="location" class="hidden">
					<div class="clearfix">
						${comps.label(table_form["external_location"])}
						<div class="input">
							${comps.field(table_form["external_location"], attrs=dict(
								placeholder='/user/user_name/data_dir',
				              )
				            )}
							<span class="help-inline"><a id="pathChooser" href="#" data-filechooser-destination="table-external_location">Choose File</a></span>
							<span class="help-block">
							Enter the path (on HDFS) to your table's data location
							</span>
						</div>
					</div>
				</div>
			</fieldset>
		</div>
			<div id="step6" class="stepDetails hidden">
				<fieldset>
					<legend>Configure Table Columns</legend>
					% for form in columns_form.forms:
		                ${render_column(form)}
		            %endfor
					<div class="hidden">
		              ${unicode(columns_form.management_form) | n}
		            </div>
					<div class="clearfix">
						<div class="input">
							<button class="btn" value="True" name="columns-add" type="submit">Add a column</button>
						</div>
					</div>
				</fieldset>
				<fieldset>
					<legend>Configure Partitions</legend>
					<div class="clearfix">
						<div class="input">
							If your data is naturally partitioned (by, say, date),
				              partitions are a way to tell Hive that data
				              for a specific partition value are stored together.
				              Hive establishes a mapping between directories on disk
				              (<em>e.g.,</em> <code>/user/hive/warehouse/logs/dt=20100101/</code>)
				              and the data for that day.  Partitions are virtual
				              columns; they are not represented in the data themselves,
				              but are determined by the data location.  Hive implements
				              query optimizations such that queries that are specific
				              to a single partition need not read the data in other partitions.
						</div>
					</div>
					% for form in partitions_form.forms:
	                  ${render_column(form, True)}
	                % endfor
					<div class="hidden">
		              ${unicode(partitions_form.management_form) | n}
		            </div>
					<div class="clearfix">
						<div class="input">
							<button class="btn" value="True" name="partitions-add" type="submit">Add a partition</button>
						</div>
					</div>
		
				</fieldset>
			</div>
		<div class="actions">
			<input id="backBtn" type="button" class="btn hidden" value="Back" />
			<input id="nextBtn" type="button" class="btn primary" value="Next" />
			<input id="submit" type="submit" class="btn primary hidden" value="Create table" />
		</div>
	</form>
</div>

		<%def name="render_column(form, is_partition_form=False)">
			<div class="cnt">
			<div class="clearfix">
				<label>Column name</label>
				<div class="input">
					<input name="${form["column_name"].html_name | n}" value="${form["column_name"].data or ''}" placeholder="Column Name"/>
					<span class="help-inline">
					Column name must be single words that start with a letter or a digit.
					</span>
				</div>
			</div>
			<div class="clearfix">
				<label>Column type</label>
				<div class="input columnType">
					${comps.field(form["column_type"],
                        render_default=True
                      )}
					<span class="help-inline">
					Type for this column.  Certain advanced types (namely, structs) are not exposed in this interface.
					</span>
				</div>
			</div>
			 % if is_partition_form == False: 
			<div class="arraySpec hidden">
				<div class="clearfix">
					<label>Array value type</label>
					<div class="input">
						${comps.field(form["array_type"], render_default=True)}
						<span class="help-inline">
						Type of the array values.
						</span>
					</div>
				</div>
			</div>
			<div class="mapSpec hidden">
				<div class="clearfix">
					<label>Map Key type</label>
					<div class="input">
						${comps.field(form["map_key_type"], render_default=True)}
						<span class="help-inline">
						Type of the map keys.
						</span>
					</div>
				</div>
				<div class="clearfix">
					<label>Map Value type</label>
					<div class="input">
						${comps.field(form["map_value_type"], render_default=True)}
						<span class="help-inline">
						Type of the map values.
						</span>
					</div>
				</div>
			</div>
			% endif
			<div class="clearfix">
				<div class="input">
					${comps.field(form['_deleted'], tag="button", button_text="Remove", notitle=True, attrs=dict(
						type="submit",
						title="Delete this column",
						klass="btn small danger"
					), value=True)}
					
				</div>
			</div>
            ${unicode(form["_exists"]) | n}

			</div>
		
            </%def>
            
         


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
		
		
		$(".step").click(function(event){
			event.preventDefault();
			$(".stepDetails").hide();
			var _step = $(this).attr("href");
			$(_step).show();
			$("#backBtn").hide();
			if (_step != "#step1"){
				$("#backBtn").show();
			}
			if (_step != "#step6"){
				$("#nextBtn").show();
				$("#submit").hide();
			}
			else {
				$("#nextBtn").hide();
				$("#submit").show();
			}
			$(".step").parent().removeClass("active");
			$(this).parent().addClass("active");
		});
		$("#nextBtn").click(function(){
			$("ul.pills li.active").next().find("a").click();
		});
		$("#backBtn").click(function(){
			$("ul.pills li.active").prev().find("a").click();
		});
		var _url = location.href;
		if (_url.indexOf("#")>-1){
			$(".step[href='"+_url.substring(_url.indexOf("#"),_url.length)+"']").click();
		}
		
		$("#id_table-field_terminator_1").css("margin-left","4px").attr("placeholder","Write here your field terminator").hide();
		$("#id_table-field_terminator_0").change(function(){
			if ($(this).val() == "__other__"){
				$("#id_table-field_terminator_1").show();
			}
			else {
				$("#id_table-field_terminator_1").hide();
			}
		});
		$("#id_table-collection_terminator_1").css("margin-left","4px").attr("placeholder","Write here your collection terminator").hide();
		$("#id_table-collection_terminator_0").change(function(){
			if ($(this).val() == "__other__"){
				$("#id_table-collection_terminator_1").show();
			}
			else {
				$("#id_table-collection_terminator_1").hide();
			}
		});
		$("#id_table-map_key_terminator_1").css("margin-left","4px").attr("placeholder","Write here your map key terminator").hide();
		$("#id_table-map_key_terminator_0").change(function(){
			if ($(this).val() == "__other__"){
				$("#id_table-map_key_terminator_1").show();
			}
			else {
				$("#id_table-map_key_terminator_1").hide();
			}
		});
		
		$("input[name='table-row_format']").change(function(){
			$(".stepDetailsInner").hide();
			$("#step3"+$(this).val()).show();
		});

		$("input[name='table-file_format']").change(function(){
			$("#inputFormatDetails").hide();
			if ($(this).val() == "InputFormat"){
				$("#inputFormatDetails").slideDown();
			}
		});
		
		$("#id_table-use_default_location").change(function(){
			if (!$(this).is(":checked")){
				$("#location").slideDown();
			}
			else {
				$("#location").slideUp();
			}
		});
		
		
		$("#step6").find("button").click(function(){
			$("#mainForm").attr("action","#step6");
		});
		
		$(".columnType").find("select").change(function(){
			$(this).parents(".cnt").find(".arraySpec").hide();
			$(this).parents(".cnt").find(".mapSpec").hide();
			if ($(this).val() == "array"){
				$(this).parents(".cnt").find(".arraySpec").show();
			}
			if ($(this).val() == "map"){
				$(this).parents(".cnt").find(".mapSpec").show();
			}
		});
		
		$("#step4").find("ul").addClass("inputs-list");
	});
</script>
${wrappers.foot()}
