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
${wrappers.head('Choose a File')}
<div class="toolbar">
  <ul class="ccs-breadcrumb clearfix">
    <li class="tabSelected"><a href="${ url('beeswax.create_table.import_wizard') }">Choose File</a></li>
    <li><a>Choose Delimiter</a></li>
    <li><a>Define Columns</a></li>
  </ul>
</div>
<div class="view" id="choose-file">
    <div class="bw-choose-file">
      <div class="ccs-bc-section">
          <a name="step1"></a>
            <form action="${action}" method="POST">
              <dt>Step 1: Name Your Table and Choose A File</dt>
              <dd>
              <p>Enter the name of your new table and a file (compressed files are okay) to base this new table definition on.</p>
              <dl class="clearfix">
                ${comps.field(file_form["name"], attrs=dict(
                  klass='required bw-validate-name',
                  data_filters="OverText",
                  alt='table_name',
                ),
                help="Name of the new table.  Table names must be globally unique.  Table names tend to correspond as well to the directory where the data will be stored.",
                help_attrs=dict(
                  data_help_direction='1'
                )
              )}
              ${comps.field(file_form["comment"], attrs=dict(
                  klass='bw-table-comment',
                  data_filters="OverText",
                  alt='Optional'
                ),
                help="Use a table comment to describe your table.  For example, you might mention the data's provenance, and any caveats users of this table should expect.")}

                ${comps.field(file_form["path"], attrs=dict(
                    klass='required bw-validate-file',
                    data_filters="OverText",
                    alt="/user/user_name/data_dir",
                  ),
                  help="The HDFS path to the file that you would like to base this new table definition on.  It can be compressed (gzip) or not.")}
                <a class="ccs-art_button ccs-choose_file" data-icon-styles="{'width': 16, 'height' : 16, 'top' : 3, 'left' : 6 }" data-chooseFor="path">Choose File</a>
                <div class="bw-import_data">
                  ${comps.field(file_form["do_import"],
                    render_default=True,
                    help="Check this box if you want to import the data in this file after creating the table definition.  Leave it unchecked if you just want to define an empty table."
                  )}
                </div>
                ## TODO(marcus): Button style?
                <a class="ccs-multipart-next ccs-form_submit ccs-visible" style="display:none" data-extraData="{'submit_file' : 'Step 2: Choose Your Delimiter'}">
                  Step 2: Choose Your Delimiter&raquo;
                </a>
                  <input type="submit" name="submit_file" value="Step 2: Choose Your Delimiter" class="ccs-hidden ccs-form_submit ccs-multipart-next ccs-visible"/>
              </dl>
            </form>
          </dd>
        </div>
      </div>
</div>
${wrappers.foot()}
