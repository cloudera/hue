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
<%!  from beeswax.views import collapse_whitespace %>
${wrappers.head("Beeswax: My Queries", section='my queries')}

##
## ----------------- Saved queries -------------------
##
<div id="my_queries" class="view">
  <div data-filters="Tabs">
    <ul class="toolbar bw-my_queries_tabs tabs clearfix">
      <li><span>Recent Saved Queries</span></li>
      <li><span>Recent Run Queries</span></li>
    </ul>

    <ul class="tab_sections jframe-clear">
      <li>
        <table data-filters="HtmlTable" class="selectable" cellpadding="0" cellspacing="0">
          <thead>
            <tr>
              <th colspan="2">Name</th>
              <th>Type</th>
              <th colspan="2">Last Modified</th>
            </tr>
          </thead>
          <tbody>
          <%!
            from beeswax import models
          %>
          % for design in q_page.object_list:
            <tr data-dblclick-delegate="{'dblclick_loads':'.bw-query_edit, .bw-query_clone'}" class="jframe-no_select hue-help_links_small"
            data-filters="ContextMenu"
            data-context-menu-actions="[{'events':['contextmenu','click:relay(a.bw-options)'],'menu':'ul.context-menu'}]">
              <td>
                % if design.type == models.SavedQuery.REPORT:
                  <a href="${ url('beeswax.views.edit_report', design_id=design.id) }">${design.name}</a>
                % else:
                  <a href="${ url('beeswax.views.execute_query', design_id=design.id) }">${design.name}</a>
                % endif

                <ul class="jframe-hidden context-menu">
                  % if design.type == models.SavedQuery.REPORT:
                    <li><a href="${ url('beeswax.views.edit_report', design_id=design.id) }" class="bw-query_edit frame_tip" title="Edit this report.">Edit</a></li>
                  % else:
                    <li><a href="${ url('beeswax.views.execute_query', design_id=design.id) }" class="bw-query_edit frame_tip" title="Edit this query.">Edit</a></li>
                  % endif
                  <li><a href="${ url('beeswax.views.delete_design', design_id=design.id) }" class="bw-query_delete frame_tip" title="Delete this query.">Delete</a></li>
                  <li><a href="${ url('beeswax.views.list_query_history') }?design_id=${design.id}" class="bw-query_history frame_tip" title="View the usage history of this query.">Usage History</a></li>
                  <li><a href="${ url('beeswax.views.clone_design', design_id=design.id) }" class="bw-query_clone frame_tip" title="Copy this query.">Clone</a></li>
                </ul>
              </td>
              <td>
                % if design.desc:
                 <p class="jframe-inline" data-filters="InfoTip">${design.desc}</p>
                % endif
              </td>
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
        % if q_page.number != q_page.num_pages():
          <a href="${ url('beeswax.views.list_designs') }?user=${request.user.username|u}" class="bw-view_more">View all my queries &raquo;</a>
        % endif
      </li>
      <li>
        ##
        ## ----------------- My history -------------------
        ##
        <table data-filters="HtmlTable" class="selectable" cellpadding="0" cellspacing="0">
          <thead>
            <tr>
              <th>Time</th>
              <th>Name</th>
              <th>Query</th>
              <th>State</th>
              <th>Result</th>
            </tr>
          </thead>
          <tbody>
          <%!
            from beeswax import models, views
          %>
          % for query in h_page.object_list:
            <%
	      qcontext = ""
	      try:
		design = query.design
		qcontext = views.make_query_context('design', design.id)
	      except:
		pass
            %>
            <tr data-dblclick-delegate="{'dblclick_loads':'.bw-view_result'}" class="jframe-no_select hue-help_links_small">
              <td>${query.submission_date.strftime("%x %X")}</td>
              ## TODO (bc): Only showing HQL (not REPORT)
              <td><a href="${ url('beeswax.views.execute_query', design_id=design.id) }" class="bw-view_query">${design.name}</a></td>
              <td>
                <p class="jframe-inline" data-filters="InfoTip">
                  % if len(query.query) > 100:
                    <code>${collapse_whitespace(query.query[:100])}...</code>
                  % else:
                    <code>${collapse_whitespace(query.query)}</code>
                  % endif
                </p>
              </td>
              <td>${models.QueryHistory.STATE[query.last_state]}</td>
              <td class="bw-query_result">
                % if qcontext and query.last_state != models.QueryHistory.STATE.expired.index:
                  <a href="${ url('beeswax.views.watch_query', id=query.id) }?context=${qcontext|u}" class="bw-view_result" data-filters="ArtButton" data-icon-styles="{'width': 16, 'height': 16, 'top': 2}">View</a>
                % else:
                  ~
                % endif
              </td>
            </tr>
          % endfor
          </tbody>
        </table>
        % if h_page.number != h_page.num_pages():
          <a href="${ url('beeswax.views.list_query_history') }" class="bw-view_more">View my entire query history &raquo;</a>
        % endif
      </li>
    </ul>
  </div>
</div>
${wrappers.foot()}
