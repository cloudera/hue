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
from desktop.lib.i18n import smart_unicode
from desktop.views import commonheader, commonfooter
import re
%>
<%namespace name="layout" file="about_layout.mako" />
${commonheader("About", "about", "100px")}
${layout.menubar(section='log_view')}
	<div class="container-fluid">
		<h1>Log entries (most recent first)</h1>

		<a href="/download_logs">Download entire log as zip</a>
		<hr/>
		<% log.reverse() %>
		<pre>
		% for l in log:
${smart_unicode(l) | h}
		% endfor
		</pre>

	</div>

${commonfooter()}
