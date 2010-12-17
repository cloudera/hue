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
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="wrappers" file="header_footer.mako" />
<%namespace name="util" file="util.mako" />
${wrappers.head('Query Explanation', section='saved queries')}
<div class="view" id="watch_wait">
  <div class="resizable" data-filters="SplitView">
    <div class="left_col">
      ${util.render_query_context(query_context)}
    </div>
    <div class="right_col jframe_padded">
      <div data-filters="Tabs">
        <ul class="toolbar bw-results_tabs tabs jframe-right clearfix">
          <li><span>Explanation</span></li>
          <li><span>Query</span></li>
        </ul>

        <ul class="tab_sections jframe-clear">
          <li>
            <pre>${explanation}</pre>
          </li>
          <li>
            <pre>${query}</pre>
          </li>
        </ul>
      </div>
    </div>
  </div>
</div>
${wrappers.foot()}
