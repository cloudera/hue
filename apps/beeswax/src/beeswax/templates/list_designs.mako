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
from django.template.defaultfilters import timesince
%>
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="wrappers" file="header_footer.mako" />
${wrappers.head("Beeswax: Queries", section='saved queries')}
<h1>Saved Queries</h1>
  <table class="datatables">
    <thead>
      <tr>
        <th>Name</th>
		<th>Description</th>
        <th>Owner</th>
        <th>Type</th>
        <th>Last Modified</th>
		<th></th>
      </tr>
    </thead>
    <tbody>
    <%!
      from beeswax import models
    %>
    % for design in page.object_list:
      <%
        may_edit = user == design.owner
      %>
      <tr>
        <td>
          % if may_edit:
            % if design.type == models.SavedQuery.REPORT:
              <a href="${ url('beeswax.views.edit_report', design_id=design.id) }">${design.name}</a>
            % else:
              <a href="${ url('beeswax.views.execute_query', design_id=design.id) }">${design.name}</a>
            % endif
          % else:
            ${design.name}
          % endif
          
          
          <ul>
            % if may_edit:
              % if design.type == models.SavedQuery.REPORT:
                <li><a href="${ url('beeswax.views.edit_report', design_id=design.id) }" title="Edit this report.">Edit</a></li>
              % else:
                <li><a href="${ url('beeswax.views.execute_query', design_id=design.id) }" title="Edit this query.">Edit</a></li>
              % endif
              <li><a href="${ url('beeswax.views.delete_design', design_id=design.id) }" title="Delete this query.">Delete</a></li>
              <li><a href="${ url('beeswax.views.list_query_history') }?design_id=${design.id}" title="View the usage history of this query.">Usage History</a></li>
            % endif
            <li><a href="${ url('beeswax.views.clone_design', design_id=design.id) }" title="Copy this query.">Clone</a></li>
          </ul>
        </td>
        <td>
          % if design.desc:
           <p>${design.desc}</p>
          % endif
        </td>
        <td>${design.owner.username}</td>
        <td>
          % if design.type == models.SavedQuery.REPORT:
            Report
          % else:
            Query
          % endif
        </td>
        <td>
          ${ timesince(design.mtime) } ago
        </td>
        <td>
          <a class="bw-options">options</a>
        </td>
      </tr>
    % endfor
    </tbody>
  </table>
${comps.pagination(page)}

<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$(".tabs").tabs();
		$(".datatables").dataTable({
			"bPaginate": false,
		    "bLengthChange": false,
			"bInfo": false,
			"bFilter": false
		});

	});
</script>

${wrappers.foot()}
