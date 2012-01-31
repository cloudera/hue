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
##
##
## no spaces in this method please; we're declaring a CSS class, and ART uses this value for stuff, and it splits on spaces, and 
## multiple spaces and line breaks cause issues
<%!
def is_selected(section, matcher):
  if section == matcher:
    return "selected"
  else:
    return ""
%>

<%def name="menubar(section='')">
	<div class="menubar">
		<div class="menubar-inner">
			<div class="container-fluid">
				<ul class="nav">
					<li><a href="/beeswax/execute" class="${is_selected(section, 'query')}">Query Editor</a></li>
					<li><a href="/beeswax/my_queries" class="${is_selected(section, 'my queries')}">My Queries</a></li>
					<li><a href="/beeswax/list_designs" class="${is_selected(section, 'saved queries')}">Saved Queries</a></li>
					<li><a href="/beeswax/query_history" class="${is_selected(section, 'history')}">History</a></li>
					<li><a href="/beeswax/tables" class="${is_selected(section, 'tables')}">Tables</a></li>
					<li><a href="/beeswax/configuration" class="${is_selected(section, 'hive configuration')}">Settings</a></li>
				</ul>
			</div>
		</div>
	</div>
</%def>

