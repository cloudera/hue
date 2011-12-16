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
<%namespace name="comps" file="beeswax_components.mako" />
${wrappers.head("Beeswax: Query Results", section='query')}
<h1>Beeswax: Query Results: ${util.render_query_context(query_context)}</h1>
<div class="sidebar withTitle">
	<div class="well">
		% if download_urls:
		<h6>Downloads</h6>
		<ul>
			<li><a target="_blank" href="${download_urls["csv"]}" class="bw-download_csv">Download as CSV</a></li>
			<li><a target="_blank" href="${download_urls["xls"]}" class="bw-download_xls">Download as XLS</a></li>
			<li><a href="${url('beeswax.views.save_results', query.id)}">Save</a></li>
		</ul>
 		% endif
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
	
                <div class="collapsible jframe-hidden bw-save_query_results" style="display:none" data-filters="Accordion"> 
                  <form action="${url('beeswax.views.save_results', query.id) }" method="POST">
                    ## Writing the save_target fields myself so I can match them to their respective text input fields.
                    <div> 
                      <input id="id_save_target_0" type="radio" name="save_target" value="to a new table" class="toggle" checked="checked"/>
                      <label for="id_save_target_0">In a new table</label>
                    </div>
                    ${comps.field(save_form['target_table'], notitle=True, klass="target", attrs=dict(
                      data_filters="OverText",
                      alt="table_name"
                    ))}
                    <div>
                      <input id="id_save_target_1" type="radio" name="save_target" value="to HDFS directory" class="toggle"> 
                      <label for="id_save_target_1">In an HDFS directory</label>
                    </div>
                    <div class="target">
                      ${comps.field(save_form['target_dir'], notitle=True, attrs=dict(
                      data_filters="OverText",
                      alt="/user/dir"
                      ))}
                      <a data-filters="ArtButton" class="hue-choose_file" data-icon-styles="{'width': 16, 'height': 16, 'top': 1, 'left': 4 }" data-chooseFor="target_dir">Choose File</a>
                    </div>
                    <input type="submit" value="Save" name="save" data-filters="ArtButton"> 
                  </form>
                </div>

				<ul class="tabs">
					<li class="active"><a href="#results">
		  			%if error:
			            Error
					%else:
						Results
					%endif
					</a></li>
					<li><a href="#query">Query</a></li>
					<li><a href="#log">Log</a></li>
				</ul>
	
				<div class="tab-content">
					<div class="active tab-pane" id="results">
					% if error:
		            <div class="jframe-error jframe_padded">
		              <h3 class="jframe-hidden">Error!</h3> 
		              <pre>${error_message}</pre>
		            </div>
          			% else:
            		<div class="bw-result_nav toolbar">
		              % if has_more:
		                <a href="${ url('beeswax.views.view_results', query.id, next_row) }" title="Next page" class="bw-nextBlock">[next]</a>
		              % endif
		              % if start_row != 0:
		                <a href="${ url('beeswax.views.view_results', query.id, 0) }" title="Back to first row" class="bw-firstBlock">[top]</a>
		              % endif
		            </div>
		            % if expected_first_row != start_row:
		              <div class="bw-result_warning">Warning:</i> Page offset may have incremented since last view.</div>
		            % endif
            		<table class="resultTable" cellpadding="0" cellspacing="0">
		              <thead>
		                <tr>
		                  <th>-</th>
		                  % for col in columns:
		                    <th>${col}</th>
		                  % endfor
		                </tr>
		              </thead>
		              <tbody>
		                % for i, row in enumerate(results):
		                <tr>
		                  <td>${start_row + i}</td>
		                  % for item in row:
		                    <td>${ item }</td>
		                  % endfor
		                </tr>
		                % endfor
		              </tbody>
		            </table>
		          % endif
				</div>
				<div class="tab-pane" id="query">
					
						<pre>${query.query}</pre>
					
				</div>
				<div class="tab-pane" id="log">
					<pre>${log}</pre>
				</div>
			</div>

</div>

<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		$(".tabs").tabs();
		$(".resultTable").dataTable({
			"bPaginate": false,
		    "bLengthChange": false,
			"bInfo": false
		});
		$(".dataTables_wrapper").css("min-height","0");
		$(".dataTables_filter").hide();

	});
</script>

${wrappers.foot()}
