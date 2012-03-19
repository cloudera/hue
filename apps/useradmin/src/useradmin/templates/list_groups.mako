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
<% from useradmin.models import group_permissions %>
<% _ = ugettext %>

<%namespace name="layout" file="layout.mako" />
${commonheader("Hue Groups", "useradmin", "100px")}
${layout.menubar(section='groups')}

<div class="container-fluid">
	<h1>Hue Groups</h1>
	<div class="well">
		<p class="pull-right">
			%if user.is_superuser == True:
			<a id="addGroupBtn" href="#" class="btn">Add group</a>
			%endif
		</p>
		<form class="form-search">
			Filter: <input id="filterInput" class="input-xlarge search-query" placeholder="Search for group name, members, etc...">
		    <a href="#" id="clearFilterBtn" class="btn">Clear</a>
		</form>
	</div>
      <table class="table table-striped datatables">
        <thead>
          <tr>
            <th>${_('Group Name')}</th>
            <th>${_('Members')}</th>
            <th>${_('Permissions')}</th>
			%if user.is_superuser == True:
			<th>&nbsp;</th>
			%endif
          </tr>
        </head>
        <tbody>
        % for group in groups:
          <tr class="groupRow" data-search="${group.name}${', '.join([group_user.username for group_user in group.user_set.all()])}">
            <td>${group.name}</td>
            <td>${', '.join([group_user.username for group_user in group.user_set.all()])}</td>
            <td>${', '.join([perm.app + "." + perm.action for perm in group_permissions(group)])}</td>
			%if user.is_superuser == True:
            <td>
              <a title="Edit ${group.name}" class="btn small editGroupBtn" data-url="${ url('useradmin.views.edit_group', name=urllib.quote(group.name)) }" data-name="${group.name}">Edit</a>
              <a title="Delete ${group.name}" class="btn small confirmationModal" alt="Are you sure you want to delete ${group.name}?" href="javascript:void(0)" data-confirmation-url="${ url('useradmin.views.delete_group', name=urllib.quote_plus(group.name)) }">Delete</a>
            </td>
			%endif
          </tr>
        % endfor
        </tbody>
      </table>



<div id="deleteGroup" class="modal hide fade groupModal">
	<form id="deleteGroupForm" action="" method="POST">
	<div class="modal-header">
		<a href="#" class="close" data-dismiss="modal">&times;</a>
		<h3 id="deleteGroupMessage">Confirm action</h3>
	</div>
	<div class="modal-footer">
		<input type="submit" class="btn primary" value="Yes"/>
		<a href="#" class="btn secondary hideModal">No</a>
	</div>
	</form>
</div>

<div id="addGroup" class="modal hide fade groupModal">
	<div class="modal-header">
		<a href="#" class="close" data-dismiss="modal">&times;</a>
		<h3>Add group</h3>
	</div>
	<div id="addGroupBody" class="modal-body">
		<iframe id="addGroupFrame" frameBorder="0"></iframe>
	</div>
	<div class="modal-footer">
		<button id="addGroupSaveBtn" class="btn primary">Save</button>
	</div>
</div>

<div id="editGroup" class="modal hide fade groupModal">
	<div class="modal-header">
		<a href="#" class="close" data-dismiss="modal">&times;</a>
		<h3>Edit group <span class="groupName"></span></h3>
	</div>
	<div id="editGroupBody" class="modal-body">
		<iframe id="editGroupFrame" frameBorder="0"></iframe>
	</div>
	<div class="modal-footer">
		<button id="editGroupSaveBtn" class="btn primary">Save</button>
	</div>
</div>

</div>

	<script type="text/javascript" charset="utf-8">
		$(document).ready(function(){
			$(".datatables").dataTable({
				"bPaginate": false,
			    "bLengthChange": false,
				"bInfo": false,
				"bFilter": false,
				"aoColumns": [
					{ "sWidth": "20%" },
					{ "sWidth": "20%" },
					null,
					%if user.is_superuser == True:
					{ "sWidth": "120px" },
					%endif
				 ]
			});
			$(".dataTables_wrapper").css("min-height","0");
			$(".dataTables_filter").hide();

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

		          if($(value).data("search").toLowerCase().indexOf($("#filterInput").val().toLowerCase()) == -1 && $("#filterInput").val() != ""){
		            $(value).hide(250);
		          }else{
		            $(value).show(250);
		          }
		        });

		    });

		    $("#clearFilterBtn").click(function(){
		        $("#filterInput").val("");
		        $.each($(".groupRow"), function(index, value) {
		            $(value).show(250);
		        });
		    });

			$("#addGroupBtn").click(function(){
				$("#addGroupFrame").css("height","400px").attr("src","${url('useradmin.views.edit_group')}");
				$("#addGroup").modal("show");
			});

			$("#addGroupSaveBtn").click(function(){
				$("#addGroupFrame").contents().find('form').submit();
			});

			$(".editGroupBtn").click(function(){
				$("#editGroup").find(".groupName").text($(this).data("name"));
				$("#editGroupFrame").css("height","400px").attr("src", $(this).data("url"));
				$("#editGroup").modal("show");
			});

			$("#editGroupSaveBtn").click(function(){
				$("#editGroupFrame").contents().find('form').submit();
			});


		});
	</script>

${commonfooter()}
