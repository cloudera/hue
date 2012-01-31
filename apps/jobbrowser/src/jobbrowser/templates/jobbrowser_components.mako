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

<%def name="task_counters(counters)">
<%
  from jobbrowser.views import format_counter_name
%>
	% for group in counters.groups:
		<h3>${format_counter_name(group.displayName)}</h3>
	    <table class="taskCountersTable">
	      <thead>
	         <tr>
	           <th>Counter Name</th>
	           <th>Value</th>   
	        </tr>
	      </thead>
	      <tbody>
	      % for name, counter in sorted(group.counters.iteritems()):
	       <tr>
	          <td class="jt_counter_display_name">${format_counter_name(counter.displayName)}</td>
	          <td class="jt_counter_total">${counter.value}</td>
	        </tr>
	      % endfor
      </tbody>
     </table>
      % endfor
</%def>

<%def name="job_counters(counters)">
<%
  from jobbrowser.views import format_counter_name
%>

	% for group in counters.itervalues():
      <h3>${format_counter_name(group['displayName'])}</h3>
	  <table class="jobCountersTable">
      <thead>
         <tr>
           <th>Name</th>
           <th>Maps Total</th>
           <th>Reduces Total</th>
           <th>Total</th>   
        </tr>
      </thead>
      <tbody>
		 % for name, counter in sorted(group['counters'].iteritems()):
	      <%
	        map_count = counter.get('map', 0)
	        reduce_count = counter.get('reduce', 0)
	        job_count = counter.get('job', 0)
	      %>
	       <tr>
	          <td>${format_counter_name(counter.get('displayName', 'n/a'))}</td>
	          <td>${map_count}</td>
	          <td>${reduce_count}</td>
	          <td>${map_count + reduce_count + job_count}</td>
	        </tr>
	      % endfor
			</tbody>
	     </table>
	% endfor
    

   
</%def>

<%def name="mr_graph(job)">
  <div class="jt_mr_display">
    ${mr_graph_maps(job)}
    ${mr_graph_reduces(job)}
  </div>
</%def>

<%def name="mr_graph_maps(job)">
  <div class="jt_maps">
    <span class="jt_maps_complete" style="width: ${job.maps_percent_complete}%;">${job.finishedMaps} / ${job.desiredMaps}</span>
    <span class="jt_white_border"></span>
  </div>
</%def>
<%def name="mr_graph_reduces(job, right_border=False)">
  <div class="jt_reduces">
    <span class="jt_reduces_complete" style="width: ${job.reduces_percent_complete}%;">${job.finishedReduces} / ${job.desiredReduces}</span>
    % if right_border:
      <span class="jt_white_border"></span>
    % endif
  </div>
</%def>
