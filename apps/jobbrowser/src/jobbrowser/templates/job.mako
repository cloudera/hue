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
<%namespace name="comps" file="jobbrowser_components.mako" />
<%!
  from jobbrowser.views import format_counter_name
  from filebrowser.views import location_to_url
  import os
  import re
%>

<%def name="task_table(tasks)">
  <table class="taskTable">
    <thead>
      <tr>
        <th>Tasks</th>
        <th>Type</th>
		<th>&nbsp;</th>
      </tr>
    </thead>
    <tbody>
      % for task in tasks:
        <tr>
			<td>${task.taskId_short}</td>
			<td>${task.taskType}</td>
          	<td>
				<a title="View this task" href="${ url('jobbrowser.views.single_task', jobid=job.jobId, taskid=task.taskId) }">View</a>
			</td>
        </tr>
      % endfor
    </tbody>
  </table>
</%def>
<%def name="rows_for_conf_vars(rows)">
    %  for k, v in rows.iteritems():
      <tr>
          <td>${format_counter_name(k)}</td>
          <%
            splitArray = v.split(",")
          %>
            <td>
            % for i, val in enumerate(splitArray):
               <%
                  url_splitted = request.fs.urlsplit(val)
                  is_hdfs_uri = bool(url_splitted[1])
               %>
               % if is_hdfs_uri:
                  <%
                    if request.fs.isfile(url_splitted[2]):
                      target = "FileViewer"
                    else:
                      target = "FileBrowser"
                  %>
                  <a href="${location_to_url(request, val)}" title="${val}" target="${target}">${val}</a>
                  % if i != len(splitArray) - 1:
                    <br>
                  % endif  
               % else: 
                  ${val}
               % endif
            % endfor
            </td>
        </tr>
    % endfor
</%def>

