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

<div id="list_designs" class="view">
  ${comps.pagination(page)}
  <h2 class="jframe-hidden">Saved Queries:</h2>
  <table data-filters="HtmlTable" class="selectable" cellpadding="0" cellspacing="0">
    <thead>
      <tr>
        <th colspan="2">Name</th>
        <th>Owner</th>
        <th>Type</th>
        <th colspan="2">Last Modified</th>
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
      <tr data-dblclick-delegate="{'dblclick_loads':'.bw-query_edit, .bw-query_clone'}" class="jframe-no_select hue-help_links_small"
      data-filters="ContextMenu"
      data-context-menu-actions="[{'events':['contextmenu','click:relay(a.bw-options)'],'menu':'ul.context-menu'}]">
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
          
          
          <ul class="jframe-hidden context-menu">
            % if may_edit:
              % if design.type == models.SavedQuery.REPORT:
                <li><a href="${ url('beeswax.views.edit_report', design_id=design.id) }" class="bw-query_edit frame_tip" title="Edit this report.">Edit</a></li>
              % else:
                <li><a href="${ url('beeswax.views.execute_query', design_id=design.id) }" class="bw-query_edit frame_tip" title="Edit this query.">Edit</a></li>
              % endif
              <li><a href="${ url('beeswax.views.delete_design', design_id=design.id) }" class="bw-query_delete frame_tip" title="Delete this query.">Delete</a></li>
              <li><a href="${ url('beeswax.views.list_query_history') }?design_id=${design.id}" class="bw-query_history frame_tip" title="View the usage history of this query.">Usage History</a></li>
            % endif
            <li><a href="${ url('beeswax.views.clone_design', design_id=design.id) }" class="bw-query_clone frame_tip" title="Copy this query.">Clone</a></li>
          </ul>
        </td>
        <td>
          % if design.desc:
           <p class="jframe-inline" data-filters="InfoTip">${design.desc}</p>
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
</div>
${wrappers.foot()}
