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
<%!
  from desktop.lib.django_util import extract_field_data
%>

<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="wrappers" file="header_footer.mako" />
<%namespace name="util" file="util.mako" />

<%def name="query()">
  <dl class="bw-query">
    <dt class="bw-query_header clearfix ccs-help_links_small">
      % if design and not design.is_auto and design.name:
        <label>
          ${design.name}
          % if design.desc:
            <p class="ccs-info_text" data-help-direction="6">${design.desc}</p>
          % endif
        </label>
      % else:
        <label>New Query</label>
      % endif
      <ul class="query_edit_actions clearfix">
        <li class="ccs-button_bar bw-query_save_buttons">
          <a href="${ url('beeswax.views.execute_query') }"
            class="ccs-art_button bw-query_new"
            data-icon-styles="{'width': 16, 'height': 16, 'top': 4, 'left': 5}">New</a>

          % if design and not design.is_auto and design.name:
            <input type="submit" name="saveform-save" value="Save" class="ccs-art_button bw-query_save"
              data-icon-styles="{'width':16,'height':16, 'left':7}"/>
          % endif
          <input type="submit" name="saveform-saveas" value="Save As..." class="ccs-art_button bw-query_save_as"
            data-icon-styles="{'width':16,'height':16, 'left':7}"/>
          <a href="#settings" class="ccs-art_button bw-query_settings_toggle" data-icon-styles="{'width':16, 'height': 16}">Advanced</a>
          <input type="submit" name="button-explain" value="Explain" class="ccs-art_button bw-query_explain"
           data-icon-styles="{'width':16,'height':16, left: 7}"/>
          <input type="submit" name="button-submit" value="Execute" class="ccs-art_button bw-query_execute"
           data-icon-styles="{'width':16,'height':16, 'left':52, 'top':3}"/>
        </li>
      </ul>
    </dt>
    <dd class="bw-query_bottom default" style="height: auto;">
      <textarea class="bw-query-field ccs-simple-posteditor" data-filters="OverText"
        alt="Example: SELECT * FROM tablename" name="${form.query["query"].html_name | n}">${extract_field_data(form.query["query"]) or ''}</textarea>
        % if len(form.query["query"].errors):
          <div class="validation-advice">
             ${str(form.query["query"].errors) | n}
          </div>
        % endif
    </dd>
  </dl>
  <div class="bw-query_save_form">
    ${comps.field(form.saveform['name'])}
    ${comps.field(form.saveform['desc'])}
  </div>
</%def>



${wrappers.head('Hive Query', section='query')}
% if error_message:
<div class="alert_popup jframe_renders">
  <dl class="bw-query">
    <dt class="ccs-dt_cap">Your Query Has the Following Error(s):</dt>
    <dd class="ccs-dd_bottom ccs-error">
      <div class="validation-advice">
        ${error_message}
      </div>
      % if log:
        <div class="bw-error_tab_msg">
          (click the <b>Error Log</b> tab above for details)
        </div>
      % endif
    </dd>
  </dl>
</div>
% endif

