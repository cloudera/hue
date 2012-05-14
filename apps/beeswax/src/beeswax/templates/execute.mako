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
  from desktop.lib.django_util import extract_field_data
  from desktop.views import commonheader, commonfooter
%>

<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />
<%namespace name="util" file="util.mako" />

<%def name="query()">
	<h1>Hive Query</h1>
	<fieldset>
		% if design and not design.is_auto and design.name:
	          <legend>${design.name}</legend>
	          % if design.desc:
	            <p>${design.desc}</p>
	          % endif

	      % else:
	        <legend>Query</legend>
	      % endif

      <div class="clearfix">
        <div class="input">
            <textarea class="span9" rows="9" placeholder="Example: SELECT * FROM tablename" name="${form.query["query"].html_name | n}" id="queryField">${extract_field_data(form.query["query"]) or ''}</textarea>
			<div id="validationResults">
			% if len(form.query["query"].errors):
				${unicode(form.query["query"].errors) | n}
			 % endif
			</div>
        </div>
      </div>
    </fieldset>

	<div class="actions">
		<a id="executeQuery" class="btn primary">Execute</a>
		% if design and not design.is_auto and design.name:
        <a id="saveQuery" class="btn">Save</a>
        % endif
        <a id="saveQueryAs" class="btn">Save as...</a>
        <a id="explainQuery" class="btn">Explain</a>
		&nbsp; or create a &nbsp;<a class="btn" href="${ url('beeswax.views.execute_query') }">New query</a>
	</div>
</%def>


${commonheader("Hive Query", "beeswax", "100px")}
${layout.menubar(section='query')}

