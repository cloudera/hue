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
			Filter by name: <input id="filterInput"/> <a href="#" id="clearFilterBtn" class="btn">Clear</a>
	</div>
      <table class="datatables">
        <thead>
          <tr>
            <th>${_('Application')}</th>
            <th>${_('Permission')}</th>
            <th>${_('Groups')}</th>
			<th>&nbsp;</th>
          </tr>
        </head>
        <tbody>
        % for perm in permissions:
          <tr class="permissionRow" data-search="${perm.app}${perm.description}">
            <td>${perm.app}</td>
            <td>${perm.description}</td>
            <td>${', '.join([group.name for group in Group.objects.filter(grouppermission__hue_permission=perm).order_by('name')])}</td>
            <td>
              <a title="Edit groups" class="btn small" href="${ url('useradmin.views.edit_permission', app=urllib.quote(perm.app), priv=urllib.quote(perm.action)) }">Edit</a>
            </td>
          </tr>
        % endfor
        </tbody>
      </table>

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
