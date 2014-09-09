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
    from django.utils.translation import ugettext as _
%>

<%def name="render()">
    <div class="actionbar-main" style="padding: 10px;">
        <div class="pull-right actionbar-creation">
            %if hasattr(caller, "creation"):
                ${caller.creation()}
            %endif
        </div>
        <div class="actionbar-actions">
            %if hasattr(caller, "search"):
                ${caller.search()}
            %else:
                <input id="filterInput" type="text" class="input-xlarge search-query" placeholder="${_('Search...')}">
            %endif
            %if hasattr(caller, "actions"):
                &nbsp;&nbsp;&nbsp;&nbsp;
                ${caller.actions()}
            %endif
        </div>
    </div>
</%def>