<div class="view" id="execute">
  <form action="${action}" method="POST" class="form-validator">
    <div class="splitview resizable">
      <%
        if form.settings.forms or form.file_resources.forms or form.functions.forms:
          width = 230
        else:
          width = 0
      %>
      <div class="left_col" style="width: ${width}px;">
        <a name="settings"></a>
        <dl class="jframe_padded bw-query_settings">
          <dt class="ccs-dt_cap">Hive Settings</dt>
          <dd class="ccs-dd_bottom">
            <dl>
              % for i, f in enumerate(form.settings.forms):
                % if i > 0:
                  <hr/>
                % endif
                ${comps.field(f['key'], attrs=dict(
                  alt="mapred.reduce.tasks",
                  data_filters="OverText"
                ))}
                <div class="bw-query_settings_delete">
                  ${comps.field(f['_deleted'], tag="button", button_text="x", notitle=True, attrs=dict(
                      type="submit",
                      title="Delete this setting"
                    ), value=True)}
                </div>

                ${comps.field(f['value'], attrs=dict(
                  alt="1",
                  data_filters="OverText",
                ))}
                ${comps.field(f['_exists'], hidden=True)}
              % endfor
              <div class="bw-query_settings_add">
                <button id="id_settings-add" value="True" name="settings-add" type="submit">+</button>
                <div class="ccs-hidden">${str(form.settings.management_form) | n }</div>
              </div>
            </dl>
          </dd>
          <dt class="ccs-dt_cap">File Resources</dt>
          <dd class="ccs-dd_bottom">
            <dl>
              % for i, f in enumerate(form.file_resources.forms):
                % if i > 0:
                  <hr/>
                % endif

                ${comps.field(f['type'], render_default=True)}
                <div class="bw-query_settings_delete">
                  ${comps.field(f['_deleted'], tag="button", button_text="x", notitle=True, attrs=dict(
                      type="submit",
                      title="Delete this setting"
                    ), value=True)}
                </div>

                ${comps.field(f['path'], attrs=dict(
                  alt="/user/foo/udf.jar",
                  data_filters="OverText",
                ))}
                <div class="ccs-button_subbar_below clearfix">
                  <a class="ccs-art_button ccs-choose_file" data-chooseFor="${f['path'].html_name | n}" data-icon-styles="{'width':16, 'height':16, 'top':2}">Choose a File</a>
                </div>
                ${comps.field(f['_exists'], hidden=True)}
              % endfor
              <div class="bw-query_settings_add">
                <button id="id_file_resources-add" value="True" name="file_resources-add" type="submit">+</button>
                <div class="ccs-hidden">${str(form.file_resources.management_form) | n }</div>
              </div>
            </dl>
          </dd>
          <dt class="ccs-dt_cap">User-defined Functions</dt>
          <dd class="ccs-dd_bottom">
            <dl>
              % for i, f in enumerate(form.functions.forms):
                % if i > 0:
                  <hr/>
                % endif

                ${comps.field(f['name'], attrs=dict(
                  alt="myFunction",
                  data_filters="OverText",
                ))}
                <div class="bw-query_settings_delete">
                  ${comps.field(f['_deleted'], tag="button", button_text="x", notitle=True, attrs=dict(
                      type="submit",
                      title="Delete this setting"
                    ), value=True)}
                </div>

                ${comps.field(f['class_name'], attrs=dict(
                  alt="com.acme.example",
                  data_filters="OverText",
                ))}
                ${comps.field(f['_exists'], hidden=True)}
              % endfor
              <div class="bw-query_settings_add">
                <button id="id_functions-add" value="True" name="functions-add" type="submit">+</button>
                <div class="ccs-hidden">${str(form.functions.management_form) | n }</div>
              </div>
            </dl>
          </dd>
          <dt class="ccs-dt_cap">Parameterization</dt>
          <dd class="ccs-dd_bottom">
            <dl class="ccs-bw_parameters">
              ${comps.field(form.query["is_parameterized"],
                  notitle = True,
                  tag = "checkbox",
                  button_text = "Enable Parameterization", 
                  help = "If checked (the default), you can include parameters like $parameter_name in your query, and users will be prompted for a value when the query is run.",
                  help_attrs= dict(
                    data_help_direction='11'
                  )
              )}
            </dl>
          </dd>
          <dt class="ccs-dt_cap">Email Notification</dt>
          <dd class="ccs-dd_bottom">
            <dl class="ccs-bw_parameters">
          ${comps.field(form.query["email_notify"],
                        notitle = True,
                        tag = "checkbox",
                        button_text = "Email me on complete",
                        help = "If checked, you will receive an email notification when the query completes.",
                        help_attrs= dict(
                          data_help_direction='11'
                        )
                       )}
            </dl>
          </dd>
        </dl>
      </div>
      <div class="right_col">
        % if on_success_url:
          <input type="hidden" name="on_success_url" value="${on_success_url}"/>
        % endif

        % if error_messages or log:
          <div class="ccs-tab_ui">
            <ul class="toolbar bw-results_tabs ccs-tabs ccs-right clearfix">
              <li><span>Query</span></li>
              % if error_message or log:
              <li><span>
                % if log:
                  Error Log
                % endif
              </span></li>
              % endif
            </ul>
            <ul class="ccs-tab_sections ccs-clear">
              <li>
                ${query()}
              </li>
              % if log:
                <li class="jframe_padded">
                  % if log:
                    <pre>${log}</pre>
                  % endif
                </li>
              % endif
            </ul>
          </div>
        % else:
          ${query()}
        % endif

      </div>
    </div>
  </form>
</div>
${wrappers.foot()}