<div class="container-fluid">
	<div class="row-fluid">
		<div class="span3">
			<div class="well sidebar-nav">
				<form id="advancedSettingsForm" action="${action}" method="POST" class="form form-horizontal noPadding">
					<ul class="nav nav-list">
						<li class="nav-header">Hive settings</li>
						<li>
							% for i, f in enumerate(form.settings.forms):
							<div class="param">
								<div class="remove">
									${comps.field(f['_deleted'], tag="button", button_text="x", notitle=True, attrs=dict(
										type="submit",
										title="Delete this setting",
										klass="btn btn-mini settingsDelete"
									), value=True)}
								</div>

								<div class="control-group">
									${comps.label(f['key'])}
									${comps.field(f['key'], attrs=dict(
										placeholder="mapred.reduce.tasks",
										klass="settingsField span8"
									))}
							    </div>

								<div class="control-group">
									${comps.label(f['value'])}
									${comps.field(f['value'], attrs=dict(
										placeholder="1",
										klass="span8"
									))}
								</div>
							</div>
							${comps.field(f['_exists'], hidden=True)}

						    % endfor
							<div class="control-group">
								<a class="btn btn-small" data-form-prefix="settings">Add</a>
							</div>
						</li>
						<li class="nav-header">File Resources</li>
						<li>
							% for i, f in enumerate(form.file_resources.forms):
							<div class="param">
								<div class="remove">
									${comps.field(f['_deleted'], tag="button", button_text="x", notitle=True, attrs=dict(
										type="submit",
										title="Delete this setting",
										klass="btn btn-mini file_resourcesDelete"
									), value=True)}
								</div>

								<div class="control-group">
									${comps.label(f['type'])}
									${comps.field(f['type'], render_default=True, attrs=dict(
										klass="span8"
									))}
							    </div>

								<div class="control-group">
									${comps.label(f['path'])}
									${comps.field(f['path'], attrs=dict(
										placeholder="/user/foo/udf.jar",
										klass="input-small file_resourcesField",
										data_filters=f['path'].html_name
									))}
								</div>
							</div>
							${comps.field(f['_exists'], hidden=True)}

				            % endfor
							<div class="control-group">
								<a class="btn btn-small" data-form-prefix="file_resources">Add</a>
							</div>
						</li>
						<li class="nav-header">User-defined Functions</li>
						<li>
							% for i, f in enumerate(form.functions.forms):
								<div class="param">
									<div class="remove">
										${comps.field(f['_deleted'], tag="button", button_text="x", notitle=True, attrs=dict(
											type="submit",
											title="Delete this setting",
											klass="btn btn-mini file_resourcesDelete"
										), value=True)}
									</div>

									<div class="control-group">
										${comps.label(f['name'])}
										${comps.field(f['name'], attrs=dict(
											placeholder="myFunction",
											klass="span8 functionsField"
										))}
								    </div>

									<div class="control-group">
										${comps.label(f['class_name'])}
										${comps.field(f['class_name'], attrs=dict(
											placeholder="com.acme.example",
											klass="span8"
										))}
									</div>
								</div>

					          ${comps.field(f['_exists'], hidden=True)}
					        % endfor
							<div class="control-group">
								<a class="btn btn-small" data-form-prefix="functions">Add</a>
							</div>
						</li>
						<li class="nav-header">Parametrization</li>
						<li>
							${comps.field(form.query["is_parameterized"],
					            notitle = True,
					            tag = "checkbox",
					            button_text = "Enable Parameterization",
					            help = "If checked (the default), you can include parameters like $parameter_name in your query, and users will be prompted for a value when the query is run.",
					            help_attrs= dict(
					              data_help_direction='11'
					            )
					        )}
						</li>
						<li class="nav-header">Email Notification</li>
						<li>
							${comps.field(form.query["email_notify"],
		                      notitle = True,
		                      tag = "checkbox",
		                      button_text = "Email me on complete",
		                      help = "If checked, you will receive an email notification when the query completes.",
		                      help_attrs= dict(
		                        data_help_direction='11'
		                      )
		                     )}
						</li>
					</ul>
					<input type="hidden" name="${form.query["query"].html_name | n}" class="query" value="" />
				</form>
			</div>
		</div>
		<div class="span9">
			% if error_message:
				<div class="alert alert-error">
					<p><strong>Your query has the following error(s):</strong></p>
					<p>${error_message}</p>
					% if log:
						<small>click the <b>Error Log</b> tab below for details</small>
					% endif
				</div>
			% endif

	        % if on_success_url:
	          <input type="hidden" name="on_success_url" value="${on_success_url}"/>
	        % endif

	        % if error_messages or log:
                <ul class="nav nav-tabs">
                    <li class="active">
                        <a href="#queryPane" data-toggle="tab">Query</a>
                    </li>
                    % if error_message or log:
                      <li>
                        <a href="#errorPane" data-toggle="tab">
                        % if log:
                            Error Log
                        % else:
                            &nbsp;
                        % endif
                        </a>
                    </li>
                    % endif
                </ul>

				<div class="tab-content">
					<div class="active tab-pane" id="queryPane">
						${query()}
					</div>
					% if error_message or log:
						<div class="tab-pane" id="errorPane">
						% if log:
							<pre>${log | h}</pre>
						% endif
						</div>
					% endif
				</div>
			% else:
				${query()}
			% endif
			<br/>
		</div>
	</div>
</div>


<div id="chooseFile" class="modal hide fade">
	<div class="modal-header">
		<a href="#" class="close" data-dismiss="modal">&times;</a>
		<h3>Choose a file</h3>
	</div>
	<div class="modal-body">
		<div id="filechooser">
		</div>
	</div>
	<div class="modal-footer">
	</div>
</div>

<div id="saveAs" class="modal hide fade">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>Choose a name</h3>
    </div>
    <div class="modal-body">
        <div class="clearfix">
            <label>Name</label>
            ${comps.field(form.saveform['name'])}
        </div>
        <div class="clearfix">
            <label>Description</label>
            ${comps.field(form.saveform['desc'])}
        </div>
    </div>
    <div class="modal-footer">
        <button id="saveAsNameBtn" class="btn primary">Save</button>
    </div>
</div>

<style>
	#filechooser {
		min-height:100px;
		overflow-y:scroll;
	}
	.control-group label {
	    float: left;
	    padding-top: 5px;
	    text-align: left;
	    width: 40px;
	}
	.nav-list {
		padding:0;
	}
	.param {
		background:#FDFDFD;
		padding: 8px 8px 1px 8px;
		border-radius: 4px;
	    -webkit-border-radius: 4px;
	    -moz-border-radius: 4px;
		margin-bottom:5px;
		border:1px solid #EEE;
	}
	.remove {
		float:right;
	}
	.file_resourcesField {
		border-radius: 3px 0 0 3px;
		border-right:0;
	}
	.fileChooserBtn {
		border-radius: 0 3px 3px 0;
	}

