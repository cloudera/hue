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
  import urllib

  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext, ungettext, get_language, activate
  from desktop.lib.django_util import extract_field_data

  _ = ugettext
%>

<%namespace name="layout" file="layout.mako" />

${commonheader("Job Designer", "jobsub", "100px")}
${layout.menubar(section='designs')}



<link rel="stylesheet" href="/static/ext/css/jquery-ui-autocomplete-1.8.18.css" type="text/css" media="screen" title="no title" charset="utf-8" />
<script src="/static/ext/js/knockout-2.0.0.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/ext/js/jquery/plugins/jquery-ui-autocomplete-1.8.18.min.js" type="text/javascript" charset="utf-8"></script>


<%def name="render_field(field)">
  %if not field.is_hidden:
    <div class="clearfix">
      <label>${field.label | n}</label>
      <div class="input">
		<input name="${field.html_name | n}" class="input input-xlarge" value="${extract_field_data(field) or ''}" />
      </div>
      % if len(field.errors):
        ${unicode(field.errors) | n}
      % endif
    </div>
  %endif
</%def>

<div class="container-fluid">
  <form id="workflowForm" action="${urllib.quote(action)}" method="POST">
    <fieldset>

        % for field in form.wf:
          ${render_field(field)}
        % endfor

        <hr/>
        <p class="alert alert-info">
            You can parameterize the values, using <code>$myVar</code> or
            <code>${"${"}myVar}</code>. When the design is submitted, you will be
            prompted for the actual value of <code>myVar</code>.
        </p>
        % for field in form.action:
          ${render_field(field)}
        % endfor

        <div class="clearfix">
            <label>Job Properties</label>
            <div class="input">
                ## Data bind for job properties
                <table class="table table-condensed" data-bind="visible: properties().length > 0">
                  <thead>
                    <tr>
                      <th>Property name</th>
                      <th>Value</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody data-bind="foreach: properties">
                    <tr>
                      <td><input class="input input-small required propKey" data-bind="value: name, uniqueName: false" /></td>
                      <td><input class="input input-small required" data-bind="value: value, uniqueName: false" /></td>
                      <td><a class="btn" href="#" data-bind="click: $root.removeProp">Delete</a></td>
                    </tr>
                  </tbody>
                </table>
                % if len(form.action["job_properties"].errors):
                  ${unicode(form.action["job_properties"].errors) | n}
                % endif

                <button class="btn" data-bind="click: addProp">Add Property</button>
            </div>
        </div>

        <div class="clearfix">
            <label>Files</label>
            <div class="input">
                ## Data bind for files (distributed cache)
                <table class="table table-condensed" data-bind="visible: files().length > 0">
                  <thead>
                    <tr>
                      <th>Files</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody data-bind="foreach: files">
                    <tr>
                      <td><input class="input input-xlarge required"
                                data-bind="fileChooser: $data, value: name, uniqueName: false" /></td>
                      <td><a class="btn" href="#" data-bind="click: $root.removeFile">Delete</a></td>
                    </tr>
                  </tbody>
                </table>
                % if len(form.action["files"].errors):
                  ${unicode(form.action["files"].errors) | n}
                % endif

                <button class="btn" data-bind="click: addFile">Add File</button>
            </div>
        </div>

        <div class="clearfix">
            <label>Archives</label>
            <div class="input">
                ## Data bind for archives (distributed cache)
                <table class="table table-condensed" data-bind="visible: archives().length > 0">
                  <thead>
                    <tr>
                      <th>Archives</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody data-bind="foreach: archives">
                    <tr>
                      <td><input class="input input-xlarge required"
                                data-bind="fileChooser: $data, value: name, uniqueName: false" /></td>
                      <td><a class="btn" href="#" data-bind="click: $root.removeArchive">Delete</a></td>
                    </tr>
                  </tbody>
                </table>
                % if len(form.action["archives"].errors):
                  ${unicode(form.action["archives"].errors) | n}
                % endif

                <button class="btn" data-bind="click: addArchive">Add Archive</button>
            </div>
        </div>
    </fieldset>

    ## Submit
    <div class="actions">
      <button data-bind="click: submit" class="btn primary">Save</button>
    </div>
  </form>

</div>

<div id="fileChooserModal" class="smallModal">
	<a href="#" class="close" data-dismiss="modal">&times;</a>
</div>

<div id="fileChooserModalBackdrop" class="modal-backdrop hide"></div>

## Modal for file chooser
<div id="chooseFile" class="modal hide fade">
    <div class="modal-header">
        <a href="#" class="close" data-dismiss="modal">&times;</a>
        <h3>Choose a file</h3>
    </div>
    <div class="modal-body">
        <div id="fileChooserModalz">
        </div>
    </div>
    <div class="modal-footer">
    </div>
