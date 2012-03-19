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
${commonheader("Hue Users", "useradmin", "100px")}
${layout.menubar(section='users')}

<div class="container-fluid">
	<h1>Hue Users</h1>
	<div class="well">
		<p class="pull-right">
			%if user.is_superuser == True:
			<a id="addUserBtn" href="#" class="btn">Add user</a>
			%endif
		</p>
		<form class="form-search">
			Filter: <input id="filterInput" class="input-xlarge search-query" placeholder="Search for username, name, e-mail, etc...">
		    <a href="#" id="clearFilterBtn" class="btn">Clear</a>
		</form>
	</div>
	<table class="table table-striped datatables">
		<thead>
			<tr>
            	<th>${_('Username')}</th>
	            <th>${_('First Name')}</th>
	            <th>${_('Last Name')}</th>
	            <th>${_('E-mail')}</th>
				<th>${_('Groups')}</th>
	            <th>${_('Last Login')}</th>
				<th>&nbsp;</th>
			</tr>
		</thead>
		<tbody>
        % for listed_user in users:
			<tr class="userRow" data-search="${listed_user.username}${listed_user.first_name}${listed_user.last_name}${listed_user.email}${', '.join([group.name for group in listed_user.groups.all()])}">
            	<td>${listed_user.username}</td>
	            <td>${listed_user.first_name}</td>
	            <td>${listed_user.last_name}</td>
	            <td>${listed_user.email}</td>
				<td>${', '.join([group.name for group in listed_user.groups.all()])}</td>
	            <td>
	              ${listed_user.last_login.strftime('%c')}
	            </td>
	            <td>
				%if user.is_superuser == True:
					<a title="Edit ${listed_user.username}" class="btn small editUserBtn" data-url="${ url('useradmin.views.edit_user', username=urllib.quote(listed_user.username)) }" data-name="${listed_user.username}">Edit</a>
					<a title="Delete ${listed_user.username}" class="btn small confirmationModal" alt="Are you sure you want to delete ${listed_user.username}?" href="javascript:void(0)" data-confirmation-url="${ url('useradmin.views.delete_user', username=urllib.quote_plus(listed_user.username)) }">Delete</a>
				%else:
					%if user.username == listed_user.username:
						<a title="Edit ${listed_user.username}" class="btn small editUserBtn" data-url="${ url('useradmin.views.edit_user', username=urllib.quote(listed_user.username)) }" data-name="${listed_user.username}">Edit</a>
					%else:
						&nbsp;
					%endif
				%endif
				</td>
			</tr>
		% endfor
		</tbody>
	</table>

	<div id="addUser" class="modal hide fade userModal">
		<div class="modal-header">
			<a href="#" class="close" data-dismiss="modal">&times;</a>
			<h3>Add user</h3>
		</div>
		<div id="addUserBody" class="modal-body">
			<iframe id="addUserFrame" class="scroll" frameBorder="0"></iframe>
		</div>
		<div class="modal-footer">
			<button id="addUserSaveBtn" class="btn primary">Save</button>
		</div>
	</div>

	<div id="editUser" class="modal hide fade userModal">
		<div class="modal-header">
			<a href="#" class="close" data-dismiss="modal">&times;</a>
			<h3>Edit user <span class="username"></span></h3>
		</div>
		<div id="editUserBody" class="modal-body">
			<iframe id="editUserFrame" class="scroll" frameBorder="0"></iframe>
		</div>
		<div class="modal-footer">
			<button id="editUserSaveBtn" class="btn primary">Save</button>
		</div>
	</div>

	<div id="deleteUser" class="modal hide fade userModal">
		<form id="deleteUserForm" action="" method="POST">
		<div class="modal-header">
			<a href="#" class="close" data-dismiss="modal">&times;</a>
			<h3 id="deleteUserMessage">Confirm action</h3>
		</div>
		<div class="modal-footer">
			<input type="submit" class="btn primary" value="Yes"/>
			<a href="#" class="btn secondary" data-dismiss="modal">No</a>
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

			$(".confirmationModal").click(function(){
				var _this = $(this);
				$.getJSON(_this.attr("data-confirmation-url"), function(data){
					$("#deleteUserForm").attr("action", data.path);
					$("#deleteUserMessage").text(_this.attr("alt"));
				});
				$("#deleteUser").modal("show");
			});

			$("#filterInput").keyup(function(){
		        $.each($(".userRow"), function(index, value) {
		          if($(value).data("search").toLowerCase().indexOf($("#filterInput").val().toLowerCase()) == -1 && $("#filterInput").val() != ""){
		            $(value).hide(250);
		          }else{
		            $(value).show(250);
		          }
		        });

		    });

		    $("#clearFilterBtn").click(function(){
		        $("#filterInput").val("");
		        $.each($(".userRow"), function(index, value) {
		            $(value).show(250);
		        });
		    });

			$("#addUserBtn").click(function(){
				$("#addUserFrame").css("height","300px").attr("src","${ url('useradmin.views.edit_user') }");
				$("#addUser").modal("show");
			});

			$("#addUserSaveBtn").click(function(){
				$("#addUserFrame").contents().find('form').submit();
			});

			$(".editUserBtn").click(function(){
				$("#editUser").find(".username").text($(this).data("name"));
				$("#editUserFrame").css("height","300px").attr("src", $(this).data("url"));
				$("#editUser").modal("show");
			});

			$("#editUserSaveBtn").click(function(){
				$("#editUserFrame").contents().find('form').submit();
			});


		});
	</script>

${commonfooter()}
