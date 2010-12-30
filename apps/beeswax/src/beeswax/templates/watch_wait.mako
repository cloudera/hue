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

<div class="view" id="watch_wait">
  <div class="resizable" data-filters="SplitView">
    <div class="left_col">
      ${util.render_query_context(query_context)}
      <dl class="jframe_padded">
        % if download_urls:
        <dt class="hue-dt_cap">Downloads</dt>
        <dd class="hue-dd_bottom bw-actions">
          <ul>
            <li><a target="_blank" href="${download_urls["csv"]}" class="bw-download_csv">Download as CSV</a>
            <li><a target="_blank" href="${download_urls["xls"]}" class="bw-download_xls">Download as XLS</a>
          </ul>
        </dd>
        % endif
      <%
        n_jobs = hadoop_jobs and len(hadoop_jobs) or 0
        mr_jobs = (n_jobs == 1) and "MR Job" or "MR Jobs"
      %>
      <dt class="hue-dt_cap">${mr_jobs}</dt>
        <dd class="hue-dd_bottom bw-actions">
          <ul data-single-partial-id="num_jobs">
            % if n_jobs > 0:
              <h3 class="jframe-hidden">This query launched ${n_jobs} ${mr_jobs}:</h3>
              <ul class="beeswax_hadoop_job_links">
                % for jobid in hadoop_jobs:
                <li><a href="${url("jobbrowser.views.single_job", jobid=jobid)}" target="JobBrowser" class="bw-hadoop_job">${jobid.replace("job_", "")}</a></li>
                % endfor
              </ul>
            % else:
              <p class="bw-no_jobs">No Hadoop jobs were launched in running this query.</p>
            % endif 
          </ul>
        </dd>
      </dl>
    </div>
    <div class="right_col jframe_padded">
      <div data-filters="Tabs">
        <ul class="toolbar bw-results_tabs tabs jframe-right clearfix">
          <li><span>Log</span></li>
          <li><span>Query</span></li>
        </ul>

        <ul class="tab_sections jframe-clear">
          <li>
            <h3 class="jframe-hidden">Server Log</h3>
            <pre data-single-partial-id="log">${log}</pre>
          </li>
          <li>
            <pre>${query.query}</pre>
          </li>
        </ul>
    </div>
  </div>
</div>
${wrappers.foot()}
