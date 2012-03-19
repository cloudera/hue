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
<%namespace name="layout" file="layout.mako" />
<%namespace name="comps" file="beeswax_components.mako" />
<%!  from beeswax.views import collapse_whitespace %>
${commonheader("Beeswax: Query History", "beeswax", "100px")}
${layout.menubar(section='history')}
<%def name="show_saved_query(design, history)">
  % if design:
    % if request.user == design.owner:
      % if design.type == models.SavedQuery.REPORT:
        <a href="${ url('beeswax.views.edit_report', design_id=design.id) }" class="bw-view_query">
      % else:
        <a href="${ url('beeswax.views.execute_query', design_id=design.id) }" class="bw-view_query">
      % endif
    % endif
    % if design.is_auto:
      [ Unsaved ]
    % else:
      ${design.name}
    % endif
    % if request.user == design.owner:
    </a>
    % else:
    ## TODO (bc/nutron): Shouldn't be able to edit someone else's design. Let user clone instead.
    <a href="${ url('beeswax.views.clone_design', design_id=design.id) }" title="Copy this query.">Clone</a>
    % endif
  % else:
    [ Auto generated action ]
  % endif
</%def>

<div class="container-fluid">
	<h1>Beeswax: Query History</h1>
	<div class="row-fluid">
		<div class="span3">
			<div class="well sidebar-nav">
				<ul class="nav nav-list">
					<li class="nav-header">Actions</li>
					% if filter_params.get('user') == '_all':
				      <%
				        my_querydict = filter_params.copy()
				        my_querydict['user'] = request.user.username
				      %>
					<li><a href="?${my_querydict.urlencode()}">Show my queries</a></li>
				 	% else:
				      <%
				        my_querydict = filter_params.copy()
				        my_querydict['user'] = '_all'
				      %>
				      <li><a href="?${my_querydict.urlencode()}">Show everyone's queries</a></li>
				    % endif

				 	% if filter_params.get('auto_query', None):
				      <%
				        my_querydict = filter_params.copy()
				        my_querydict['auto_query'] = ''
				      %>
				      <li><a href="?${my_querydict.urlencode()}">Show user queries</a></li>
				    % else:
				      <%
				        my_querydict = filter_params.copy()
				        my_querydict['auto_query'] = 'on'
				      %>
				      <li><a href="?${my_querydict.urlencode()}">Show auto actions</a></li>
				    % endif
				</ul>
			</div>
		</div>
		<div class="span9">

		<table class="table table-striped table-condensed datatables">
		    <thead>
		      <tr>
		        <th>Time</th>
		        <th>Name</th>
		        <th>Query</th>
		        <th>User</th>
		        <th>State</th>
		        <th>Result</th>
		      </tr>
		    </thead>
		    <tbody>
		    <%!
		      from beeswax import models, views
		    %>
		    % for query in page.object_list:
		      <%
		        qcontext = ""
			try:
			  design = query.design
		          qcontext = views.make_query_context('design', design.id)
			except:
			  pass
		      %>
		      <tr class="histRow" data-search="${show_saved_query(design, query)}">
		        <td>${query.submission_date.strftime("%x %X")}</td>
		        <td>${show_saved_query(design, query)}</td>
		        <td>
		          <p>
		            % if len(query.query) > 100:
		              <code>${collapse_whitespace(query.query[:100])}...</code>
		            % else:
		              <code>${collapse_whitespace(query.query)}</code>
		            % endif
		          </p>
		        </td>
		        <td>${query.owner}</td>
		        <td>${models.QueryHistory.STATE[query.last_state]}</td>
		        <td>
		          % if qcontext and query.last_state != models.QueryHistory.STATE.expired.index:
		            <a href="${ url('beeswax.views.watch_query', id=query.id) }?context=${qcontext|u}">Results</a>
		          % else:
		            ~
		          % endif
		        </td>
		      </tr>
		    % endfor
		    </tbody>
		  </table>
		 ${comps.pagination(page)}
		</div>
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



	});
</script>
${commonfooter()}
