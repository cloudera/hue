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

<div class="view" id="watch_results">
  <div class="splitview resizable">
    <div class="left_col">
      ${util.render_query_context(query_context)}
        <dl class="jframe_padded">
          % if download_urls:
            ## Download results
            <dt class="ccs-dt_cap">Actions</dt>
            <dd class="ccs-dd_bottom bw-actions">
              <ul>
                <li><a target="_blank" href="${download_urls["csv"]}" class="bw-download_csv">Download as CSV</a>
                <li><a target="_blank" href="${download_urls["xls"]}" class="bw-download_xls">Download as XLS</a>
                <li><a class="bw-save collapser jframe_ignore" href="${url('beeswax.views.save_results', query.id)}">Save</a>
                  <div class="collapsible accordion ccs-hidden bw-save_query_results" style="display:none"> 
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
                        <a class="ccs-art_button ccs-choose_file" data-icon-styles="{'width': 16, 'height': 16, 'top': 1, 'left': 4 }" data-chooseFor="target_dir">Choose File</a>
                      </div>
                      <input type="submit" value="Save" name="save" class="ccs-art_button"> 
                    </form>
                  </div>
                </li>
              </ul>
            </dd>
          % endif
          <%
            n_jobs = hadoop_jobs and len(hadoop_jobs) or 0
            mr_jobs = (n_jobs == 1) and "MR Job" or "MR Jobs"
          %>
          <dt class="ccs-dt_cap">${mr_jobs}</dt>
          <dd class="ccs-dd_bottom bw-actions">
            <ul>
              % if n_jobs > 0:
                <h3 class="ccs-hidden">This query launched ${n_jobs} ${mr_jobs}:</h3>
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
    <div class="right_col">
      <div class="ccs-tab_ui">
          <ul class="toolbar bw-results_tabs ccs-tabs ccs-right clearfix">
            <li><span>
                % if error:
                  Error
                % else:
                  Results
                % endif
              </span></li>
            <li><span>Query</span></li>
            <li><span>Log</span></li>
          </ul>

        <ul class="ccs-tab_sections ccs-clear">
          <li>
            % if error:
              <div class="ccs-error jframe_padded">
                <h3 class="ccs-hidden">Error!</h3> 
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
              <table class="ccs-data_table" cellpadding="0" cellspacing="0">
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
          </li>
          <li class="jframe_padded">
            <pre>${query.query}</pre>
          </li>
          <li class="jframe_padded">
            <pre>${log}</pre>
          </li>
        </ul>
      </div>
    </div>
  </div>
</div>
${wrappers.foot()}
