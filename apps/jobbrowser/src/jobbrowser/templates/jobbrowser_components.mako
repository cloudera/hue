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

<%def name="header(title, section='', subsection='', subsubsection='', trackersLink=False)">
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
	<title>${title}</title>
	<link rel="stylesheet" href="/static/ext/css/bootstrap.min.css" type="text/css" media="screen" title="no title" charset="utf-8" />
	<link rel="stylesheet" href="/static/css/jhue.css" type="text/css" media="screen" title="no title" charset="utf-8" />
	
	<style type="text/css">
      body {
        padding-top: 60px;
      }
    </style>
	<script src="/static/ext/js/jquery/jquery-1.7.min.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/js/Source/jHue/jquery.showusername.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/ext/js/jquery/plugins/jquery.simpleplaceholder.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/ext/js/jquery/plugins/jquery.dataTables.1.8.2.min.js" type="text/javascript" charset="utf-8"></script>
	<script src="/static/ext/js/bootstrap-tabs.js" type="text/javascript" charset="utf-8"></script>

	

	<script type="text/javascript" charset="utf-8">
		$(document).ready(function(){
			$("#username").showUsername();
			$("input:text[placeholder]").simplePlaceholder();
			$(".submitter").keydown(function(e){
				if (e.keyCode==13){
					$(this).closest("form").submit();
				}
			}).change(function(){
				$(this).closest("form").submit();
			});
		});
	</script>
	
</head>
<body>
	<div class="topbar">
		<div class="topbar-inner">
			<div class="container-fluid">
				<a class="brand" href="#">jHue</a>
				<ul class="nav">
					<li><a href="/beeswax">Beeswax</a></li>
					<li><a href="/filebrowser/">File Browser</a></li>
					<li><a href="/jobsub/">Job Designer</a></li>
					<li class="active"><a href="/jobbrowser/jobs/">Job Browser</a></li>
					<li><a href="/useradmin/">User Admin</a></li>
					<li><a href="/shell/">Shell</a></li>
					<li><a href="/help/">Help</a></li>
					<li><a href="/about/">About</a></li>
				</ul>
				<p class="pull-right">Logged in as <strong><span id="username">xxx</span></strong> - <a href="/accounts/logout">Sign out</a></p>
			</div>
		</div>
		<!--div class="sectionbar">
			%if subsubsection != '':
				<h2 class="section selected">${section}</h2>
				<h3>&gt;</h3>
				<h2 class="subsection selected">${subsection}</h2>
				<h3>&gt;</h3>
				<h2 class="subsubsection">${subsubsection}</h2>
			%else:
				%if subsection != '':
					<h2 class="section selected">${section}</h2>
					<h3>&gt;</h3>
					<h2 class="subsection">${subsection}</h2>
				%else:
					<h2 class="section">${section}</h2>
				%endif
			%endif
			%if trackersLink:
			<a href="/jobbrowser/trackers">view all task trackers &raquo;</a>
			%endif
		</div-->
		
	</div>
	
	<div class="container-fluid">
		% if section != '':
		<h1>${section}</h1>
		% endif

</%def>

<%def name="footer()">

	</div>
</body>
</html>
</%def>


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