</style>


<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$("*[rel=tooltip]").tooltip({
			placement: 'right'
		});
		// hack!!!
		$("select").addClass("span8");

		$("a[data-form-prefix]").each(function(){
			var _prefix = $(this).attr("data-form-prefix");
			var _nextID = 0;
			if ($("."+_prefix+"Field").length){
				_nextID= ($("."+_prefix+"Field").last().attr("name").substr(_prefix.length+1).split("-")[0]*1)+1;
			}
			$("<input>").attr("type","hidden").attr("name",_prefix+"-next_form_id").attr("value",_nextID).appendTo($("#advancedSettingsForm"));
			$("."+_prefix+"Delete").click(function(e){
				e.preventDefault();
				$("input[name="+_prefix+"-add]").attr("value","");
				$("<input>").attr("type","hidden").attr("name", $(this).attr("name")).attr("value","True").appendTo($("#advancedSettingsForm"));
				checkAndSubmit();
			});
		});

		$("a[data-form-prefix]").click(function(){
			var _prefix = $(this).attr("data-form-prefix");
			$("<input>").attr("type","hidden").attr("name",_prefix+"-add").attr("value","True").appendTo($("#advancedSettingsForm"));
			checkAndSubmit();
		});

		$(".file_resourcesField").each(function(){
			var self = $(this);
			self.after(getFileBrowseButton(self));
		});

		function getFileBrowseButton(inputElement) {
			return $("<button>").addClass("btn").addClass("fileChooserBtn").text("..").click(function(e){
				e.preventDefault();
				$("#filechooser").jHueFileChooser({
	                onFileChoose: function(filePath) {
	                    inputElement.val(filePath);
	                    $("#chooseFile").modal("hide");
	                },
	                createFolder: false
	            });
	            $("#chooseFile").modal("show");
			})
		}

		$("#executeQuery").click(function(){
			$("<input>").attr("type","hidden").attr("name","button-submit").attr("value","Execute").appendTo($("#advancedSettingsForm"));
			checkAndSubmit();
		});

        $("#saveQuery").click(function(){
            $("<input>").attr("type","hidden").attr("name","saveform-name")
                .attr("value", "${extract_field_data(form.saveform["name"])}").appendTo($("#advancedSettingsForm"));
            $("<input>").attr("type","hidden").attr("name","saveform-desc")
                .attr("value", "${extract_field_data(form.saveform["desc"])}").appendTo($("#advancedSettingsForm"));
            $("<input>").attr("type","hidden").attr("name","saveform-save").attr("value","Save").appendTo($("#advancedSettingsForm"));
            checkAndSubmit();
        });

		$("#saveQueryAs").click(function(){
			$("<input>").attr("type","hidden").attr("name","saveform-saveas").attr("value","Save As...").appendTo($("#advancedSettingsForm"));
			$("#saveAs").modal("show");
		});

        $("#saveAsNameBtn").click(function(){
             $("<input>").attr("type","hidden").attr("name","saveform-name")
                 .attr("value", $("input[name=saveform-name]").val()).appendTo($("#advancedSettingsForm"));
             $("<input>").attr("type","hidden").attr("name","saveform-desc")
                 .attr("value", $("input[name=saveform-desc]").val()).appendTo($("#advancedSettingsForm"));

            checkAndSubmit();
        });

		$("#explainQuery").click(function(){
			$("<input>").attr("type","hidden").attr("name","button-explain").attr("value","Explain").appendTo($("#advancedSettingsForm"));
			checkAndSubmit();
		});

		$("#queryField").change(function(){
			$(".query").val($(this).val());
		});

		$("#queryField").focus(function(){
			$(this).removeClass("fieldError");
			$("#validationResults").empty();
		});

		function checkAndSubmit(){
			// TODO: client side validation
			$(".query").val($("#queryField").val());
			$("#advancedSettingsForm").submit();
		}


	});
</script>


${commonfooter()}
