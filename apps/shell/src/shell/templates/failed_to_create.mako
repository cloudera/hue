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

${commonheader("Hue Shell", "shell")}
<div class="container-fluid">
<div>
	Failed to create a shell of the given type. The possible reasons for this are:
	<ol>
		<li>The system is out of PTYs.</li>
		<li>The system cannot create more subprocesses.</li>
		<li>You do not have permission to create shells of this type.</li>
		<li>There is no shell with that name.</li>
		<li>There is no Unix user account for you.</li>
	</ol>
</div>
</div>
${commonfooter()}
