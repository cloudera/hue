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
  import cgi
  import urllib

  from desktop.lib.django_util import extract_field_data
  from desktop.views import commonheader, commonfooter
%>
<%namespace name="layout" file="layout.mako" />

${commonheader("Job Designer", "jobsub", "100px")}
${layout.menubar(section='designs')}

<script src="/static/ext/js/datatables-paging-0.1.js" type="text/javascript" charset="utf-8"></script>

<div class="container-fluid">
    <h1>Job Designs</h1>
    <div class="well">
        Filter: <input id="filterInput"/>
        <p class="pull-right">
            <a href="${ url('jobsub.views.new_design', action_type='mapreduce') }" class="btn">Create Mapreduce Design</a>
            <a href="${ url('jobsub.views.new_design', action_type='streaming') }" class="btn">Create Streaming Design</a>
            <a href="${ url('jobsub.views.new_design', action_type='java') }" class="btn">Create Java Design</a>
        </p>
    </div>

    <table id="designTable" class="datatables">
        <thead>
            <tr>
                <th>Owner</th>
                <th>Name</th>
                <th>Type</th>
                <th>Description</th>
                <th>Last Modified</th>
                <th nowrap="nowrap">&nbsp;</th>
            </tr>
        </thead>
        <tbody>
            %for wf in workflows:
                <tr>
                    <td>${wf.owner.username}</td>
                    <td>${wf.name}</td>
                    <td>${wf.root_action.action_type}</td>
                    <td>${wf.description}</td>
                    <td nowrap="nowrap">${wf.last_modified.strftime('%c')}</td>
                    <td nowrap="nowrap" class="pull-right">
                      %if currentuser.is_superuser:
                        %if currentuser.username == wf.owner.username:
                          <a title="Edit ${wf.name}" class="btn small"
                              href="${ url('jobsub.views.edit_design', wf_id=wf.id) }">Edit</a>
                          <a title="Submit ${wf.name}" class="btn small submitConfirmation"
                              alt="Submit ${wf.name} to the cluster"
                              href="javascript:void(0)"
                              data-param-url="${ url('jobsub.views.get_design_params', wf_id=wf.id) }"
                              data-submit-url="${ url('jobsub.views.submit_design', wf_id=wf.id) }">Submit</a>
                        %endif
                        <a title="Delete ${wf.name}" class="btn small deleteConfirmation"
                            alt="Are you sure you want to delete ${wf.name}?"
                            href="javascript:void(0)"
                            data-confirmation-url="${ url('jobsub.views.delete_design', wf_id=wf.id) }">Delete</a>
                      %endif
                      <a title="Clone ${wf.name}" class="btn small" href="${ url('jobsub.views.clone_design', wf_id=wf.id) }">Clone</a>
                    </td>
                </tr>
            %endfor
        </tbody>
    </table>

</div>


<div id="submitWf" class="modal hide fade">
	<form id="submitWfForm" action="" method="POST">
        <div class="modal-header">
            <a href="#" class="close">&times;</a>
            <h3 id="submitWfMessage">Submit this design?</h3>
        </div>
        <div class="modal-body">
            <fieldset>
                <div id="param-container">
                </div>
            </fieldset>
        </div>
        <div class="modal-footer">
            <input id="submitBtn" type="submit" class="btn primary" value="Yes"/>
            <a href="#" class="btn secondary hideModal">No</a>
        </div>
	</form>
</div>

<div id="deleteWf" class="modal hide fade">
	<form id="deleteWfForm" action="" method="POST">
        <div class="modal-header">
            <a href="#" class="close">&times;</a>
            <h3 id="deleteWfMessage">Delete this design?</h3>
        </div>
        <div class="modal-footer">
            <input type="submit" class="btn primary" value="Yes"/>
            <a href="#" class="btn secondary hideModal">No</a>
        </div>
	</form>
</div>

<script type="text/javascript" charset="utf-8">
    $(document).ready(function() {
        $(".modal").modal({
            backdrop: "static",
            keyboard: true
        });

        $(".deleteConfirmation").click(function(){
            var _this = $(this);
            var _action = _this.attr("data-confirmation-url");
            $("#deleteWfForm").attr("action", _action);
            $("#deleteWfMessage").text(_this.attr("alt"));
            $("#deleteWf").modal("show");
        });
        $("#deleteWf .hideModal").click(function(){
            $("#deleteWf").modal("hide");
        });

        $(".submitConfirmation").click(function(){
            var _this = $(this);
            var _action = _this.attr("data-submit-url");
            $("#submitWfForm").attr("action", _action);
            $("#submitWfMessage").text(_this.attr("alt"));
            // We will show the model form, but disable the submit button
            // until we've finish loading the parameters via ajax.
            $("#submitBtn").attr("disabled", "disabled");
            $("#submitWf").modal("show");

            $.get(_this.attr("data-param-url"), function(data) {
                var params = data["params"]
                var container = $("#param-container");
                container.empty();
                for (key in params) {
                    if (!params.hasOwnProperty(key)) {
                        continue;
                    }
                    container.append(
                        $("<div/>").addClass("clearfix")
                          .append($("<label/>").text(params[key]))
                          .append(
                              $("<div/>").addClass("input")
                                .append($("<input/>").attr("name", key).attr("type", "text"))
                          )
                    )
                }
                // Good. We can submit now.
                $("#submitBtn").removeAttr("disabled");
            }, "json");
        });
        $("#submitWf .hideModal").click(function(){
            $("#submitWf").modal("hide");
        });
        
        var oTable = $('#designTable').dataTable( {
          "sPaginationType": "bootstrap",
          "bLengthChange": false,
          "sDom": "<'row'r>t<'row'<'span8'i><''p>>"
        });

        $("#filterInput").keyup(function() {
            oTable.fnFilter($(this).val());
        });
    });
</script>
${commonfooter()}
