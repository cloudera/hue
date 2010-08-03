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
${wrappers.head("Beeswax: Table List", section='tables')}
  <div class="toolbar">
    <div class="bw-show_tables_subnav" data-filters="ArtButtonBar">
      % if not examples_installed:
        <a href="${ url('beeswax.views.install_examples') }" data-filters="ArtButton" class="bw-install_samples" data-icon-styles="{'width': 16, 'height': 16, 'top': 1}">install samples</a>
      % endif
      <a href="${ url('beeswax.create_table.index') }" data-filters="ArtButton" class="bw-new_table" data-icon-styles="{'width': 16, 'height': 16, 'top': 1}">new table</a>
    </div>
  </div>

<div id="show_tables" class="view">
  <h2 class="ccs-hidden">Tables</h2>

  <table data-filters="HtmlTable" class="selectable sortable" cellpadding="0" cellspacing="0">
    <thead>
      <tr>
        <th>Table Name</th>
        <th>Browse</th>
      </tr>
    </thead>
    <tbody>
      % for table in tables:
        <tr data-dblclick-delegate="{'dblclick_loads':'.bw-tables_table a'}" class="ccs-no_select">
          <td class="bw-tables_table ccs-no_select">
            <a href="${ url("beeswax.views.describe_table", table=table) }">${ table }</a>
            <!-- <p class="ccs-inline" data-filters="HelpTip">TODO</p> -->
          </td>
          <td class="bw-tables_browse"><a href="${ url("beeswax.views.read_table", table=table) }">Browse Data</a></td>
        </tr>
      % endfor
    </tbody>
  </table>
</div>
${wrappers.foot()}
