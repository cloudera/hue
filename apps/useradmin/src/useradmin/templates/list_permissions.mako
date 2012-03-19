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
<% from django.contrib.auth.models import Group %>
<% _ = ugettext %>

<%namespace name="layout" file="layout.mako" />
${commonheader("Hue Permissions", "useradmin", "100px")}
${layout.menubar(section='permissions')}

<div class="container-fluid">
	<h1>Hue Permissions</h1>
	<div class="well">
		<form class="form-search">
			Filter: <input id="filterInput" class="input-xlarge search-query" placeholder="Search for application name, description, etc...">
		    <a href="#" id="clearFilterBtn" class="btn">Clear</a>
		</form>
	</div>
      <table class="table table-striped datatables">
        <thead>
          <tr>
            <th>${_('Application')}</th>
            <th>${_('Permission')}</th>
            <th>${_('Groups')}</th>
			%if user.is_superuser == True:
			<th>&nbsp;</th>
			%endif
          </tr>
        </head>
        <tbody>
        % for perm in permissions:
          <tr class="permissionRow" data-search="${perm.app}${perm.description}${', '.join([group.name for group in Group.objects.filter(grouppermission__hue_permission=perm).order_by('name')])}">
            <td>${perm.app}</td>
            <td>${perm.description}</td>
            <td>${', '.join([group.name for group in Group.objects.filter(grouppermission__hue_permission=perm).order_by('name')])}</td>
			%if user.is_superuser == True:
            <td>
              <a title="Edit permission" class="btn small editPermissionBtn" data-url="${ url('useradmin.views.edit_permission', app=urllib.quote(perm.app), priv=urllib.quote(perm.action)) }" data-name="${perm.app}">Edit</a>
            </td>
			%endif
          </tr>
        % endfor
        </tbody>
      </table>

</div>


<div id="editPermission" class="modal hide fade">
	<div class="modal-header">
		<a href="#" class="close" data-dismiss="modal">&times;</a>
		<h3>Edit permissions for <span class="applicationName"></span></h3>
	</div>
	<div id="editPermissionBody" class="modal-body">
		<iframe id="editPermissionFrame" frameBorder="0"></iframe>
	</div>
	<div class="modal-footer">
		<button id="editPermissionSaveBtn" class="btn primary">Save</button>
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

			$("#filterInput").keyup(function(){
		        $.each($(".permissionRow"), function(index, value) {
		          if($(value).data("search").toLowerCase().indexOf($("#filterInput").val().toLowerCase()) == -1 && $("#filterInput").val() != ""){
		            $(value).hide(250);
		          }else{
		            $(value).show(250);
		          }
		        });

		    });

		    $("#clearFilterBtn").click(function(){
		        $("#filterInput").val("");
		        $.each($(".permissionRow"), function(index, value) {
		            $(value).show();
		        });
		    });

			$(".editPermissionBtn").click(function(){
				$("#editPermission").find(".applicationName").text($(this).data("name"));
				$("#editPermissionFrame").css("height","260px").attr("src", $(this).data("url"));
				$("#editPermission").modal("show");
			});

			$("#editPermissionSaveBtn").click(function(){
				$("#editPermissionFrame").contents().find('form').submit();
			});


		});
	</script>

${commonfooter()}
