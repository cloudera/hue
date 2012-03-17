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

<div class="container-fluid">
    <h1>Job Designs</h1>
    <div class="well">
        Filter: <input id="filterInput"/> <a href="#" id="clearFilterBtn" class="btn">Clear</a>
        <p class="pull-right">
            <a href="${ url('jobsub.views.new_design', action_type='mapreduce') }" class="btn">Create Mapreduce Design</a>
            <a href="${ url('jobsub.views.new_design', action_type='streaming') }" class="btn">Create Streaming Design</a>
            <a href="${ url('jobsub.views.new_design', action_type='java') }" class="btn">Create Java Design</a>
        </p>
    </div>

    <table class="datatables">
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
                <tr class="wfRow" data-search="${wf.owner.username}${wf.name}${wf.root_action.action_type}${wf.description}">
                    <td>${wf.owner.username}</td>
                    <td>${wf.name}</td>
                    <td>${wf.root_action.action_type}</td>
                    <td>${wf.description}</td>
                    <td nowrap="nowrap">${wf.last_modified.strftime('%c')}</td>
                    <td nowrap="nowrap">
                      %if currentuser.is_superuser or currentuser.username == wf.owner.username:
                        <a title="Edit ${wf.name}" class="btn small" href="${ url('jobsub.views.edit_design', wf_id=wf.id) }">Edit</a>
                        <a title="Submit ${wf.name}" class="btn small" href="${ url('jobsub.views.submit_design', wf_id=wf.id) }">Submit</a>
                        <a title="Delete ${wf.name}" class="btn small confirmationModal" alt="Are you sure you want to delete ${wf.name}?" href="javascript:void(0)" data-confirmation-url="${ url('jobsub.views.delete_design', wf_id=wf.id) }">Delete</a>
                      %endif
                    </td>
                </tr>
            %endfor
        </tbody>
    </table>

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
        $(".datatables").dataTable({
            "bPaginate": false,
            "bLengthChange": false,
            "bInfo": false,
            "bFilter": false
        });
        $(".dataTables_wrapper").css("min-height","0");
        $(".dataTables_filter").hide();

        $("#deleteWf").modal({
            backdrop: "static",
            keyboard: true
        });

        $(".confirmationModal").click(function(){
            var _this = $(this);
            var _action = _this.attr("data-confirmation-url");
            $("#deleteWfForm").attr("action", _action);
            $("#deleteWfMessage").text(_this.attr("alt"));
            $("#deleteWf").modal("show");
        });
        $(".hideModal").click(function(){
            $("#deleteWf").modal("hide");
        });
        
        $("#filterInput").keyup(function(){
            $.each($(".wfRow"), function(index, value) {

              if($(value).attr("data-search").toLowerCase().indexOf($("#filterInput").val().toLowerCase()) == -1 && $("#filterInput").val() != ""){
                $(value).hide(250);
              }else{
                $(value).show(250);
              }
            });

        });

        $("#clearFilterBtn").click(function(){
            $("#filterInput").val("");
            $.each($(".wfRow"), function(index, value) {
                $(value).show(250);
            });
        });
		   
    });
</script>
${commonfooter()}
