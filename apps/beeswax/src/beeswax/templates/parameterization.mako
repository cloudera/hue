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
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="layout" file="layout.mako" />
${commonheader("Parameterize Hive Query", "beeswax", "100px")}
${layout.menubar()}
<div class="container-fluid">
<div class="prompt_popup">
Please specify parameters for this query.
<%
if explain:
  action = url('beeswax.views.explain_parameterized_query', design.id)
else:
  action = url('beeswax.views.execute_parameterized_query', design.id)
%>
<form method="POST" action=${action}>
<dl>
% for field in form:
  ${comps.field(field)}
% endfor
</dl>
<input class="jframe-hidden" type="submit">
</form>
</div>
</div>
${commonfooter()}