</div>
</div>
<style>

	.smallModal {
		display:none;
	    background-clip: padding-box;
	    background-color: #FFFFFF;
	    border: 1px solid rgba(0, 0, 0, 0.3);
	    border-radius: 6px 6px 6px 6px;
	    box-shadow: 0 3px 7px rgba(0, 0, 0, 0.3);
	    width:600px;
		position:fixed;
		background-color:#FFFFFF;
		top:10px;
		left: 50%;
		margin: 0 0 0 -300px;
	    z-index: 1050;
	}

    #fileChooserModal {
		padding:14px;
        height:370px;
    }

	#fileChooserModal ul {
		height:330px;
		overflow-y:auto;
	}
</style>


<script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
        var propertiesHint = ${properties_hint};

        // The files and archives are dictionaries in the model, because we
        // can add and remove it the same way we add/remove properties.
        // But the server expects them to be arrays. So we transform the
        // two representations back and forth.
        var arrayToDictArray = function(arr) {
            var res = [ ];
            for (var i in arr) {
                res.push( { name: arr[i], dummy: "" } );
            }
            return res;
        };

        var dictArrayToArray = function(dictArray) {
            var res = [ ];
            for (var i in dictArray) {
                res.push(dictArray[i]["name"]);
            }
            return res;
        };

        // Handles adding autocomplete to job properties.
        // We need to propagate the selected value to knockoutjs.
        var addAutoComplete = function(i, elem) {
            $(elem).autocomplete({
                source: propertiesHint,
                select: function(event, ui) {
                    var context = ko.contextFor(this);
                    context.$data.name = ui.item.value;

                }
            });
        };

        var ViewModel = function(properties, files, archives) {
            var self = this;

            self.properties = ko.observableArray(properties);
            self.files = ko.observableArray(files);
            self.archives = ko.observableArray(archives);
            self.myVar = ko.observable();

            self.addProp = function() {
                self.properties.push({ name: "", value: "" });
                $(".propKey:last").each(addAutoComplete);
            };

            self.removeProp = function(val) {
                self.properties.remove(val);
            };

            self.addFile = function() {
                self.files.push({ name: "", dummy: "" });
            };

            self.removeFile = function(val) {
                self.files.remove(val);
            };

            self.addArchive = function() {
                self.archives.push({ name: "", dummy: "" });
            };

            self.removeArchive = function(val) {
                self.archives.remove(val);
            };

            self.submit = function(form) {
                var form = $("#workflowForm");
                var files_arr = dictArrayToArray(ko.toJS(self.files));
                var archives_arr = dictArrayToArray(ko.toJS(self.archives));

                $("<input>").attr("type", "hidden")
                    .attr("name", "action-job_properties")
                    .attr("value", ko.utils.stringifyJson(self.properties))
                    .appendTo(form);
                $("<input>").attr("type", "hidden")
                    .attr("name", "action-files")
                    .attr("value", JSON.stringify(files_arr))
                    .appendTo(form);
                $("<input>").attr("type", "hidden")
                    .attr("name", "action-archives")
                    .attr("value", JSON.stringify(archives_arr))
                    .appendTo(form);
                form.submit();
            };
        };

        var viewModel = new ViewModel(${properties},
                arrayToDictArray(${files}),
                arrayToDictArray(${archives}));

        ko.bindingHandlers.fileChooser = {
            init: function(element, valueAccessor, allBindings, model) {

                $(element).click(function() {
                    $("#fileChooserModal").jHueFileChooser({
                        onFileChoose: function(filePath) {
                            var binding = valueAccessor();
                            binding["name"] = filePath;
                            $("#fileChooserModal").hide();
							$("#fileChooserModalBackdrop").hide();
                            $(element).val(filePath);
                        },
						createFolder: false
                    });
					$("#fileChooserModalBackdrop").show();
                    $("#fileChooserModal").slideDown();
                });

            }
        };

        ko.applyBindings(viewModel);

        $(".pathChooser").click(function(){
            var _destination = $(this).attr("data-filechooser-destination");
            var self = this;
            $("#fileChooserModal").jHueFileChooser({
                onFileChoose: function(filePath) {
                    $(self).val(filePath);
                    $("#fileChooserModal").hide();
					$("#fileChooserModalBackdrop").hide();
                },
				createFolder: false
            });
            $("#fileChooserModal").slideDown();
        });

        $(".propKey").each(addAutoComplete);

		$("#fileChooserModalBackdrop").click(function(){
			$("#fileChooserModal").hide();
			$(this).hide();
		});

    });
</script>


${commonfooter()}
