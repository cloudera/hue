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

## Note that this is similar to the config_dump management command.
<%!
from desktop.lib.conf import BoundContainer, is_anonymous
from desktop.views import commonheader, commonfooter
%>
<%namespace name="layout" file="about_layout.mako" />
${commonheader("About", "about", "100px")}
${layout.menubar(section='dump_config')}

	<div class="container-fluid">

		Configuration files located in <code>${conf_dir}</code>
		<br/><br/>

		<h2>Installed applications</h2>
		<ul>
		% for app in sorted(apps, key=lambda app: app.name.lower()):
			<li>${app.name}</li>
		% endfor
		</ul>

		<h2>Configuration Sections and Variables</h2>

		<ul class="nav nav-tabs">
			% for obj in top_level.get().values():
				<li><a href="#${obj.config.key}Conf" data-toggle="tab">${obj.config.key}</a></li>
			% endfor
		</ul>

		<%def name="showTopLevel(config_obj, depth=0)">
			<div class="tab-content">
				% if isinstance(config_obj, BoundContainer):
					% for v in config_obj.get().values():
				<%
				      # Don't recurse into private variables.
				      if v.config.private and not show_private:
				        continue
				%>
					<div id="${v.config.key}Conf" class="tab-pane">
				    	${recurse(v, depth + 1)}
					</div>
				    % endfor
				% endif
			</div>
		</%def>

		<%def name="recurse(config_obj, depth=0)">
			<table class="table table-striped">
			<tr>
			 % if depth > 1:
			  <th>
			  % if is_anonymous(config_obj.config.key):
			    <i>(default section)</i>
			  % else:
			    ${config_obj.config.key}
			  % endif
			  </th>
			 % endif
    		 % if depth == 1:
				<td style="border-top:0">
	         % else:
			  	<td>
			 % endif
			  % if isinstance(config_obj, BoundContainer):
			    <p class="dump_config_help"><i>${config_obj.config.help or "No help available."}</i></p>

			    % for v in config_obj.get().values():
			<%
			      # Don't recurse into private variables.
			      if v.config.private and not show_private:
			        continue
			%>
			    ${recurse(v, depth + 1)}
			    % endfor
			  % else:
			    <p>${str(config_obj.get())}</p>
			    <p class="dump_config_help"><i>${config_obj.config.help or "No help available."}</i></p>
			    <p class="dump_config_default">Default: <i>${config_obj.config.default}</i></p>
			  % endif
			  </td>
			</tr>
			</table>
		</%def>


		${showTopLevel(top_level)}

		<br/>
		<br/>
		<br/>

	</div>


${commonfooter()}