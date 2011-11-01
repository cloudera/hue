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
<%namespace name="wrappers" file="header_footer.mako" />
<%namespace name="comps" file="beeswax_components.mako" />
<%!  from beeswax.views import collapse_whitespace %>
${wrappers.head("Beeswax: Query History", section='history')}
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

<h1>History</h1>

<div class="sidebar">
	<div class="well">
		<h6>Actions</h6>
	    % if filter_params.get('user') == '_all':
	      <%
	        my_querydict = filter_params.copy()
	        my_querydict['user'] = request.user.username
	      %>
	   <a href="?${my_querydict.urlencode()}">Show my queries</a>
	 % else:
	      <%
	        my_querydict = filter_params.copy()
	        my_querydict['user'] = '_all'
	      %>
	      <a href="?${my_querydict.urlencode()}">Show everyone's queries</a>
	    % endif
	
	 % if filter_params.get('auto_query', None):
	      <%
	        my_querydict = filter_params.copy()
	        my_querydict['auto_query'] = ''
	      %>
	      <a href="?${my_querydict.urlencode()}" class="bw-show_group_noauto" data-filters="ArtButton">Show user queries</a>
	    % else:
	      <%
	        my_querydict = filter_params.copy()
	        my_querydict['auto_query'] = 'on'
	      %>
	      <a href="?${my_querydict.urlencode()}" class="bw-show_group_auto" data-filters="ArtButton">Show auto actions</a>
	    % endif
    </div>
</div>


<div class="content">
 

  
  <table class="datatables">
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
      <tr data-dblclick-delegate="{'dblclick_loads':'.bw-view_result'}" class="jframe-no_select hue-help_links_small">
        <td>${query.submission_date.strftime("%x %X")}</td>
        <td>${show_saved_query(design, query)}</td>
        <td>
          <p class="jframe-inline" data-filters="InfoTip">
            % if len(query.query) > 100:
              <code>${collapse_whitespace(query.query[:100])}...</code>
            % else:
              <code>${collapse_whitespace(query.query)}</code>
            % endif
          </p>
        </td>
        <td>${query.owner}</td>
        <td>${models.QueryHistory.STATE[query.last_state]}</td>
        <td class="bw-query_result">
          % if qcontext and query.last_state != models.QueryHistory.STATE.expired.index:
            <a href="${ url('beeswax.views.watch_query', id=query.id) }?context=${qcontext|u}" class="bw-view_result" data-filters="ArtButton" data-icon-styles="{'width': 16, 'height': 16, 'top': 2}">Results</a>
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
<!-- <div>
  <div class="bw-input-filter">
    <input type="text" class="jframe-hidden" data-filters="OverText, ArtInput, FilterInput" data-art-input-type="search"
      title="Filter by Name"
      data-filter-elements="tbody tr" value=""/>
  </div> -->
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
