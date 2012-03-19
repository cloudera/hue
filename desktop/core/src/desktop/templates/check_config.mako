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
from desktop.lib.conf import BoundConfig
from desktop.views import commonheader, commonfooter
%>
<%namespace name="layout" file="about_layout.mako" />
${commonheader("About", "about", "100px")}
${layout.menubar(section='check_config')}

	<div class="container-fluid">

		Configuration files located in <code>${conf_dir}</code>
		<br/><br/>
		% if error_list:
	      <h2>Potential misconfiguration detected. Please fix and restart HUE.</h2>
		  <br/>
			<table class="table table-striped">
	      % for confvar, error in error_list:
			<tr>
				<td width="5%">
					<code>
		            % if isinstance(confvar, str):
		              ${confvar | n}
		            % else:
		              ${confvar.get_fully_qualifying_key()}
		            % endif
		          </code>
		        </td>
				<td>
		          ## Doesn't make sense to print the value of a BoundContainer
		          % if type(confvar) is BoundConfig:
		            Current value: <code>${confvar.get()}</code><br/>
		          % endif
		          ${error | n}
	        	</td>
			</tr>
	      % endfor
		</table>
	    % else:
	      <h2>All ok. Configuration check passed!</h2>
	    % endif

	</div>


${commonfooter()}

