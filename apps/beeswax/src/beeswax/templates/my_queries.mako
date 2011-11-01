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
<h1>My Queries</h1>
##
## ----------------- Saved queries -------------------
##


	<ul class="tabs">
		<li class="active"><a href="#recentSavedQueries">Recent Saved Queries</a></li>
		<li><a href="#recentRunQueries">Recent Run Queries</a></li>
	</ul>
	

		<div class="pill-content">
			<div class="active" id="recentSavedQueries">
	
				 <table class="datatables">
			          <thead>
			            <tr>
			              <th>Name</th>
						  <th>Desc</th>
			              <th>Type</th>
			              <th>Last Modified</th>
						  <th></th>
			            </tr>
			          </thead>
			          <tbody>
			          <%!
			            from beeswax import models
			          %>
			          % for design in q_page.object_list:
			            <tr>
			              <td>
			                % if design.type == models.SavedQuery.REPORT:
			                  <a href="${ url('beeswax.views.edit_report', design_id=design.id) }">${design.name}</a>
			                % else:
			                  <a href="${ url('beeswax.views.execute_query', design_id=design.id) }">${design.name}</a>
			                % endif

			                <ul class="jframe-hidden context-menu">
			                  % if design.type == models.SavedQuery.REPORT:
			                    <li><a href="${ url('beeswax.views.edit_report', design_id=design.id) }" title="Edit this report.">Edit</a></li>
			                  % else:
			                    <li><a href="${ url('beeswax.views.execute_query', design_id=design.id) }" title="Edit this query.">Edit</a></li>
			                  % endif
			                  <li><a href="${ url('beeswax.views.delete_design', design_id=design.id) }" title="Delete this query.">Delete</a></li>
			                  <li><a href="${ url('beeswax.views.list_query_history') }?design_id=${design.id}" title="View the usage history of this query.">Usage History</a></li>
			                  <li><a href="${ url('beeswax.views.clone_design', design_id=design.id) }" title="Copy this query.">Clone</a></li>
			                </ul>
			              </td>
			              <td>
			                % if design.desc:
			                 <p>${design.desc}</p>
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
			                <a>options</a>
			              </td>
			            </tr>
			          % endfor
			          </tbody>
			        </table>
			        % if q_page.number != q_page.num_pages():
			          <a href="${ url('beeswax.views.list_designs') }?user=${request.user.username|u}" >View all my queries &raquo;</a>
			        % endif
			</div>
			
			<div id="recentRunQueries">
				<table class="datatables">
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
		            <tr >
		              <td>${query.submission_date.strftime("%x %X")}</td>
		              ## TODO (bc): Only showing HQL (not REPORT)
		              <td><a href="${ url('beeswax.views.execute_query', design_id=design.id) }" >${design.name}</a></td>
		              <td>
		                <p>
		                  % if len(query.query) > 100:
		                    <code>${collapse_whitespace(query.query[:100])}...</code>
		                  % else:
		                    <code>${collapse_whitespace(query.query)}</code>
		                  % endif
		                </p>
		              </td>
		              <td>${models.QueryHistory.STATE[query.last_state]}</td>
		              <td>
		                % if qcontext and query.last_state != models.QueryHistory.STATE.expired.index:
		                  <a href="${ url('beeswax.views.watch_query', id=query.id) }?context=${qcontext|u}">View</a>
		                % else:
		                  ~
		                % endif
		              </td>
		            </tr>
		          % endfor
		          </tbody>
		        </table>
		        % if h_page.number != h_page.num_pages():
		          <a href="${ url('beeswax.views.list_query_history') }">View my entire query history &raquo;</a>
		        % endif
			</div>

</div>

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
