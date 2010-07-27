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
${wrappers.head('Choose a Delimiter')}
<div class="toolbar">
  <ul class="ccs-breadcrumb clearfix">
    ## TODO(marcus) These links should be part of the form, and do POST
    <li><a href="${ url('beeswax.create_table.import_wizard') }">Choose File</a></li>
    <li class="tabSelected"><a href="${ url('beeswax.create_table.import_wizard') }">Choose Delimiter</a></li>
    <li><a href="${ url('beeswax.create_table.import_wizard') }">Define Columns</a></li>
  </ul>
</div>
<div class="view" id="choose-delimiter">
    <div class="bw-choose-delimiter">
        <div class="ccs-bc-section">
          <form action ="${action}" method="POST">
            <div class="ccs-hidden">
              ${util.render_form(file_form)}
              ${comps.field(delim_form['file_type'])}
            </div>
            <a name="step2"></a>
            <dt>Step 2: Choose A Delimiter</dt>
            <dd>
              <dl class="clearfix">
                <dt>
                  % if initial:
                    <div class="bw-confirm_delim" style="display: none">
                      <p class="delimiter_confirmation">Beeswax has determined that this file is delimited by ${delim_readable}.  Is this correct?</p>
                      <label>
                        Yes
                        ## TODO(marcus)  The YES button does nothing
                        <input type="submit" name="submit_delim" value="Select this Delimiter" class="ccs-hidden"/>
                      </label>
                      <label>
                        No
                        ## TODO(marcus)  The NO + preview jump out of jframe
                        <input type="button" name="No" class="ccs-hidden"/>
                      </label>
                    </div>
                  % endif
                  <div class="bw-select_delim" class="ccs-hidden">
                    ${comps.field(delim_form["delimiter"], render_default=True, help=r'Enter the column delimiter.  Must be a single character.  Use syntax like "\001" or "\t" for special characters.', klass="ccs-select-with-other")}

                    <input class="ccs-hidden" type="submit" value="Preview" name="submit_preview"/>
                    <input class="ccs-hidden" type="submit" value="Select this Delimiter" name="submit_delim"/>
                  </div>
                  <div class="delimiter_preview_holder">
                    <table class="delimiter_preview">
                      <thead>
                        <tr>
                          % for i in range(n_cols):
                            <th>col_${i+1}</th>
                          % endfor
                        </tr>
                      </thead>
                      <tbody>
                        % for row in fields_list:
                          <tr>
                            % for val in row:
                            <td>${val}</td>
                            % endfor
                          </tr>
                        % endfor
                      </tbody>
                    </table>
                  </div>
                </dt>
              </dl>
              <a class="ccs-submit_form ccs-visible ccs-multipart-next" data-extra-data="{'submit_delim': 'Step 3: Define Your Columns'}">
              Step 3: Define Your Columns&raquo;
              </a>
              <input type="submit" name="submit_delim" value="Step 3: Define Your Columns" class="ccs-hidden"/>
            </dd>
          </div>
        </form>
      </div>
</div>
${wrappers.foot()}
