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
<%namespace name="util" file="util.mako" />
${wrappers.head("Beeswax: Waiting for query...", section='query')}

<meta http-equiv="refresh" content="3;${url('beeswax.views.watch_query', query.id)}?${fwd_params}" />

<h1>${util.render_query_context(query_context)}</h1>
<div class="sidebar">
	<div class="well">
		% if download_urls:
		<h6>Downloads</h6>
		<a target="_blank" href="${download_urls["csv"]}" class="bw-download_csv">Download as CSV</a><br/>
		<a target="_blank" href="${download_urls["xls"]}" class="bw-download_xls">Download as XLS</a><br/>
		<a class="bw-save collapser jframe_ignore" href="${url('beeswax.views.save_results', query.id)}">Save</a><br/>
		%endif
		<br/>
		<%
          n_jobs = hadoop_jobs and len(hadoop_jobs) or 0
          mr_jobs = (n_jobs == 1) and "MR Job" or "MR Jobs"
        %>
        
	 	% if n_jobs > 0:
			<h6>${mr_jobs} (${n_jobs})</h6>
	             
			% for jobid in hadoop_jobs:
			<a href="${url("jobbrowser.views.single_job", jobid=jobid)}" class="bw-hadoop_job">${jobid.replace("job_", "")}</a><br/>
			% endfor
		% else:
			<h6>${mr_jobs}</h6>
			<p class="bw-no_jobs">No Hadoop jobs were launched in running this query.</p>
		% endif 
	</div>
</div>


<div class="content">
	
	<ul class="tabs">
		<li class="active"><a href="#log">Log</a></li>
		<li><a href="#query">Query</a></li>
	</ul>
  
   	<div class="pill-content">
		<div class="active" id="log">
			<pre>${log}</pre>
		</div>
		<div id="query">
			<pre>${query.query}</pre>
		</div>
	</div>
</div>

<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$(".tabs").tabs();
	

	});
</script>
${wrappers.foot()}
