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
<% import urllib %>
<% from django.utils.translation import ugettext, ungettext, get_language, activate %>
<% _ = ugettext %>

<%namespace name="layout" file="layout.mako" />
${commonheader("Hue Groups", "useradmin", "100px")}
${layout.menubar(section='groups')}

<div class="container-fluid">
	<h1>Hue Groups</h1>
	<div class="well">
			Filter by name: <input id="filterInput"/> <a href="#" id="clearFilterBtn" class="btn">Clear</a>
			<p class="pull-right">
				<a href="${ url('useradmin.views.edit_group') }" class="btn">Add group</a>
			</p>
	</div>
      <table class="datatables">
        <thead>
          <tr>
            <th>${_('Group Name')}</th>
            <th>${_('Members')}</th>
			<th>&nbsp;</th>
          </tr>
        </head>
        <tbody>
        % for group in groups:
          <tr class="groupRow" data-search="${group.name}${', '.join([user.username for user in group.user_set.all()])}">
            <td>${group.name}</td>
            <td>${', '.join([user.username for user in group.user_set.all()])}</td>
            <td>
              <a title="Edit ${group.name}" class="btn small" href="${ url('useradmin.views.edit_group', name=urllib.quote(group.name)) }">Edit</a>
              <a title="Delete ${group.name}" class="btn small confirmationModal" alt="Are you sure you want to delete ${group.name}?" href="javascript:void(0)" data-confirmation-url="${ url('useradmin.views.delete_group', name=urllib.quote_plus(group.name)) }">Delete</a>
            </td>
          </tr>
        % endfor
        </tbody>
      </table>



<div id="deleteGroup" class="modal hide fade">
	<form id="deleteGroupForm" action="" method="POST">
	<div class="modal-header">
		<a href="#" class="close">&times;</a>
		<h3 id="deleteGroupMessage">Confirm action</h3>
	</div>
	<div class="modal-footer">
		<input type="submit" class="btn primary" value="Yes"/>
		<a href="#" class="btn secondary hideModal">No</a>
	</div>
	</form>
</div>
</div>   

	<script type="text/javascript" charset="utf-8">
		$(document).ready(function(){
			$(".datatables").dataTable({
				"bPaginate": false,
			    "bLengthChange": false,
				"bInfo": false,
				"bFilter": false
			});
			$(".dataTables_wrapper").css("min-height","0");
			$(".dataTables_filter").hide();

			$("#deleteGroup").modal({
				backdrop: "static",
				keyboard: true
			});
			$(".confirmationModal").click(function(){
				var _this = $(this);
				$.getJSON(_this.attr("data-confirmation-url"), function(data){
					$("#deleteGroupForm").attr("action", data.path);
					$("#deleteGroupMessage").text(_this.attr("alt"));
				});
				$("#deleteGroup").modal("show");
			});
			$(".hideModal").click(function(){
				$("#deleteGroup").modal("hide");
			});
			
			$("#filterInput").keyup(function(){
		        $.each($(".groupRow"), function(index, value) {

		          if($(value).attr("data-search").toLowerCase().indexOf($("#filterInput").val().toLowerCase()) == -1 && $("#filterInput").val() != ""){
		            $(value).hide(250);
		          }else{
		            $(value).show(250);
		          }
		        });

		    });

		    $("#clearFilterBtn").click(function(){
		        $("#filterInput").val("");
		        $.each($(".file-row"), function(index, value) {
		            $(value).show(250);
		        });
		    });
		   

		});
	</script>

${commonfooter()}