${comps.header("Job: " + job.jobId + " - Job Browser", "", "Job Details")}

	<div class="sidebar">
		<div class="well">
			<h6>Job ID</h6>
			${job.jobId}
			
			<h6>User</h6>
			${job.user}
			
			<h6>Status</h6>
			% if job.status.lower() == 'running' or job.status.lower() == 'pending':
				<span class="label warning">${job.status.lower()}</span>
			% elif job.status.lower() == 'succeeded':
				<span class="label success">${job.status.lower()}</span>
			% else:
				<span class="label">${job.status.lower()}</span>
			% endif
			
			% if job.status.lower() == 'running' or job.status.lower() == 'pending':
	        <h6>Kill Job</h6>
			<a href="${url('jobbrowser.views.kill_job', jobid=job.jobId)}" title="Kill this job">Kill this job</a>
	        % endif
			
			
			<h6>Output</h6>
			<%
	            output_dir = job.conf_keys.get('mapredOutputDir', "")
	            location_url = location_to_url(request, output_dir)
	            basename = os.path.basename(output_dir)
	            dir_name = basename.split('/')[-1]
	          %>
	          % if location_url != None:
	            <a href="${location_url}" title="${output_dir}">${dir_name}</a>
	          % else:
	            ${dir_name}
	          % endif
		</div>
	</div>
    
    <div class="content">
		<h1>Job Details</h1>
		<ul class="tabs">
			<li class="active"><a href="#tasks">Tasks</a></li>
			<li><a href="#metadata">Metadata</a></li>
			<li><a href="#counters">Counters</a></li>
		</ul>

		<div class="tab-content">
			<div class="tab-pane active" id="tasks">
				<dl>
	                <dt>Maps:</dt>
	                <dd>${comps.mr_graph_maps(job)}</dd>
	                <dt>Reduces:</dt>
	                <dd>${comps.mr_graph_reduces(job, right_border=True)}</dd>
	              </dl>
	            %if failed_tasks:
	            <div>
	              <h3>
	                <a href="${url('jobbrowser.views.tasks', jobid=job.jobId)}?taskstate=failed">View Failed Tasks &raquo;</a>
	                Failed Tasks
	              </h3>
	              <div class="jt_task_list_container">
	                ${task_table(failed_tasks)}
	              </div>
	            </div>
	            %endif
	            <div>
					<a style="float:right;margin-right:10px" href="${url('jobbrowser.views.tasks', jobid=job.jobId)}">View All Tasks &raquo;</a>
	              <h3>
	                Recent Tasks
	              </h3>
	              <div class="jt_task_list_container">
	                ${task_table(recent_tasks)}
	              </div>
	            </div>
	
			</div>
			<div id="metadata" class="tab-pane">
				<div class="toolbar">
					<form>
						<b>Filter metadata:</b>
						<ul>
							<li>
								<input type="text" id="metadataFilter" title="Text Filter" placeholder="Text Filter"/>
							</li>
						</ul>
					</form>
		        </div>
				 <table id="metadataTable">
		              <thead>
		                <th>Name</th>
		                <th>Value</th>
		              </thead>
		              <tbody>
		                <tr>
		                  <td>ID</td>
		                  <td>${job.jobId}</td>
		                </tr>
		                <tr>
		                  <td>User</td>
		                  <td>${job.user}</td>
		                </tr>
		                <tr>
		                  <td>Maps</td>
		                  <td>${job.finishedMaps} of ${job.desiredMaps}</td>
		                </tr>
		                <tr>
		                  <td>Reduces</td>
		                  <td>${job.finishedReduces} of ${job.desiredReduces}</td>
		                </tr>
		                <tr>
		                  <td>Started</td>
		                  <td>${job.startTimeFormatted}</td>
		                </tr>
		                <tr>
		                  <td>Ended</td>
		                  <td>${job.finishTimeFormatted}</td>
		                </tr>
		                <tr>
		                  <td>Duration</td>
		                  <td>${job.duration}</td>
		                </tr>
		                <tr>
		                  <td>Status</td>
		                  <td>${job.status}</td>
		                </tr>
		                ${rows_for_conf_vars(job.conf_keys)}
		             
		              </tbody>
		            </table>
					<h3>Raw configuration:</h3>
				 <table id="rawConfigurationTable">
		              <thead>
		                <th>Name</th>
		                <th>Value</th>
		              </thead>
		              <tbody>

		              % for key, value in sorted(job.full_job_conf.items()):
		                <tr>
		                  <td width="20%">${key}</td>
		                  <td>
							<div class="wordbreak">
								${value}
							</div>
						  </td>
		                </tr>
		              % endfor
		              </tbody>
		            </table>

			</div>
			<div id="counters" class="tab-pane">
				${comps.job_counters(job.counters)}
			</div>
		</div>
	</div>

		<script type="text/javascript" charset="utf-8">
			$(document).ready(function(){
				$(".tabs").tabs();
				$(".taskTable").dataTable({
					"bPaginate": false,
				    "bLengthChange": false,
					"bInfo": false,
					"bAutoWidth": false,
					"aoColumns": [ 
						{ "sWidth": "40%" },
						{ "sWidth": "40%" },
						{ "sWidth": "20%" }
					]
				});
				var _metadataTable = $("#metadataTable").dataTable({
					"bPaginate": false,
				    "bLengthChange": false,
					"bInfo": false,
					"bAutoWidth": false,
					"aoColumns": [ 
						{ "sWidth": "30%" },
						{ "sWidth": "70%" }
					]
				});
				var _rawConfigurationTable = $("#rawConfigurationTable").dataTable({
					"bPaginate": false,
				    "bLengthChange": false,
					"bInfo": false,
					"bAutoWidth": false,
					"aoColumns": [ 
						{ "sWidth": "30%" },
						{ "sWidth": "70%" }
					]
				});
				
				$("#metadataFilter").keydown(function(){
					_metadataTable.fnFilter($(this).val());
					_rawConfigurationTable.fnFilter($(this).val());
				});
				
				$(".jobCountersTable").dataTable({
					"bPaginate": false,
				    "bLengthChange": false,
					"bInfo": false,
					"bAutoWidth": false,
					"aoColumns": [ 
						{ "sWidth": "40%" },
						{ "sWidth": "20%" },
						{ "sWidth": "20%" },
						{ "sWidth": "20%" }
					]
				});

				$(".dataTables_wrapper").css("min-height","0");
				$(".dataTables_filter").hide();

			});
		</script>


    ${comps.footer()}
