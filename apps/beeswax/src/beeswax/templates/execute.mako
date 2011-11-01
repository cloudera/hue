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

		<fieldset>
			% if design and not design.is_auto and design.name:
		          <legend>${design.name}</legend>
		          % if design.desc:
		            <p>${design.desc}</p>
		          % endif

		      % else:
		        <legend>Query</legend>
		      % endif

          <div class="clearfix">
            <div class="input">
              <textarea class="xxlarge" rows="5"
		        placeholder="Example: SELECT * FROM tablename" name="${form.query["query"].html_name | n}" id="queryField">${extract_field_data(form.query["query"]) or ''}</textarea>
            </div>
          </div><!-- /clearfix -->
        </fieldset>
		 % if len(form.query["query"].errors):
	          <div class="validation-advice">
	             ${unicode(form.query["query"].errors) | n}
	          </div>
	        % endif
		<div class="actions">
			<input type="submit" name="button-submit" value="Execute" class="btn primary"/>
			% if design and not design.is_auto and design.name:
            <input type="submit" name="saveform-save" value="Save" class="btn"/>
          	% endif
          	<input type="submit" name="saveform-saveas" value="Save As..." class="btn" />
          
			<input type="submit" name="button-explain" value="Explain" class="btn" />
			&nbsp; or <a href="${ url('beeswax.views.execute_query') }">create a new query</a>
		</div>
          
          

      
 <!--      
<a href="#settings">see the advanced settings</a>
    <div>
      ${comps.field(form.saveform['name'])}
      ${comps.field(form.saveform['desc'])}
    </div>
-->
</%def>



${wrappers.head('Hive Query', section='query')}
<h1>Query Editor</h1>
% if error_message:
<div class="alert_popup jframe_renders">
  <dl class="bw-query_error">
    <dt class="hue-dt_cap">Your Query Has the Following Error(s):</dt>
    <dd class="hue-dd_bottom jframe-error">
      <div class="validation-advice">
        ${error_message}
      </div>
      % if log:
        <div class="bw-error_tab_msg">
          (click the <b>Error Log</b> tab above the editor input for details)
        </div>
      % endif
    </dd>
  </dl>
</div>
% endif
<div class="sidebar">
	<div class="well">
		<h6>Advanced settings</h6>
		<h5>Hive settings</h5>
		<h5>File Resources</h5>
		<h5>User-defined Functions</h5>
		<h5>Parametrization</h5>
		<h5>Email Notification</h5>
    </div>
</div>

<div class="content">
<div class="view" id="execute">
  <form action="${action}" method="POST" class="form-stacked">
    <div class="resizable" data-filters="SplitView">

	<%
      if form.settings.forms or form.file_resources.forms or form.functions.forms:
        width = 230
      else:
        width = 0
    %>

	    

    <div class="left_col" style="width: ${width}px;display:none">
      <a name="settings"></a>
      <dl class="jframe_padded bw-query_settings">
        <dt class="hue-dt_cap">Hive Settings</dt>
        <dd class="hue-dd_bottom">
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
              <div class="jframe-hidden">${unicode(form.settings.management_form) | n }</div>
            </div>
          </dl>
        </dd>
        <dt class="hue-dt_cap">File Resources</dt>
        <dd class="hue-dd_bottom">
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
              <div class="jframe-button_subbar_below clearfix">
                <a class="hue-choose_file" data-filters="ArtButton" data-chooseFor="${f['path'].html_name | n}" data-icon-styles="{'width':16, 'height':16, 'top':2}">Choose a File</a>
              </div>
              ${comps.field(f['_exists'], hidden=True)}
            % endfor
            <div class="bw-query_settings_add">
              <button id="id_file_resources-add" value="True" name="file_resources-add" type="submit">+</button>
              <div class="jframe-hidden">${unicode(form.file_resources.management_form) | n }</div>
            </div>
          </dl>
        </dd>
        <dt class="hue-dt_cap">User-defined Functions</dt>
        <dd class="hue-dd_bottom">
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
              <div class="jframe-hidden">${unicode(form.functions.management_form) | n }</div>
            </div>
          </dl>
        </dd>
        <dt class="hue-dt_cap">Parameterization</dt>
        <dd class="hue-dd_bottom">
          <dl class="hue-bw_parameters">
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
        <dt class="hue-dt_cap">Email Notification</dt>
        <dd class="hue-dd_bottom">
          <dl class="hue-bw_parameters">
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
          <div data-filters="Tabs">
            <ul class="toolbar bw-results_tabs jframe-right clearfix tabs" data-filters="Tabs">
              <li><span>Query</span></li>
              % if error_message or log:
              <li><span>
                % if log:
                  Error Log
                % endif
              </span></li>
              % endif
            </ul>
            <ul class="tab_sections jframe-clear">
              <li>
                ${query()}
              </li>
              % if error_message or log:
                <li class="bw-results_log jframe_padded">
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

    </div>
  </form>
</div>
${wrappers.foot()}
