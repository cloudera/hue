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
from desktop.views import commonheader, commonfooter
%>
<% import urllib %>
<div class="container-fluid">
  % if username:
	${commonheader('Edit User: ' + username + ' -- Hue Users', "useradmin")}
	<h1>Edit User: ${username} -- Hue Users</h1>
  % else:
    ${commonheader('Create User -- Hue Users', "useradmin")}
    <h1>Create User -- Hue Users</h1>
  % endif
	<form action="${urllib.quote(action)}" method="POST" class="jframe_padded">
		<fieldset>
			<legend> 
			  % if username:
		        Edit User: ${username}
		      % else:
		        Create User 
		      % endif
			</legend>
        <%def name="render_field(field)">
			<div class="clearfix">
				${field.label_tag() | n}
				<div class="input">
					${unicode(field) | n}
				</div>
				% if len(field.errors):
					${unicode(field.errors) | n}
				% endif
			</div>
		</%def>
          
		% for field in form:
			${render_field(field)}
		% endfor
        </fieldset>
		<div class="actions">
			<input type="submit" value="Save" class="btn primary"/>
		</div>
	</form>
</div>
${commonfooter()}
