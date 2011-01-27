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
<%namespace name="util" file="util.mako" />
${wrappers.head('Define Columns')}
<div class="toolbar">
  <ul class="clearfix" data-filters="Breadcrumb">
    ## TODO(marcus) These links should be part of the form, and do POST
    <li><a href="${ url('beeswax.create_table.import_wizard') }">Choose File</a></li>
    <li><a href="${ url('beeswax.create_table.import_wizard') }">Choose Delimiter</a></li>
    <li class="tabSelected"><a href="${ url('beeswax.create_table.import_wizard') }">Define Columns</a></li>
  </ul>
</div>
<div class="view" id="define-columns">
  <div class="bw-define-columns">
    <form action="${action}" method="POST">
      <div class="jframe-hidden">
        ${util.render_form(file_form)}
        ${util.render_form(delim_form)}
        ${unicode(column_formset.management_form) | n}
      </div>
      <div class="hue-bc-section">
      <dt> Step 3: Define Your Columns </dt>
      <%
        n_rows = len(fields_list)
        if n_rows > 2: n_rows = 2
      %>
      <dd>
          Beeswax has attempted to determine the types of your columns.  Please check them as you name the columns.
        <dl class="clearfix">
          <br/>
          <dt> </dt>
          <dd>
            <table class="row_headers jframe-visible" style="display:none">
              % for i in range(n_rows):
                <tr><td> Row ${i + 1} </td></tr>
              % endfor
              <tr><td>&nbsp;</td></tr>
              <tr><td class="input_row_header"> Column Name </td></tr>
              <tr><td class="input_row_header"> Type </td></tr>
            </table>
            <div class="table_holder">
              <table class="data_table">
                % for i, row in enumerate(fields_list[:n_rows]):
                  <tr>
                    <td class="jframe-hidden"> Row ${i + 1} </td>
                    % for val in row:
                      <td>${val}</td>
                    % endfor
                  </tr>
                % endfor
                <tr><td colspan="${n_cols}">&nbsp;</td></tr>
                <tr>
                  % for form in column_formset.forms:
                    <td>
                      ${comps.field(form["column_name"],
                        render_default=False,
                        help="Column name",
                      )}
                      ${comps.field(form["column_type"],
                        render_default=True,
                        help="Type for this column",
                      )}
                      ${unicode(form["_exists"]) | n}
                    </td>
                  %endfor
                </tr>
              </table>
            </div>
          </dd>
          </dl>
          <a class="jframe-submit_form jframe-visible hue-multipart-next" data-extra-data="{'submit_create': 'Finish Creating Table'}" style="display:none">
          Finish Creating Table
          </a>
          <input type="submit" name="submit_create" value="Finish Creating Table" class="jframe-hidden"/>
          <br/><br/><br/>
        </dd>
      </div>
    </form>
  </div>
</div>
${wrappers.foot()}
