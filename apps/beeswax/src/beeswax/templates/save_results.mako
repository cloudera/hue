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
<%namespace name="layout" file="layout.mako" />
<%namespace name="comps" file="beeswax_components.mako" />
<%namespace name="util" file="util.mako" />
${commonheader("Beeswax: Create table from file", "beeswax", "100px")}
${layout.menubar(section='history')}
<div class="container-fluid">
% if error_msg:
<h4>${error_msg}</h4>
% endif

<form action="${action}" method="POST" data-filters="FormValidator">
  ${util.render_form(form)}
  <input type="submit" name="save" value="Save"/>
  <input type="submit" name="cancel" value="Cancel"/>
</form>
</div>
${commonfooter()}
