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
${wrappers.head("Beeswax Table Metadata: " + table.tableName, section='tables')}
<div id="describe_table" class="view">
  <%def name="column_table(cols)">
    <div class="bw-col_table_wrapper">
      <table class="sortable" data-filters="HtmlTable" cellpadding="0" cellspacing="0">
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Comment</th>
          </tr>
        </thead>
        <tbody>
          % for column in cols:
            <tr>
              <td>${ column.name }</td>
              <td>${ column.type }</td>
              <td>${ column.comment or "" }</td>
            </tr>
          % endfor
        </tbody>
      </table>
    </div>
  </%def>

  <div class="resizable" data-filters="SplitView">
    <div class="left_col">
      <h2>${table.tableName}</h2>
      <div class="jframe_padded">
        <dl>
          % if table.parameters.get("comment", False):
            <dt class="hue-dt_cap">Description</dt>
            <dd class="hue-dd_bottom">${ table.parameters.get("comment") }</dd>
          % endif
          <dt class="hue-dt_cap">Actions</dt>
          <dd class="hue-dd_bottom bw-actions">
            <ul>
              <li class="jframe-clear" data-filters="CollapsingElements"><a class="bw-load_data collapser">Import Data</a>
                  <div class="collapsible jframe-hidden">
                    <form action="${ url("beeswax.views.load_table", table=table_name) }">
                      <dl>
                        <div class="bw-dataNote">
                        Note that loading data will move data from its location into the table's storage location.
                        </div>
                        ## Any existing data will be erased!
                        <div class="bw-overwriteLabel">Overwrite existing data ? <input type="checkbox" name="overwrite" class="bw-overwriteCheckbox"/></div>
                        ##Path (on HDFS) of files to load.
                        ${comps.field(load_form["path"], title_klass='bw-pathLabel', attrs=dict(
                          klass='bw-loadPath',
                          data_filters="OverText",
                          alt='/user/data'))}
                        <div class="clearfix" data-filters="ArtButtonBar">
                          <a class="hue-choose_file" data-filters="ArtButton" 
                            data-icon-styles="{'width': 16, 'height': 16, 'top': 1, 'left': 4 }" data-chooseFor="path">Choose File</a>
                          <input type="submit" class="bw-loadSubmit" data-filters="ArtButton" value="Submit"/>
                        </div>
                        
                        % for pf in load_form.partition_columns:
                          ${comps.field(load_form[pf], render_default=True)}
                        % endfor
                        ## This table is partitioned.  Therefore,
                        ## you must specify what partition
                        ## this data corresponds to.
                      </dl>
                    </form>
                  </div>
              </li>
              <li class="jframe-clear"><a href="${ url("beeswax.views.read_table", table=table_name) }" class="bw-browse_data">Browse Data</a></li>
              <li class="jframe-clear"><a href="${ url("beeswax.views.drop_table", table=table_name) }" class="bw-drop_table">Drop Table</a></li>
              <li class="jframe-clear"><a href="${hdfs_link}" target="FileBrowser" class="tip bw-location_link" data-filters="PointyTip" data-tip-direction="11" rel="${ table.sd.location }">View File Location</a></li>
            </ul>
          </dd>
        </dl>
      </div>
    </div>
    <div class="right_col">
      <div data-filters="Tabs">
        <ul class="toolbar tabs">
          % if top_rows is not None:
            <li><span>Sample</span></li>
          % endif
          <li><span>Columns</span></li>
          % if len(table.partitionKeys) > 0:
            <li><span>Partition Columns</span></li>
          % endif
        </ul>
        <ul class="tab_sections jframe-clear">
          % if top_rows is not None:
            <li class="bw-table_sample">
              <table data-filters="HtmlTable" cellpadding="0" cellspacing="0">
                <thead>
                  <tr>
                    % for col in table.sd.cols:
                      <th>${col.name}</th>
                    % endfor
                  </tr>
                </thead>
                <tbody>
                  % for i, row in enumerate(top_rows):
                    <tr>
                      % for item in row:
                        <td>${ item }</td>
                      % endfor
                    </tr>
                  % endfor
                </tbody>
              </table>
            </li>
          % endif
          <li>${column_table(table.sd.cols)}</li>
          % if len(table.partitionKeys) > 0:
            <li>
              ${column_table(table.partitionKeys)}
              <a href="${ url("beeswax.views.describe_partitions", table=table_name) }">Show Partitions</a>
            </li>
          % endif
        </ul>
      </div>

${wrappers.foot()}
